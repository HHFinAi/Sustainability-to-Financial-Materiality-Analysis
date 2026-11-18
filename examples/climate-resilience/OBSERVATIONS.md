# Primary-source operating indicators — Q3 2026

**Prepared 18 November 2026.** Three different earnings disclosures are monitored as original calculations, NOT an apples-to-apples valuation ranking and NOT proof of a climate adaptation revenue tailwind.

| Cohort | Actual Q3 2026 evidence | Independently calculated indicator | Fundamental evidence still missing |
| --- | --- | --- | --- |
| HVAC: TT | [Trane press release, 29 October 2026](https://investors.tranetechnologies.com/news-and-events/news-releases/news-release-details/2026/Trane-Technologies-Reports-Strong-Third-Quarter-Results-Raises-Full-Year-Revenue-Guidance-Reaffirms-Full-Year-EPS-Guidance/default.aspx): $7,248m bookings and $6,760m consolidated continuing-operations revenue | Reported book-to-bill **1.072x** | Region-specific funded cooling replacement orders, margin to FCF bridge and price expectations |
| Grid: GEV | [GE Vernova SEC exhibit, 28 October 2026](https://www.sec.gov/Archives/edgar/data/1996810/000199681026000162/gevpressrelease3q26.htm): Electrification segment orders $5,371m, revenue $3,862m and segment EBITDA $739m | Book-to-bill **1.391x**; segment EBITDA / sales **19.1%** | Company discloses organic orders **−9%** versus reported positive order growth; M&A, AI/general electrification and weather hardening must be reconciled |
| Flood materials: HEI.DE | [Heidelberg Materials Q3 press release, 4 November 2026](https://www.heidelbergmaterials.com/en/pr-2026-11-04): revenue €6,413m versus €5,807m; RCO €1,281m | Revenue **+10.4%** YoY; RCO / revenue **20.0%** | Named flood-defense tenders, geography, company capture, delivered contribution margins and market price |

**No comparable cross-company margin ranking:** TT's GAAP operating income, GEV segment EBITDA and HEI.DE RCO differ by accounting definition and business scope. GEV acquisition effects also make reported and organic growth distinct; do not sum organic and reported orders. The source data above do **not** validate any of the hypothetical assumptions in `inputs.json`.

```bash
python examples/climate-resilience/monitor.py
python -m unittest discover -s tests -p test_climate_issuer_monitor.py -v
```

The next real investment step is to verify buyer budgets, awarded contracts, issuer geographic share and cash conversion, then value incremental economics at timestamped current security prices. **Issuer adaptation attribution and stock return ranking: NEEDS_DATA.**
