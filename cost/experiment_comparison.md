# Pilot Experiment Comparison

All experiments used the supplied `cost_100.csv`, local Ollama inference, thinking disabled, temperature 0, a fixed seed, validated structured output, and $0 API spend. Agreement is a 10-review same-model independent consistency check, not human-labeled accuracy.

| Experiment | Model and format | Batch / workers | Cold seconds | Full base hours | Topic | Intent | Severity |
|---|---|---:|---:|---:|---:|---:|---:|
| V2 baseline | Qwen 4B, indexed verbose JSON | 10 / 1 | 357.090 | 388.99 | 90% | 100% | 100% |
| V3 numeric | Qwen 4B, numeric label codes | 10 / 1 | 166.715 | 155.34 | 70% | 80% | 90% |
| V4 hybrid | Qwen 4B, short keys/readable labels | 10 / 1 | 181.387 | 177.29 | 90% | 90% | 70% |
| V5 isolated/small batch | Qwen 4B, stronger isolation instruction | 5 / 2 | 237.632 | 229.21 | 100% | 100% | 70% |
| V5 smaller model | Qwen 2B | 5 / 1 | 209.155 | 248.47 | 80% | 80% | 80% |
| V5 isolated/fast batch | Qwen 4B | 10 / 1 | 195.141 | 198.91 | 90% | 80% | 70% |

The base projections use measured enrichment throughput for 484,189 distinct nonempty texts and exact-text result reuse. They are not guarantees. A conservative 25% overhead makes the V3 numeric projection 194.17 hours and the V4 hybrid projection 221.61 hours.

## Important observed errors

- V3 corrected the premium-only-control topic to `billing`, but did not correct the mixed-language uninstall/cancellation record.
- V4 and V5 ten-review batches sometimes transferred the following review's downloads complaint to the one-word review `Good`, despite correct integer IDs and an explicit isolation instruction.
- Five-review V5 batches correctly classified `Good` as `other` / `praise` / severity 1 and produced 100% topic/intent consistency, but remained inconsistent on severity and were too slow for the deadline.
- Qwen 2B was slower in the projected enrichment stage, less consistent, and badly mislabeled the mixed-language uninstall record. It is rejected.
- The `qwen3.5:4b-mlx` tag downloaded successfully but Ollama returned HTTP 501 for chat requests in this setup. It is unsupported and was not used for a measured pilot.

## October 13 deadline assessment

The quality-first local configurations do not fit before October 13 on this Mac. V3 numeric can fit only in the base case if the scalable runner is completed and the full cached checkpoint-to-corpus run starts by October 6. Its conservative estimate consumes essentially the entire remaining calendar and its observed consistency is below the desired gate.

Do not claim that the deadline is safe under a local-only plan. The defensible choices are:

1. Accept the V3 numeric quality and schedule risk, complete the scalable runner immediately, and run continuously while plugged in and awake.
2. Use a faster paid API with a hard spending cap after a measured 100-review pilot.
3. Obtain more compute or a second machine and measure a genuine comparable worker run before relying on it.

## Decision at the time (subsequently superseded)

The initial route was the no-cost numeric configuration, followed by narrow deterministic contract rules. The 500-review checkpoint measured approximately 0.787 distinct texts per second across an interrupted and resumed run, projecting about 171 hours for all 484,189 full-corpus distinct texts before sustained-load overhead. After the assignment was revised to permit a representative 100,000-review scope and the instructor recommended Jev, this local-only decision was superseded. The final production run used Jev v2; the local experiments remain evidence for the measured speed/quality tradeoff and provider decision.
