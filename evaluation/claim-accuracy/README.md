# Issuer claim accuracy: observed assistant comparison

This is a small, reproducible evidence task using **32 newly selected questions from eight primary issuer documents**. It compares a fresh assistant session given a short direct prompt with another fresh session given explicit financial and environmental scope checks. The archived responses are actual session outputs. The deterministic scorer only measures those responses against separately frozen assistant labels; it does not generate model predictions.

Read [the observed comparison](comparison-results.json), [the frozen scoring contract](SCORING.md), [reference-label sensitivity and locator errata](REFERENCE_SENSITIVITY.md), and [the blind gold-review record](gold-review.json) together. The result is a narrow assistant-session comparison, not a validation of automated document ingestion, the Python workflow engine, a production model or investment performance. A stronger prompt is not assumed to outperform the baseline: both outcomes and every mismatch are published.

## Observed results

| Metric | Baseline session | Structured session |
|---|---:|---:|
| Claim decisions matching either reference | 32 / 32 | 32 / 32 |
| Complete items matching the author reference | 24 / 32 | 24 / 32 |
| Complete items matching the blind reviewer reference | 32 / 32 | 32 / 32 |
| Complete items on the shared-label subset | 24 / 24 | 24 / 24 |
| Unsupported accepted claims | 0 | 0 |
| Unsupported numeric records on absent requests | 0 | 0 |
| Abstentions | 0 | 0 |

The runs show **no observed improvement from the structured prompt on this set**. The eight author-reference mismatches are exclusively `FY2024` versus `CY2024` annotations; decisions, values, units, entities and scopes agree. Both frozen assistant label sets remain published without human adjudication or post hoc normalization. The shared-label subset excludes these eight items and is disclosed alongside both full-set results. Controlled fragments and planted errors make this task easier than end-to-end research; the counts do not establish general model accuracy.

## Evidence and task

