#!/usr/bin/env python3
"""Create the reproducible 100,000-review final analysis sample.

The sample is selected across the complete source file by the lowest values of
SHA-256(seed + ":" + review_id). This is deterministic, independent of source
row order, and preserves duplicate review texts as separate review records.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import heapq
import json
import os
from collections import Counter
from pathlib import Path
from typing import Any


FIELDS = [
    "review_id",
    "review_text",
    "review_rating",
    "review_likes",
    "app_version",
    "review_timestamp",
]
DEFAULT_SEED = "berkeley-fall-2026-assignment-5-v1"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def sampling_rank(seed: str, review_id: str) -> int:
    payload = f"{seed}:{review_id}".encode("utf-8")
    return int.from_bytes(hashlib.sha256(payload).digest(), "big")


def load_ids(path: Path | None) -> set[str]:
    if path is None or not path.exists():
        return set()
    with path.open("r", encoding="utf-8", newline="") as handle:
        return {row["review_id"] for row in csv.DictReader(handle)}


def write_csv_atomic(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    with temp.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    os.replace(temp, path)


def write_json_atomic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temp, path)


def write_quarantine_atomic(path: Path, rows: list[dict[str, str]]) -> None:
    """Write source defects separately so they remain auditable, not classified."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    with temp.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            payload = {
                **row,
                "quarantine_reason": "empty_review_text",
                "source_row_sha256": hashlib.sha256(
                    json.dumps(row, sort_keys=True, ensure_ascii=False).encode("utf-8")
                ).hexdigest(),
            }
            handle.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")
    os.replace(temp, path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--sample-size", type=int, default=100_000)
    parser.add_argument("--seed", default=DEFAULT_SEED)
    parser.add_argument("--golden", type=Path)
    parser.add_argument("--analysis-10000", type=Path)
    parser.add_argument("--quarantine", type=Path)
    args = parser.parse_args()

    if args.sample_size < 1:
        raise SystemExit("--sample-size must be positive")

    source_rows = 0
    eligible_rows = 0
    empty_rows: list[dict[str, str]] = []
    duplicate_review_ids = 0
    invalid_rating_rows = 0
    seen_ids: set[str] = set()
    sample: list[tuple[int, str, dict[str, str]]] = []

    with args.input.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != FIELDS:
            raise ValueError(f"Unexpected source columns: {reader.fieldnames!r}")
        for row in reader:
            source_rows += 1
            review_id = row["review_id"]
            if review_id in seen_ids:
                duplicate_review_ids += 1
                continue
            seen_ids.add(review_id)

            if not row["review_text"].strip():
                empty_rows.append(row)
                continue
            if row["review_rating"] not in {"1", "2", "3", "4", "5"}:
                invalid_rating_rows += 1
                continue

            eligible_rows += 1
            rank = sampling_rank(args.seed, review_id)
            entry = (-rank, review_id, row)
            if len(sample) < args.sample_size:
                heapq.heappush(sample, entry)
            elif rank < -sample[0][0]:
                heapq.heapreplace(sample, entry)

    if eligible_rows < args.sample_size:
        raise ValueError(
            f"Requested {args.sample_size:,} rows but only {eligible_rows:,} are eligible"
        )

    selected_entries = sorted(sample, key=lambda entry: (-entry[0], entry[1]))
    selected = [entry[2] for entry in selected_entries]
    selected_ids = {row["review_id"] for row in selected}
    review_text_counts = Counter(row["review_text"] for row in selected)
    months = Counter(row["review_timestamp"][:7] for row in selected)
    ratings = Counter(row["review_rating"] for row in selected)
    timestamps = [row["review_timestamp"] for row in selected]

    write_csv_atomic(args.output, selected)
    if args.quarantine is not None:
        write_quarantine_atomic(args.quarantine, empty_rows)

    golden_ids = load_ids(args.golden)
    analysis_10000_ids = load_ids(args.analysis_10000)
    manifest = {
        "version": "representative-100k-v1",
        "source": {
            "path": args.input.name,
            "sha256": sha256_file(args.input),
            "rows": source_rows,
            "duplicate_review_ids": duplicate_review_ids,
            "empty_review_text_rows": len(empty_rows),
            "invalid_rating_rows": invalid_rating_rows,
            "eligible_nonempty_rows": eligible_rows,
        },
        "sample": {
            "path": args.output.name,
            "sha256": sha256_file(args.output),
            "rows": len(selected),
            "seed": args.seed,
            "method": "Select the lowest SHA-256(seed + ':' + review_id) ranks across all eligible source rows.",
            "eligibility": "Unique nonempty review_id with review_rating in 1..5; duplicate review text remains eligible and keeps its original ID.",
            "order": "Ascending sampling rank, then review_id.",
            "unique_review_texts": len(review_text_counts),
            "exact_duplicate_text_rows": len(selected) - len(review_text_counts),
            "first_timestamp": min(timestamps),
            "last_timestamp": max(timestamps),
            "reviews_by_month": dict(sorted(months.items())),
            "reviews_by_rating": dict(sorted(ratings.items())),
        },
        "scope_accounting": {
            "nonempty_reviews_to_classify": len(selected),
            "empty_reviews_to_quarantine_from_full_source": len(empty_rows),
            "full_source_rows_profiled": source_rows,
            "quarantine_path": args.quarantine.name if args.quarantine else None,
        },
        "nesting_checks": {
            "golden_rows": len(golden_ids),
            "golden_rows_in_sample": len(golden_ids & selected_ids),
            "analysis_10000_rows": len(analysis_10000_ids),
            "analysis_10000_rows_in_sample": len(analysis_10000_ids & selected_ids),
        },
    }
    write_json_atomic(args.manifest, manifest)
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
