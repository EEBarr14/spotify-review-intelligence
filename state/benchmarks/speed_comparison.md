# Production speed comparison

The tests used the frozen Qwen 4B production prompt on the non-golden `cost_100.csv` development set. Each configuration used an isolated SQLite database. Neither test changed production predictions or Golden 50 results.

| Configuration | Seconds / 100 | Unique texts/sec | Projected remaining hours | Topic agreement | Intent agreement | Severity agreement |
|---|---:|---:|---:|---:|---:|---:|
| Production sustained rate, batch 10 / worker 1 | — | 0.679 | 194.48 | Reference | Reference | Reference |
| Batch 20 / worker 1 | 162.567 | 0.615 | 214.81 | 95% | 93% | 92% |
| Batch 10 / workers 2 | 225.978 | 0.443 | 298.60 | 100% | 100% | 99% |

Agreement compares each isolated test with the saved production predictions for the same 100 review texts. The two-worker severity difference affected one record. Sentiment mean absolute differences were 0.2646 for batch 20 and 0.0542 for two workers.

## Decision

Keep batch size 10 and one worker. Batch 20 was slower than the sustained 10,000-review rate and changed more labels because each request contained more review context. Two workers were substantially slower on the shared local hardware. The current production database accounts for 129,578 of 660,622 source rows through 8,492 saved unique predictions and exact-text reuse. Completing the remaining 475,697 unique texts at the measured sustained rate requires about 194.5 hours.
