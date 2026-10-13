# Jev hybrid cost pilot

This folder is the isolated 100-review cold/warm experiment required by the assignment. The fixed input is `Final Assignment - Spotify Reviews Dataset/cost_100.csv` (100 rows and 100 distinct texts). Jev performs fixed-label enrichment; the existing local Ollama model performs the bounded verification, issue-naming, and memo roles. Code performs validation, grouping arithmetic, ranking, and cache lookup.

The TypeSafe account contains $5.00 of prepaid credit. Local caps are intentionally much smaller than the balance: $0.01 for connectivity and $0.10 for the cold 100. The runner reports and persists 50%, 75%, 90%, and cap-blocked budget events. Confirm auto-refill is disabled in the TypeSafe console; the API's token-usage response is not a provider-side dollar notification.

The October 11 cold run completed all 100 reviews with no failures for $0.004443054. The warm replay made zero Jev calls and cost $0. The exact-text-reuse full-sample projection is $3.4700, or $4.3375 with a conservative 25% allowance. See `report.md` for the reproducible offline calculation.

## Safe order of operations

1. Add `TYPESAFE_API_KEY` to the repository-root `.env`. Do not paste or commit the key.
2. Make one paid connectivity call in a separate state database.
3. Inspect that saved result before authorizing the cold pilot.
4. Run the cold pilot once with one worker and an explicit cap.
5. Run the warm replay. It reads saved Jev results locally and should make zero new enrichment calls.
6. Rebuild the report offline.

Connectivity test (paid; only after explicit approval):

```bash
python3 run_pipeline.py jev-process \
  --input "Final Assignment - Spotify Reviews Dataset/cost_100.csv" \
  --state state/jev_connectivity.sqlite3 \
  --workers 1 --max-new-records 1 --max-spend-usd 0.01 \
  --confirm-paid-run
```

Cold pilot (paid; only after separately inspecting and approving the connectivity result):

```bash
python3 run_pipeline.py jev-pilot \
  --input "Final Assignment - Spotify Reviews Dataset/cost_100.csv" \
  --cost-dir cost/jev-pilot --run-kind cold \
  --max-spend-usd 0.10 --confirm-paid-run
```

Warm replay (no Jev call):

```bash
python3 run_pipeline.py jev-pilot \
  --input "Final Assignment - Spotify Reviews Dataset/cost_100.csv" \
  --cost-dir cost/jev-pilot --run-kind warm
```

Offline calculator replay (no API key and no model calls):

```bash
python3 run_pipeline.py jev-report --cost-dir cost/jev-pilot --budget-usd 5.00
```

The runner refuses to overwrite an existing cold or warm evidence directory. Starting a new experiment therefore requires choosing a new `--cost-dir`; do not delete measured evidence merely to rerun it.
