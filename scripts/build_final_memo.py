#!/usr/bin/env python3
"""Create the bounded final recommendation with the local Ollama memo role."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from spotify_pipeline.core import MODEL, MODEL_DIGEST, canonical, ollama_chat, write_json  # noqa: E402


ISSUE_DESCRIPTIONS = {
    "issue_access": "Login, signup, password, and account-access problems.",
    "issue_usability": "Navigation, controls, layout, queue or playlist management, and ad interruptions.",
    "issue_playback": "Playback failures, crashes, lag, connection failures, audio quality, and resource use.",
    "issue_downloads": "Downloading, saved music, offline listening, and disappearing downloads.",
    "issue_catalog": "Missing music, search and discovery, recommendations, and lyrics availability.",
    "issue_billing": "Price, charges, subscriptions, paywalls, premium entitlement, and premium-only controls.",
    "issue_support": "Contacting support and the quality or timeliness of support responses.",
    "issue_other": "General praise or criticism and reviews without a supported specific product topic.",
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ranking", type=Path, required=True)
    parser.add_argument("--evaluation", type=Path, required=True)
    parser.add_argument("--out-json", type=Path, required=True)
    parser.add_argument("--out-markdown", type=Path, required=True)
    parser.add_argument("--call-log", type=Path, required=True)
    args = parser.parse_args()

    with args.ranking.open("r", encoding="utf-8", newline="") as handle:
        ranking = list(csv.DictReader(handle))
    for row in ranking:
        row["rank"] = int(row["rank"])
        row["complaint_count"] = int(row["complaint_count"])
        row["severity_sum"] = int(row["severity_sum"])
        row["priority_score"] = int(row["priority_score"])

    evaluation = json.loads(args.evaluation.read_text(encoding="utf-8"))
    metrics = evaluation["metrics"]
    verification = {
        "sample_size": evaluation["records"],
        "topic_agreement": metrics["topic_accuracy"],
        "intent_agreement": metrics["intent_accuracy"],
        "severity_exact_agreement": metrics["severity_exact_accuracy"],
        "severity_mae": metrics["severity_mae"],
    }
    issue_catalog = {
        "issues": [
            {
                "issue_id": row["issue_id"],
                "name": row["issue_id"].removeprefix("issue_").replace("_", " ").title(),
                "description": ISSUE_DESCRIPTIONS[row["issue_id"]],
            }
            for row in ranking
        ]
    }
    memo_input = {
        "business_question": "Where should Spotify focus next-quarter product effort?",
        "ranking": ranking,
        "issues": issue_catalog["issues"],
        "held_out_evaluation": verification,
        "sample_scope": {
            "sampled_reviews": 100000,
            "source_reviews": 660622,
            "sampling": "deterministic pseudorandom sample across the full source window",
        },
    }
    issue_ids = [row["issue_id"] for row in ranking]
    schema = {
        "type": "object",
        "additionalProperties": False,
        "required": ["priority_issue_id", "recommendation", "alternative_issue_ids", "limitations"],
        "properties": {
            "priority_issue_id": {"type": "string", "enum": issue_ids},
            "recommendation": {"type": "string"},
            "alternative_issue_ids": {"type": "array", "items": {"type": "string", "enum": issue_ids}},
            "limitations": {"type": "array", "items": {"type": "string"}, "minItems": 3},
        },
    }
    memo, calls = ollama_chat(
        role="final-memo",
        system=(
            "Answer the supplied Spotify business question with one concise executive recommendation. "
            "Use the deterministic ranking as evidence: name the selected issue, cite its exact complaint count "
            "and severity sum, and propose a concrete next-quarter discovery or product action. Mention a higher-"
            "severity secondary issue if useful. Treat issue_other as a taxonomy bucket, not a product feature. "
            "State at least three real limitations: self-selected historical reviews, classification uncertainty "
            "or the held-out sample, and no causal/revenue/customer-outcome data. Use only supplied facts; do not "
            "invent counts, customers, revenue, or causal effects. Return structured JSON only."
        ),
        user=canonical(memo_input),
        schema=schema,
        review_ids=[],
        phase="final",
        label_config="final-100k-memo-v2",
        run_id="final-100k-memo",
    )
    if memo.get("priority_issue_id") not in issue_ids:
        raise ValueError("Memo selected an unknown issue")
    ranked = {row["issue_id"]: row for row in ranking}
    priority = ranked[memo["priority_issue_id"]]
    markdown = (
        "# Final Decision Memo\n\n"
        "## Recommendation\n\n"
        f"{memo['recommendation']}\n\n"
        f"The deterministic ranking places `{priority['issue_id']}` first with "
        f"{priority['complaint_count']:,} complaint or cancellation records, a severity sum of "
        f"{priority['severity_sum']:,}, and mean severity {priority['mean_severity']}.\n\n"
        "## Alternatives\n\n"
        + (", ".join(f"`{value}`" for value in memo["alternative_issue_ids"]) or "No additional alternative was selected.")
        + "\n\n## Limitations\n\n"
        + "\n".join(f"- {item}" for item in memo["limitations"])
        + "\n\nThis memo describes the representative 100,000-review sample; it does not establish population-wide causality or business impact.\n"
    )
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    write_json(args.out_json, memo)
    args.out_markdown.write_text(markdown, encoding="utf-8")
    args.call_log.write_text("".join(canonical(call) + "\n" for call in calls), encoding="utf-8")
    print(json.dumps({
        "memo": str(args.out_json),
        "new_local_calls": len(calls),
        "model": f"{MODEL}@{MODEL_DIGEST}",
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
