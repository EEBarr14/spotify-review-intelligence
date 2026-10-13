# Submission audit — October 12, 2026

This audit compares the saved project with the revised assignment document and its 4/3/3 rubric. It also checks the candidate public repository files, dashboard source/seed, and grading package for credential and privacy risks.

## Overall result

The analysis pipeline, 100,000-review run, evaluation evidence, deterministic ranking, final memo, grading adapter, API, database schema, dashboard, and interruption/resume walkthrough are complete. The instructor checker reports `status: pass` for the declared representative 100,000-review scope. The public [Spotify Review Intelligence](https://spotify-review-intelligence.groovyfern6.chatgpt.site) deployment, anonymous API and evidence access, and all nine D1 tables were verified on October 12. The 52-second silent captioned walkthrough presents the saved 26,640-before and 100,000-after checkpoints and call evidence without another paid run.

## Rubric audit

| Item | Result | Evidence or remaining action |
|---|---|---|
| D1: code/setup/artifacts accessible | Met | Root README, `pyproject.toml`, pipeline CLI, dashboard README, and final grading folder are in the public [GitHub repository](https://github.com/EEBarr14/spotify-review-intelligence). The repository and raw README returned HTTP `200` without authentication. |
| D2: architecture/schema/provenance | Met | `docs/ARCHITECTURE.md`, source and sample checksums, label configuration, and original IDs/hashes are saved. |
| D3: memo numbers trace correctly | Met | Claims, ranking, membership, memo, and the real-review trace agree. The checker passed. |
| D4: recommendation/alternative/limitations | Met | Usability is primary; access is the alternative; sample bias, classification uncertainty, and lack of causal/revenue evidence are disclosed. |
| T1: Golden 50 and error analysis | Met | Fifty human labels and per-field Jev v1 metrics/disagreements are saved; the v2 changes were based on separate adversarial evidence. |
| T2: independent/system tests | Met with a modest verifier sample | A deterministic 10-review local verifier sample reports 80% topic, intent, and exact-severity agreement and 0.20 severity MAE. Planted errors are automated; v2 passed 5/5 adversarial cases. |
| T3: cost/runtime calculator and controls | Met | Real Jev v2 cold/warm 100-review evidence, editable rates/usage, offline replay, hard caps, alerts, retries, cache, and resume controls are saved. |
| W1: ingestion and classification coverage | Met for revised scope | All 660,622 source rows were profiled; 13 empty texts were quarantined; 100,000 representative nonempty IDs were classified; no selected rows remain pending. |
| W2: runnable stages and resume | Met | Enrich, verify, group, rank, and memo roles have saved calls/artifacts. Snapshots show 26,640 → 100,000 completed IDs without duplicate classification, and the captioned walkthrough presents that saved evidence. |
| W3: ranking and deployed application | Met | Ranking is reproducible and the frontend/API/D1 application is publicly deployed. Anonymous requests returned the final dashboard data and database-backed usability evidence, and all nine D1 tables contain the expected bounded seed. |

## Security and privacy audit

Scopes inspected:

- root candidate tracked files (`git ls-files --cached --others --exclude-standard`);
- dashboard source and immutable production seed;
- `grading/final-submission/` and the raw Jev export;
- README, reports, progress snapshots, and call logs intended for publication.

Checks performed:

- common API-key, private-key, GitHub/AWS/Google token, JWT, bearer-token, and nonempty credential-assignment patterns;
- `.env` ignore behavior and blank `.env.example` contents;
- credential-bearing URL query parameters;
- personal workstation paths and owner-identifying strings;
- email, URL, phone-number-like, and payment-card-like patterns in evidence quotes;
- generated runtime databases, caches, and spreadsheet working files that should not be published.

Results and fixes:

- No real secret or API key was detected. `tests/test_jev.py` intentionally contains the fake value `secret-test-value` to test dotenv loading.
- `.env` is ignored and absent from candidate public files. `.env.example` contains only blank variable names.
- The exact dashboard source set was rescanned immediately before upload; it contained no API key, token, credential-bearing URL, or personal absolute path. Sites source credentials and access tokens were not written to the repository or deployment bundle.
- Personal absolute Mac paths were converted to repository-relative paths in saved public progress/summary files.
- SQLite state, generated caches, runtime state, raw source CSV, and working spreadsheets are ignored.
- The dashboard seed is limited to 24 traceable excerpts and now excludes review flags, obvious contact details, URLs, long number patterns, explicit abuse, and high-risk personal/security allegations. The API applies the same filter.
- The full grading package retains exact source excerpts because the assignment requires quote membership and traceability. The course extract removed author names and author IDs, and the source is public CC0 data. The memo does not repeat unnecessary personal details or present allegations as verified facts.

## Final checks after publication

- Recheck the public walkthrough link without authentication after the final documentation commit is pushed.
- The public dashboard homepage, API, and usability evidence drill-down have been verified without authentication; recheck them once more after any later deployment.
- Compare the live completed count, spend, Golden accuracy, issue ranking, and recommendation with the saved grading files.
- Scan staged files and Git history again before changing repository visibility.
- The root README contains the GitHub URL, live dashboard URL, access information, and walkthrough link.
