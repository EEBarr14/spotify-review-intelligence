from __future__ import annotations

import csv
import json
import os
import sqlite3
import time
import uuid
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any

from .core import (
    ENRICH_SYSTEM,
    LABEL_CONFIG,
    MODEL,
    MODEL_DIGEST,
    grouping_and_ranking,
    memo_stage,
    atomic_text,
    canonical,
    classify_batch,
    read_rows,
    row_sha,
    sha256_bytes,
    sha256_file,
    utc_now,
    verify_records,
    write_json,
)


def connect_state(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path, timeout=60)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("PRAGMA synchronous=FULL")
    db.execute("PRAGMA foreign_keys=ON")
    db.executescript(
        """
        CREATE TABLE IF NOT EXISTS predictions (
            label_config TEXT NOT NULL,
            text_sha256 TEXT NOT NULL,
            review_text TEXT NOT NULL,
            source_review_id TEXT NOT NULL,
            topic TEXT NOT NULL,
            intent TEXT NOT NULL,
            sentiment REAL NOT NULL,
            severity INTEGER NOT NULL,
            needs_review INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            PRIMARY KEY (label_config, text_sha256)
        );
        CREATE TABLE IF NOT EXISTS calls (
            request_id TEXT PRIMARY KEY,
            label_config TEXT NOT NULL,
            role TEXT NOT NULL,
            phase TEXT NOT NULL,
            event_json TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS snapshots (
            name TEXT NOT NULL,
            label_config TEXT NOT NULL,
            input_sha256 TEXT NOT NULL,
            completed_ids_json TEXT NOT NULL,
            created_at TEXT NOT NULL,
            PRIMARY KEY (name, label_config, input_sha256)
        );
        """
    )
    return db


