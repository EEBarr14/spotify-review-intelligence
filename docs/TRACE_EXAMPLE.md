# Real review audit trace

This example follows one real sampled review from source identity through the final recommendation. Review text is quoted only as evidence and is never treated as an instruction.

1. **Source and sample.** Review `d87536c5-6fe0-4b38-b0b1-c47936e4a0d8` has canonical source-row SHA-256 `b3f456d9b01b391413554189218102907d4ce724b924f562f38e72eb31441fce`. It is row 322 of the frozen 100,000-review file, whose order is the deterministic SHA-256 sampling rank.
2. **Cache decision.** Its exact review-text SHA-256 is `352890d2836f8c31fdcc2eee6a8a112b4b31c00239b6247a4c4fa3e9ad021865`. This text had no earlier cache source, so it received a real Jev classification.
3. **Call evidence.** Request `jev-enrich-3c61a0ee-4bf1-4132-9218-2952702d8df7` used resolved model `jev-1.13.0`, succeeded in 0.180334 seconds, consumed 1,147 input and 233 output tokens, and recorded cost `$0.000048174`.
4. **Validated label.** The saved v2 result is topic `usability`, intent `complaint`, sentiment `-0.94`, and severity `5`. It is conservatively routed to human review because the minimum primary-label confidence was `0.53`, below the fixed `0.55` threshold; unsupported-language probability was `0.04` and ambiguity probability was `0.32`.
5. **Issue membership.** The record contributes one member and five severity points to `issue_usability`.
6. **Aggregate and decision linkage.** Across the complete sample, `issue_usability` contains 14,510 complaint/cancellation records with severity sum 36,500 and mean severity 2.515507. Those deterministic facts place it first in the ranking and support the saved recommendation titled **The Business Question Comes First: Focus on Usability**.
7. **Dashboard evidence policy.** This review remains traceable in `grading/final-submission/records.jsonl`, membership, and call evidence. The public API exposes a separately filtered set of high-severity usability excerpts that excludes review-routed, contact-like, explicitly abusive, and sensitive allegation text; public curation does not alter the ranking or memo calculations.

The classification is a model judgment, not ground truth. Its explicit review flag and preserved probability evidence are part of the audit trail rather than hidden uncertainty.
