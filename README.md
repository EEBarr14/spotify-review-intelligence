# Spotify Review Insight Pipeline

This repository builds an auditable, resumable pipeline that converts the supplied Spotify review dataset into validated labels, issue membership, deterministic priority rankings, and a grounded recommendation.

Python owns source accounting, sampling, hashes, validation, exact-text caching, aggregation, ranking, and evidence logs. The original pilot used a local Qwen model through Ollama. The completed final workflow uses Jev for fixed-label enrichment and the local model for bounded verification and memo writing. All paid gates and the 100,000-review run are complete; their measured settings and results are recorded below.

## Revised scope and representative sample

The revised assignment permits a completed analysis of at least 100,000 reviews and requires a deployed dashboard backed by a deployed API and database. The instructor also extended the deadline by one week; the linked assignment document still displays the earlier October 13 date. The internal completion target is October 19, 2026.

The pipeline still ingests and profiles all 660,622 source rows. Semantic classification is scoped to a deterministic representative sample of exactly 100,000 nonempty reviews, while all 13 empty-text records are separately accounted for and quarantined as `empty_review_text`.

The sample is not the first 100,000 source rows. It selects the lowest values of `SHA-256(seed + ':' + review_id)` across all 660,609 eligible nonempty source records, using the fixed seed `berkeley-fall-2026-assignment-5-v1`. This produces a reproducible pseudorandom sample independent of source row order while retaining duplicate review texts as separate business records.

Verified sample profile:

- 100,000 sampled nonempty review IDs
- 78,099 distinct review texts
- 21,901 rows eligible for exact-text result reuse
- Date coverage from May 17, 2022 through November 15, 2023
- All 50 golden-set review IDs included in the final sample
- All 10,000 development-checkpoint review IDs included in the final sample
- Sample SHA-256: `cf2641e8f3075e392a4c693c7cd45484c68e907569c48718cf131f0e321d643c`

Reproduce the sample without model calls:

```bash
python3 scripts/create_representative_sample.py \
  --input "Final Assignment - Spotify Reviews Dataset/spotify_reviews_18months.csv" \
  --output "Final Assignment - Spotify Reviews Dataset/analysis_100000.csv" \
  --manifest "Final Assignment - Spotify Reviews Dataset/analysis_100000_manifest.json" \
  --quarantine "state/empty_review_text_quarantine.jsonl" \
  --golden "Final Assignment - Spotify Reviews Dataset/golden_50_to_label.csv" \
  --analysis-10000 "Final Assignment - Spotify Reviews Dataset/analysis_10000.csv"
```

The final dashboard recommendation is titled **The Business Question Comes First: Focus on Usability**. The deployment-ready Sites application has a server-rendered frontend, backend API routes, and a D1 database. Its bounded production seed contains verified run metadata, aggregates, rankings, recommendation claims, evaluation results, and 24 traceable source-review evidence records; the complete 100,000-row result set remains in the grading package. This keeps the web application small while preserving the full local audit trail. A static-only GitHub Pages deployment would not satisfy the revised brief.

