# Architecture and audit trail

```text
660,622-row source CSV
        |
        +--> deterministic full-file profile --> 13 empty-text quarantine records
        |
        +--> fixed SHA-256 sample across all eligible IDs --> 100,000 review IDs
                                                           |
                                                           v
                                      exact-text/config cache lookup
                                             |           |
                                             | hit       | miss
                                             v           v
                                      copy saved label   Jev typed questions
                                             |           |
                                             +-----+-----+
                                                   v
                                     validation + atomic SQLite save
                                                   |
                   +-------------------------------+------------------+
                   |                               |                  |
                   v                               v                  v
         independent local verifier       deterministic grouping   Golden 50
                                           and priority ranking     evaluation
                   |                               |                  |
                   +-------------------------------+------------------+
                                                   v
                                       bounded local memo model
                                                   |
                          +------------------------+----------------------+
                          |                                               |
                          v                                               v
               machine-checkable grading export                chunked D1 import
                                                                  |
                                                                  v
                                                        deployed API + dashboard
```

Python owns source identity, sampling, cache identity, validation, spend admission, storage, counts, ranking arithmetic, exports, and checker inputs. Jev receives only review text and fixed typed questions. Star ratings and other metadata remain available for analysis but are not classification inputs. The local model is restricted to bounded verification, issue naming, and memo writing from saved artifacts.

Every Jev classification is keyed by the exact review-text hash plus the resolved model, release date, question version, sentiment mapping, and confidence threshold. Duplicate review IDs never disappear: a reused record points directly to the original classified source ID with identical text and labels.

The dashboard never invokes a model. It reads saved aggregates, recommendation claims, evaluation metrics, and review evidence through server API routes backed by D1.

## Trace template

One completed real-review trace is preserved in `docs/TRACE_EXAMPLE.md`:

1. Original review ID and source-row SHA-256.
2. Deterministic sample rank and inclusion.
3. Exact-text cache decision.
4. Jev request ID, resolved model, phase, token usage, and recorded cost.
5. Validated topic, intent, sentiment, severity, confidence, and review-routing flags.
6. Issue membership and reproducible priority contribution.
7. Claim/evidence linkage used by the recommendation and dashboard.

No placeholder values are presented as measured evidence. The trace comes from the saved SQLite event and final grading export.
