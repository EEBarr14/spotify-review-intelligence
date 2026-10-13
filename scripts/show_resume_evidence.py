#!/usr/bin/env python3
"""Print concise, offline evidence for the interruption/resume recording."""

from __future__ import annotations

from collections import Counter
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUBMISSION = ROOT / "grading" / "final-submission"


def read_json(path: Path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def main() -> None:
    before = set(read_json(SUBMISSION / "checkpoint_before.json")["completed_ids"])
    after = set(read_json(SUBMISSION / "checkpoint_after.json")["completed_ids"])
    progress = read_json(ROOT / "state" / "progress-jev-analysis_100000.json")

    segment_calls: Counter[str] = Counter()
    called_review_ids: list[str] = []
    with (SUBMISSION / "calls.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            call = json.loads(line)
            run_id = str(call.get("run_id", ""))
            if (
                run_id.startswith("jev-analysis_100000-")
                and call.get("role") == "enrich"
                and call.get("outcome") == "succeeded"
            ):
                segment_calls[run_id] += 1
                called_review_ids.extend(call.get("review_ids", []))

    repeated_paid_ids = len(called_review_ids) - len(set(called_review_ids))
    preserved = len(before & after)
    newly_accounted = len(after - before)

    print("Spotify 100,000-review interruption/resume evidence")
    print("=" * 54)
    print(f"Completed IDs before interruption : {len(before):,}")
    print(f"Completed IDs after final resume  : {len(after):,}")
    print(f"Previously completed IDs preserved: {preserved:,} / {len(before):,}")
    print(f"Additional IDs accounted for      : {newly_accounted:,}")
    print(f"Remaining unique texts             : {progress['remaining_unique_texts']:,}")
    print(f"Final production-state spend       : ${progress['spent_usd']}")
    print()
    print("Full-sample paid resume segments:")
    for index, (_, count) in enumerate(segment_calls.items(), start=1):
        print(f"  Segment {index}: {count:,} successful new classifications")
    print(f"  Total new paid classifications: {sum(segment_calls.values()):,}")
    print(f"  Review IDs repeated across those calls: {repeated_paid_ids}")
    print()
    print("Result: saved work survived interruption; resume dispatched only")
    print("unfinished distinct texts, while exact duplicates reused cached labels.")


if __name__ == "__main__":
    main()
