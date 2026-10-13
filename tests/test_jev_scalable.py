from __future__ import annotations

import csv
import sys
import tempfile
import unittest
import uuid
import sqlite3
from contextlib import closing
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from spotify_pipeline.core import FIELDS
from spotify_pipeline.jev import parse_classification
from spotify_pipeline.jev_scalable import (
    export_jev_artifacts,
    jev_status,
    process_with_jev,
    save_jev_snapshot,
)


def response_for(text: str) -> dict:
    topic = "playback" if "crash" in text.lower() else "other"
    intent = "complaint" if topic == "playback" else "praise"
    severity = "4" if topic == "playback" else "1"
    return {
        "model": "jev-2026-09-15",
        "usage": {"input_tokens": 50, "output_tokens": 10},
        "answers": {
            "topic": {"type": "choice", "choice": topic, "confidence": 0.9, "probabilities": {topic: 1.0}},
            "intent": {"type": "choice", "choice": intent, "confidence": 0.9, "probabilities": {intent: 1.0}},
            "severity": {"type": "choice", "choice": severity, "confidence": 0.9, "probabilities": {severity: 1.0}},
            "sentiment": {
                "type": "score",
                "score": 0 if intent == "complaint" else 4,
                "confidence": 0.9,
                "legend": {"0": "negative", "4": "positive"},
                "probabilities": {"0": 1.0 if intent == "complaint" else 0.0, "4": 0.0 if intent == "complaint" else 1.0},
            },
            "unsupported_language": {"type": "noul", "noul": 0.01},
            "ambiguous": {"type": "noul", "noul": 0.01},
        },
    }


class FakeJevClient:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def list_models(self):
        return [{"name": "jev-latest", "release_date": "2026-09-15", "description": "test"}]

    def classify_with_events(self, text, **kwargs):
        self.calls.append(text)
        ledger = kwargs["ledger"]
        reservation = ledger.reserve(500)
        cost = ledger.reconcile(reservation, 50)
        parsed = parse_classification(response_for(text), confidence_threshold=kwargs["confidence_threshold"])
        event = {
            "request_id": f"fake-{uuid.uuid4()}",
            "run_id": kwargs["run_id"],
            "role": "enrich",
            "review_ids": [kwargs["review_id"]],
            "model": parsed["resolved_model"],
            "phase": kwargs["phase"],
            "outcome": "succeeded",
            "label_config": kwargs["label_config"],
            "provider": "typesafe-jev",
            "attempt": 1,
            "input_tokens": 50,
            "output_tokens": 10,
            "cost_usd": str(cost),
        }
        kwargs["events_out"].append(event)
        return parsed, kwargs["events_out"]


class JevScalableTests(unittest.TestCase):
    def test_exact_duplicate_cache_and_warm_resume(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            input_path = root / "reviews.csv"
            state_path = root / "jev.sqlite3"
            rows = [
                dict(zip(FIELDS, ["1", "App crashes", "1", "0", "1.0", "2023-01-01"])),
                dict(zip(FIELDS, ["2", "App crashes", "2", "0", "1.0", "2023-01-02"])),
                dict(zip(FIELDS, ["3", "Great app", "5", "0", "1.0", "2023-01-03"])),
            ]
            with input_path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=FIELDS)
                writer.writeheader()
                writer.writerows(rows)

            client = FakeJevClient()
            first = process_with_jev(
                input_path=input_path,
                state_path=state_path,
                workers=1,
                max_spend_usd=Decimal("0.01"),
                max_new_records=1,
                client=client,
            )
            self.assertEqual(len(client.calls), 1)
            self.assertEqual(first["completed_unique_texts"], 1)
            self.assertEqual(first["accounted_rows"], 2)
            before_path = root / "before.json"
            before = save_jev_snapshot(input_path, state_path, "before", before_path)
            self.assertEqual(before["completed_ids"], 2)

            second = process_with_jev(
                input_path=input_path,
                state_path=state_path,
                workers=1,
                max_spend_usd=Decimal("0.01"),
                max_new_records=None,
                client=client,
            )
            self.assertEqual(len(client.calls), 2)
            self.assertEqual(second["completed_unique_texts_this_run"], 1)
            after_path = root / "after.json"
            after = save_jev_snapshot(input_path, state_path, "after", after_path)
            self.assertEqual(after["completed_ids"], 3)

            warm = process_with_jev(
                input_path=input_path,
                state_path=state_path,
                workers=1,
                max_spend_usd=Decimal("0.01"),
                max_new_records=None,
                client=client,
            )
            self.assertEqual(len(client.calls), 2)
            self.assertEqual(warm["completed_unique_texts_this_run"], 0)
            with closing(sqlite3.connect(state_path)) as db:
                self.assertEqual(db.execute("SELECT COUNT(*) FROM run_history").fetchone()[0], 3)
            status = jev_status(input_path, state_path)
            self.assertEqual(status["configurations"][0]["accounted_rows"], 3)

            exported = export_jev_artifacts(input_path, state_path, root / "grading")
            self.assertEqual(exported["completed"], 3)
            self.assertEqual(exported["pending_quarantined"], 0)
            record_lines = (root / "grading" / "records.jsonl").read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(record_lines), 3)
            self.assertIn('"cache_source_id":"1"', record_lines[1])


if __name__ == "__main__":
    unittest.main()
