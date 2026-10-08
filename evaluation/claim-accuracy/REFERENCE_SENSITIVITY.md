# Reference-label uncertainty and locator errata

The third fresh assistant completed its review blind to the frozen author key and both prediction responses. It agreed on every decision, numeric value, unit, entity and scope, but used `FY2024` where the author used `CY2024` on eight annual records: **SH01, SH02, SH03, UL01, UL02, IB01, IB02 and IB03**.

The candidate vocabulary supplied both tokens without a required per-issuer mapping. For these calendar-aligned financial/reporting years, the two tokens can describe the same underlying year. The experiment therefore exposes a canonical-period annotation ambiguity. Neither reference is independently human adjudicated. The reviewer was not asked to copy the author tokens, and neither reference was revised to match predictions.

The original [scoring contract](SCORING.md), candidate corpus, prompts, author key and prediction bytes remain frozen. The supplemental policy applies **the same original exact-string scoring** three ways: all 32 items against the original author labels, all 32 against the independently frozen blind labels, and the 24 items on which both reference records agree. All reference versions and disagreements are reported. There is no merged consensus key, permissive period normalization, selective deletion from the full-set results or claim of human-validated accuracy.

The [comparison results](comparison-results.json) expose `metrics_by_reference.author`, `metrics_by_reference.blind_reviewer` and `metrics_by_reference.common_agreement` for each run. The common subset contains 24 items, including 16 answerable quantity requests and eight unanswerable requests. It is a descriptive sensitivity view, not a substitute held-out sample selected independently of label disagreement. Full 32-item decision/record metrics remain visible under both references.

This supplement was specified after the blind labels and predictions froze and before the coordinator inspected/scored the prediction contents. It corrects the implementation's former single-key disagreement block by reporting unresolved reference uncertainty explicitly; it does not change the mathematical scoring rules or claim that uncertainty was adjudicated. A future clean evaluation should specify the calendar/fiscal token mapping before new questions and runs freeze.

## Printed-page errata

Primary PDF checks confirmed the source values and all PDF page indices, but found three Unilever printed-page labels off by one. [blind-gold-review-metadata.json](blind-gold-review-metadata.json) records the review. The frozen corpus is preserved to keep the original trial inspectable.

| Fragment | Correct PDF page | Frozen printed-page label | Verified printed-page label |
|---|---:|---:|---:|
| `UL-profit` | 47 | 45 | **44** |
| `UL-emissions` | 246 | 244 | **243** |
| `UL-sales` | 45 | 43 | **42** |

These locator corrections do not change any supplied fragment, numeric fact or prediction. They are disclosed separately in [locator-errata.json](locator-errata.json). Full documents remain excluded from the repository.
