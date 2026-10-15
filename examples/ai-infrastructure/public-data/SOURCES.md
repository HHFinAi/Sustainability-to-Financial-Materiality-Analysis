# Primary-source register and extraction record

Research cutoff and retrieval date: **16 October 2026, Asia/Almaty**. AI-assisted source review and extraction; **no human review is attested**. The input file contains only the small factual extract required for this comparison. No third-party broker report, chart or table is reproduced or cited.

## EIA-861-HIST-2026 — annual electricity sales, revenue and price

- Publisher: U.S. Energy Information Administration.
- Official index: <https://www.eia.gov/electricity/data/state/>.
- Download: <https://www.eia.gov/electricity/data/state/xls/861/HS861%202010-.xlsx>.
- Publication: **7 October 2026**, final 2025 annual electric sales and revenue release; official release link and final-data designation: <https://www.eia.gov/electricity/data/eia861/>. The annual historical workbook contains 2010–2025.
- Observation periods used: full calendar years **2015, 2020, 2025**; US, VA, TX, OH, GA, OR, WA. These are selected jurisdictions, not a complete state panel or causal control group.
- Read locator: worksheet **Total Electric Industry**; column A year, B state, S total revenue in thousand dollars, T total sales in MWh, V total price in cents/kWh. Each observation in `inputs.json` has its exact Excel row locator.
- Source file downloaded successfully: **487,659 bytes**. SHA-256: `e4c74d03f4a6b8c68045e3d2d3392b81bb5230f5d9989edd3c7046611092af16`.
- Processing: selected 21 unique state/year observations from the same current workbook vintage. No interpolation, imputation, sector averaging or monthly/annual splicing. The reported total-price cell is the CAGR input; total revenue / total sales independently checks the rounded price.
- Reuse: EIA federal-government data; [official copyright and reuse policy](https://www.eia.gov/about/copyrights_reuse.php). Attribution retained. The full workbook is not included in this repository.
- Scope limitation: prices cover all customer sectors and all electric-industry provider types, not data-center contracts, marginal power costs or wholesale prices. State aggregation can change as customer mix changes. Nominal prices are not inflation-adjusted. Differences across two selected periods do not establish causation.

**Vintage trap documented:** the older `avgprice_annual.xlsx` URL downloaded in this session stops at 2020. It is not used for final calculations. The state-profile landing page still displays 2024 with its next profile release scheduled for November 2026, while the underlying final 2025 sales/revenue dataset was already released. Use the actual observation range and release record, not the apparent currency of a URL or overview page.

### Re-extract from the workbook

```bash
# Existing download: verify bytes and selected observations without modifying inputs.
python examples/ai-infrastructure/public-data/refresh_eia.py --workbook /tmp/eia-hs861.xlsx

# Download to a new file; refuses overwrite. A revised source is reported explicitly.
python examples/ai-infrastructure/public-data/refresh_eia.py --download-to /tmp/eia-hs861-new.xlsx --extract-to /tmp/eia-extract-new.json

# Reproduce the published calculations offline.
python examples/ai-infrastructure/public-data/analysis.py --check
```

The refresh helper uses only the Python standard library to read the source XLSX XML. A changed source hash or any changed selected cell raises a review notice. It does not silently rewrite the frozen input. Validate revisions against the original workbook, update source metadata/locators deliberately, then regenerate the calculation output.

## LBNL-QUEUED-2026 — transmission generation/storage queues

- Authors/publishers: Joseph Rand and coauthors; Lawrence Berkeley National Laboratory and GridTracker.
- Publication page: <https://emp.lbl.gov/publications/queued-2026-edition-characteristics>.
- Series page: <https://emp.lbl.gov/queues>.
- Observation cutoff: **31 December 2025**. Series page states data file last updated **May 2026**, slide deck published **June 2026**. The publication landing page labels publication month May 2026; these refer to different release objects and are preserved separately.
- Original data workbook: <https://eta-publications.lbl.gov/sites/default/files/2026-05/lbnl_ix_queue_data_file_thru2025.xlsx>.
- Original slide deck: <https://eta-publications.lbl.gov/sites/default/files/2026-06/queued_up_2026_edition.pdf>.
- Locator: publication-page abstract (included/excluded connections) and key highlights, bullets 1 (active totals), 4 (agreements), 5 (duration), 6 (cohort outcomes). Date distinctions are from the series-page introductory paragraphs.
- Extracted facts: 1,312 GW generation; approximately 749 GW storage; roughly 8,200 active projects; 549 GW with draft/executed agreements but not operating; completed-2025 median request-to-operation duration **greater than five years**, in regions with available data; 2000–2020 requested-capacity cohort outcomes 13% operating, 75% withdrawn, 10% active as of end-2025.
- Processing: manual numeric transcription from the retrieved **official web summary**, followed by independent addition, ratios and category-total checks. `analysis.py` does **not** independently reaggregate project records or recompute the median. The displayed 2,061 GW is a sum of rounded components, not newly recovered exact capacity.
- Access limitation: source XLSX download returned **HTTP 403**. Its original-file SHA-256 is consequently **unavailable** (`null`), not replaced with a hash of another object. The source page was accessible. No unsupported precision is added to the duration or approximate project count.
- Data-file license: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Attribution: Lawrence Berkeley National Laboratory and GridTracker; underlying data copyright 2026, The Regents of the University of California through Lawrence Berkeley National Laboratory and GridTracker. This small extract and derived arithmetic are adaptations; no endorsement is implied. No full source file or figure is redistributed.
- Scope limitation: transmission generation/storage queue, explicitly excluding load requests, distribution connections and behind-the-meter projects. Completed-project duration has selection bias relative to pending/withdrawn requests. Requested nameplate capacity cannot be equated to firm deliverable supply. Storage power in GW omits duration in GWh. A draft/executed agreement does not itself establish financial close, construction completion or energization.

## Open research dependencies

| Status | Dependency | Consequence |
|---|---|---|
| OPEN MATERIAL | LBNL project-level workbook retrieval and precise cohort/sample reconciliation | National reaggregation, exact median and remaining outcome categories remain unverified here |
| OPEN MATERIAL | Site utility tariff/contract, load-study status, upgrade allocation and service date | Regional prices and generator queues cannot underwrite a named data-center project |
| OPEN MATERIAL | Credible identification of data-center demand effects versus fuel, weather, mix and rate-base changes | No causal attribution of state electricity-price growth |

These open items limit the scope of conclusions; they do not prevent reproduction of the clearly labelled arithmetic on observed inputs.
