from __future__ import annotations

import csv
import json
import os
import sqlite3
import sys
import time
import uuid
from collections import Counter, defaultdict
from contextlib import closing
from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any

from .core import atomic_text, canonical, read_rows, row_sha, sha256_bytes, sha256_file, utc_now, write_json
from .jev import (
    DEFAULT_CONFIDENCE_THRESHOLD,
    JEV_INPUT_PRICE_PER_MILLION,
    JEV_MODEL_ALIAS,
    JEV_QUESTION_VERSION,
    JevClient,
    JevError,
    SpendLedger,
    load_env_value,
)


def text_sha(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def connect_jev_state(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path, timeout=60)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("PRAGMA synchronous=FULL")
    db.execute("PRAGMA foreign_keys=ON")
    db.executescript(
        """
        CREATE TABLE IF NOT EXISTS run_configs (
            label_config TEXT PRIMARY KEY,
            provider TEXT NOT NULL,
            requested_model TEXT NOT NULL,
            release_date TEXT NOT NULL,
            resolved_model TEXT,
            question_version TEXT NOT NULL,
            confidence_threshold REAL NOT NULL,
            created_at TEXT NOT NULL
        );
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
            confidence_json TEXT NOT NULL,
            review_signals_json TEXT NOT NULL,
            raw_answers_json TEXT NOT NULL,
            resolved_model TEXT NOT NULL,
            input_tokens INTEGER NOT NULL,
            output_tokens INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            PRIMARY KEY (label_config, text_sha256),
            FOREIGN KEY (label_config) REFERENCES run_configs(label_config)
        );
        CREATE TABLE IF NOT EXISTS calls (
            request_id TEXT PRIMARY KEY,
            label_config TEXT NOT NULL,
            role TEXT NOT NULL,
            phase TEXT NOT NULL,
            outcome TEXT NOT NULL,
            input_tokens INTEGER NOT NULL,
            output_tokens INTEGER NOT NULL,
            cost_usd TEXT NOT NULL,
            event_json TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (label_config) REFERENCES run_configs(label_config)
        );
        CREATE INDEX IF NOT EXISTS idx_jev_predictions_config
            ON predictions(label_config);
        CREATE INDEX IF NOT EXISTS idx_jev_calls_config
            ON calls(label_config);
        CREATE TABLE IF NOT EXISTS snapshots (
            name TEXT NOT NULL,
            label_config TEXT NOT NULL,
            input_sha256 TEXT NOT NULL,
            completed_ids_json TEXT NOT NULL,
            created_at TEXT NOT NULL,
            PRIMARY KEY (name, label_config, input_sha256),
            FOREIGN KEY (label_config) REFERENCES run_configs(label_config)
        );
        CREATE TABLE IF NOT EXISTS run_history (
            run_id TEXT PRIMARY KEY,
            label_config TEXT NOT NULL,
            input_sha256 TEXT NOT NULL,
            phase TEXT NOT NULL,
            workers INTEGER NOT NULL,
            completed_unique_texts INTEGER NOT NULL,
            elapsed_seconds REAL NOT NULL,
            stopped_for_spending_cap INTEGER NOT NULL,
            started_at TEXT NOT NULL,
            finished_at TEXT NOT NULL,
            FOREIGN KEY (label_config) REFERENCES run_configs(label_config)
        );
        CREATE TABLE IF NOT EXISTS budget_alerts (
            run_id TEXT NOT NULL,
            label_config TEXT NOT NULL,
            threshold_percent INTEGER NOT NULL,
            spent_usd TEXT NOT NULL,
            reserved_usd TEXT NOT NULL,
            max_spend_usd TEXT NOT NULL,
            event TEXT NOT NULL,
            created_at TEXT NOT NULL,
            PRIMARY KEY (run_id, threshold_percent),
            FOREIGN KEY (label_config) REFERENCES run_configs(label_config)
        );
        """
    )
    return db


def resolve_model_metadata(client: JevClient, requested_model: str) -> dict[str, str]:
    models = client.list_models()
    match = next((item for item in models if item.get("name") == requested_model), None)
    if match is None:
        available = [item.get("name") for item in models]
        raise JevError(f"Requested model {requested_model!r} is unavailable; available models: {available}")
    release_date = match.get("release_date")
    if not isinstance(release_date, str) or not release_date:
        raise JevError("Selected Jev model is missing a release date")
    return {"name": requested_model, "release_date": release_date}


def label_config_for(model: str, release_date: str, confidence_threshold: float) -> str:
    return (
        f"typesafe:{model}@{release_date}+{JEV_QUESTION_VERSION}"
        f"+sentiment-score-v1+confidence-{confidence_threshold:g}"
    )


def unique_nonempty_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    seen: set[str] = set()
    result: list[dict[str, str]] = []
    for row in rows:
        text = row["review_text"]
        if not text:
            continue
        digest = text_sha(text)
        if digest not in seen:
            seen.add(digest)
            result.append(row)
    return result


def _existing_spend(db: sqlite3.Connection, label_config: str) -> Decimal:
    total = Decimal("0")
    for row in db.execute("SELECT cost_usd FROM calls WHERE label_config = ?", (label_config,)):
        total += Decimal(row[0])
    return total


def _completed_hashes(db: sqlite3.Connection, label_config: str) -> set[str]:
    return {
        row[0]
        for row in db.execute(
            "SELECT text_sha256 FROM predictions WHERE label_config = ?", (label_config,)
        )
    }


def _save_events(db: sqlite3.Connection, label_config: str, events: list[dict[str, Any]]) -> None:
    for event in events:
        db.execute(
            """INSERT OR IGNORE INTO calls
            (request_id, label_config, role, phase, outcome, input_tokens,
             output_tokens, cost_usd, event_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                event["request_id"],
                label_config,
                event["role"],
                event["phase"],
                event["outcome"],
                int(event.get("input_tokens", 0)),
                int(event.get("output_tokens", 0)),
                str(event.get("cost_usd", "0")),
                canonical(event),
                utc_now(),
            ),
        )


def _save_success(
    db: sqlite3.Connection,
    *,
    label_config: str,
    row: dict[str, str],
    prediction: dict[str, Any],
    events: list[dict[str, Any]],
) -> None:
    with db:
        _save_events(db, label_config, events)
        db.execute(
            """INSERT OR IGNORE INTO predictions
            (label_config, text_sha256, review_text, source_review_id, topic,
             intent, sentiment, severity, needs_review, confidence_json,
             review_signals_json, raw_answers_json, resolved_model,
             input_tokens, output_tokens, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                label_config,
                text_sha(row["review_text"]),
                row["review_text"],
                row["review_id"],
                prediction["topic"],
                prediction["intent"],
                float(prediction["sentiment"]),
                int(prediction["severity"]),
                int(prediction["needs_review"]),
                canonical(prediction["confidence"]),
                canonical(prediction["review_signals"]),
                canonical(prediction["raw_answers"]),
                prediction["resolved_model"],
                int(prediction["usage"]["input_tokens"]),
                int(prediction["usage"]["output_tokens"]),
                utc_now(),
            ),
        )


def _save_failed_events(db: sqlite3.Connection, label_config: str, events: list[dict[str, Any]]) -> None:
    if not events:
        return
    with db:
        _save_events(db, label_config, events)


def _record_budget_alerts(
    db: sqlite3.Connection,
    *,
    run_id: str,
    label_config: str,
    ledger: SpendLedger,
    cap_blocked: bool = False,
) -> list[int]:
    """Persist and print each crossed local budget threshold once per run."""
    snapshot = ledger.snapshot()
    used_percent = float(snapshot["used_percent"])
    crossed = [threshold for threshold in (50, 75, 90) if used_percent >= threshold]
    if cap_blocked:
        crossed.append(100)
    inserted: list[int] = []
    for threshold in crossed:
        event = "dispatch_blocked_by_cap" if threshold == 100 else "threshold_crossed"
        with db:
            cursor = db.execute(
                """INSERT OR IGNORE INTO budget_alerts
                (run_id, label_config, threshold_percent, spent_usd,
                 reserved_usd, max_spend_usd, event, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    run_id,
                    label_config,
                    threshold,
                    snapshot["spent_usd"],
                    snapshot["reserved_usd"],
                    snapshot["max_spend_usd"],
                    event,
                    utc_now(),
                ),
            )
        if cursor.rowcount:
            inserted.append(threshold)
            print(
                "Jev local budget alert: "
                f"{threshold}% ({event}); spent=${snapshot['spent_usd']}, "
                f"reserved=${snapshot['reserved_usd']}, cap=${snapshot['max_spend_usd']}",
                file=sys.stderr,
                flush=True,
            )
    return inserted


def _status_payload(
    rows: list[dict[str, str]],
    done: set[str],
    input_path: Path,
    state_path: Path,
    label_config: str,
    spend: Decimal,
    *,
    multiplicity: Counter[str] | None = None,
    input_sha256: str | None = None,
) -> dict[str, Any]:
    text_counts = multiplicity or Counter(
        text_sha(row["review_text"]) for row in rows if row["review_text"]
    )
    completed = set(text_counts) & done
    empty_rows = sum(not row["review_text"] for row in rows)
    return {
        "input": str(input_path.resolve()),
        "input_sha256": input_sha256 or sha256_file(input_path),
        "label_config": label_config,
        "rows": len(rows),
        "empty_rows": empty_rows,
        "unique_nonempty_texts": len(text_counts),
        "completed_unique_texts": len(completed),
        "remaining_unique_texts": len(text_counts) - len(completed),
        "accounted_rows": empty_rows + sum(text_counts[key] for key in completed),
        "spent_usd": str(spend),
        "state_database": str(state_path.resolve()),
    }


def jev_status(input_path: Path, state_path: Path) -> dict[str, Any]:
    rows = read_rows(input_path)
    with closing(connect_jev_state(state_path)) as db:
        configs = [row[0] for row in db.execute("SELECT label_config FROM run_configs ORDER BY created_at")]
        details = []
        for config in configs:
            details.append(
                _status_payload(
                    rows,
                    _completed_hashes(db, config),
                    input_path,
                    state_path,
                    config,
                    _existing_spend(db, config),
                )
            )
    return {"configurations": details, "input": str(input_path.resolve())}


def _select_label_config(db: sqlite3.Connection, requested: str | None = None) -> str:
    configs = [
        row[0]
        for row in db.execute("SELECT label_config FROM run_configs ORDER BY created_at")
    ]
    if requested is not None:
        if requested not in configs:
            raise ValueError(f"Unknown Jev label configuration: {requested}")
        return requested
    if len(configs) != 1:
        raise ValueError(
            f"Expected exactly one Jev label configuration, found {len(configs)}; "
            "pass --label-config explicitly"
        )
    return configs[0]


def save_jev_snapshot(
    input_path: Path,
    state_path: Path,
    name: str,
    out_path: Path,
    label_config: str | None = None,
) -> dict[str, Any]:
    if name not in {"before", "after"}:
        raise ValueError("snapshot name must be before or after")
    rows = read_rows(input_path)
    with closing(connect_jev_state(state_path)) as db:
        selected = _select_label_config(db, label_config)
        done = _completed_hashes(db, selected)
        ids = [
            row["review_id"]
            for row in rows
            if row["review_text"] and text_sha(row["review_text"]) in done
        ]
        payload = {"completed_ids": ids}
        write_json(out_path, payload)
        with db:
            db.execute(
                "INSERT OR REPLACE INTO snapshots VALUES (?, ?, ?, ?, ?)",
                (name, selected, sha256_file(input_path), canonical(ids), utc_now()),
            )
    return {"snapshot": name, "completed_ids": len(ids), "path": str(out_path.resolve())}


def export_jev_artifacts(
    input_path: Path,
    state_path: Path,
    out_dir: Path,
    label_config: str | None = None,
) -> dict[str, Any]:
    """Export saved Jev enrichment as machine-checkable grading artifacts."""
    rows = read_rows(input_path)
    out_dir.mkdir(parents=True, exist_ok=True)
    input_digest = sha256_file(input_path)
    with closing(connect_jev_state(state_path)) as db:
        selected = _select_label_config(db, label_config)
        predictions = {
            row["text_sha256"]: row
            for row in db.execute(
                "SELECT * FROM predictions WHERE label_config = ?", (selected,)
            )
        }
        call_events = [
            json.loads(row[0])
            for row in db.execute(
                "SELECT event_json FROM calls WHERE label_config = ? ORDER BY rowid", (selected,)
            )
        ]
        snapshots = {
            row["name"]: json.loads(row["completed_ids_json"])
            for row in db.execute(
                """SELECT name, completed_ids_json FROM snapshots
                WHERE label_config = ? AND input_sha256 = ?""",
                (selected, input_digest),
            )
        }

    temp_records = out_dir / "records.jsonl.tmp"
    membership_rows: list[dict[str, str]] = []
    issue_values: dict[str, list[int]] = defaultdict(list)
    completed = pending = 0
    with temp_records.open("w", encoding="utf-8", newline="") as handle:
        for row in rows:
            base = {"review_id": row["review_id"], "source_sha256": row_sha(row)}
            saved = predictions.get(text_sha(row["review_text"])) if row["review_text"] else None
            if saved is None:
                record = base | {
                    "status": "quarantined",
                    "reason": "empty_review_text" if not row["review_text"] else "classification_pending",
                }
                pending += bool(row["review_text"])
            else:
                record = base | {
                    "status": "completed",
                    "topic": saved["topic"],
                    "intent": saved["intent"],
                    "sentiment": saved["sentiment"],
                    "severity": saved["severity"],
                    "entities": [],
                    "evidence_quote": row["review_text"],
                    "needs_review": bool(saved["needs_review"]),
                    "label_config": selected,
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
        total = sum(values)
        mean = (Decimal(total) / Decimal(len(values))).quantize(
            Decimal("0.000001"), rounding=ROUND_HALF_UP
        )
        ranking.append(
            {
                "issue_id": issue_id,
                "complaint_count": len(values),
                "severity_sum": total,
                "mean_severity": f"{mean:.6f}",
                "priority_score": total,
            }
        )
    ranking.sort(key=lambda value: (-value["priority_score"], value["issue_id"]))
    ranked = [{"rank": index, **value} for index, value in enumerate(ranking, 1)]
    with (out_dir / "ranking.csv").open("w", encoding="utf-8", newline="") as handle:
        fields = ["rank", "issue_id", "complaint_count", "severity_sum", "mean_severity", "priority_score"]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(ranked)

    with (out_dir / "claims.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["claim_id", "issue_id", "metric", "value"])
        writer.writeheader()
        for index, item in enumerate(ranked, 1):
            for metric in ("complaint_count", "severity_sum", "mean_severity", "priority_score"):
                writer.writerow(
                    {
                        "claim_id": f"claim_{index}_{metric}",
                        "issue_id": item["issue_id"],
                        "metric": metric,
                        "value": item[metric],
                    }
                )

    atomic_text(out_dir / "calls.jsonl", "".join(canonical(event) + "\n" for event in call_events))
    write_json(
        out_dir / "run.json",
        {
            "version": "a5-audit-v1",
            "analysis_count": len(rows),
            "analysis_sha256": input_digest,
            "classification_input_fields": ["review_text"],
            "allow_multi_issue": False,
            "label_config": selected,
        },
    )
    for name in ("before", "after"):
        write_json(out_dir / f"checkpoint_{name}.json", {"completed_ids": snapshots.get(name, [])})
    return {
        "output_directory": str(out_dir.resolve()),
        "label_config": selected,
        "records": len(rows),
        "completed": completed,
        "pending_quarantined": pending,
        "calls": len(call_events),
        "issues": len(ranked),
    }


def process_with_jev(
    *,
    input_path: Path,
    state_path: Path,
    workers: int,
    max_spend_usd: Decimal,
    max_new_records: int | None,
    confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD,
    requested_model: str = JEV_MODEL_ALIAS,
    client: JevClient | None = None,
) -> dict[str, Any]:
    if not 1 <= workers <= 32:
        raise ValueError("workers must be between 1 and 32")
    rows = read_rows(input_path)
    unique_rows = unique_nonempty_rows(rows)
    status_multiplicity = Counter(
        text_sha(row["review_text"]) for row in rows if row["review_text"]
    )
    input_digest = sha256_file(input_path)
    active_client = client or JevClient(load_env_value("TYPESAFE_API_KEY"))
    metadata = resolve_model_metadata(active_client, requested_model)
    label_config = label_config_for(metadata["name"], metadata["release_date"], confidence_threshold)
    run_id = f"jev-{input_path.stem}-{uuid.uuid4()}"
    run_started_at = utc_now()

    db = connect_jev_state(state_path)
    try:
        with db:
            db.execute(
                """INSERT OR IGNORE INTO run_configs
                (label_config, provider, requested_model, release_date,
                 resolved_model, question_version, confidence_threshold, created_at)
                VALUES (?, 'typesafe-jev', ?, ?, NULL, ?, ?, ?)""",
                (
                    label_config,
                    metadata["name"],
                    metadata["release_date"],
                    JEV_QUESTION_VERSION,
                    confidence_threshold,
                    utc_now(),
                ),
            )
        done = _completed_hashes(db, label_config)
        pending = [row for row in unique_rows if text_sha(row["review_text"]) not in done]
        if max_new_records is not None:
            pending = pending[:max_new_records]
        phase = "resume" if done else "initial"

        ledger = SpendLedger(max_spend_usd, JEV_INPUT_PRICE_PER_MILLION)
        ledger.seed_spent(_existing_spend(db, label_config))
        started = time.perf_counter()
        completed_this_run = 0
        stopped_for_cap = False
        last_progress_write = 0.0

        def classify(row: dict[str, str]) -> tuple[dict[str, Any] | None, list[dict[str, Any]], Exception | None]:
            events: list[dict[str, Any]] = []
            try:
                prediction, _ = active_client.classify_with_events(
                    row["review_text"],
                    model=requested_model,
                    confidence_threshold=confidence_threshold,
                    attempts=2,
                    review_id=row["review_id"],
                    phase=phase,
                    label_config=label_config,
                    run_id=run_id,
                    ledger=ledger,
                    events_out=events,
                )
                return prediction, events, None
            except Exception as exc:  # returned to the main thread for durable logging
                return None, events, exc

        with ThreadPoolExecutor(max_workers=workers) as executor:
            for wave_start in range(0, len(pending), workers):
                wave = pending[wave_start : wave_start + workers]
                results = list(executor.map(classify, wave))
                for row, (prediction, events, error) in zip(wave, results, strict=True):
                    if error is not None:
                        _save_failed_events(db, label_config, events)
                        if isinstance(error, JevError) and "Spending cap reached" in str(error):
                            stopped_for_cap = True
                            continue
                        raise error
                    assert prediction is not None
                    saved_model = db.execute(
                        "SELECT resolved_model FROM run_configs WHERE label_config = ?", (label_config,)
                    ).fetchone()[0]
                    if saved_model is not None and saved_model != prediction["resolved_model"]:
                        _save_failed_events(db, label_config, events)
                        raise JevError(
                            f"Resolved Jev model changed from {saved_model!r} to {prediction['resolved_model']!r}; stopping"
                        )
                    with db:
                        if saved_model is None:
                            db.execute(
                                "UPDATE run_configs SET resolved_model = ? WHERE label_config = ?",
                                (prediction["resolved_model"], label_config),
                            )
                    _save_success(
                        db,
                        label_config=label_config,
                        row=row,
                        prediction=prediction,
                        events=events,
                    )
                    done.add(text_sha(row["review_text"]))
                    completed_this_run += 1
                alerts = _record_budget_alerts(
                    db,
                    run_id=run_id,
                    label_config=label_config,
                    ledger=ledger,
                    cap_blocked=stopped_for_cap,
                )
                now = time.perf_counter()
                is_last_wave = wave_start + workers >= len(pending)
                if alerts or stopped_for_cap or is_last_wave or now - last_progress_write >= 1.0:
                    status = _status_payload(
                        rows,
                        done,
                        input_path,
                        state_path,
                        label_config,
                        ledger.spent_usd,
                        multiplicity=status_multiplicity,
                        input_sha256=input_digest,
                    )
                    status.update(
                        {
                            "run_id": run_id,
                            "phase": phase,
                            "workers": workers,
                            "completed_unique_texts_this_run": completed_this_run,
                            "elapsed_seconds_this_run": round(now - started, 3),
                            "stopped_for_spending_cap": stopped_for_cap,
                            "budget": ledger.snapshot(),
                            "new_budget_alerts_percent": alerts,
                            "updated_at": utc_now(),
                        }
                    )
                    progress_path = state_path.parent / f"progress-jev-{input_path.stem}.json"
                    atomic_text(progress_path, json.dumps(status, indent=2, sort_keys=True) + "\n")
                    last_progress_write = now
                if stopped_for_cap:
                    break

        elapsed_seconds = round(time.perf_counter() - started, 3)
        with db:
            db.execute(
                """INSERT INTO run_history
                (run_id, label_config, input_sha256, phase, workers,
                 completed_unique_texts, elapsed_seconds, stopped_for_spending_cap,
                 started_at, finished_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    run_id,
                    label_config,
                    input_digest,
                    phase,
                    workers,
                    completed_this_run,
                    elapsed_seconds,
                    int(stopped_for_cap),
                    run_started_at,
                    utc_now(),
                ),
            )
        return _status_payload(
            rows,
            done,
            input_path,
            state_path,
            label_config,
            ledger.spent_usd,
            multiplicity=status_multiplicity,
            input_sha256=input_digest,
        ) | {
            "run_id": run_id,
            "phase": phase,
            "workers": workers,
            "completed_unique_texts_this_run": completed_this_run,
            "elapsed_seconds_this_run": elapsed_seconds,
            "stopped_for_spending_cap": stopped_for_cap,
            "budget": ledger.snapshot(),
        }
    finally:
        db.close()
