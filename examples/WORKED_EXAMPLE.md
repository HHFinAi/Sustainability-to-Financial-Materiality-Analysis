# Heidelberg Materials: what Brevik CCS must earn to matter

**Research question:** Does an operating carbon-capture project justify a material uplift to Heidelberg Materials' equity valuation?

**Assessment: WATCH — evidence supports a real transition investment, but the cash economics remain conditional.** The central sensitivity produces **€56.08m of discounted incremental cash flow over 2026–2030**, with a **−€47.55m to +€193.60m** downside/upside range. These are reproducible scenarios, not a company forecast, full project valuation or share-price target. No probability weights are assigned.

**Information cutoff and valuation date: 25 February 2026. Prepared: 3 October 2026.** This is retrospective research using dated documents, not a contemporaneous investment recommendation. No post-cutoff operating results are used. Human research approval is **not recorded**. This standalone analyst case is separate from the workflow engine's generated demonstration packets.

[Inputs and classifications](heidelberg-brevik/inputs.json) · [Source register](heidelberg-brevik/sources.csv) · [Full calculated tables](heidelberg-brevik/RESULTS.md) · [Calculation code](heidelberg-brevik/model.py) · [Original synthetic example](SYNTHETIC_CASHFLOW_EXAMPLE.md)

## Investment judgment

**INFERENCE:** Brevik provides a useful test of whether decarbonisation creates incremental cash earnings. It does not, by itself, substantiate a group-wide valuation premium. In the central sensitivity, 2030 incremental cash flow is **€18.59m**, approximately **0.88%** of the group's preliminary FY2025 reported free cash flow. That comparison establishes scale only: the project measure and reported group FCF have different accounting boundaries.

The most useful underwriting question is the required incremental cement premium. With the central assumptions, the five-year cash-flow window breaks even at **€13.08 per tonne of cement**. If no avoided-carbon cash benefit reaches the business, the hurdle rises to **€46.50/t**, holding the other central inputs fixed. A buyer should therefore ask for the realized premium and the subsidy/allowance cash waterfall before attaching value to the emissions headline.

**Decision:** retain the project as a monitored source of potential earnings. Do not add a separate “green” multiple or reduce the discount rate on top of modeled cash benefits. A buy/hold/sell view on the whole stock requires a reconciled group forecast, current valuation and a mandate; none is implied here.

## What the primary evidence establishes

| ID / classification | Observation | Financial use and boundary |
|---|---|---|
| HM1 — FACT | FY2025 reported group FCF was €2,109m, preliminary and unaudited. | Scale comparator; not a project cash-flow input or full group valuation. |
| HM2 — FACT | Brevik's stated capture capacity is 400,000 tonnes of CO₂ annually, approximately half of plant emissions. | Physical ceiling; capacity is not actual capture or independently verified permanent storage. |
| HM3 — FACT OF MANAGEMENT EXPECTATION | Brevik cement volumes were planned at 350/450/500/550/550kt for 2026–2030. | Source for the ramp before analyst realization haircuts; cement tonnes are separate from captured CO₂ tonnes. |
| HM3 — FACT OF MANAGEMENT EXPECTATION | Management's carbon-price assumption is €80/t in 2025–2026, rising linearly to €100/t in 2030. It describes higher plant margins supported by pricing, avoided carbon costs and grants. | Scenario reference; not a market forward curve, disclosed realized premium, or demonstrated net project cash margin. |
| NO1 — HISTORICAL POLICY CONTEXT | The original Longship design combined public support with incentives from allowance savings. | Confirms the relevance of grant/allowance interactions; does not establish today's executed grant terms. |

Sources and exact document locators appear in [sources.csv](heidelberg-brevik/sources.csv). The investor deck's displayed cover says Q3 2025 despite an older URL folder and stale PDF metadata. This case uses the displayed version. Source links were reviewed on the preparation date; publicly hosted documents can subsequently be replaced.

## Financial transmission and counterfactual

**METHOD:** compare Brevik with CCS to otherwise identical conventional cement production without CCS. Hold ordinary cement revenue, underlying plant costs and ordinary carbon-price pass-through constant. Include only the incremental premium, retained avoided-carbon cash, uncovered CCS operating expense, incremental cash taxes, capex and working capital.

For each year:

1. Realized cement sales = management's planned production × analyst realization fraction. Same-year sale of that volume is assumed.
2. Captured tonnes = 400,000 × realized cement tonnes / 550,000, capped at nameplate capacity. This is an assumed ramp linkage, **not an engineering emissions factor** or an observed capture rate.
3. Incremental operating cash surplus = cement tonnes × incremental premium + captured tonnes × management carbon price × retained cash fraction − captured tonnes × net CCS opex.
4. Incremental cash flow = surplus − modeled cash tax − incremental capex − change in premium-related working capital.
5. Discount year-end cash flows to 25 February 2026 using actual days / 365.25. No terminal value is included.

**Double-counting control:** the cement premium excludes ordinary carbon-price pass-through already present in the conventional product. Net CCS opex is after operating grants but before the separately modeled carbon benefit. The retained cash fraction represents residual monetization after allowance eligibility, free allocation, aid settlement and cash timing. Grant income or avoided allowances must not appear in two lines. These definitions need reconciliation to the actual contracts; the model does not assert the two parameters can vary independently under those contracts.

