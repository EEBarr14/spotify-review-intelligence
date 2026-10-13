#!/usr/bin/env python3
"""Score saved Jev predictions against the frozen Golden 50; makes no API calls."""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from spotify_pipeline.jev_scalable import text_sha  # noqa: E402


def accuracy(human: list[dict[str, Any]], model: list[dict[str, Any]], field: str) -> float:
    return sum(a[field] == b[field] for a, b in zip(human, model, strict=True)) / len(human)


def macro_f1(human: list[dict[str, Any]], model: list[dict[str, Any]], field: str) -> float:
    labels = sorted({str(row[field]) for row in human} | {str(row[field]) for row in model})
    scores: list[float] = []
    for label in labels:
        tp = sum(str(a[field]) == label and str(b[field]) == label for a, b in zip(human, model, strict=True))
        fp = sum(str(a[field]) != label and str(b[field]) == label for a, b in zip(human, model, strict=True))
        fn = sum(str(a[field]) == label and str(b[field]) != label for a, b in zip(human, model, strict=True))
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        scores.append(2 * precision * recall / (precision + recall) if precision + recall else 0.0)
    return sum(scores) / len(scores) if scores else 0.0


def confusion(human: list[dict[str, Any]], model: list[dict[str, Any]], field: str) -> dict[str, dict[str, int]]:
    counts: dict[str, Counter[str]] = {}
    for expected, actual in zip(human, model, strict=True):
        counts.setdefault(str(expected[field]), Counter())[str(actual[field])] += 1
    return {label: dict(sorted(values.items())) for label, values in sorted(counts.items())}


def select_config(db: sqlite3.Connection, requested: str | None) -> str:
    configs = [row[0] for row in db.execute("SELECT label_config FROM run_configs ORDER BY created_at")]
    if requested:
        if requested not in configs:
            raise ValueError(f"Unknown label configuration: {requested}")
        return requested
    if len(configs) != 1:
        raise ValueError(f"Expected one saved configuration, found {len(configs)}; use --label-config")
    return configs[0]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--labels", type=Path, required=True)
    parser.add_argument("--state", type=Path, required=True)
    parser.add_argument("--json-out", type=Path, required=True)
    parser.add_argument("--markdown-out", type=Path, required=True)
    parser.add_argument("--label-config")
    args = parser.parse_args()

    human = json.loads(args.labels.read_text(encoding="utf-8"))
    if len(human) != 50:
        raise ValueError(f"Expected 50 frozen human labels, found {len(human)}")

    with sqlite3.connect(args.state) as db:
        db.row_factory = sqlite3.Row
        selected = select_config(db, args.label_config)
        saved = {
            row["text_sha256"]: dict(row)
            for row in db.execute("SELECT * FROM predictions WHERE label_config = ?", (selected,))
        }

    missing = [row["review_id"] for row in human if text_sha(row["review_text"]) not in saved]
    if missing:
        raise ValueError(f"Missing {len(missing)} Golden-50 predictions; first IDs: {missing[:5]}")
    model = [saved[text_sha(row["review_text"])] for row in human]
    fields = ("topic", "intent", "sentiment", "severity", "needs_review")
    disagreements = []
    for gold, predicted in zip(human, model, strict=True):
        differing = [field for field in fields if gold[field] != predicted[field]]
        if differing:
            disagreements.append(
                {
                    "review_id": gold["review_id"],
                    "differing_fields": differing,
                    "human": {field: gold[field] for field in fields},
                    "model": {field: predicted[field] for field in fields},
                }
            )

    metrics = {
        "topic_accuracy": accuracy(human, model, "topic"),
        "topic_macro_f1": macro_f1(human, model, "topic"),
        "intent_accuracy": accuracy(human, model, "intent"),
        "intent_macro_f1": macro_f1(human, model, "intent"),
        "severity_exact_accuracy": accuracy(human, model, "severity"),
        "severity_mae": sum(abs(int(a["severity"]) - int(b["severity"])) for a, b in zip(human, model, strict=True)) / len(human),
        "sentiment_mae": sum(abs(float(a["sentiment"]) - float(b["sentiment"])) for a, b in zip(human, model, strict=True)) / len(human),
        "needs_review_accuracy": accuracy(human, model, "needs_review"),
        "joint_exact_accuracy": sum(all(a[field] == b[field] for field in fields) for a, b in zip(human, model, strict=True)) / len(human),
        "rows_with_any_disagreement": len(disagreements),
        "model_needs_review_count": sum(bool(row["needs_review"]) for row in model),
    }
    result = {
        "evaluated_at": datetime.now(timezone.utc).isoformat(),
        "label_config": selected,
        "records": len(human),
        "metrics": metrics,
        "topic_confusion": confusion(human, model, "topic"),
        "intent_confusion": confusion(human, model, "intent"),
        "disagreements": disagreements,
    }
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# Jev Golden 50 evaluation",
        "",
        "The frozen human answers were used only after model inference for comparison.",
        "",
        f"- Label configuration: `{selected}`",
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
                f"Human: `{json.dumps(item['human'], ensure_ascii=False, sort_keys=True)}`",
                "",
                f"Model: `{json.dumps(item['model'], ensure_ascii=False, sort_keys=True)}`",
                "",
            ]
        )
    args.markdown_out.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(metrics, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
