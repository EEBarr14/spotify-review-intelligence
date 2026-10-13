# Jev v2 500-review checkpoint

- Input rows: 500
- Distinct nonempty texts: 479
- Exact-text reuses: 21
- Workers: 2
- Completed calls: 479
- Failed attempts: 0
- Retries: 0
- Incremental Jev spend: $0.022884960
- Enrichment wall time: 43.681 seconds
- Median latency: 0.162 seconds
- P95 latency: 0.213 seconds
- Maximum latency: 0.575 seconds
- Needs-review: 189/479 distinct texts (39.5%)
- Before snapshot: 0 completed input IDs
- After snapshot: 500 completed input IDs

The checkpoint passed the cost, reliability, caching, and routing-stability gates. Two-worker elapsed time was approximately 1.7 times faster than the single-worker pilot projection. The next proposed checkpoint contains 10,000 rows and 8,448 distinct texts. Its before snapshot already accounts for 1,437 review IDs through 479 cached texts; 7,969 new calls are projected to cost about $0.381. Four workers and a $0.50 cumulative production-state cap are recommended, subject to explicit approval.
