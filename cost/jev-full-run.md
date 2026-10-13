# Jev v2 final 100,000-review run

## Completion

- Sample rows completed: 100,000/100,000
- Distinct sample texts classified: 78,099
- Exact-text reuse rows: 21,901
- Pending or quarantined final rows: 0
- Full-sample before snapshot: 26,640 completed IDs
- Full-sample after snapshot: 100,000 completed IDs
- Workers: 4
- Active full-run enrichment time: approximately 61.8 minutes across three resumable segments

The segments include one deliberate pause to remove repeated whole-input progress hashing, one later Codex-session interruption, and a final resume. SQLite WAL/full durability and exact-text cache keys preserved every committed classification. Resumes dispatched only unfinished text hashes.

## Reliability and performance

- V2 call events: 78,104, including five adversarial cases
- Successful events: 78,104
- Failed attempts: 0
- Retry attempts: 0
- Median API latency: 0.166 seconds
- P95 latency: 0.228 seconds
- P99 latency: 0.418 seconds
- Maximum latency: 2.813 seconds
- Database integrity after completion: OK

## Cost

- Incremental full-run spend: $3.333519756
- Production-state spend: $3.737583948
- All-project Jev spend: $3.749242854
- Production cap: $4.70
- Prepaid account balance: $5.00 with auto-recharge disabled
- Approximate unused balance: $1.25076

The projected incremental full-run spend was $3.3295; actual spend differed by about $0.0040. Stored 50% and 75% threshold alerts fired during the run. The cap was not reached.

## Routing and primary labels

- Unique texts marked `needs_review`: 32,245/78,099 (41.3%)
- Unsupported-language threshold: 4,225
- Ambiguity threshold: 12,535
- Low primary-label confidence: 21,714

Routing reasons overlap. These are conservative audit flags; the saved typed classifications remain available for aggregate analysis, while the dashboard and README disclose the review rate.

## Deterministic issue ranking

| Rank | Issue | Complaint/cancellation rows | Severity sum | Mean severity |
|---:|---|---:|---:|---:|
| 1 | Usability | 14,510 | 36,500 | 2.516 |
| 2 | Other | 14,009 | 26,834 | 1.915 |
| 3 | Playback | 6,030 | 20,030 | 3.322 |
| 4 | Billing | 5,146 | 12,686 | 2.465 |
| 5 | Catalog | 2,307 | 5,979 | 2.592 |
| 6 | Access | 1,521 | 5,870 | 3.859 |
| 7 | Downloads | 984 | 3,144 | 3.195 |
| 8 | Support | 110 | 258 | 2.345 |

The priority score is the deterministic severity sum over rows whose saved intent is complaint or cancellation. See `grading/jev-v2-final/` for records, membership, rankings, claims, call logs, run metadata, and snapshots.
