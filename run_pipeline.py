#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from decimal import Decimal, InvalidOperation
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from spotify_pipeline.core import build_report, run_pilot  # noqa: E402
from spotify_pipeline.jev_scalable import (  # noqa: E402
    export_jev_artifacts,
    jev_status,
    process_with_jev,
    save_jev_snapshot,
)
from spotify_pipeline.jev_pilot import build_jev_pilot_report, run_jev_pilot  # noqa: E402
from spotify_pipeline.scalable import dataset_status, export_artifacts, finalize_dataset, process_dataset, save_snapshot  # noqa: E402


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description="Spotify review pipeline and offline cost calculator")
    commands = result.add_subparsers(dest="command", required=True)
    pilot = commands.add_parser("pilot", help="Run the real 100-review local-model pilot")
    pilot.add_argument("--input", type=Path, required=True)
    pilot.add_argument("--cost-dir", type=Path, default=Path("cost"))
    pilot.add_argument("--run-kind", choices=("cold", "warm"), required=True)
    pilot.add_argument("--reset-cache", action="store_true")
    pilot.add_argument("--batch-size", type=int, default=10)
    pilot.add_argument("--workers", type=int, default=1)
    pilot.add_argument("--verification-size", type=int, default=10)
    replay = commands.add_parser("replay", help="Recompute the report from saved measurements; no model calls")
    replay.add_argument("--cost-dir", type=Path, default=Path("cost"))
    process = commands.add_parser("process", help="Resumably classify a checkpoint or full CSV into SQLite")
    process.add_argument("--input", type=Path, required=True)
    process.add_argument("--state", type=Path, default=Path("state/pipeline.sqlite3"))
    process.add_argument("--batch-size", type=int, default=10)
    process.add_argument("--workers", type=int, default=1)
    process.add_argument("--max-new-batches", type=int)
    status = commands.add_parser("status", help="Show saved progress without model calls")
    status.add_argument("--input", type=Path, required=True)
    status.add_argument("--state", type=Path, default=Path("state/pipeline.sqlite3"))
    snapshot = commands.add_parser("snapshot", help="Save before/after resume evidence without model calls")
    snapshot.add_argument("--input", type=Path, required=True)
    snapshot.add_argument("--state", type=Path, default=Path("state/pipeline.sqlite3"))
    snapshot.add_argument("--name", choices=("before", "after"), required=True)
    snapshot.add_argument("--out", type=Path, required=True)
    export = commands.add_parser("export", help="Export current saved state into grading artifacts")
    export.add_argument("--input", type=Path, required=True)
    export.add_argument("--state", type=Path, default=Path("state/pipeline.sqlite3"))
    export.add_argument("--out-dir", type=Path, default=Path("grading"))
    finalize = commands.add_parser("finalize", help="Run verification, grouping and memo after enrichment")
    finalize.add_argument("--input", type=Path, required=True)
    finalize.add_argument("--state", type=Path, default=Path("state/pipeline.sqlite3"))
    finalize.add_argument("--verification-size", type=int, default=20)
    jev_process = commands.add_parser(
        "jev-process", help="Explicit paid command: resumably classify a CSV with Jev"
    )
    jev_process.add_argument("--input", type=Path, required=True)
    jev_process.add_argument("--state", type=Path, default=Path("state/jev_pipeline.sqlite3"))
    jev_process.add_argument("--workers", type=int, default=1)
    jev_process.add_argument("--max-spend-usd", required=True)
    jev_process.add_argument("--max-new-records", type=int)
    jev_process.add_argument("--confidence-threshold", type=float, default=0.55)
    jev_process.add_argument("--model", default="jev-latest")
    jev_process.add_argument(
        "--confirm-paid-run",
        action="store_true",
        help="Required acknowledgement that this command can consume TypeSafe credits",
    )
    jev_status_command = commands.add_parser(
        "jev-status", help="Inspect saved Jev progress without an API key or model call"
    )
    jev_status_command.add_argument("--input", type=Path, required=True)
    jev_status_command.add_argument("--state", type=Path, default=Path("state/jev_pipeline.sqlite3"))
    jev_snapshot = commands.add_parser(
        "jev-snapshot", help="Save Jev before/after resume evidence without model calls"
    )
    jev_snapshot.add_argument("--input", type=Path, required=True)
    jev_snapshot.add_argument("--state", type=Path, default=Path("state/jev_pipeline.sqlite3"))
    jev_snapshot.add_argument("--name", choices=("before", "after"), required=True)
    jev_snapshot.add_argument("--out", type=Path, required=True)
    jev_snapshot.add_argument("--label-config")
    jev_export = commands.add_parser(
        "jev-export", help="Export saved Jev results into grading artifacts without model calls"
    )
    jev_export.add_argument("--input", type=Path, required=True)
    jev_export.add_argument("--state", type=Path, default=Path("state/jev_pipeline.sqlite3"))
    jev_export.add_argument("--out-dir", type=Path, default=Path("grading"))
    jev_export.add_argument("--label-config")
    jev_pilot = commands.add_parser(
        "jev-pilot", help="Run or replay the required hybrid 100-review Jev pilot"
    )
    jev_pilot.add_argument("--input", type=Path, required=True)
    jev_pilot.add_argument("--cost-dir", type=Path, default=Path("cost/jev-pilot"))
    jev_pilot.add_argument("--run-kind", choices=("cold", "warm"), required=True)
    jev_pilot.add_argument("--max-spend-usd")
    jev_pilot.add_argument("--confirm-paid-run", action="store_true")
    jev_report = commands.add_parser(
        "jev-report", help="Rebuild the Jev pilot report from saved measurements; no API calls"
    )
    jev_report.add_argument("--cost-dir", type=Path, default=Path("cost/jev-pilot"))
    jev_report.add_argument("--budget-usd", default="5.10")
    return result


