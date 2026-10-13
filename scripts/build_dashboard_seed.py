#!/usr/bin/env python3
"""Create the bounded, idempotent hosted-dashboard seed from the verified local D1 database."""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
from pathlib import Path


TABLE_KEYS = {
    "runs": {
        "run_id": "runId", "source_rows": "sourceRows", "sampled_nonempty": "sampledNonempty",
        "completed": "completed", "quarantined": "quarantined", "unique_texts": "uniqueTexts",
        "cache_reuse_rows": "cacheReuseRows", "provider": "provider", "model": "model",
        "cost_usd": "costUsd", "elapsed_seconds": "elapsedSeconds", "generated_at": "generatedAt",
    },
    "topic_metrics": {"run_id": "runId", "topic": "topic", "review_count": "reviewCount", "complaint_count": "complaintCount", "mean_severity": "meanSeverity", "mean_sentiment": "meanSentiment"},
    "intent_metrics": {"run_id": "runId", "intent": "intent", "review_count": "reviewCount"},
    "monthly_trends": {"run_id": "runId", "month": "month", "review_count": "reviewCount", "complaint_count": "complaintCount", "complaint_share": "complaintShare", "mean_severity": "meanSeverity", "mean_sentiment": "meanSentiment", "partial_month": "partialMonth"},
    "issue_rankings": {"run_id": "runId", "rank": "rank", "issue_id": "issueId", "complaint_count": "complaintCount", "severity_sum": "severitySum", "mean_severity": "meanSeverity", "priority_score": "priorityScore"},
    "recommendations": {"recommendation_id": "recommendationId", "run_id": "runId", "title": "title", "summary": "summary", "primary_issue_id": "primaryIssueId", "alternatives": "alternatives", "limitations": "limitations", "model": "model", "created_at": "createdAt"},
    "recommendation_claims": {"recommendation_id": "recommendationId", "claim_id": "claimId", "issue_id": "issueId", "metric": "metric", "value": "value", "evidence_review_ids": "evidenceReviewIds"},
    "evaluation_summary": {"run_id": "runId", "golden_size": "goldenSize", "topic_accuracy": "topicAccuracy", "intent_accuracy": "intentAccuracy", "severity_exact_accuracy": "severityExactAccuracy", "severity_mae": "severityMae", "sentiment_mae": "sentimentMae", "ambiguous_cases": "ambiguousCases"},
    "review_results": {"review_id": "reviewId", "run_id": "runId", "source_sha256": "sourceSha256", "topic": "topic", "intent": "intent", "sentiment": "sentiment", "severity": "severity", "needs_review": "needsReview", "review_rating": "reviewRating", "review_timestamp": "reviewTimestamp", "evidence_quote": "evidenceQuote", "cache_source_id": "cacheSourceId", "label_config": "labelConfig"},
}

BOOLEAN_FIELDS = {"partialMonth", "needsReview"}

PUBLIC_CONTACT_PATTERNS = (
    re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.IGNORECASE),
    re.compile(r"https?://|www\.", re.IGNORECASE),
    re.compile(r"(?:\+?[0-9][ .()_-]){7,}[0-9]"),
    re.compile(r"(?<![0-9])(?:[0-9][ -]){12,18}[0-9](?![0-9])"),
)
PUBLIC_HIGH_RISK_TERMS = re.compile(
    r"\b(?:hack(?:ed|er|ing)?|scam(?:med|ming)?|fraud\w*|stole(?:n)?|steal(?:ing)?|"
    r"breach(?:ed)?|spy|privacy|track(?:ed|er|ing)?|advertis(?:e|ing)|merchant|"
    r"email|data|card|bank|permission|suicid(?:e|al)|kill(?:ed|ing)?|porn|racist|"
    r"nazi|fuck|shit|trash|stupid|suck\w*)\b",
    re.IGNORECASE,
)


def safe_public_evidence(text: str) -> bool:
    """Keep public examples product-focused and free of obvious contact/high-risk text."""
    return (
        0 < len(text) <= 500
        and not any(pattern.search(text) for pattern in PUBLIC_CONTACT_PATTERNS)
        and not PUBLIC_HIGH_RISK_TERMS.search(text)
    )


def convert(table: str, row: sqlite3.Row) -> dict[str, object]:
    result = {target: row[source] for source, target in TABLE_KEYS[table].items()}
    for field in BOOLEAN_FIELDS & result.keys():
        result[field] = bool(result[field])
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--evidence-per-issue", type=int, default=3)
    args = parser.parse_args()
    with sqlite3.connect(args.database) as db:
        db.row_factory = sqlite3.Row
        payload: dict[str, list[dict[str, object]]] = {}
        for table in TABLE_KEYS:
            if table == "review_results":
                continue
            payload[table] = [convert(table, row) for row in db.execute(f"SELECT * FROM {table}")]
        for recommendation in payload["recommendations"]:
            recommendation["title"] = "The Business Question Comes First: Focus on Usability"
        evidence = []
        for topic in ("access", "usability", "playback", "downloads", "catalog", "billing", "support", "other"):
            rows = db.execute(
                """SELECT * FROM review_results
                WHERE topic = ? AND intent IN ('complaint', 'cancellation') AND needs_review = 0
                ORDER BY severity DESC, review_id""",
                (topic,),
            )
            selected = []
            for row in rows:
                if safe_public_evidence(row["evidence_quote"]):
                    selected.append(convert("review_results", row))
                if len(selected) == args.evidence_per_issue:
                    break
            if len(selected) != args.evidence_per_issue:
                raise RuntimeError(f"Not enough safe public evidence for {topic}: {len(selected)}")
            evidence.extend(selected)
        payload["review_results"] = evidence
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"path": str(args.out), "evidence_rows": len(evidence)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
