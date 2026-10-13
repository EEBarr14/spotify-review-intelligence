from __future__ import annotations

import csv
import json
import sqlite3
import time
from decimal import Decimal
from pathlib import Path
from typing import Any

from .core import (
    atomic_text,
    canonical,
    grouping_and_ranking,
    memo_stage,
    read_rows,
    utc_now,
    verify_records,
    write_json,
)
from .jev import JEV_INPUT_PRICE_PER_MILLION
from .jev_scalable import export_jev_artifacts, process_with_jev


EXPECTED_PILOT_SHA256 = "c884ac3b9be5066995d5063f96ad9af6e5e082975788c1684c4f6b6ea661dd0e"
RATE_SOURCE = "https://typesafe.ai/blog/introducing-system-one-models-and-jev"
RATE_CHECKED_DATE = "2026-10-11"
PROJECTED_ROWS = 100_000
PROJECTED_UNIQUE_TEXTS = 78_099


def _saved_config(state_path: Path) -> str:
    with sqlite3.connect(state_path) as db:
        configs = [row[0] for row in db.execute("SELECT label_config FROM run_configs")]
    if len(configs) != 1:
        raise ValueError(f"Expected one pilot configuration, found {len(configs)}")
    return configs[0]


def _saved_calls(state_path: Path, label_config: str) -> list[dict[str, Any]]:
    with sqlite3.connect(state_path) as db:
        return [
            json.loads(row[0])
            for row in db.execute(
                "SELECT event_json FROM calls WHERE label_config = ? ORDER BY rowid",
                (label_config,),
            )
        ]


def _downstream(
    rows: list[dict[str, str]],
    records: list[dict[str, Any]],
    cache_dir: Path,
    run_id: str,
    phase: str,
) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, float], dict[str, bool]]:
    stage_seconds: dict[str, float] = {}
    started = time.perf_counter()
    verification, verify_calls, verify_cached = verify_records(
        rows, records, cache_dir, run_id, phase, 10
    )
    stage_seconds["verify"] = time.perf_counter() - started

    started = time.perf_counter()
    membership, ranking, issues, group_calls, group_cached = grouping_and_ranking(
        rows, records, cache_dir, run_id, phase
    )
    stage_seconds["group_rank"] = time.perf_counter() - started

    started = time.perf_counter()
    memo, memo_markdown, memo_calls, memo_cached = memo_stage(
        ranking, issues, verification, cache_dir, run_id, phase
    )
    stage_seconds["memo"] = time.perf_counter() - started
    return (
        {
            "verification": verification,
            "membership": membership,
            "ranking": ranking,
            "issues": issues,
            "memo": memo,
            "memo_markdown": memo_markdown,
        },
        verify_calls + group_calls + memo_calls,
        stage_seconds,
        {"verify": verify_cached, "group": group_cached, "memo": memo_cached},
    )


def _write_downstream(output_dir: Path, artifacts: dict[str, Any]) -> None:
    write_json(output_dir / "verification.json", artifacts["verification"])
    write_json(output_dir / "issues.json", artifacts["issues"])
    write_json(output_dir / "memo.json", artifacts["memo"])
    atomic_text(output_dir / "memo.md", artifacts["memo_markdown"])


def _write_usage(cost_dir: Path, calls: list[dict[str, Any]]) -> None:
    with (cost_dir / "rates.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["item", "unit", "price_per_unit_usd", "as_of", "source"],
        )
        writer.writeheader()
        writer.writerow(
            {
                "item": "jev_input_tokens",
                "unit": "token",
                "price_per_unit_usd": str(JEV_INPUT_PRICE_PER_MILLION / Decimal(1_000_000)),
                "as_of": RATE_CHECKED_DATE,
                "source": RATE_SOURCE,
            }
        )
        writer.writerow(
            {
                "item": "jev_output_tokens",
                "unit": "token",
                "price_per_unit_usd": "0",
                "as_of": RATE_CHECKED_DATE,
                "source": RATE_SOURCE,
            }
        )
    with (cost_dir / "usage.csv").open("w", encoding="utf-8", newline="") as handle:
        fields = ["request_id", "provider", "role", "phase", "model", "outcome", "input_tokens", "output_tokens", "cost_usd", "wall_seconds"]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for call in calls:
            writer.writerow({field: call.get(field, "") for field in fields})