def main() -> int:
    args = parser().parse_args()
    if args.command == "pilot":
        if not 1 <= args.batch_size <= 50:
            raise SystemExit("--batch-size must be between 1 and 50")
        if not 1 <= args.workers <= 4:
            raise SystemExit("--workers must be between 1 and 4")
        run_dir = run_pilot(
            input_path=args.input,
            cost_dir=args.cost_dir,
            run_kind=args.run_kind,
            reset_cache=args.reset_cache,
            batch_size=args.batch_size,
            verification_size=args.verification_size,
            workers=args.workers,
        )
        print(run_dir)
        return 0
    if args.command == "replay":
        print(build_report(args.cost_dir))
        return 0
    if args.command == "process":
        if not 1 <= args.batch_size <= 50:
            raise SystemExit("--batch-size must be between 1 and 50")
        if not 1 <= args.workers <= 4:
            raise SystemExit("--workers must be between 1 and 4")
        if args.max_new_batches is not None and args.max_new_batches < 1:
            raise SystemExit("--max-new-batches must be positive")
        print(json.dumps(process_dataset(
            input_path=args.input, state_path=args.state, batch_size=args.batch_size,
            workers=args.workers, max_new_batches=args.max_new_batches,
        ), indent=2, sort_keys=True))
        return 0
    if args.command == "status":
        print(json.dumps(dataset_status(args.input, args.state), indent=2, sort_keys=True))
        return 0
    if args.command == "snapshot":
        print(json.dumps(save_snapshot(args.input, args.state, args.name, args.out), indent=2, sort_keys=True))
        return 0
    if args.command == "export":
        print(json.dumps(export_artifacts(args.input, args.state, args.out_dir), indent=2, sort_keys=True))
        return 0
    if args.command == "jev-status":
        print(json.dumps(jev_status(args.input, args.state), indent=2, sort_keys=True))
        return 0
    if args.command == "jev-snapshot":
        print(json.dumps(save_jev_snapshot(
            args.input, args.state, args.name, args.out, args.label_config,
        ), indent=2, sort_keys=True))
        return 0
    if args.command == "jev-export":
        print(json.dumps(export_jev_artifacts(
            args.input, args.state, args.out_dir, args.label_config,
        ), indent=2, sort_keys=True))
        return 0
    if args.command == "jev-pilot":
        if args.run_kind == "cold" and not args.confirm_paid_run:
            raise SystemExit("Refusing paid Jev pilot without --confirm-paid-run")
        max_spend = None
        if args.max_spend_usd is not None:
            try:
                max_spend = Decimal(args.max_spend_usd)
            except InvalidOperation as exc:
                raise SystemExit("--max-spend-usd must be a decimal number") from exc
            if max_spend <= 0:
                raise SystemExit("--max-spend-usd must be positive")
        if args.run_kind == "cold" and max_spend is None:
            raise SystemExit("Cold Jev pilot requires --max-spend-usd")
        print(json.dumps(run_jev_pilot(
            input_path=args.input,
            cost_dir=args.cost_dir,
            run_kind=args.run_kind,
            max_spend_usd=max_spend,
        ), indent=2, sort_keys=True))
        return 0
    if args.command == "jev-report":
        try:
            budget = Decimal(args.budget_usd)
        except InvalidOperation as exc:
            raise SystemExit("--budget-usd must be a decimal number") from exc
        print(build_jev_pilot_report(args.cost_dir, budget))
        return 0
    if args.command == "jev-process":
        if not args.confirm_paid_run:
            raise SystemExit("Refusing paid Jev calls without --confirm-paid-run")
        if not 1 <= args.workers <= 32:
            raise SystemExit("--workers must be between 1 and 32")
        if args.max_new_records is not None and args.max_new_records < 1:
            raise SystemExit("--max-new-records must be positive")
        if not 0 <= args.confidence_threshold <= 1:
            raise SystemExit("--confidence-threshold must be between 0 and 1")
        try:
            max_spend = Decimal(args.max_spend_usd)
        except InvalidOperation as exc:
            raise SystemExit("--max-spend-usd must be a decimal number") from exc
        if max_spend <= 0:
            raise SystemExit("--max-spend-usd must be positive")
        print(json.dumps(process_with_jev(
            input_path=args.input,
            state_path=args.state,
            workers=args.workers,
            max_spend_usd=max_spend,
            max_new_records=args.max_new_records,
            confidence_threshold=args.confidence_threshold,
            requested_model=args.model,
        ), indent=2, sort_keys=True))
        return 0
    if not 1 <= args.verification_size <= 50:
        raise SystemExit("--verification-size must be between 1 and 50")
    print(json.dumps(finalize_dataset(args.input, args.state, args.verification_size), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
