from __future__ import annotations

import csv
import json
import sys
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from spotify_pipeline.jev_pilot import build_jev_pilot_report


class JevPilotReportTests(unittest.TestCase):
    def test_offline_report_uses_editable_rate_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "cold").mkdir()
            (root / "warm").mkdir()
            cold = {
                "created_at": "2026-10-08T00:00:00Z",
                "input_sha256": "abc",
                "completed": 100,
                "failed": 0,
                "jev_enrichment_calls": 100,
                "wall_seconds": 10.0,
                "stage_seconds": {"enrich": 8.0},
                "api_spend_usd": "0.0000042",
            }
            warm = {"wall_seconds": 0.1, "jev_enrichment_calls": 0, "api_spend_usd": "0"}
            (root / "cold" / "summary.json").write_text(json.dumps(cold), encoding="utf-8")
            (root / "warm" / "summary.json").write_text(json.dumps(warm), encoding="utf-8")
            with (root / "usage.csv").open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=["provider", "input_tokens", "output_tokens"])
                writer.writeheader()
                writer.writerow({"provider": "typesafe-jev", "input_tokens": 100, "output_tokens": 50})
            with (root / "rates.csv").open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=["item", "price_per_unit_usd"])
                writer.writeheader()
                writer.writerow({"item": "jev_input_tokens", "price_per_unit_usd": "0.000000042"})
                writer.writerow({"item": "jev_output_tokens", "price_per_unit_usd": "0"})

            report = build_jev_pilot_report(root, Decimal("5.10")).read_text(encoding="utf-8")
            self.assertIn("$0.000004", report)
            rate_path = root / "rates.csv"
            rate_path.write_text(rate_path.read_text(encoding="utf-8").replace("0.000000042", "0.000000084"), encoding="utf-8")
            doubled = build_jev_pilot_report(root, Decimal("5.10")).read_text(encoding="utf-8")
            self.assertIn("$0.000008", doubled)


if __name__ == "__main__":
    unittest.main()