## Explicit analyst assumptions

| Assumption | Downside | Central sensitivity | Upside |
|---|---:|---:|---:|
| Realization of management cement ramp | 60% | 85% | 100% |
| Incremental cement premium, €/t cement | 20 | 60 | 100 |
| Retained fraction of gross carbon-price benefit | 0% | 50% | 100% |
| Net CCS operating cost after grants, €/t captured | 60 | 40 | 20 |

These ranges deliberately challenge the economics. **They are not observed prices, calibrated forecasts, management guidance or probability bounds.** The central column is a reference sensitivity, not a most-likely outcome. The upside is especially dependent on favorable joint pricing, grants and allowance economics.

All scenarios assume €5m annual incremental capex, a 25% cash-tax charge on positive operating surplus, working capital equal to 5% of premium revenue, zero opening premium working capital and an 8% discount rate. Tax is a simplified analyst cash charge: no jurisdiction-specific tax opinion, loss tax shield or depreciation tax shield is modeled. There is no financing cash flow, working-capital release, terminal value or recovery of original construction spending. The zero opening balance can overstate the first year's working-capital drain. No separate inflation escalation is applied to unit premiums, unit costs or capex. The full-year 2026 net flow is placed at year-end; pre-cutoff cash movements are not stripped out. This is a timing approximation, not an exact as-of cash reconciliation.

**Interpretation boundary:** the five-year PV is the value of the defined future cash-flow window. It is not total project NPV, a project IRR, incremental equity market capitalization, or a replacement for an enterprise-to-equity bridge. Excluding historical construction expenditure prevents a claim that the project has earned its original investment back.

## Results and challenge

| Scenario | 2026 incremental FCF | 2030 incremental FCF | Five-year PV |
|---|---:|---:|---:|
| Downside | −€10.17m | −€12.80m | −€47.55m |
| Central sensitivity | €7.50m | €18.59m | €56.08m |
| Upside | €30.95m | €60.25m | €193.60m |

The [annual bridge and two-dimensional sensitivity](heidelberg-brevik/RESULTS.md) show where those results come from. Holding central assumptions fixed, increasing the incremental premium from €20/t to €100/t moves PV from €8.27m to €103.89m. Changing only the discount rate from 6% to 10% moves it from €59.44m to €53.00m. **INFERENCE:** commercial realization and retained cash economics deserve more attention than fine-tuning the discount rate.

The strongest contrary case is that successful operating evidence could make the assumed 85% realization and 50% retained benefit too cautious, while replication across other plants could create value beyond this single asset. Neither replication nor post-2030 cash flow is capitalized here. Conversely, capacity availability does not establish customer willingness to pay, and emissions performance does not establish cash profitability. Construction-cycle weakness, storage interruptions, additional maintenance spending and subsidy adjustments can overwhelm the premium.

## Evidence gates and engagement questions

| Material open issue | Specific evidence to obtain | Decision affected |
|---|---|---|
| Realized premium and demand | Invoiced premium net of rebates, contracted offtake volumes, cancellations and like-for-like conventional pricing | Replace the €20/60/100 sensitivity; test the break-even hurdle. |
| Grant and allowance economics | Executed support agreements, grant cash receipts, eligible operating expenses, allowance reconciliation and a single net cash waterfall | Replace retained-benefit and net-opex assumptions together; eliminate overlap. |
| Capture and storage delivery | Monthly capture, uptime, shipped/stored tonnes, independent verification and reconciliation to certificate sales | Replace the assumed cement-to-capture linkage; assess delivery risk. |
| Sustaining expenditure and tax | Project cash-cost ledger, maintenance plan, residual capex and usable tax treatment | Rebuild the simplified cash bridge and evaluate full project returns. |
| Whole-company investment context | Updated issuer model, existing CCS assumptions, net debt/share count and dated market valuation | Avoid adding benefits already in the baseline; assess security-level attractiveness. |

**WATCH upgrades** when realized unit economics clear a recalculated premium hurdle, physical delivery is verified and the cash waterfall reconciles. **Thesis weakens** if sustained realized premiums fall below the hurdle, net costs rise without support, or capture/storage availability prevents the planned ramp. Re-run with new dated evidence rather than relabeling these assumptions as facts.

## Reproduce and review

From the repository root, using Python 3.10+ and no external packages:

```bash
python examples/heidelberg-brevik/model.py --check
python -m unittest discover -s tests -v
```

To change assumptions, edit `examples/heidelberg-brevik/inputs.json`, run `python examples/heidelberg-brevik/model.py`, and reconcile this memo to the generated results. Preserve the source/assumption classifications and update the cutoff when adding new evidence. Generated CSVs retain more precision than displayed tables.

This case demonstrates issuer research, materiality judgment, model discipline and engagement priorities. It does not change the engine's [methodology-only source study](reports/source-study-packet.md), which correctly remains `NEEDS_DATA`, or record human approval on its behalf.
