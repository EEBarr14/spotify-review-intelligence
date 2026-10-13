from __future__ import annotations

import csv
import json
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from contextlib import closing
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from spotify_pipeline.core import FIELDS, canonical, row_sha


class DashboardImportTests(unittest.TestCase):
    def test_builds_ordered_sql_without_preview_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            rows = [
                dict(zip(FIELDS, ["1", "App crashes", "1", "0", "1.0", "2023-01-01 00:00:00"])),
                dict(zip(FIELDS, ["2", "Great app", "5", "0", "1.0", "2023-02-01 00:00:00"])),
            ]
            sample = root / "sample.csv"
            with sample.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=FIELDS)
                writer.writeheader()
                writer.writerows(rows)
            config = "typesafe:test"
            records = [
                {"review_id": "1", "source_sha256": row_sha(rows[0]), "status": "completed", "topic": "playback", "intent": "complaint", "sentiment": -1.0, "severity": 4, "entities": [], "evidence_quote": "App crashes", "needs_review": False, "label_config": config},
                {"review_id": "2", "source_sha256": row_sha(rows[1]), "status": "completed", "topic": "other", "intent": "praise", "sentiment": 1.0, "severity": 1, "entities": [], "evidence_quote": "Great app", "needs_review": False, "label_config": config},
            ]
            records_path = root / "records.jsonl"
            records_path.write_text("".join(canonical(row) + "\n" for row in records), encoding="utf-8")
            ranking = root / "ranking.csv"
            ranking.write_text("rank,issue_id,complaint_count,severity_sum,mean_severity,priority_score\n1,issue_playback,1,4,4.000000,4\n", encoding="utf-8")
            claims = root / "claims.csv"
            claims.write_text("claim_id,issue_id,metric,value\nC1,issue_playback,priority_score,4\n", encoding="utf-8")
            evaluation = root / "evaluation.json"
            evaluation.write_text(json.dumps({"records": 50, "metrics": {"topic_accuracy": 0.8, "intent_accuracy": 0.9, "severity_exact_accuracy": 0.7, "severity_mae": 0.4, "sentiment_mae": 0.2, "model_needs_review_count": 3}}), encoding="utf-8")
            memo = root / "memo.json"
            memo.write_text(json.dumps({"priority_issue_id": "issue_playback", "recommendation": "Investigate playback failures.", "alternative_issue_ids": [], "limitations": ["Historical reviews."]}), encoding="utf-8")
            state = root / "state.sqlite3"
            with closing(sqlite3.connect(state)) as db:
                db.executescript("""
                    CREATE TABLE run_configs (label_config TEXT, requested_model TEXT, resolved_model TEXT, created_at TEXT);
                    CREATE TABLE calls (label_config TEXT, cost_usd TEXT);
                    CREATE TABLE run_history (label_config TEXT, elapsed_seconds REAL);
                """)
                db.execute("INSERT INTO run_configs VALUES (?, 'jev-latest', 'jev-test', 'now')", (config,))
                db.execute("INSERT INTO calls VALUES (?, '0.01')", (config,))
                db.execute("INSERT INTO run_history VALUES (?, 12.5)", (config,))
                db.commit()
            output = root / "sql"
            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "build_dashboard_import.py"), "--sample", str(sample), "--records", str(records_path), "--ranking", str(ranking), "--claims", str(claims), "--evaluation", str(evaluation), "--memo", str(memo), "--state", str(state), "--out-dir", str(output), "--chunk-size", "1"],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["records"], 2)
            self.assertEqual(manifest["chunks"], 2)
            sql_text = "".join(path.read_text(encoding="utf-8") for path in output.glob("*.sql"))
            self.assertNotIn("preview-fixture", sql_text)
            self.assertIn("The Business Question Comes First", sql_text)


if __name__ == "__main__":
    unittest.main()
