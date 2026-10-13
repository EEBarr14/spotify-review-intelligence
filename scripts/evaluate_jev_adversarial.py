#!/usr/bin/env python3
"""Evaluate saved Jev adversarial predictions; makes no API calls."""

from __future__ import annotations

import argparse
import csv
import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from spotify_pipeline.jev_scalable import text_sha  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--expectations", type=Path, required=True)
    parser.add_argument("--state", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--label-config")
    args = parser.parse_args()
    with args.input.open("r", encoding="utf-8", newline="") as handle:
        reviews = list(csv.DictReader(handle))
    expectations = json.loads(args.expectations.read_text(encoding="utf-8"))
    with sqlite3.connect(args.state) as db:
        db.row_factory = sqlite3.Row
        configs = [row[0] for row in db.execute("SELECT label_config FROM run_configs ORDER BY created_at")]
        selected = args.label_config or (configs[0] if len(configs) == 1 else None)
        if selected is None or selected not in configs:
            raise ValueError("Select an existing Jev label configuration with --label-config")
        predictions = {
            row["text_sha256"]: dict(row)
            for row in db.execute("SELECT * FROM predictions WHERE label_config = ?", (selected,))
        }
    cases = []
    for review in reviews:
        prediction = predictions.get(text_sha(review["review_text"]))
        expected = expectations[review["review_id"]]
        checks = {
            field: prediction is not None and prediction[field] in allowed
            for field, allowed in expected.items()
        }
        cases.append(
            {
                "review_id": review["review_id"],
                "passed": all(checks.values()),
                "checks": checks,
                "expected": expected,
                "actual": None if prediction is None else {field: prediction[field] for field in expected},
            }
        )
    result = {
        "label_config": selected,
        "cases": cases,
        "passed": sum(case["passed"] for case in cases),
        "total": len(cases),
        "all_passed": all(case["passed"] for case in cases),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
