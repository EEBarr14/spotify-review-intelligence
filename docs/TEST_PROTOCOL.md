# Test and scaling protocol

## Before paid calls

- Verify the 100,000-review sample checksum and full-source accounting.
- Run unit tests for schema validation, retries, spend reservations, caching, resume storage, exports, offline rate recalculation, and dashboard imports.
- Confirm the paid CLI refuses to run without both a dollar cap and `--confirm-paid-run`.
- Keep `.env` outside Git and never print its value.
- Confirm TypeSafe auto-refill is disabled; the provider exposes token usage to the runner but no documented dollar-price notification event.
- Pin the checked Jev input rate in code and compare it with the current published rate before the full run.

## Paid gates

1. **Connectivity:** one review, one worker, separate state database, $0.01 local cap.
2. **Cold 100:** untouched `cost_100.csv`, empty isolated result/artifact cache, one worker, $0.10 local cap, all roles included.
3. **Warm 100:** replay saved results locally; expected zero Jev enrichment calls and zero incremental API spend.
4. **Golden 50:** freeze the configuration before scoring against human labels. Human labels are never model inputs.
5. **Adversarial 5:** run the saved injection, unsupported-language, ambiguity, and serious-harm set; investigate every failed expectation.
6. **Checkpoint 500:** compare quality, retries, latency, and spend; test two workers on a like-for-like cold subset only if the 100-review gate passes.
7. **Checkpoint 10,000:** confirm sustained throughput, rate-limit behavior, exact-text reuse, projected cost, and interruption/resume evidence.
8. **100,000:** proceed only when the revised conservative projection is within the account balance and declared cap.

## Scaling and spending controls

- Batch all six typed questions into one request for each review.
- Do not combine multiple reviews into one request unless Jev adds per-review response IDs; correct ID-to-label attachment takes priority over fewer HTTP calls.
- Reuse exact-text classifications only under the same frozen label configuration.
- Rebuild the pending queue deterministically from input hashes minus committed SQLite predictions after every restart.
- Dispatch only one bounded worker wave at a time. Test 2 and then 4 workers on comparable subsets before increasing sustained concurrency.
- Reserve estimated cost before dispatch through one shared ledger so concurrent workers cannot each spend the full cap.
- Emit and store local alerts at 50%, 75%, and 90% of the command cap and record any dispatch blocked by the cap.
- Keep the production-state command cap at or below $4.70 of the $5.00 prepaid balance. With prior isolated evidence runs below $0.012, this preserves more than $0.28 even if the production cap is fully consumed.

At every gate, failed or uncertain calls remain logged. A timeout with unknown usage keeps its conservative reservation charged locally until reconciled. Increasing concurrency is a timing decision, not a cost-saving claim.

### Measured 500-review gate

The v2 checkpoint passed: 500/500 rows accounted for, 479 distinct paid calls, 21 exact-text reuses, zero failed attempts, zero retries, and $0.022884960 incremental spend. Two-worker enrichment took 43.681 seconds; median, p95, and maximum API latency were 0.162, 0.213, and 0.575 seconds. The needs-review rate was 39.5%, compared with 37% in the v2 100-review pilot. Before/after snapshots prove 0 → 500 completed checkpoint IDs. These results permit consideration of a four-worker 10,000 checkpoint under a $0.50 cumulative production-state cap, but do not authorize it.

### Measured 10,000-review gate

The four-worker v2 checkpoint passed: 10,000/10,000 rows accounted for, including 7,969 new paid calls; zero failed attempts and zero retries; $0.380942394 incremental spend; and 409.669 seconds elapsed. Median, p95, p99, and maximum API latency were 0.161, 0.219, 0.407, and 1.924 seconds. The stored 50% and 75% alerts confirm the live budget-notification path. Before/after snapshots prove 1,437 → 10,000 completed input IDs.

The full-sample before snapshot accounted for 26,640 of 100,000 IDs through cached texts. The separately authorized remaining work completed 69,651 distinct calls across three resumable segments in approximately 61.8 active minutes. Incremental full-run spend was $3.333519756; final production-state spend was $3.737583948; and all-project spend was $3.749242854. All 100,000 rows and 78,099 distinct sample texts completed with zero failed attempts and zero retries. The after snapshot contains all 100,000 IDs, the database integrity check passed, and the final export contains zero pending/quarantined rows.

## Planted-error coverage

Automated tests deliberately provide invalid choices, malformed responses, an authentication failure, a retryable validation failure, and unknown timeout usage. Passing means these conditions are rejected, logged, retried only when appropriate, and prevented from silently becoming completed records.

## Prompt-injection coverage

Review text is carried only in the Jev `state`; the fixed question definitions remain program-controlled. The adversarial fixture contains text that instructs the classifier to return false labels. The expected result follows the actual review meaning, not those embedded instructions. A non-English case must be routed to review under the declared policy.

The initial v1 candidate passed 3/5 cases and was stopped before the 500-review gate. The v2 candidate adds an explicit untrusted-text rule, defines unsupported language as primarily non-English even when translatable, and uses a 0.75 direct ambiguity threshold while retaining the 0.55 minimum label-confidence rule. These changes were derived from the adversarial set, not from Golden-50 answers. Both versions' evidence is preserved. The v2 re-test passed 5/5, followed by successful v2 cold/warm 100, 500, 10,000, and 100,000 stages with zero failed attempts and zero warm API usage.