**Publication status as of October 12, 2026:** the source code and grading evidence are published in the public [Spotify Review Intelligence GitHub repository](https://github.com/EEBarr14/spotify-review-intelligence); both the repository and raw README returned HTTP `200` in a signed-out check. The public dashboard, API, and D1 database are deployed at [Spotify Review Intelligence](https://spotify-review-intelligence.groovyfern6.chatgpt.site). Anonymous checks returned HTTP `200` for the homepage, final-results API, and usability evidence endpoint. The API returned the saved 100,000-review results, and the live D1 database contains the expected run, aggregate, recommendation, evaluation, and 24 evidence rows.

The silent captioned [interruption/resume walkthrough](https://github.com/EEBarr14/spotify-review-intelligence/raw/refs/heads/main/demo/spotify-resume-walkthrough.webm) demonstrates the saved 26,640-review checkpoint, the resumed segments, and the final 100,000-review checkpoint without rerunning paid classification. The direct link opens or downloads the public video file because GitHub does not embed WebM playback on its code page.

## Actual execution history

- **October 5:** Built the local Ollama pipeline and measured multiple 100-review cold/warm experiments with Qwen 4B and 2B. Tested verbose JSON, compact numeric codes, hybrid schemas, smaller batches, and one- versus two-worker execution. Compact codes improved speed, but independent consistency checks exposed topic, intent, severity, and cross-review contamination risks. These experiments are preserved in [`cost/baselines/`](cost/baselines/) and summarized in [`cost/experiment_comparison.md`](cost/experiment_comparison.md).
- **October 5–6:** Demonstrated atomic checkpoint/resume behavior with the local runner, completed the 500-review local checkpoint, and completed the 10,000-review local checkpoint: 10,000 rows, 8,448 distinct texts, and about 3.26 hours of active processing. Two local workers were slower than one on the shared Mac, so local parallelism was rejected. The projected 100,000-review local run remained roughly 35 hours at the measured 10,000-review rate; the earlier full-corpus projection was much longer.
- **October 6:** Finished and corrected the hand-labeled Golden 50, saved the local-model evaluation, and retained the local results as baseline evidence rather than presenting them as the final provider run.
- **October 8:** Applied the revised assignment scope, profiled all 660,622 source rows, created the deterministic 100,000-review sample, explicitly quarantined the 13 empty source texts, and built the resumable Jev runner plus the dashboard/API/D1 foundation.
- **October 11:** After explicit paid-run approvals, completed the Jev connectivity check, v1 cold/warm 100-review pilot, Golden-50 evaluation, adversarial testing, v2 correction, v2 cold/warm pilot, 500-review gate, 10,000-review gate, and the full 100,000-review run. The final run used four workers, exact-text caching, a durable queue, and three resumable segments. It completed all 100,000 sampled IDs for $3.737583948 in production-state spend and $3.749242854 across all Jev work.
- **October 11–12:** Generated the final local memo, deterministic ranking, claims, 100,000-record grading package, trace example, and bounded dashboard seed. The instructor checker passed with 100% valid coverage for the declared 100,000-review scope, and the dashboard passed local lint, build, API, database, and browser checks. On October 12, deployed Sites version 2, verified an authenticated `200` response from the production API, and confirmed all nine D1 tables were populated. The first deployment check exposed an interrupted lazy seed; the final implementation uses an atomic D1 batch so an interrupted first request cannot leave a partial database.
- **October 12:** Generated and verified a 52-second, 1920-by-1080 silent captioned interruption/resume walkthrough from saved run evidence. It contains no screen capture, microphone audio, credentials, or additional Jev calls.

The paid sequence was deliberately gated. Completion of setup or a smaller checkpoint never automatically authorized the next paid stage.

## Rubric and submission evidence

The linked evidence below maps directly to the revised 4/3/3 rubric. “Complete” means the saved local artifact exists and has been checked; publication-dependent items remain explicitly pending.

The detailed release review is saved in [`docs/SUBMISSION_AUDIT.md`](docs/SUBMISSION_AUDIT.md).

| Rubric item | Status | Evidence |
|---|---|---|
| D1 — accessible code, setup, and artifacts | Complete | The public [GitHub repository](https://github.com/EEBarr14/spotify-review-intelligence) and raw README were verified without authentication; evidence includes [`pyproject.toml`](pyproject.toml), [`run_pipeline.py`](run_pipeline.py), [`dashboard/README.md`](dashboard/README.md), and [`grading/final-submission/`](grading/final-submission/). |
| D2 — architecture, schema, and provenance | Complete | [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md), the fixed labels in [`Final Assignment - Spotify Reviews Dataset/GRADING_CONTRACT.md`](Final%20Assignment%20-%20Spotify%20Reviews%20Dataset/GRADING_CONTRACT.md), and the source/sample checksums above |
| D3 — memo numbers linked to calculations and source evidence | Complete | [`memo.md`](grading/final-submission/memo.md), [`claims.csv`](grading/final-submission/claims.csv), [`ranking.csv`](grading/final-submission/ranking.csv), and [`docs/TRACE_EXAMPLE.md`](docs/TRACE_EXAMPLE.md) |
| D4 — recommendation, alternative, and limitations | Complete | [`memo.md`](grading/final-submission/memo.md) identifies usability, access as the alternative, and three limitations |
| T1 — 50 human labels and per-field error analysis | Complete | [`golden_50_to_label.csv`](Final%20Assignment%20-%20Spotify%20Reviews%20Dataset/golden_50_to_label.csv), [`state/jev_golden_50_evaluation.md`](state/jev_golden_50_evaluation.md), and the Golden-50 section below |
| T2 — independent verification and planted/injection tests | Complete, with disclosed sample size | The independent local verifier relabeled a deterministic 10-review sample without seeing Jev's answers: 80% topic agreement, 80% intent agreement, 80% exact-severity agreement, and severity MAE 0.20. See [`verification.json`](cost/jev-pilot-v2/cold/verification.json), [`tests/test_jev.py`](tests/test_jev.py), and the v2 5/5 adversarial result in [`state/jev_adversarial_evaluation_v2.json`](state/jev_adversarial_evaluation_v2.json). |
| T3 — cold/warm calculator and retry/spend/recovery controls | Complete | [`cost/jev-pilot-v2/report.md`](cost/jev-pilot-v2/report.md), [`cost/jev-pilot-v2/README.md`](cost/jev-pilot-v2/README.md), [`docs/TEST_PROTOCOL.md`](docs/TEST_PROTOCOL.md), and the measured pilot below |
| W1 — ingestion, coverage, and valid classifications | Complete for revised scope | Full-file ingestion profiles 660,622 rows and quarantines 13 empty texts; the representative run classifies 100,000 nonempty IDs. [`state/submission_check_final.json`](state/submission_check_final.json) reports `status: pass`. |
| W2 — runnable bounded stages, saved handoffs, and resume | Complete | [`run_pipeline.py`](run_pipeline.py), [`checkpoint_before.json`](grading/final-submission/checkpoint_before.json), [`checkpoint_after.json`](grading/final-submission/checkpoint_after.json), and [`calls.jsonl`](grading/final-submission/calls.jsonl) show bounded calls and 26,640 → 100,000 completed IDs without relabeling saved work. The [captioned walkthrough](https://github.com/EEBarr14/spotify-review-intelligence/raw/refs/heads/main/demo/spotify-resume-walkthrough.webm) presents that saved evidence. |
| W3 — reproducible ranking and deployed database-backed dashboard | Complete | [`ranking.csv`](grading/final-submission/ranking.csv), [`dashboard/`](dashboard/), and the public [Spotify Review Intelligence](https://spotify-review-intelligence.groovyfern6.chatgpt.site) application. The homepage, production API, evidence drill-down, and all nine D1 tables were verified. |

### Offline verification commands

These commands do not make paid model calls:

```bash
python3 -m unittest discover -s tests
python3 run_pipeline.py jev-report --cost-dir cost/jev-pilot-v2 --budget-usd 5.00
python3 "Final Assignment - Spotify Reviews Dataset/check_submission.py" check \
  --reference state/reference_100000.json \
  --submission grading/final-submission \
  --out state/submission_check_final.json
(cd dashboard && npm run lint && npm run build)
```

### Public-safety check

- Real credentials belong only in the ignored local `.env`; the repository contains a blank [`.env.example`](.env.example). Both the root and dashboard ignore rules exclude environment files, generated runtime state, and local databases.
- Candidate public files were scanned for common API-key/private-key/token patterns, nonempty credential assignments, credential-bearing URLs, personal workstation paths, email addresses, and phone/payment-number-like strings. No real credential was found. The one nonempty key-shaped value is an explicit fake value used by a unit test.
- Personal absolute workstation paths were removed from saved public progress/summary artifacts. The dashboard's 24 public evidence excerpts contain no detected email address, phone number, payment-card-like number, or credential-bearing URL.
- The full grading export necessarily contains exact evidence excerpts from the public CC0 source because the assignment requires traceability. Source author names and author IDs were already removed by the course dataset. The memo and dashboard avoid unnecessary personal details and do not treat reviewer allegations as verified facts.
- Repeat the secret scan against staged files and Git history after the first commit and before making the repository public. If a real credential is ever committed, revoke and rotate it; deleting the file is not enough.

## Jev runner and measured paid pilot

The Jev path uses compact typed questions, a separate durable SQLite database, exact-text reuse, atomic per-result saves, bounded retry/backoff, a shared concurrency-safe spending ledger, and a required hard spend ceiling. Put `TYPESAFE_API_KEY` in the local `.env` file; never commit or paste the key into a report or chat.

Inspect saved Jev progress without an API key or model call:

```bash
python3 run_pipeline.py jev-status \
  --input "Final Assignment - Spotify Reviews Dataset/analysis_100000.csv" \
  --state state/jev_pipeline.sqlite3
```

Paid processing requires both an explicit dollar ceiling and the acknowledgement flag. The first authorized call should use `--max-new-records 1`; worker count and cap for later stages will be chosen from measured pilot results rather than guessed in advance.

The no-call commands `jev-snapshot` and `jev-export` preserve required interruption/resume evidence and produce the grading adapter from saved results. `scripts/evaluate_jev_golden.py` scores the frozen model configuration against the hand-labeled Golden 50 only after inference, so human answers are never sent to Jev.

The required hybrid cold/warm experiment is wrapped by `jev-pilot`. The initial v1 evidence is documented in [`cost/jev-pilot/README.md`](cost/jev-pilot/README.md); the final v2 calculator and replay commands are in [`cost/jev-pilot-v2/README.md`](cost/jev-pilot-v2/README.md). Cold evidence is immutable by default, the first run is fixed at one worker, and the warm run reads the saved Jev cache without contacting Jev.

Measured October 11, 2026 results:

- Connectivity: 1/1 classification saved successfully; 1,043 input tokens; **$0.000043806**; 0.202 seconds of API wall time.
- The connectivity review was non-English and was correctly routed to `needs_review` through high unsupported-language and ambiguity probabilities.
- Cold 100: 100/100 classifications; 0 failed calls; 109,248 input tokens; **$0.004443054**; 16.161 seconds for Jev enrichment and 65.814 seconds for the complete hybrid workflow.
- Warm 100: 100/100 cache hits; **0 Jev calls**; **$0 incremental spend**; 0.008 seconds for the complete replay.
- Exact-text-reuse projection for 78,099 unique texts: **$3.4700**; conservative 25% allowance: **$4.3375**.

The connectivity and cold-pilot local ledger total was **$0.004486860**. Completing that pilot did not itself authorize later paid gates; Golden, adversarial, 500-, 10,000-, and 100,000-review stages were subsequently authorized and executed as separate gates, as documented below.

### Golden 50 evaluation

The frozen October 11 configuration was then run on the label-free Golden-50 input. The human labels were kept local and used only for offline comparison after all predictions were saved. Fifty rows contained 49 distinct texts, so exact-text caching reduced the paid work to 49 Jev calls. The run cost **$0.002172954**, took 7.902 seconds, and had no failed calls.

Measured agreement with the frozen human labels:

- Topic accuracy: **88%**; macro F1: **0.828**
- Intent accuracy: **92%**; macro F1: **0.790**
- Exact severity accuracy: **86%**; severity MAE: **0.160**
- Sentiment MAE: **0.222**
- Needs-review accuracy: **50%**

The low 4% joint-exact result is not an appropriate headline measure because it requires the continuous Jev sentiment score to exactly equal the discrete hand-entered sentiment value; 47 of 50 rows differed numerically on that field. The actionable weakness is conservative review routing: the human set marked 3 rows for review, while the current rule marked 28. It caught all 3 human-marked rows but produced 25 additional review flags, primarily from the 0.50 ambiguity threshold.

The Golden 50 will not be used to tune that threshold. Any change must be justified using the separate development/adversarial evidence and declared before further evaluation, avoiding test-set leakage. Full metrics and disagreements are preserved in `state/jev_golden_50_evaluation.json` and `state/jev_golden_50_evaluation.md`.

### Adversarial gate and v2 candidate

The frozen v1 candidate passed 3 of 5 adversarial cases. It handled a crash-related prompt injection, the intentionally ambiguous review, and the serious privacy-harm review. It failed a second prompt-injection case by following embedded label commands, and it interpreted a Spanish review correctly instead of applying the project's separate unsupported-language policy.

Those failures motivated a v2 candidate without consulting Golden-50 answers:

- topic, intent, severity, and sentiment questions now state that `review_text` is untrusted user feedback and commands inside it must be ignored;
- unsupported language now means primarily not English, even when Jev can understand or translate the text;
- review routing uses a direct ambiguity threshold of 0.75 instead of also treating the entire 0.35–0.65 probability band as automatically uncertain; and
- the independent minimum label-confidence threshold remains 0.55.

The intentionally ambiguous adversarial case scored 0.77 and remains routed to review; the failed injected case already had low minimum confidence and also remains routed. The v1 Golden evaluation remains the unbiased held-out score.

The separately authorized v2 re-test passed **5/5** adversarial cases with no failed calls. It cost **$0.000236838** and took 0.782 seconds. The v2 results correctly ignored both embedded label commands, routed the Spanish review to review, retained the ambiguous case, and assigned severity 5 to the privacy-harm case. The failed v1 result is preserved in `state/jev_adversarial_evaluation.json`; the passing v2 result is preserved in `state/jev_adversarial_evaluation_v2.json`.

The fresh v2 100-review validation then completed 100/100 reviews with no failed calls. Cold enrichment cost **$0.004779054** and took 15.752 seconds; the complete hybrid workflow took 53.713 seconds. Its warm replay made zero Jev calls, cost $0, and took 0.008 seconds. Review routing fell from 64/100 under v1 to 37/100 under v2; topic changed on 2 rows, intent on 1, and severity on 2. The v2 exact-text-reuse projection is **$3.7324** for 78,099 unique texts, or **$4.6655** with a conservative 25% retry/overhead allowance.

The authorized 500-review checkpoint completed all 500 rows, representing 479 distinct paid classifications and 21 exact-text cache reuses. With two workers, enrichment took 43.681 seconds and cost **$0.022884960** incrementally. All 479 calls succeeded with zero retries: median API latency was 0.162 seconds, p95 was 0.213 seconds, and maximum latency was 0.575 seconds. The before/after snapshots contain 0 and 500 completed checkpoint IDs, respectively. The needs-review rate was 39.5%, close to the v2 pilot's 37%, providing a stable routing signal across a larger sample.

The authorized 10,000-review checkpoint then reused those cached texts and completed all 7,969 remaining distinct classifications with four workers. All calls succeeded with zero retries or failed attempts. The run took 409.669 seconds (6.83 minutes) and cost **$0.380942394** incrementally, bringing cumulative production-state spend to **$0.404064192**. Median latency was 0.161 seconds, p95 was 0.219 seconds, p99 was 0.407 seconds, and maximum latency was 1.924 seconds. The local 50% and 75% budget alerts fired and were saved as designed. Needs-review routing was 42.7% across the 8,448 distinct texts: 459 met the non-English rule, 1,571 met the ambiguity threshold, and 2,275 had at least one low-confidence primary label; these reasons can overlap.

The authorized full run began with **26,640 of 100,000 review IDs** already accounted for through 8,448 cached texts. It completed the remaining 69,651 distinct classifications across three resumable segments: one deliberate optimization pause, one Codex-session interruption, and the final resume. No saved classification was repeated. Active enrichment time across the three segments was approximately **61.8 minutes**. Incremental full-run spend was **$3.333519756**, compared with the $3.3295 projection.

Final production results:

- 100,000/100,000 rows completed; zero pending or quarantined rows
- 78,099 distinct sample texts classified; 21,901 duplicate rows reused exactly
- 78,104 total v2 calls including five adversarial cases; zero failed attempts and zero retries
- Median API latency 0.166 seconds; p95 0.228 seconds; p99 0.418 seconds; maximum 2.813 seconds
- 32,245/78,099 unique texts (41.3%) routed for review under overlapping language, ambiguity, or low-confidence rules
- Production-state spend **$3.737583948** against the $4.70 cap
- All-project Jev spend **$3.749242854** against the $5.00 prepaid balance, leaving approximately $1.25076
- Before/after full-sample snapshots: 26,640 → 100,000 completed IDs

The raw provider/configuration export is in `grading/jev-v2-final/`. The checker-facing package is `grading/final-submission/`; it contains 100,000 validated records, membership, deterministic rankings, claims, normalized final-run call evidence, full-file ingestion evidence, the final memo, configuration metadata, and checkpoint snapshots. The instructor checker reports `status: pass`, 100% accounted and valid completion, 21,901 valid cache reuses, no issue codes, and a 1.0 working coverage candidate. Database integrity passed after completion. See `state/submission_check_final.json` and [docs/TRACE_EXAMPLE.md](docs/TRACE_EXAMPLE.md).

### Scaling techniques considered and final decision

| Technique | Decision | Reason and implementation |
|---|---|---|
| Question batching | Use | The six typed classification questions are sent together for each review, avoiding six separate API requests. |
| Multiple reviews in one Jev request | Do not use | Jev returns one answer set for the supplied state and no per-review response IDs. Keeping one review per request preserves auditable ID-to-label alignment. |
| Exact-text caching | Use | A SHA-256 text key plus the frozen label configuration reuses a validated result for every exact duplicate. The 100,000-row sample has 21,901 duplicate rows eligible for reuse. |
| Parallelization | Use cautiously | The runner has a shared concurrency-safe spend ledger and supports bounded workers. Concurrency starts at one, then advances 2 → 4 only after like-for-like checkpoint evidence shows stable quality, retries, and cost. More workers improve elapsed time, not token cost. |
| Queueing | Use a bounded deterministic queue | Pending work is reconstructed from the input minus committed SQLite predictions, then dispatched in waves no larger than the worker count. This is resumable after interruption without adding a separate message-broker dependency. |
| Provider asynchronous batch queue | Do not use | No asynchronous batch/queue endpoint is present in the documented Jev API. The local bounded queue supplies the required back-pressure and recovery behavior. |

### Jev spending protection and notifications

The account started with **$5.00 of prepaid Jev credit** and auto-recharge disabled. The one-record connectivity cap was $0.01, each cold-100 cap was $0.10, and the maximum production-state cap was **$4.70**. Actual all-project Jev spend was **$3.749242854**, leaving approximately **$1.25076**.

Jev's documented response reports input/output token usage, not a provider-supplied dollar price or billing-alert event. Therefore the project uses its own price notifications and guardrails:

- the current published input rate is pinned at **$0.042 per million input tokens**;
- every request reserves a conservative worst-case amount before dispatch;
- one concurrency-safe ledger admits work only while spent plus reserved cost is within `--max-spend-usd`;
- 50%, 75%, and 90% threshold alerts, plus any cap-blocked event, are printed and stored in SQLite;
- the live progress JSON reports spent, reserved, remaining, and percentage used;
- timeouts with uncertain charges retain their conservative reservation; and
- every larger checkpoint still requires separate explicit approval.

These are local safeguards, not a substitute for the provider account setting. Auto-refill remained disabled in the TypeSafe console, so the prepaid $5.00 was an independent outer limit. The rate assumption was rechecked against [TypeSafe's Jev announcement and pricing](https://typesafe.ai/blog/introducing-system-one-models-and-jev) before the 100,000-review run.

The planted-error tests in `tests/test_jev.py` prove invalid choices, malformed responses, authentication failures, and uncertain charges cannot silently become completed labels. The separate `tests/fixtures/jev_adversarial_reviews.csv` set contains prompt-injection, unsupported-language, ambiguity, and serious-harm cases. It was run after each Jev configuration was frozen; `scripts/evaluate_jev_adversarial.py` scored its saved results offline. The final v2 contract passed all five cases.

`scripts/build_dashboard_import.py` converts the grading records, rankings, claims, Golden-50 evaluation, memo, and durable Jev run history into ordered, chunked D1 SQL files. `scripts/build_dashboard_seed.py` creates the bounded idempotent hosted seed. Preview fixture data is never included in either final artifact.

See `docs/ARCHITECTURE.md` for the end-to-end data flow and real-review trace template, and `docs/TEST_PROTOCOL.md` for the paid gates, scaling rules, planted-error checks, and prompt-injection protocol.

## Pilot model

- Ollama 0.35.1
- `qwen3.5:4b-q4_K_M`
- Pinned digest `d8b0f5e9760c`
- Thinking disabled
- Temperature 0 and fixed seed
- JSON Schema constrained output

See [cost/README.md](cost/README.md) for the explicit pilot commands and offline replay.

## Measured 100 review pilot

The v2 baseline cold pilot finished 100 records in 357.090 seconds with 13 local model calls and $0 API spend. Its initial single-worker full-run projection was 388.99 hours with exact-text reuse. That evidence is preserved under `cost/baselines/v2-indexed/`.

The v3 compact-code pilot finished the same 100 records in 166.715 seconds: 2.14 times faster than v2. Its unchanged warm replay finished in 0.009 seconds with 100 cache hits and zero model calls. The corresponding base full-run projection is 155.34 hours with exact-text reuse, or 194.17 hours with 25% overhead.

The speed gain came with a quality warning. The independent 10-review verifier's agreement changed from 90% to 70% for topic, from 100% to 80% for intent, and from 100% to 90% for exact severity. Later hybrid and smaller-batch experiments improved some topic/intent checks but projected 177–248 hours and still showed severity or cross-review errors. See [cost/experiment_comparison.md](cost/experiment_comparison.md). With an October 13 deadline, the local-only plan is not safely inside both the quality and schedule gates.

See [cost/report.md](cost/report.md) for measurements, projections, controls, and replay instructions.

## Earlier local-model decision and measured tradeoff

The original plan selected a no-API-cost local route. That work remains as measured baseline evidence rather than the final provider decision. The selected local pilot configuration was `qwen3.5:4b-q4_K_M@d8b0f5e9760c` with compact numeric model output, deterministic mapping to the contract labels, and conservative text-only corrections for generic praise and explicit cancellation language.

The completed 500-review checkpoint contained 479 distinct texts and required about 608.9 seconds of enrichment across the initial and resumed runs, or approximately 0.787 distinct classifications per second. Linear extrapolation gave roughly 171 hours for all 484,189 distinct nonempty texts before sustained-load overhead. The revised final plan replaces that projected local full run with a measured Jev run on the representative 100,000-review scope.

The local experiments remain useful for comparing model choices and explaining the decision to switch. See [cost/experiment_comparison.md](cost/experiment_comparison.md).

## Scalable resumable runner

The production runner stores validated predictions and real call logs in a SQLite database using WAL journaling and a full durability setting. Each successful batch is committed atomically. The 500, 10,000, and full inputs share the same database, so checkpoint work is reused by the full run.

Inspect progress without making model calls:

```bash
python3 run_pipeline.py status \
  --input "Final Assignment - Spotify Reviews Dataset/analysis_10000.csv" \
  --state state/pipeline.sqlite3
```

Process or resume an input:

```bash
python3 run_pipeline.py process \
  --input "Final Assignment - Spotify Reviews Dataset/analysis_10000.csv" \
  --state state/pipeline.sqlite3 --batch-size 10 --workers 1
```

Stopping and rerunning the same command dispatches only unfinished distinct texts. Use `--max-new-batches N` for a bounded interruption test.

After enrichment completes, run the bounded verification, grouping and memo stages:

```bash
python3 run_pipeline.py finalize \
  --input "Final Assignment - Spotify Reviews Dataset/spotify_reviews_18months.csv" \
  --state state/pipeline.sqlite3 --verification-size 20
```

Export final grading artifacts:

```bash
python3 run_pipeline.py export \
  --input "Final Assignment - Spotify Reviews Dataset/spotify_reviews_18months.csv" \
  --state state/pipeline.sqlite3 --out-dir grading
```

The demonstrated resume snapshots contain 7,101 completed full-corpus IDs before resuming and 66,577 after completing additional work. The instructor's offline checker accepted IDs, hashes, schemas, exact-text cache provenance, resume evidence, and ranking arithmetic on the partial full export; its only remaining issue was unfinished classification.
