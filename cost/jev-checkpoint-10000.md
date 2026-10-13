# Jev v2 10,000-review checkpoint

- Input rows: 10,000
- Distinct nonempty texts: 8,448
- IDs accounted for before the run: 1,437
- New paid classifications: 7,969
- Workers: 4
- Completed calls: 7,969
- Failed attempts: 0
- Retries: 0
- Incremental Jev spend: $0.380942394
- Cumulative production-state spend: $0.404064192
- Enrichment wall time: 409.669 seconds (6.83 minutes)
- Median latency: 0.161 seconds
- P95 latency: 0.219 seconds
- P99 latency: 0.407 seconds
- Maximum latency: 1.924 seconds
- Needs-review: 3,610/8,448 distinct texts (42.7%)
- Stored budget alerts: 50% and 75%
- After snapshot: 10,000 completed input IDs

The checkpoint passed cost, reliability, parallelism, caching, resume, and notification gates. The full 100,000-row before snapshot already accounts for 26,640 IDs through cached text results. Remaining work is 69,651 new distinct classifications, projected to cost $3.3295 and take approximately 60 minutes at measured four-worker throughput. Project-wide final spend is projected at $3.7453, or $4.5776 with a conservative 25% allowance on the remaining calls. The full run remains subject to explicit approval and the $4.70 cumulative production-state cap.
