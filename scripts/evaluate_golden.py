#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import sqlite3
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from spotify_pipeline.core import FIELDS, LABEL_CONFIG  # noqa: E402
from spotify_pipeline.scalable import text_sha  # noqa: E402


def prepare(source: Path, output: Path) -> None:
    with source.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle, strict=True))
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows([{field: row[field] for field in FIELDS} for row in rows])
    print(json.dumps({"rows": len(rows), "output": str(output.resolve())}, indent=2))


def accuracy(human: list[dict[str, Any]], model: list[dict[str, Any]], field: str) -> float:
    return sum(a[field] == b[field] for a, b in zip(human, model, strict=True)) / len(human)


def macro_f1(human: list[dict[str, Any]], model: list[dict[str, Any]], field: str) -> float:
    labels = sorted({row[field] for row in human} | {row[field] for row in model})
    scores: list[float] = []
    for label in labels:
        tp = sum(a[field] == label and b[field] == label for a, b in zip(human, model, strict=True))
        fp = sum(a[field] != label and b[field] == label for a, b in zip(human, model, strict=True))
        fn = sum(a[field] == label and b[field] != label for a, b in zip(human, model, strict=True))
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        scores.append(2 * precision * recall / (precision + recall) if precision + recall else 0.0)
    return sum(scores) / len(scores) if scores else 0.0


def confusion(human: list[dict[str, Any]], model: list[dict[str, Any]], field: str) -> dict[str, dict[str, int]]:
    counts: dict[str, Counter[str]] = {}
    for a, b in zip(human, model, strict=True):
        counts.setdefault(str(a[field]), Counter())[str(b[field])] += 1
    return {label: dict(sorted(values.items())) for label, values in sorted(counts.items())}


def evaluate(labels_path: Path, state_path: Path, json_out: Path, markdown_out: Path) -> None:
    human = json.loads(labels_path.read_text(encoding="utf-8"))
    if len(human) != 50:
        raise ValueError(f"Expected 50 human labels, found {len(human)}")
    with sqlite3.connect(state_path) as db:
        db.row_factory = sqlite3.Row
        saved = {
            row["text_sha256"]: dict(row)
            for row in db.execute("SELECT * FROM predictions WHERE label_config = ?", (LABEL_CONFIG,))
        }
    model: list[dict[str, Any]] = []
    for row in human:
        prediction = saved.get(text_sha(row["review_text"]))
        if prediction is None:
            raise ValueError(f"Missing prediction for {row['review_id']}")
        model.append(prediction)

    disagreements: list[dict[str, Any]] = []
    fields = ("topic", "intent", "sentiment", "severity", "needs_review")
    for gold, pred in zip(human, model, strict=True):
        differing = [field for field in fields if gold[field] != pred[field]]
        if differing:
            disagreements.append(
                {
                    "review_id": gold["review_id"],
                    "review_text": gold["review_text"],
                    "differing_fields": differing,
                    "human": {field: gold[field] for field in fields},
                    "model": {field: pred[field] for field in fields},
                }
            )

    topic_accuracy = accuracy(human, model, "topic")
    intent_accuracy = accuracy(human, model, "intent")
    severity_accuracy = accuracy(human, model, "severity")
    needs_review_accuracy = accuracy(human, model, "needs_review")
    severity_mae = sum(abs(a["severity"] - b["severity"]) for a, b in zip(human, model, strict=True)) / len(human)
    sentiment_mae = sum(abs(float(a["sentiment"]) - float(b["sentiment"])) for a, b in zip(human, model, strict=True)) / len(human)
    joint_exact = sum(all(a[field] == b[field] for field in fields) for a, b in zip(human, model, strict=True)) / len(human)
    result = {
        "evaluated_at": datetime.now(timezone.utc).isoformat(),
        "label_config": LABEL_CONFIG,
        "records": len(human),
        "metrics": {
            "topic_accuracy": topic_accuracy,
            "topic_macro_f1": macro_f1(human, model, "topic"),
            "intent_accuracy": intent_accuracy,
            "intent_macro_f1": macro_f1(human, model, "intent"),
            "severity_exact_accuracy": severity_accuracy,
            "severity_mae": severity_mae,
            "sentiment_mae": sentiment_mae,
            "needs_review_accuracy": needs_review_accuracy,
            "joint_exact_accuracy": joint_exact,
            "rows_with_any_disagreement": len(disagreements),
        },
        "topic_confusion": confusion(human, model, "topic"),
        "intent_confusion": confusion(human, model, "intent"),
        "disagreements": disagreements,
    }
    json_out.parent.mkdir(parents=True, exist_ok=True)
    json_out.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    metrics = result["metrics"]
    lines = [
        "# Golden 50 evaluation",
        "",
        "The frozen production configuration classified review text only. Human labels were loaded only after inference for comparison.",
        "",
        f"- Label configuration: `{LABEL_CONFIG}`",
        f"- Reviews: {len(human)}",
        f"- Topic accuracy: {metrics['topic_accuracy']:.1%}",
        f"- Topic macro F1: {metrics['topic_macro_f1']:.3f}",
        f"- Intent accuracy: {metrics['intent_accuracy']:.1%}",
        f"- Intent macro F1: {metrics['intent_macro_f1']:.3f}",
        f"- Severity exact accuracy: {metrics['severity_exact_accuracy']:.1%}",
        f"- Severity MAE: {metrics['severity_mae']:.3f}",
        f"- Sentiment MAE: {metrics['sentiment_mae']:.3f}",
        f"- Needs-review accuracy: {metrics['needs_review_accuracy']:.1%}",
        f"- Joint exact accuracy: {metrics['joint_exact_accuracy']:.1%}",
        f"- Rows with any disagreement: {len(disagreements)}",
        "",
        "## Disagreements",
        "",
    ]
    for item in disagreements:
        lines.extend(
            [
                f"### {item['review_id']}",
                "",
                f"Fields: {', '.join(item['differing_fields'])}",
                "",
                f"Review: {item['review_text']}",
                "",
                f"Human: `{json.dumps(item['human'], ensure_ascii=False, sort_keys=True)}`",
                "",
                f"Model: `{json.dumps(item['model'], ensure_ascii=False, sort_keys=True)}`",
                "",
            ]
        )
    markdown_out.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(result["metrics"], indent=2, sort_keys=True))


def main() -> None:
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)
    prep = commands.add_parser("prepare")
    prep.add_argument("--source", type=Path, required=True)
    prep.add_argument("--output", type=Path, required=True)
    score = commands.add_parser("score")
    score.add_argument("--labels", type=Path, required=True)
    score.add_argument("--state", type=Path, required=True)
    score.add_argument("--json-out", type=Path, required=True)
    score.add_argument("--markdown-out", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "prepare":
        prepare(args.source, args.output)
    else:
        evaluate(args.labels, args.state, args.json_out, args.markdown_out)


if __name__ == "__main__":
    main()