def text_sha(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def completed_hashes(db: sqlite3.Connection) -> set[str]:
    return {row[0] for row in db.execute(
        "SELECT text_sha256 FROM predictions WHERE label_config = ?", (LABEL_CONFIG,)
    )}


def unique_nonempty_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    seen: set[str] = set()
    unique: list[dict[str, str]] = []
    for row in rows:
        text = row["review_text"]
        if not text:
            continue
        digest = text_sha(text)
        if digest not in seen:
            seen.add(digest)
            unique.append(row)
    return unique


def save_batch(
    db: sqlite3.Connection,
    rows: list[dict[str, str]],
    predictions: list[dict[str, Any]],
    calls: list[dict[str, Any]],
) -> None:
    with db:
        for event in calls:
            db.execute(
                "INSERT OR REPLACE INTO calls VALUES (?, ?, ?, ?, ?, ?)",
                (
                    event["request_id"], event["label_config"], event["role"], event["phase"],
                    canonical(event), utc_now(),
                ),
            )
        for row, prediction in zip(rows, predictions, strict=True):
            db.execute(
                """INSERT OR IGNORE INTO predictions
                (label_config, text_sha256, review_text, source_review_id, topic, intent,
                 sentiment, severity, needs_review, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    LABEL_CONFIG, text_sha(row["review_text"]), row["review_text"], row["review_id"],
                    prediction["topic"], prediction["intent"], float(prediction["sentiment"]),
                    int(prediction["severity"]), int(prediction["needs_review"]), utc_now(),
                ),
            )


def dataset_status(input_path: Path, state_path: Path) -> dict[str, Any]:
    rows = read_rows(input_path)
    unique = unique_nonempty_rows(rows)
    input_digest = sha256_file(input_path)
    empty_count = sum(not row["review_text"] for row in rows)
    with connect_state(state_path) as db:
        done = completed_hashes(db)
        call_counts = {
            row["phase"]: row["count"]
            for row in db.execute(
                "SELECT phase, COUNT(*) AS count FROM calls WHERE label_config = ? GROUP BY phase",
                (LABEL_CONFIG,),
            )
        }
    unique_hashes = {text_sha(row["review_text"]) for row in unique}
    completed_unique = len(unique_hashes & done)
    completed_rows = sum(not row["review_text"] or text_sha(row["review_text"]) in done for row in rows)
    return {
        "input": str(input_path.resolve()),
        "input_sha256": input_digest,
        "label_config": LABEL_CONFIG,
        "rows": len(rows),
        "empty_rows": empty_count,
        "unique_nonempty_texts": len(unique),
        "completed_unique_texts": completed_unique,
        "remaining_unique_texts": len(unique) - completed_unique,
        "accounted_rows": completed_rows,
        "call_counts_by_phase": call_counts,
        "state_database": str(state_path.resolve()),
    }


def process_dataset(
    *,
    input_path: Path,
    state_path: Path,
    batch_size: int,
    workers: int,
    max_new_batches: int | None,
) -> dict[str, Any]:
    rows = read_rows(input_path)
    unique = unique_nonempty_rows(rows)
    input_digest = sha256_file(input_path)
    empty_count = sum(not row["review_text"] for row in rows)
    db = connect_state(state_path)
    try:
        done_before = completed_hashes(db)
        multiplicity = Counter(text_sha(row["review_text"]) for row in rows if row["review_text"])
        scope_hashes = set(multiplicity)
        completed_scope = scope_hashes & done_before
        completed_unique_count = len(completed_scope)
        accounted_rows = empty_count + sum(multiplicity[key] for key in completed_scope)
        pending = [row for row in unique if text_sha(row["review_text"]) not in done_before]
        existing_calls = db.execute(
            "SELECT COUNT(*) FROM calls WHERE label_config = ? AND role = 'enrich'", (LABEL_CONFIG,)
        ).fetchone()[0]
        phase = "resume" if existing_calls or done_before else "initial"
        batches = [pending[i : i + batch_size] for i in range(0, len(pending), batch_size)]
        if max_new_batches is not None:
            batches = batches[:max_new_batches]
        started = time.perf_counter()
        completed_batches = 0
        processed_unique = 0

        def classify(rows_for_call: list[dict[str, str]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
            user = "Classify every item independently. Return each integer i exactly once.\n" + canonical(
                [{"i": index, "x": row["review_text"]} for index, row in enumerate(rows_for_call)]
            )
            return classify_batch(
                role="enrich", system=ENRICH_SYSTEM, user=user, rows=rows_for_call,
                phase=phase, label_config=LABEL_CONFIG, run_id=f"scale-{input_path.stem}",
            )

        with ThreadPoolExecutor(max_workers=workers) as executor:
            for wave_start in range(0, len(batches), workers):
                wave = batches[wave_start : wave_start + workers]
                futures = [executor.submit(classify, batch) for batch in wave]
                for batch, future in zip(wave, futures, strict=True):
                    try:
                        predictions, call_events = future.result()
                    except Exception as exc:
                        failure = {
                            "request_id": f"local-enrich-failed-{uuid.uuid4()}",
                            "run_id": f"scale-{input_path.stem}",
                            "role": "enrich",
                            "review_ids": [row["review_id"] for row in batch],
                            "model": f"{MODEL}@{MODEL_DIGEST}",
                            "phase": phase,
                            "outcome": "failed",
                            "label_config": LABEL_CONFIG,
                            "provider": "ollama-local",
                            "input_tokens": 0,
                            "output_tokens": 0,
                            "error_type": type(exc).__name__,
                            "error": str(exc)[:500],
                            "started_at": utc_now(),
                            "finished_at": utc_now(),
                        }
                        save_batch(db, [], [], [failure])
                        raise
                    save_batch(db, batch, predictions, call_events)
                    completed_batches += 1
                    processed_unique += len(batch)
                    for row in batch:
                        digest = text_sha(row["review_text"])
                        if digest not in completed_scope:
                            completed_scope.add(digest)
                            completed_unique_count += 1
                            accounted_rows += multiplicity[digest]
                    elapsed = time.perf_counter() - started
                    rate = processed_unique / elapsed if elapsed else 0
                    remaining = len(scope_hashes) - completed_unique_count
                    status = {
                        "input": str(input_path.resolve()),
                        "input_sha256": input_digest,
                        "label_config": LABEL_CONFIG,
                        "rows": len(rows),
                        "empty_rows": empty_count,
                        "unique_nonempty_texts": len(scope_hashes),
                        "completed_unique_texts": completed_unique_count,
                        "remaining_unique_texts": remaining,
                        "accounted_rows": accounted_rows,
                        "state_database": str(state_path.resolve()),
                        "phase": phase,
                        "new_batches_this_run": completed_batches,
                        "elapsed_seconds_this_run": round(elapsed, 3),
                        "observed_unique_texts_per_second": round(rate, 6),
                        "estimated_remaining_hours": round(remaining / rate / 3600, 2) if rate else None,
                        "updated_at": utc_now(),
                    }
                    write_json(state_path.parent / f"progress-{input_path.stem}.json", status)
        return dataset_status(input_path, state_path) | {
            "phase": phase,
            "new_batches_this_run": completed_batches,
            "elapsed_seconds_this_run": round(time.perf_counter() - started, 3),
        }
    finally:
        db.close()


def completed_ids_for_input(input_path: Path, state_path: Path) -> list[str]:
    rows = read_rows(input_path)
    with connect_state(state_path) as db:
        done = completed_hashes(db)
    return [row["review_id"] for row in rows if row["review_text"] and text_sha(row["review_text"]) in done]


def save_snapshot(input_path: Path, state_path: Path, name: str, out_path: Path) -> dict[str, Any]:
    if name not in {"before", "after"}:
        raise ValueError("snapshot name must be before or after")
    ids = completed_ids_for_input(input_path, state_path)
    payload = {"completed_ids": ids}
    write_json(out_path, payload)
    with connect_state(state_path) as db, db:
        db.execute(
            "INSERT OR REPLACE INTO snapshots VALUES (?, ?, ?, ?, ?)",
            (name, LABEL_CONFIG, sha256_file(input_path), canonical(ids), utc_now()),
        )
    return {"snapshot": name, "completed_ids": len(ids), "path": str(out_path)}


def finalize_dataset(
    input_path: Path,
    state_path: Path,
    verification_size: int,
) -> dict[str, Any]:
    rows = read_rows(input_path)
    with connect_state(state_path) as db:
        predictions = _prediction_map(db)
    missing = [row["review_id"] for row in rows if row["review_text"] and text_sha(row["review_text"]) not in predictions]
    if missing:
        raise ValueError(f"Cannot finalize: {len(missing)} nonempty rows are pending; first IDs: {missing[:5]}")

    records: list[dict[str, Any]] = []
    for row in rows:
        if not row["review_text"]:
            records.append({"review_id": row["review_id"], "source_sha256": row_sha(row), "status": "quarantined", "reason": "empty_review_text"})
            continue
        saved = predictions[text_sha(row["review_text"])]
        records.append(
            {
                "review_id": row["review_id"],
                "source_sha256": row_sha(row),
                "status": "completed",
                "topic": saved["topic"],
                "intent": saved["intent"],
                "sentiment": saved["sentiment"],
                "severity": saved["severity"],
                "entities": [],
                "evidence_quote": row["review_text"],
                "needs_review": bool(saved["needs_review"]),
                "label_config": LABEL_CONFIG,
            }
        )

    cache_dir = state_path.parent / "artifact-cache"
    run_id = f"finalize-{input_path.stem}-{datetime.now().strftime('%Y%m%dT%H%M%S')}"
    verification, verify_calls, verify_cached = verify_records(
        rows, records, cache_dir, run_id, "resume", verification_size,
    )
    membership, ranking, issues, group_calls, group_cached = grouping_and_ranking(
        rows, records, cache_dir, run_id, "resume",
    )
    memo, memo_markdown, memo_calls, memo_cached = memo_stage(
        ranking, issues, verification, cache_dir, run_id, "resume",
    )
    call_events = verify_calls + group_calls + memo_calls
    call_db = connect_state(state_path)
    try:
        save_batch(call_db, [], [], call_events)
    finally:
        call_db.close()
    write_json(state_path.parent / f"verification-{input_path.stem}.json", verification)
    write_json(state_path.parent / f"issues-{input_path.stem}.json", issues)
    write_json(state_path.parent / f"memo-{input_path.stem}.json", memo)
    atomic_text(state_path.parent / f"memo-{input_path.stem}.md", memo_markdown)
    return {
        "input": str(input_path.resolve()),
        "records": len(rows),
        "verification": {key: verification[key] for key in ("sample_size", "topic_agreement", "intent_agreement", "severity_exact_agreement", "severity_mae")},
        "membership_rows": len(membership),
        "ranked_issues": len(ranking),
        "new_model_calls": len(call_events),
        "cache_hits": {"verify": verify_cached, "group": group_cached, "memo": memo_cached},
        "memo_path": str((state_path.parent / f"memo-{input_path.stem}.md").resolve()),
    }


def _prediction_map(db: sqlite3.Connection) -> dict[str, sqlite3.Row]:
    return {
        row["text_sha256"]: row
        for row in db.execute("SELECT * FROM predictions WHERE label_config = ?", (LABEL_CONFIG,))
    }


def export_artifacts(input_path: Path, state_path: Path, out_dir: Path) -> dict[str, Any]:
    rows = read_rows(input_path)
    out_dir.mkdir(parents=True, exist_ok=True)
    with connect_state(state_path) as db:
        predictions = _prediction_map(db)
        call_events = [
            json.loads(row[0])
            for row in db.execute(
                "SELECT event_json FROM calls WHERE label_config LIKE ? ORDER BY rowid", (LABEL_CONFIG + "%",)
            )
        ]
        snapshots = {
            row["name"]: json.loads(row["completed_ids_json"])
            for row in db.execute(
                "SELECT name, completed_ids_json FROM snapshots WHERE label_config = ? AND input_sha256 = ?",
                (LABEL_CONFIG, sha256_file(input_path)),
            )
        }

    temp_records = out_dir / "records.jsonl.tmp"
    membership_rows: list[dict[str, str]] = []
    issue_values: dict[str, list[int]] = defaultdict(list)
    completed = quarantined = pending = 0
    with temp_records.open("w", encoding="utf-8", newline="") as handle:
        for row in rows:
            text = row["review_text"]
            base = {"review_id": row["review_id"], "source_sha256": row_sha(row)}
            if not text:
                record = base | {"status": "quarantined", "reason": "empty_review_text"}
                quarantined += 1
            else:
                saved = predictions.get(text_sha(text))
                if saved is None:
                    record = base | {"status": "quarantined", "reason": "classification_pending"}
                    pending += 1
                else:
                    record = base | {
                        "status": "completed",
                        "topic": saved["topic"],
                        "intent": saved["intent"],
                        "sentiment": saved["sentiment"],
                        "severity": saved["severity"],
                        "entities": [],
                        "evidence_quote": text,
                        "needs_review": bool(saved["needs_review"]),
                        "label_config": LABEL_CONFIG,
                    }
                    if row["review_id"] != saved["source_review_id"]:
                        record["cache_source_id"] = saved["source_review_id"]
                    completed += 1
                    if saved["intent"] in {"complaint", "cancellation"}:
                        issue_id = f"issue_{saved['topic']}"
                        membership_rows.append({"issue_id": issue_id, "review_id": row["review_id"]})
                        issue_values[issue_id].append(int(saved["severity"]))
            handle.write(canonical(record) + "\n")
    os.replace(temp_records, out_dir / "records.jsonl")

    with (out_dir / "membership.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["issue_id", "review_id"])
        writer.writeheader()
        writer.writerows(membership_rows)

    ranking: list[dict[str, Any]] = []
    for issue_id, values in issue_values.items():
        severity_sum = sum(values)
        count = len(values)
        mean = (Decimal(severity_sum) / Decimal(count)).quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP)
        ranking.append(
            {
                "issue_id": issue_id,
                "complaint_count": count,
                "severity_sum": severity_sum,
                "mean_severity": f"{mean:.6f}",
                "priority_score": severity_sum,
            }
        )
    ranking.sort(key=lambda item: (-item["priority_score"], item["issue_id"]))
    with (out_dir / "ranking.csv").open("w", encoding="utf-8", newline="") as handle:
        fields = ["rank", "issue_id", "complaint_count", "severity_sum", "mean_severity", "priority_score"]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows([{"rank": index, **item} for index, item in enumerate(ranking, 1)])

    with (out_dir / "claims.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["claim_id", "issue_id", "metric", "value"])
        writer.writeheader()
        for index, item in enumerate(ranking, 1):
            for metric in ("complaint_count", "severity_sum", "mean_severity", "priority_score"):
                writer.writerow(
                    {"claim_id": f"claim_{index}_{metric}", "issue_id": item["issue_id"], "metric": metric, "value": item[metric]}
                )

    atomic_text(out_dir / "calls.jsonl", "".join(canonical(event) + "\n" for event in call_events))
    write_json(
        out_dir / "run.json",
        {
            "version": "a5-audit-v1",
            "analysis_count": len(rows),
            "analysis_sha256": sha256_file(input_path),
            "classification_input_fields": ["review_text"],
            "allow_multi_issue": False,
            "label_config": LABEL_CONFIG,
        },
    )
    for name in ("before", "after"):
        write_json(out_dir / f"checkpoint_{name}.json", {"completed_ids": snapshots.get(name, [])})
    memo_path = state_path.parent / f"memo-{input_path.stem}.md"
    if memo_path.exists():
        atomic_text(out_dir / "memo.md", memo_path.read_text(encoding="utf-8"))
    return {
        "output_directory": str(out_dir.resolve()),
        "records": len(rows),
        "completed": completed,
        "empty_quarantined": quarantined,
        "pending_quarantined": pending,
        "calls": len(call_events),
        "issues": len(ranking),
    }
