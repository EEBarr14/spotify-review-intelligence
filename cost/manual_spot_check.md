# Pilot Manual Spot Check

This is a development review of selected `cost_100.csv` predictions. It is separate from the protected golden 50 and may be used to improve the pipeline.

## Confirmed mechanical behavior

- All 100 source IDs produced one completed record.
- Every evidence quote is the exact complete source review text.
- Both v2 and v3 cold runs had no malformed structured outputs or retries.
- The warm replay made zero model calls.

## V2 inspected likely failures

### Premium only controls

- Review ID: `ad730d1a-829a-4dc4-9561-7e1cd07e2c30`
- Review: `Why it requires premium just to play next music / to choose music ?? And why the specific part of song cannot be played ?`
- Model topic: `playback`
- Likely contract topic: `billing`
- Reason: the common-label contract explicitly assigns premium-only controls to billing.

### Multilingual uninstall statement

- Review ID: `45c561b9-cc47-4d80-95d3-f0d20bc84af3`
- Review: `The update made the app useless .... Uninstall krdia ye app ab bekar hai ... Wynk hi theek h`
- Model output: topic `playback`, intent `complaint`, severity `4`, needs_review `false`
- Likely issue: the text explicitly says the app was uninstalled, so cancellation has precedence. It does not clearly identify playback as the broken function. The unsupported-language/mixed-language content should also be considered for `needs_review`.

## Decision before scaling

Do not run either tested prompt on the full corpus unchanged. The v3 compact numeric format reduced the 100-review cold runtime from 357.090 to 166.715 seconds, a 2.14x speedup, but verifier agreement worsened:

| Measure | V2 indexed JSON | V3 numeric codes |
|---|---:|---:|
| Topic agreement | 90% | 70% |
| Intent agreement | 100% | 80% |
| Exact severity agreement | 100% | 90% |
| Severity MAE | 0.00 | 0.10 |

The v3 result for the premium-only-control record changed to `billing` / `complaint`, correcting the main topic error, although severity `4` still appears high. The multilingual uninstall record remained `playback` / `complaint` / severity `4` / `needs_review=false`, so the cancellation-precedence and uncertainty problem remains.

Before the 500-review checkpoint:

1. Test a hybrid compact schema: short keys, integer sentiment, and readable topic/intent strings.
2. Keep the strengthened premium-control, cancellation-precedence, and mixed-language rules.
3. Repeat the same 100-review cold/warm comparison and manual spot check.
4. Require zero schema/ID failures and at least 90% verifier agreement on topic, intent, and exact severity before moving to 500 reviews.
5. Keep the golden 50 labels out of prompts and tuning.
