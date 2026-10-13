# Jev hybrid 100-review cost and runtime report

Generated from saved measurements on 2026-10-12T01:12:24.706519+00:00. Offline replay makes no API calls.

## Measured pilot

- Input: 100 rows / 100 unique texts; SHA-256 `c884ac3b9be5066995d5063f96ad9af6e5e082975788c1684c4f6b6ea661dd0e`
- Cold completion: 100 completed, 0 failed
- Cold Jev enrichment calls: 100
- Cold wall time: 65.814 seconds
- Cold measured API spend: $0.004443
- Saved-ledger reconciliation: $0.004443; difference from rate-file calculation: $0.000000
- Warm wall time: 0.008 seconds
- Warm new enrichment calls: 0
- Warm incremental API spend: $0.000000
- Local compute/electricity cost: unknown (not silently treated as zero)

## 100,000-review projection

- Exact-text reuse case: 78,099 Jev classifications, estimated $3.4700
- No-reuse comparison: 100,000 Jev classifications, estimated $4.4431
- Conservative 25% retry/overhead case: $4.3375
- Declared budget: $5.00 — within the declared budget
- Single-worker linear enrichment estimate: 3.54 hours; parallel estimates remain provisional until measured at 500 and 10,000.

## Rate and controls

- Jev input: $0.042 per million input tokens; output tokens free, checked 2026-10-11 at https://typesafe.ai/blog/introducing-system-one-models-and-jev.
- The production runner uses a concurrency-safe pre-dispatch reservation ledger, bounded retries, atomic saves, exact-text cache keys, and a required hard spending cap.
- The pilot uses one worker. Production concurrency is increased only after like-for-like checkpoint measurements.
- This projection is refreshed after 500 and 10,000 reviews before authorizing 100,000.
