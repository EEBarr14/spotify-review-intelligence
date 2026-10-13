#!/usr/bin/env python3
"""Build the checker-facing final package from raw Jev evidence without model calls."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path


def read_jsonl(path: Path) -> list[dict[str, object]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw", type=Path, required=True)
    parser.add_argument("--support-calls", type=Path, required=True)
    parser.add_argument("--memo-call", type=Path, required=True)
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        raise ValueError(f"Output directory already exists: {args.out}")
    args.out.mkdir(parents=True)

    for name in (
        "records.jsonl", "membership.csv", "ranking.csv", "claims.csv", "run.json",
        "checkpoint_before.json", "checkpoint_after.json", "memo.json", "memo.md",
    ):
        shutil.copy2(args.raw / name, args.out / name)

    records = read_jsonl(args.raw / "records.jsonl")
    expected = {row["review_id"] for row in records}
    before = set(json.loads((args.raw / "checkpoint_before.json").read_text(encoding="utf-8"))["completed_ids"])
    calls = []
    removed_non_sample = 0
    for event in read_jsonl(args.raw / "calls.jsonl"):
        ids = event.get("review_ids")
        if event.get("role") != "enrich" or not isinstance(ids, list) or not ids or not all(rid in expected for rid in ids):
            removed_non_sample += 1
            continue
        normalized = dict(event)
        normalized["phase"] = "initial" if set(ids) <= before else "resume"
        calls.append(normalized)

    support = read_jsonl(args.support_calls)
    for role in ("verify", "group"):
        event = next(item for item in support if item.get("role") == role and item.get("outcome") == "succeeded")
        ids = event.get("review_ids", [])
        if not isinstance(ids, list) or any(rid not in expected for rid in ids):
            raise ValueError(f"{role} evidence contains IDs outside the final sample")
        calls.append(event)
    memo = read_jsonl(args.memo_call)
    if len(memo) != 1 or memo[0].get("outcome") != "succeeded":
        raise ValueError("Expected one successful final memo call")
    memo_event = dict(memo[0])
    memo_event["role"] = "memo"
    calls.append(memo_event)

    request_ids = [str(event["request_id"]) for event in calls]
    if len(request_ids) != len(set(request_ids)):
        raise ValueError("Duplicate request IDs in final call evidence")
    (args.out / "calls.jsonl").write_text(
        "".join(json.dumps(event, ensure_ascii=False, separators=(",", ":"), sort_keys=True) + "\n" for event in calls),
        encoding="utf-8",
    )
    reference = json.loads(args.reference.read_text(encoding="utf-8"))
    (args.out / "ingestion.json").write_text(
        json.dumps(reference["ingestion"], ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "output": str(args.out),
        "records": len(records),
        "calls": len(calls),
        "removed_non_sample_or_non_enrich_calls": removed_non_sample,
        "phase_semantics": "initial=completed before final resume snapshot; resume=completed afterward",
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