| Issuer | Primary historical document | Items | Typical boundary |
|---|---|---:|---|
| Apple | [2025 Environmental Progress Report](https://www.apple.com/environment/pdf/Apple_Environmental_Progress_Report_2025.pdf) | 4 | Gross versus net footprint; fiscal periods |
| Amazon | [2024 Sustainability Report](https://sustainability.aboutamazon.com/content/dam/sustainability-marketing-site/pdfs/reports-docs/2024-amazon-sustainability-report.pdf) | 4 | Comparative year; market-based Scope 2 |
| Shell | [2024 Strategic Report](https://www.shell.com/who-we-are/our-values/_jcr_content/root/main/section_874829968/list/list_item_copy.multi.stream/1752576274096/eb6d18269c7e9e79b6539e1b0780747d5e2c8b31/strategic-report-ar-two-four.pdf) | 4 | Group versus segment; cash flow versus investment |
| Unilever | [2024 Annual Report and Accounts](https://www.unilever.com/files/unilever-annual-report-and-accounts-2024.pdf) | 4 | Statutory versus underlying profit; target emissions coverage |
| Maersk | [2024 Annual Report](https://www.maersk.com/~/media_sc9/maersk/corporate/sustainability/files/resources/2024/maersk-annual-report-2024.pdf) | 4 | Market versus location-based totals; thousands of tonnes |
| Schneider Electric | [Q4 2024 sustainability dashboard](https://www.se.com/ww/en/assets/564/document/505452/schneider-sustainability-impact-q4-2024-results.pdf?download=true) | 4 | Observed score versus target; cumulative customer outcomes |
| Iberdrola | [2024 results highlights](https://www.iberdrola.com/documents/20125/4994767/250227-pr-record-investment-17-billion-boosts-iberdrolas-net-profit-5612-billion-up-17.pdf) | 4 | Organic versus total investment; geographic intensity |
| Volkswagen | [2024 Annual Report](https://uploads.vw-mms.de/system/production/documents/cws/002/940/file_en/dfed3f8c2cd2a5f5616e3371f8674356349e032e/Y_2024_e.pdf?1741784299=) | 4 | Group versus additional operational control; published rounding |

Every candidate item identifies a primary document, a PDF/printed-page locator and a supplied fragment. The [locator errata](REFERENCE_SENSITIVITY.md#printed-page-errata) correct three Unilever printed-page labels while preserving the frozen corpus; their PDF page indices and supplied values were verified. Fragments are selected factual table/chart cells, faithfully transcribed numeric disclosures and short original prose excerpts. Table layout is converted into JSON rows; units and labels are made machine-readable, and author context is identified separately. The original prose quotation budget stays below 25 words per source document. Full reports are not redistributed.

[sources.json](sources.json) records the actual downloaded issuer-PDF byte hashes, retrieval timestamps and resolved URLs. Those hashes identify the reviewed source versions; a later publisher download may differ. Offline checks verify the committed source manifest and fragment/corpus integrity, rather than claiming to redownload or authenticate every original PDF.

For each proposed claim, a run must classify evidence as `supported`, `contradicted`, `insufficient`, or `abstain`. It must separately extract the requested reported quantity with the correct unit, entity, period and scope, or return `record:null` when absent. A contradicted candidate can still have an extractable corrected fact. The fixed annotation vocabulary makes automated scoring explicit. It does not test arbitrary prose equivalence.

## Separation and reproducibility

The [candidate corpus](candidate-corpus.json), two prompts and scoring contract were frozen before prediction access. [freeze.json](freeze.json) records raw/canonical corpus hashes, source-manifest hash, prompt/contract hashes and the separately frozen author-key hash. The baseline and structured runs use fresh sessions with candidate-only file access, no retrieval or scorer access. Both receive the same fragments, schema and annotation vocabulary.

The original [author key](answer-key.json) retains its creation-time review status and byte identity. A third fresh assistant independently labels the same candidate set, blind to author labels and both prediction runs, with the source PDFs available for checking. Completed review is recorded separately in [gold-review.json](gold-review.json). Eight records differ only on `FY2024` versus `CY2024`; the candidate vocabulary did not specify an issuer mapping. [Reference sensitivity](REFERENCE_SENSITIVITY.md) preserves both frozen label sets and reports identical exact-field scoring against each, plus their 24-item common-agreement subset. No consensus labels or human adjudication are inferred. **These are two assistant label sets, not independent human expert adjudication.**

Access declarations and context isolation are host/coordinator attestations, not audited security proofs. The exact model revision was unavailable. One run per prompt cannot establish an incremental workflow benefit or distinguish prompt effects from sampling/session effects. Runs, reasons and metadata remain available for scrutiny in [runs/](runs/). The scorer does not rewrite their decisions or records.

```bash
# Reproduce all hashes, reference disagreements and observed metrics without writes.
python evaluation/claim-accuracy/score.py --check

# Print the reproduced report, or explicitly write a requested copy.
python evaluation/claim-accuracy/score.py
python evaluation/claim-accuracy/score.py --output /tmp/hhfinai-claim-results.json

# Exercise scoring failures and archive-integrity checks with synthetic fixtures.
python -m unittest discover -s tests -p test_claim_accuracy.py -v
```

Reproduction verifies archived scoring; it does not rerun a model. To repeat the experiment, use a new fresh candidate-only session for each archived prompt and record raw response/prompt/corpus hashes, actual timing if measured, available model identity and access attestations. Public questions are now development material and should be replaced for a future held-out evaluation.

## Interpretation limits

The set deliberately plants value, period, scope and unsupported financial-attribution errors. Several items share fragments and all four questions per issuer share a source, so 32 items are not 32 independent observations. Some claims are intentionally easy to reject; source context, clean transcription and controlled labels remove much of real document-extraction difficulty. The model may already have seen public issuer documents during training. “Held out” means newly selected after the existing prompts and engineered metadata tests were developed, not guaranteed absent from pretraining or authoring context.

Report decision accuracy, full-record accuracy, each extraction field, unsupported acceptance/fabrication, abstention and source groups under both reference label sets together. Reference-period ambiguity affects exact extraction scores; it is not silently normalized. Reasons are archived but their free-text factual entailment is not automatically graded. A null selective accuracy or acceptance denominator is not a perfect score. No independent human accuracy, production cost/latency, human review-time saving, empirical avoided loss, investment alpha or regulatory compliance is measured.

The earlier [48-case engineered metadata exercise](../../examples/microsoft-ai/EVALUATION.md) remains a separate deterministic contract test. It should not be combined with these observed assistant results to inflate a single accuracy figure.
