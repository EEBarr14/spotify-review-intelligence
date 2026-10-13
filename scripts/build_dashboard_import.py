#!/usr/bin/env python3
"""Build chunked D1 import SQL from final saved artifacts; makes no model calls."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sqlite3
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from spotify_pipeline.core import read_rows  # noqa: E402


TOPICS = ("access", "usability", "playback", "downloads", "catalog", "billing", "support", "other")
INTENTS = ("cancellation", "complaint", "request", "praise", "unclear")


def sql(value: Any) -> str:
    if value is None:
        return "NULL"
    if isinstance(value, bool):
        return "1" if value else "0"
    if isinstance(value, (int, float, Decimal)):
        return str(value)
    return "'" + str(value).replace("'", "''") + "'"


def statement(table: str, columns: list[str], rows: list[list[Any]]) -> str:
    names = ", ".join(columns)
    values = ",\n".join("(" + ", ".join(sql(value) for value in row) + ")" for row in rows)
    return f"INSERT INTO {table} ({names}) VALUES\n{values};\n"


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def state_metadata(state_path: Path, label_config: str | None) -> dict[str, Any]:
    with sqlite3.connect(state_path) as db:
        db.row_factory = sqlite3.Row
        configs = list(db.execute("SELECT * FROM run_configs ORDER BY created_at"))
        if label_config:
            configs = [row for row in configs if row["label_config"] == label_config]
        if len(configs) != 1:
            raise ValueError(f"Expected one Jev configuration, found {len(configs)}")
        config = configs[0]
        cost = sum(
            (Decimal(row[0]) for row in db.execute("SELECT cost_usd FROM calls WHERE label_config = ?", (config["label_config"],))),
            Decimal("0"),
        )
        elapsed = db.execute(
            "SELECT COALESCE(SUM(elapsed_seconds), 0) FROM run_history WHERE label_config = ?",
            (config["label_config"],),
        ).fetchone()[0]
    return {
        "label_config": config["label_config"],
        "model": config["resolved_model"] or config["requested_model"],
        "cost_usd": float(cost),
        "elapsed_seconds": float(elapsed),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sample", type=Path, required=True)
    parser.add_argument("--records", type=Path, required=True)
    parser.add_argument("--ranking", type=Path, required=True)
    parser.add_argument("--claims", type=Path, required=True)
    parser.add_argument("--evaluation", type=Path, required=True)
    parser.add_argument("--memo", type=Path, required=True)
    parser.add_argument("--state", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--label-config")
    parser.add_argument(
        "--cost-usd",
        type=Decimal,
        help="Audited production spend override; use when the shared state also contains gate calls.",
    )
    parser.add_argument(
        "--elapsed-seconds",
        type=float,
        help="Audited active production runtime override across resumable segments.",
    )
    parser.add_argument("--source-rows", type=int, default=660_622)
    parser.add_argument("--quarantined", type=int, default=13)
    parser.add_argument("--chunk-size", type=int, default=250)
    args = parser.parse_args()
    if args.out_dir.exists():
        raise ValueError(f"Output directory already exists: {args.out_dir}")
    if args.chunk_size < 1:
        raise ValueError("--chunk-size must be positive")

    sample = read_rows(args.sample)
    source = {row["review_id"]: row for row in sample}
    records = read_jsonl(args.records)
    if {row["review_id"] for row in records} != set(source):
        raise ValueError("Dashboard records do not exactly match the 100,000-review sample IDs")
    if any(row.get("status") != "completed" for row in records):
        raise ValueError("Dashboard import requires every sampled review to be completed")
    metadata = state_metadata(args.state, args.label_config)
    if args.cost_usd is not None:
        if args.cost_usd < 0:
            raise ValueError("--cost-usd cannot be negative")
        metadata["cost_usd"] = float(args.cost_usd)
    if args.elapsed_seconds is not None:
        if args.elapsed_seconds < 0:
            raise ValueError("--elapsed-seconds cannot be negative")
        metadata["elapsed_seconds"] = args.elapsed_seconds
    if any(row["label_config"] != metadata["label_config"] for row in records):
        raise ValueError("Record label configuration differs from selected Jev state")

    with args.ranking.open("r", encoding="utf-8", newline="") as handle:
        rankings = list(csv.DictReader(handle))
    with args.claims.open("r", encoding="utf-8", newline="") as handle:
        claims = list(csv.DictReader(handle))
    evaluation = json.loads(args.evaluation.read_text(encoding="utf-8"))
    memo = json.loads(args.memo.read_text(encoding="utf-8"))

    run_id = "spotify-100k-" + hashlib.sha256(metadata["label_config"].encode()).hexdigest()[:12]
    recommendation_id = run_id + "-recommendation"
    generated_at = datetime.now(timezone.utc).isoformat()
    text_counts = Counter(row["review_text"] for row in sample)
    topics: dict[str, list[dict[str, Any]]] = defaultdict(list)
    intents = Counter()
    months: dict[str, list[dict[str, Any]]] = defaultdict(list)
    evidence: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        original = source[record["review_id"]]
        topics[record["topic"]].append(record)
        intents[record["intent"]] += 1
        months[original["review_timestamp"][:7]].append(record)
        if record["intent"] in {"complaint", "cancellation"}:
            evidence[f"issue_{record['topic']}"] .append(record)

    args.out_dir.mkdir(parents=True)
    clear_order = [
        "recommendation_claims", "recommendations", "evaluation_summary", "issue_rankings",
        "monthly_trends", "intent_metrics", "topic_metrics", "review_results", "runs",
    ]
    (args.out_dir / "000_clear.sql").write_text(
        "\n".join(f"DELETE FROM {table};" for table in clear_order) + "\n",
        encoding="utf-8",
    )

    aggregate_sql = [
        statement(
            "runs",
            ["run_id", "source_rows", "sampled_nonempty", "completed", "quarantined", "unique_texts", "cache_reuse_rows", "provider", "model", "cost_usd", "elapsed_seconds", "generated_at"],
            [[run_id, args.source_rows, len(sample), len(records), args.quarantined, len(text_counts), len(sample) - len(text_counts), "TypeSafe Jev", metadata["model"], metadata["cost_usd"], metadata["elapsed_seconds"], generated_at]],
        )
    ]
    topic_rows = []
    for topic in TOPICS:
        values = topics.get(topic, [])
        complaint = [row for row in values if row["intent"] in {"complaint", "cancellation"}]
        topic_rows.append([
            run_id, topic, len(values), len(complaint),
            sum(float(row["severity"]) for row in values) / len(values) if values else 0,
            sum(float(row["sentiment"]) for row in values) / len(values) if values else 0,
        ])
    aggregate_sql.append(statement("topic_metrics", ["run_id", "topic", "review_count", "complaint_count", "mean_severity", "mean_sentiment"], topic_rows))
    aggregate_sql.append(statement("intent_metrics", ["run_id", "intent", "review_count"], [[run_id, intent, intents[intent]] for intent in INTENTS]))
    month_names = sorted(months)
    month_rows = []
    for month in month_names:
        values = months[month]
        complaints = [row for row in values if row["intent"] in {"complaint", "cancellation"}]
        month_rows.append([
            run_id, month, len(values), len(complaints), len(complaints) / len(values),
            sum(float(row["severity"]) for row in values) / len(values),
            sum(float(row["sentiment"]) for row in values) / len(values),
            month in {month_names[0], month_names[-1]},
        ])
    aggregate_sql.append(statement("monthly_trends", ["run_id", "month", "review_count", "complaint_count", "complaint_share", "mean_severity", "mean_sentiment", "partial_month"], month_rows))
    aggregate_sql.append(statement("issue_rankings", ["run_id", "rank", "issue_id", "complaint_count", "severity_sum", "mean_severity", "priority_score"], [[run_id, int(row["rank"]), row["issue_id"], int(row["complaint_count"]), int(row["severity_sum"]), float(row["mean_severity"]), int(row["priority_score"])] for row in rankings]))

    limitations = memo.get("limitations", [])
    if isinstance(limitations, list):
        limitations = " ".join(str(item) for item in limitations)
    recommendation = memo.get("recommendation") or memo.get("summary")
    primary_issue = memo.get("priority_issue_id") or memo.get("primary_issue_id")
    alternatives = memo.get("alternative_issue_ids") or memo.get("alternatives") or []
    ranked_issue_ids = {row["issue_id"] for row in rankings}
    if not recommendation or primary_issue not in ranked_issue_ids:
        raise ValueError("Memo must contain a recommendation and a ranked primary issue")
    aggregate_sql.append(statement("recommendations", ["recommendation_id", "run_id", "title", "summary", "primary_issue_id", "alternatives", "limitations", "model", "created_at"], [[recommendation_id, run_id, "The Business Question Comes First: Focus on Usability", recommendation, primary_issue, json.dumps(alternatives), limitations, "qwen3.5:4b-q4_K_M (local Ollama)", generated_at]]))
    claim_rows = []
    for claim in claims:
        if claim["issue_id"] != primary_issue:
            continue
        chosen = sorted(evidence.get(claim["issue_id"], []), key=lambda row: (-int(row["severity"]), row["review_id"]))[:3]
        claim_rows.append([recommendation_id, claim["claim_id"], claim["issue_id"], claim["metric"], claim["value"], json.dumps([row["review_id"] for row in chosen])])
    aggregate_sql.append(statement("recommendation_claims", ["recommendation_id", "claim_id", "issue_id", "metric", "value", "evidence_review_ids"], claim_rows))
    metrics = evaluation["metrics"]
    aggregate_sql.append(statement("evaluation_summary", ["run_id", "golden_size", "topic_accuracy", "intent_accuracy", "severity_exact_accuracy", "severity_mae", "sentiment_mae", "ambiguous_cases"], [[run_id, evaluation["records"], metrics["topic_accuracy"], metrics["intent_accuracy"], metrics["severity_exact_accuracy"], metrics["severity_mae"], metrics["sentiment_mae"], metrics.get("model_needs_review_count", 0)]]))
    (args.out_dir / "010_aggregates.sql").write_text("\n".join(aggregate_sql), encoding="utf-8")

    review_rows = []
    for record in records:
        original = source[record["review_id"]]
        review_rows.append([
            record["review_id"], run_id, record["source_sha256"], record["topic"], record["intent"],
            record["sentiment"], record["severity"], record["needs_review"], int(original["review_rating"]),
            original["review_timestamp"], record["evidence_quote"], record.get("cache_source_id"), record["label_config"],
        ])
    columns = ["review_id", "run_id", "source_sha256", "topic", "intent", "sentiment", "severity", "needs_review", "review_rating", "review_timestamp", "evidence_quote", "cache_source_id", "label_config"]
    files = []
    for start in range(0, len(review_rows), args.chunk_size):
        path = args.out_dir / f"100_reviews_{start // args.chunk_size + 1:04d}.sql"
        path.write_text(statement("review_results", columns, review_rows[start:start + args.chunk_size]), encoding="utf-8")
        files.append(path.name)
    manifest = {
        "run_id": run_id,
        "generated_at": generated_at,
        "records": len(records),
        "chunks": len(files),
        "apply_in_order": ["000_clear.sql", "010_aggregates.sql", *files],
        "preview_fixture_is_not_included": True,
    }
    (args.out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