def run_jev_pilot(
    *,
    input_path: Path,
    cost_dir: Path,
    run_kind: str,
    max_spend_usd: Decimal | None = None,
) -> dict[str, Any]:
    if run_kind not in {"cold", "warm"}:
        raise ValueError("run_kind must be cold or warm")
    from .core import sha256_file

    if sha256_file(input_path) != EXPECTED_PILOT_SHA256:
        raise ValueError("cost_100.csv checksum does not match the pinned assignment input")
    rows = read_rows(input_path)
    if len(rows) != 100:
        raise ValueError(f"Pilot requires 100 rows, found {len(rows)}")

    cost_dir.mkdir(parents=True, exist_ok=True)
    state_path = cost_dir / "pilot-state.sqlite3"
    cache_dir = cost_dir / "artifact-cache"
    output_dir = cost_dir / run_kind
    summary_path = output_dir / "summary.json"
    if output_dir.exists():
        raise ValueError(f"{run_kind} pilot output already exists at {output_dir}; refusing to overwrite evidence")
    if run_kind == "cold" and state_path.exists():
        raise ValueError("Cold pilot requires a new empty state path")
    if run_kind == "cold" and cache_dir.exists():
        raise ValueError("Cold pilot requires an empty downstream artifact cache")
    if run_kind == "warm" and (
        not state_path.exists() or not (cost_dir / "cold" / "summary.json").exists()
    ):
        raise ValueError("Warm pilot requires a completed cold pilot")
    output_dir.mkdir(parents=True, exist_ok=False)
    run_id = f"jev-pilot-{run_kind}-{int(time.time())}"
    wall_started = time.perf_counter()
    stage_seconds: dict[str, float] = {}

    if run_kind == "cold":
        if max_spend_usd is None:
            raise ValueError("Cold pilot requires a spending cap")
        started = time.perf_counter()
        process_result = process_with_jev(
            input_path=input_path,
            state_path=state_path,
            workers=1,
            max_spend_usd=max_spend_usd,
            max_new_records=None,
        )
        stage_seconds["enrich"] = time.perf_counter() - started
        if process_result["completed_unique_texts"] != 100:
            raise ValueError("Cold pilot did not complete all 100 unique texts")
    else:
        started = time.perf_counter()
        process_result = {"completed_unique_texts_this_run": 0, "cache_only": True}
        stage_seconds["enrich"] = time.perf_counter() - started

    label_config = _saved_config(state_path)
    export_jev_artifacts(input_path, state_path, output_dir, label_config)
    records = [
        json.loads(line)
        for line in (output_dir / "records.jsonl").read_text(encoding="utf-8").splitlines()
        if line
    ]
    atomic_text(output_dir / "pilot_records.jsonl", "".join(canonical(row) + "\n" for row in records))
    artifacts, local_calls, downstream_seconds, cache_hits = _downstream(
        rows, records, cache_dir, run_id, "initial" if run_kind == "cold" else "resume"
    )
    stage_seconds.update(downstream_seconds)
    _write_downstream(output_dir, artifacts)

    jev_calls = _saved_calls(state_path, label_config) if run_kind == "cold" else []
    calls = jev_calls + local_calls
    atomic_text(output_dir / "pilot_calls.jsonl", "".join(canonical(call) + "\n" for call in calls))
    elapsed = time.perf_counter() - wall_started
    summary = {
        "run_id": run_id,
        "run_kind": run_kind,
        "input_sha256": EXPECTED_PILOT_SHA256,
        "input_rows": 100,
        "unique_texts": 100,
        "completed": sum(row["status"] == "completed" for row in records),
        "failed": sum(row.get("reason") == "classification_pending" for row in records),
        "label_config": label_config,
        "workers": 1,
        "verification_size": 10,
        "calls_attempted": len(calls),
        "calls_failed": sum(call.get("outcome") == "failed" for call in calls),
        "jev_enrichment_calls": sum(call.get("role") == "enrich" for call in calls),
        "input_tokens": sum(int(call.get("input_tokens", 0)) for call in calls),
        "output_tokens": sum(int(call.get("output_tokens", 0)) for call in calls),
        "api_spend_usd": str(sum((Decimal(str(call.get("cost_usd", "0"))) for call in calls), Decimal("0"))),
        "local_compute_cost_usd": None,
        "stage_seconds": {key: round(value, 6) for key, value in stage_seconds.items()},
        "wall_seconds": round(elapsed, 6),
        "downstream_cache_hits": cache_hits,
        "created_at": utc_now(),
        "process_result": process_result,
    }
    write_json(summary_path, summary)
    if run_kind == "cold":
        _write_usage(cost_dir, calls)
    return summary


