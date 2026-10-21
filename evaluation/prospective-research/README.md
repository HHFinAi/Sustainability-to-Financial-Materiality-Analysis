# Prospective operating-hypothesis evaluation

**Frozen 21 October 2026 (Asia/Almaty) · Three hypotheses · Zero observed outcomes.**

This adds prospective evaluation to the existing [source-extraction comparison](../claim-accuracy/README.md). It tests narrow research judgments from the [water/waste monitor](../../examples/water-waste/README.md), not extraction accuracy, equity returns, causal climate effects or investment alpha. Probabilities are explicitly subjective, uncalibrated assistant judgments; they are not model-estimated confidence intervals or historical hit rates.

| ID | Event in first Q3 2026 earnings release | Probability | Reason and contrary case |
|---|---|---:|---|
| XYL-2026Q3 | Xylem group organic revenue growth > 1.0% year on year | 65% | Strong Q2 orders support direction; WSS concentration and conversion timing limit conviction. The threshold is the disclosed rounded Q2 growth rate. |
| VLTO-2026Q3 | Veralto group core sales growth ≥ 4.5% year on year | 55% | Threshold is the midpoint of management's 4–5% guidance. Modest positive judgment given Water Quality momentum; mix and execution can disappoint. This is largely a guidance-based benchmark, not a claimed information advantage. |
| WM-2026Q3 | WM collection/disposal volume growth > −1.8% year on year | 60% | Q2's unusual comparator suggests possible improvement; underlying activity could weaken. Use the unadjusted total volume metric, not the ex-wildfire series. |

The comparison is a fixed 50% probability for each event. This is a transparent naive benchmark, not market consensus. All three observations are correlated and selected from one research theme; even perfect results would not establish calibration, generalization or skill.

## Freeze and observation protocol

`predictions.json` fixes probabilities, thresholds, units, exact metric scope, rationale, source inputs and expected release dates. `freeze.json` hashes the prediction and source-register bytes. Public commit history records publication; a local hash alone is not authenticated or tamper-proof preregistration. Do not change these predictions after publication. Corrections belong in a new, dated record with the old version retained and an explicit reason.

Issuer notices available before the freeze announce Xylem results on [27 October](https://www.xylem.com/en-in/about-xylem/newsroom/press-releases/xylem-to-release-third-quarter-2026-financial-results-on-october-27-2026/), WM on [27 October](https://investors.wm.com/news-releases/news-release-details/wm-sets-date-third-quarter-2026-earnings-conference-call), and Veralto on [29 October](https://investors.veralto.com/2026-10-12-Veralto-Schedules-Third-Quarter-2026-Earnings-Call) (call 30 October). Dates may change. These notices establish that the selected releases were still ahead of this cutoff; they are not observed outcomes.

After publication, add a record to `observations.json` containing `id`, `period` (`2026Q3`), `metric`, `unit`, numeric `value`, `published_on`, `retrieved_on`, `source_url`, `locator`, and `reviewer`. Use the issuer's first release and its published precision. Do not replace an outcome with a later restatement; preserve corrections separately. A tie fails the strict `>` events and succeeds the `>=` event. Unavailable, renamed or incompatible metrics remain unscored with an explicit note; never substitute zero or another segment. Human review is recommended before interpreting results but is not falsely recorded here.

`score.py` rejects duplicate/unknown observations, mismatched scope/units, non-finite values, pre-freeze or future-dated observations, and non-issuer URLs. It checks metadata, not whether the cited passage is true or the document is actually the first release. Those require review. An earlier-than-scheduled release after the freeze is valid if independently verified.

## Scoring and follow-up

Per-event Brier score = (probability − observed 0/1 outcome)²; lower is better. Report coverage and each event, plus mean score and the naive benchmark on the **same scored subset**. Missing observations do not enter the denominator. No score is reported while all are pending. The review date **30 November 2026** is a manual checkpoint, not a scheduled automation; absence after that date requires an unresolved-data explanation.

From the repository root:

```bash
python evaluation/prospective-research/score.py --check
python evaluation/prospective-research/score.py --as-of 2026-11-30
```

The first command checks frozen bytes and reproduces the archived empty [cutoff status](STATUS.json) without rewriting it; it does not score or validate later observations. The second validates and calculates a dated view from actually populated observations; it does not fetch releases or invent missing results. Preserve the original status. Source/extraction evaluation, this forecast ledger and investment performance remain distinct records.
