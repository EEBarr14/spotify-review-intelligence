# Pilot Manual Spot Check

This is a development review of selected `cost_100.csv` predictions. It is separate from the protected golden 50 and may be used to improve the pipeline.

## Confirmed mechanical behavior

- All 100 source IDs produced one completed record.
- Every evidence quote is the exact complete source review text.
- The first full indexed run had no malformed structured outputs or retries.
- The warm replay made zero model calls.

## Inspected likely failures

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

Do not run this prompt on the full corpus unchanged. Before the 500-review checkpoint:

1. Strengthen the premium-only-control and cancellation precedence examples using development records only.
2. Use compact numeric output codes to reduce generation time while mapping them back to the required labels in Python.
3. Inspect a declared development sample and report the resulting changes.
4. Keep the golden 50 labels out of prompts and tuning.

