# Electricity prices and grid queues: independently calculated context

As of **2026-10-16 (Asia/Almaty)**. Calculations: **COMPLETE**; causal attribution and project underwriting: **NEEDS_DATA**.

## Annual electricity comparison

FACT: EIA annual total-electric-industry observations, all end-use sectors, one source vintage. Prices are nominal cents/kWh. CALCULATION: compounded growth uses elapsed years, not the number of observations. The national row is EIA's revenue/sales-weighted aggregate, not an average of the selected states. [Source register](SOURCES.md).

| Geography | 2015 price | 2020 price | 2025 price | 2015–20 CAGR | 2020–25 CAGR | 2015–25 CAGR | Recent CAGR minus US |
|---|---:|---:|---:|---:|---:|---:|---:|
| United States | 10.41 | 10.59 | 13.56 | 0.34% | 5.07% | 2.68% | +0.00 pp |
| Virginia | 9.31 | 9.16 | 11.61 | -0.32% | 4.85% | 2.23% | -0.21 pp |
| Texas | 8.70 | 8.36 | 9.97 | -0.79% | 3.59% | 1.37% | -1.48 pp |
| Ohio | 9.98 | 9.44 | 12.37 | -1.11% | 5.56% | 2.17% | +0.49 pp |
| Georgia | 9.62 | 9.93 | 12.06 | 0.64% | 3.96% | 2.29% | -1.11 pp |
| Oregon | 8.75 | 8.82 | 11.29 | 0.16% | 5.06% | 2.58% | -0.01 pp |
| Washington | 7.40 | 8.33 | 11.12 | 2.40% | 5.95% | 4.16% | +0.88 pp |

CALCULATION / interpretation:

- US prices rose 28.05% cumulatively in 2020–25. Virginia's CAGR was 0.21 percentage points below the US CAGR; Texas was -1.48 points relative to the US.
- Washington's recent price CAGR was 5.95%, against all-sector retail-sales CAGR of 0.77%. Virginia's sales CAGR was 4.71%. These are descriptive comparisons, not a test that data centers caused either result.
- Texas's 2025 annual all-sector price is 0.0997 USD/kWh or 99.70 USD/MWh. Multiplying cents/kWh by 10 converts to USD/MWh; treating cents as dollars creates a 100-fold error.

METHOD: CAGR = (ending price / starting price)^(1 / elapsed years) − 1. Reported EIA prices are rounded to two decimals; underlying revenue/sales ratios are used only as a validation check. All 21 rows reconcile to the reported rounded price within 0.00501 cents/kWh. No monthly or year-to-date observation is mixed with annual data.

INFERENCE: this is a regional screening input, not a data-center procurement curve. A project needs its utility tariff or contract, demand charges, escalation, cost pass-through, and grid-upgrade allocation. The purposively selected jurisdictions are not a control group. Different customer mixes, fuel costs, rate cases, weather, and grid investment can affect observed prices. No inflation adjustment or causal identification is attempted.

## Generation queues: scope before arithmetic

FACT: Lawrence Berkeley National Laboratory and GridTracker's 2026 publication summarizes end-2025 transmission generation/storage requests. The public summary reports 1,312 GW generation, approximately 749 GW storage and roughly 8,200 active projects. [Original publication](https://emp.lbl.gov/publications/queued-2026-edition-characteristics).

| Calculation from published rounded inputs | Result |
|---|---:|
| Generation + storage nameplate capacity | 2,061 GW |
| Storage share | 36.34% |
| 549 GW with draft/executed agreement, not operating, divided by total | 26.64% |

FACT: the reported median from interconnection request to commercial operation exceeds five years for projects completed in 2025 in regions with available data. It is not the average wait of all applicants. Load connections, distribution-connected projects and behind-the-meter projects are excluded.

FACT: for capacity requested in 2000–2020, the summary reports 13% operating, 75% withdrawn and 10% active at end-2025. Those rounded categories sum to 98%; the remaining two percentage points are left unallocated. The 13% figure is a historical capacity-weighted outcome, not a project's probability of success.

LIMITATION: these queue inputs are transcribed public summary statistics; the underlying XLSX could not be downloaded in this run (HTTP 403). The national project-level aggregation and median were not independently recomputed. Only arithmetic on the extracted aggregates is reproduced. See the download link and access record in SOURCES.md.

INFERENCE: requested nameplate GW is neither dependable power nor deliverable capacity for a specific data center. Do not put the published generation-queue duration into a data-center commissioning schedule. Use the named site's load study, service agreement, required upgrades, permits, and achievable energization date. Storage GW also says nothing about energy duration without GWh.

## Reproduction and validation

```bash
python examples/ai-infrastructure/public-data/analysis.py
python examples/ai-infrastructure/public-data/analysis.py --check
```

Both commands use Python's standard library and frozen inputs; no network or API key is needed. The first regenerates this page and results.json; --check verifies their exact contents. refresh_eia.py separately re-extracts or verifies the EIA workbook without silently changing the frozen input.

Frozen inputs SHA-256: `bf20ab6415aa57d5f7999a693a1fb1608ba72b22ef2f9f95b55f8ff5014bcaf2`.

Confidence: **0.96** for EIA extraction and arithmetic; **0.88** for the scoped LBNL summary transcription. These confidence judgments do not quantify a project investment outcome. No human review is attested.