def build_jev_pilot_report(cost_dir: Path, budget_usd: Decimal) -> Path:
    cold = json.loads((cost_dir / "cold" / "summary.json").read_text(encoding="utf-8"))
    warm = json.loads((cost_dir / "warm" / "summary.json").read_text(encoding="utf-8"))
    with (cost_dir / "rates.csv").open("r", encoding="utf-8", newline="") as handle:
        rates = {
            row["item"]: Decimal(row["price_per_unit_usd"])
            for row in csv.DictReader(handle)
        }
    with (cost_dir / "usage.csv").open("r", encoding="utf-8", newline="") as handle:
        usage = list(csv.DictReader(handle))
    cold_cost = sum(
        (
            Decimal(row["input_tokens"] or "0") * rates["jev_input_tokens"]
            + Decimal(row["output_tokens"] or "0") * rates["jev_output_tokens"]
            for row in usage
            if row["provider"] == "typesafe-jev"
        ),
        Decimal("0"),
    )
    logged_cost = Decimal(cold["api_spend_usd"])
    projected_cost = cold_cost * Decimal(PROJECTED_UNIQUE_TEXTS) / Decimal(100)
    no_reuse_cost = cold_cost * Decimal(PROJECTED_ROWS) / Decimal(100)
    conservative_cost = projected_cost * Decimal("1.25")
    enrich_seconds = Decimal(str(cold["stage_seconds"]["enrich"]))
    projected_hours_single = enrich_seconds * Decimal(PROJECTED_UNIQUE_TEXTS) / Decimal(100) / Decimal(3600)
    lines = [
        "# Jev hybrid 100-review cost and runtime report",
        "",
        f"Generated from saved measurements on {cold['created_at']}. Offline replay makes no API calls.",
        "",
        "## Measured pilot",
        "",
        f"- Input: 100 rows / 100 unique texts; SHA-256 `{cold['input_sha256']}`",
        f"- Cold completion: {cold['completed']} completed, {cold['failed']} failed",
        f"- Cold Jev enrichment calls: {cold['jev_enrichment_calls']}",
        f"- Cold wall time: {cold['wall_seconds']:.3f} seconds",
        f"- Cold measured API spend: ${cold_cost:.6f}",
        f"- Saved-ledger reconciliation: ${logged_cost:.6f}; difference from rate-file calculation: ${abs(logged_cost - cold_cost):.6f}",
        f"- Warm wall time: {warm['wall_seconds']:.3f} seconds",
        f"- Warm new enrichment calls: {warm['jev_enrichment_calls']}",
        f"- Warm incremental API spend: ${Decimal(warm['api_spend_usd']):.6f}",
        f"- Local compute/electricity cost: unknown (not silently treated as zero)",
        "",
        "## 100,000-review projection",
        "",
        f"- Exact-text reuse case: {PROJECTED_UNIQUE_TEXTS:,} Jev classifications, estimated ${projected_cost:.4f}",
        f"- No-reuse comparison: {PROJECTED_ROWS:,} Jev classifications, estimated ${no_reuse_cost:.4f}",
        f"- Conservative 25% retry/overhead case: ${conservative_cost:.4f}",
        f"- Declared budget: ${budget_usd:.2f} — {'WARNING: projected conservative spend exceeds budget' if conservative_cost > budget_usd else 'within the declared budget'}",
        f"- Single-worker linear enrichment estimate: {projected_hours_single:.2f} hours; parallel estimates remain provisional until measured at 500 and 10,000.",
        "",
        "## Rate and controls",
        "",
        f"- Jev input: $0.042 per million input tokens; output tokens free, checked {RATE_CHECKED_DATE} at {RATE_SOURCE}.",
        "- The production runner uses a concurrency-safe pre-dispatch reservation ledger, bounded retries, atomic saves, exact-text cache keys, and a required hard spending cap.",
        "- The pilot uses one worker. Production concurrency is increased only after like-for-like checkpoint measurements.",
        "- This projection is refreshed after 500 and 10,000 reviews before authorizing 100,000.",
    ]
    report_path = cost_dir / "report.md"
    atomic_text(report_path, "\n".join(lines) + "\n")
    return report_path
