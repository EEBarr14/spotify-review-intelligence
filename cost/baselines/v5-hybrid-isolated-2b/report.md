# 100 Review Local Pilot Cost and Runtime Report

## Decision

Continue with `qwen3.5:2b` only if manual inspection and the later development evaluation show acceptable labels. This pilot measures runtime, structured-output reliability, caching, and local resource use; it is not the final accuracy evaluation.

## Configuration

| Field | Value |
|---|---|
| Provider | Ollama local |
| Exact model | `qwen3.5:2b@0689d44085e0` |
| Thinking | disabled |
| Prompt/schema | `ollama:qwen3.5:2b@0689d44085e0+enrich-v5-hybrid-isolated+common-labels-v1+think-false` |
| Batch size | 5 reviews |
| Workers | 1 |
| Verification sample | 10 reviews |
| Input checksum | `c884ac3b9be5066995d5063f96ad9af6e5e082975788c1684c4f6b6ea661dd0e` |

## Measured Results

| Measure | Cold run | Warm run |
|---|---:|---:|
| Input rows | 100 | 100 |
| Completed | 100 | 100 |
| Unique texts | 100 | 100 |
| New enrichment calls | 20 | 0 |
| Enrichment cache hits | 0 | 100 |
| All attempted model calls | 23 | 0 |
| Input tokens | 20736 | 0 |
| Output tokens | 6442 | 0 |
| End-to-end seconds | 209.155 | 0.017 |
| API spend | $0.000000 | $0.000000 |
| Local compute/electricity | Unknown | Unknown |

Cold throughput was 0.478 input rows per second. Warm replay used saved results and made zero enrichment calls under the unchanged configuration.

## Initial Full Run Projection

These projections linearly extrapolate the measured enrichment time and add measured pilot downstream overhead once. They must be refreshed after 500 and 10,000 reviews.

| Scenario | Distinct classifications | Estimated hours | API spend |
|---|---:|---:|---:|
| Exact-text reuse, base | 484,189 | 248.47 | $0.00 |
| Exact-text reuse, conservative 25% overhead | 484,189 | 310.59 | $0.00 |
| No reuse comparison | 660,609 | 339.01 | $0.00 |

The final run must still emit all 660,622 IDs: 660,609 completed nonempty records and 13 `empty_review_text` quarantines. Exact-text caching reduces model work, not business counts.

## Controls

- API spending limit: $0.00; any configured remote-provider call is rejected by design.
- Output cap: 2,048 tokens per request.
- Maximum workers: 1 for this pilot.
- Maximum fallback fraction: 0%; no paid fallback configured.
- Invalid structured output: one bounded retry, then fail visibly.
- Persistence: validated enrichment batches are atomically cached before the next batch.

## Offline Replay

```bash
python3 run_pipeline.py replay --cost-dir cost
```

This command reads saved measurements only and performs no model or network calls.
