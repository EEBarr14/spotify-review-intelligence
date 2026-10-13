# Jev v2 hybrid cost pilot

This directory preserves the separately authorized v2 100-review cold/warm experiment. It does not overwrite or reuse the v1 evidence in `cost/jev-pilot/`.

The v2 contract adds explicit untrusted-review handling, a primarily-non-English language rule, and the revised ambiguity threshold documented in the repository README. The cold run completed 100/100 reviews with no failed Jev calls for $0.004779054. The warm replay made zero Jev calls and cost $0.

The exact-text-reuse projection is $3.7324 for 78,099 classifications, or $4.6655 with a conservative 25% retry/overhead allowance. The production-state cap is limited to $4.70; auto-recharge is disabled, and the prepaid account balance is $5.00.

See `report.md`, `cold/summary.json`, and `warm/summary.json` for reproducible measurements. The v1 and v2 caches are intentionally distinct because their label configurations differ.

Offline calculator replay (no API key, network request, or model call):

```bash
python3 run_pipeline.py jev-report --cost-dir cost/jev-pilot-v2 --budget-usd 5.00
```

The paid cold command is intentionally separate and requires both a dollar cap and the explicit acknowledgement flag. It is preserved for reproducibility; do not rerun it merely to inspect the saved evidence:

```bash
python3 run_pipeline.py jev-pilot \
  --input "Final Assignment - Spotify Reviews Dataset/cost_100.csv" \
  --cost-dir cost/jev-pilot-v2 --run-kind cold \
  --max-spend-usd 0.10 --confirm-paid-run
```

Warm replay reads the saved result cache and should make zero Jev calls:

```bash
python3 run_pipeline.py jev-pilot \
  --input "Final Assignment - Spotify Reviews Dataset/cost_100.csv" \
  --cost-dir cost/jev-pilot-v2 --run-kind warm
```
