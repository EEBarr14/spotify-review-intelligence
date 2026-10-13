# Resumable Run State

`pipeline.sqlite3` preserves the earlier local-Ollama baseline. `jev_pipeline.sqlite3` is the completed Jev production-state database. Both are intentionally excluded from Git; the compact, machine-checkable final evidence is exported to `grading/final-submission/`.

The databases use SQLite WAL journaling. Validated predictions and their call evidence are committed after each batch. The local baseline state was reused in this order:

1. `checkpoint_500.csv`
2. `analysis_10000.csv`

The final Jev sequence used `checkpoint_500.csv`, `analysis_10000.csv`, and the representative `analysis_100000.csv` in one durable Jev state. `jev_full_100000_before.json` and `jev_full_100000_after.json` are the full-run interruption/resume snapshots. Progress JSON files are offline-readable status snapshots and make no model calls.
