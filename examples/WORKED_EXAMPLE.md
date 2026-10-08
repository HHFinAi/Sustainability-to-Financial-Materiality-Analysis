# Heidelberg Materials: what Brevik must earn to matter

**Assessment: WATCH / screen-grade.** Brevik has crossed meaningful delivery and storage milestones, but its realized premium, amended aid settlement and retained construction capital remain unresolved. The extended central sensitivity gives **€65.86m of finite-life future cash value**, versus **−€222.18m / +€356.84m** in the downside/upside stresses. Under the central operating assumptions, an incremental premium of **€114.45/t of cement** is required to add **€1 per issued share** above a baseline that already embeds the central Brevik value. These are conditional calculations, not observed project economics or a stock-price target.

**Information cutoff and valuation date: 25 February 2026. Extension prepared: 8 October 2026.** This is retrospective research. The model uses primary documents published by the cutoff; later audited accounts and operating updates are excluded. No independent human approval is recorded. Actual contractual underwriting, lifecycle returns and observed-price comparison remain **NEEDS_DATA**.

[Finite-life results and issuer bridge](heidelberg-brevik/FORWARD_VALUATION.md) · [Extended inputs](heidelberg-brevik/extended-inputs.json) · [Forward model](heidelberg-brevik/forward_model.py) · [Sources](heidelberg-brevik/sources.csv) · [Open evidence gates](heidelberg-brevik/evidence-gaps.json) · [Original five-year results](heidelberg-brevik/RESULTS.md)

## Investment judgment

**INFERENCE:** the central question is whether a verified carbon-capture chain produces retained cash that exceeds the capital committed and the cash already embedded in the company valuation. A captured tonne, a stored tonne and a premium-bearing cement tonne are different economic units. Successful emissions performance does not determine who receives allowance savings, how grants are settled or the price customers actually pay.

The finite-life central case earns positive cash during the ramp but reaches **−€1.98m FCF in 2035**, when assumed operating support has expired and a transport/storage charge begins. In that case the premium must rise from the assumed €60/t to **€41.87/t merely to achieve zero future PV** across the full modeled life. Recovering hypothetical €100m of retained construction capital at the assumed 8% required return raises the premium hurdle to **€73.36/t**. The historical retained capital is unknown, so this is a hurdle calculation, not proof of capital recovery.

**Decision:** monitor the cash economics and keep the stock-level conclusion open. A baseline valuation containing CCS expectations cannot receive the same project value again. Do not add a separate green multiple or lower discount rate on top of modeled cash benefits. No observed mispricing is established without a verified historical quote, group forecast and reconciled embedded CCS assumptions.

## What the dated primary sources establish

| Evidence | Observation and use | Boundary |
| --- | --- | --- |
| HM1: preliminary FY2025 financials, 25 February 2026 | Rounded group RCOBD €4,679m; FCF €2,109m; net debt €5,715m. Detailed income statement includes €191.2m of equity-accounted income; balance sheet and cash-flow statement support the bridge adjustments. | Preliminary and unaudited. Group FCF is a scale comparator, not project FCFF. Consolidated €73.6m government-grant cash cannot be assigned entirely to Brevik. |
| HM2: opening announcement, June 2025 | Annual capture design capacity 400,000 tonnes, approximately half of plant emissions. | Capacity is not delivered capture or certified storage. |
| HM3: displayed Q3 2025 investor deck | Brevik cement production plan 350/450/500/550/550kt for 2026–2030; management carbon-price assumption €80/t rising to €100/t. | Production plans are not invoiced sales. Deck URL metadata is stale; displayed Q3 cover and relevant slides control the version. |
| HM4: published share-cancellation notice, 2 February 2026 | 176,365,065 issued shares after January cancellation. | Not the FY2025 weighted-average EPS denominator. Later buybacks are excluded; the PDF's April URL folder does not override its printed publication date. |
| GS1: Gassnova report, June 2025 | Autumn 2024 construction forecast totals NOK4.9bn, versus original NOK3.2bn. Public support architecture is capped, with ten-year eligible operating support. | These are estimates and policy architecture, not final actual spend or current grant receipts. |
| NO2: government amendment announcement, September 2023 | Heidelberg agrees to complete the project and cover increased costs for a larger potential return share; startup-grant ceiling is NOK150m on readiness to ship the first load. | Current retained-return percentage and grant cash receipt are not established. Applying original subsidy percentages to all later overruns would be unsafe. |
| NO1 / NO3: original Longship white paper | Differentiates eligible operating support, allowance benefits and additional support for non-ETS emissions. | Historical framework; executed amended thresholds, caps and settlements remain needed. |
| HM5 / NL1: October / December 2025 announcements | First evoZero deliveries and first Northern Lights storage certificates occurred. | Full annual quantities, certificates, invoice economics and independent assurance report were not reviewed. First milestones do not establish steady-state annual performance. |

See [sources.csv](heidelberg-brevik/sources.csv) for exact locators and reviewed URLs. Source review is document-level session work, not independent human certification. Publicly hosted documents can change; no immutable source-binary archive is claimed.

## Cash waterfall and counterfactual

**METHOD:** compare incremental CCS economics with otherwise identical conventional cement production. Ordinary cement revenue, underlying plant costs and ordinary carbon-price pass-through stay in the counterfactual. Only the incremental premium and CCS cash changes enter the model.

1. **Separate physical volumes.** Management production is haircut for sales realization. Capture has its own availability ramp. Stored CO₂ equals capture multiplied by a separate storage-delivery fraction. Premium sales are capped by an assumed carbon-attribute intensity; this is a commercial-accounting constraint, not a verified engineering factor.
2. **Start with gross costs.** Fixed capture cash costs and variable captured-tonne costs are separate. Fixed costs persist when capture is weak. Transport/storage costs have separate support-period and post-support assumptions.
3. **Compute grants once.** Eligible capture costs feed a threshold/percentage aid formula, subject to a cumulative remaining cap. Grant cash then reduces gross costs once. The threshold, eligible costs and remaining EUR cap are scenario inputs requiring replacement by the amended contract.
4. **Keep ETS and non-ETS cash separate.** Only assumed eligible stored fossil tonnes generate gross ETS value. Retained ETS cash reflects free allocation, monetization and settlement uncertainty. Non-ETS aid uses a disjoint tonne base and stops earning after the assumed support period. Both cash streams have an explicit receipt lag; earned benefits are not treated as immediate cash.
5. **Deduct cash uses.** Simplified tax on positive cash surplus, sustaining capital, changes in premium-related working capital, residual capital and closure costs enter explicitly. No assumed startup-grant receipt enters future cash. Tax shields and actual aid tax treatment remain unverified.
6. **Use a finite life.** The extension models remaining 2026–2045 operations and a receipt-only carbon tail, with no perpetual terminal value. First-year operating amounts are uniformly prorated from the cutoff; this is a timing assumption, not an actual cash reconciliation.

The [annual CSV](heidelberg-brevik/forward-cashflows.csv) shows gross costs, separate aid and carbon lines, eligible volumes, tax, capital and working capital. All conclusion-driving assumptions are named in [extended-inputs.json](heidelberg-brevik/extended-inputs.json).

## Conditional scenarios and results

| Assumption / result | Downside | Central sensitivity | Upside |
| --- | ---: | ---: | ---: |
| Sell-through of planned cement | 60% | 85% | 100% |
| Steady capture availability | 60% | 90% | 100% |
| Stored / captured CO₂ | 90% | 98% | 100% |
| Incremental cement premium, €/t | 20 | 60 | 100 |
| Retained ETS monetization fraction | 25% | 50% | 100% |
| Operating / non-ETS aid modeled | No | Yes | Yes |
| Finite-life PV after residual capital, €m | −222.18 | 65.86 | 356.84 |
| Premium for zero future PV, €/t | 99.83 | 41.87 | 8.20 |
| Premium for €1/share above embedded central value, €/t | 205.87 | 114.45 | 69.89 |

These are deliberately broad analyst sensitivities, **not calibrated probabilities, forecasts or contractual bounds**. The downside removes support as a contractual-dispute/eligibility stress; it does not claim announced grants disappear. Operating-cost inputs are held common to isolate volume, premium, retention and aid effects. The €8m fixed cost, €70/t variable capture cost, €10m aid threshold, €150m remaining aid cap, 2034 support expiry, post-support €30/t storage cost, capital and 25% cash-tax charge are all explicit assumptions.

**Strong contrary case:** realized premiums, retention and support may exceed the reference case, while replication could create more value. Neither actual commercial pricing nor replication value is established here. Conversely, prolonged low premiums, storage interruptions or aid exhaustion can cause losses before the environmental thesis fails. Continuing to operate through 2045 in the downside is a stress, not optimal management behavior; a shutdown option could reduce recurring losses but create termination and closure liabilities that are not underwritten.

## Issuer bridge without double counting

**CALCULATION:** normalize rounded RCOBD by removing €191.2m of equity-accounted income, apply an assumed 7/9/11× operating multiple, remove the independently calculated embedded Brevik reference PV, and substitute the scenario PV. Then deduct reported net debt, current plus noncurrent pension provisions and an NCI book-value proxy; add a separate JV/associate book-value proxy; divide by the dated issued share count.

The normalized earnings base is **€4,487.8m**. The default central project value is fully embedded: its separate uplift is therefore **zero**. Relative to that reference, the downside/upside project stresses change common-equity value by approximately **−€1.63 / +€1.65 per issued share**, with the rest of the bridge unchanged. This shows the scale of one asset rather than implying a group-wide green re-rating.

[issuer-bridge.csv](heidelberg-brevik/issuer-bridge.csv) provides every adjustment. Pension/NCI/JV carrying values are proxies, not appraised fair values. The financial baseline is 31 December 2025; no January–February debt/cash roll-forward or announced acquisition financing is fabricated. No cash or lease deduction is added again after reported net debt.

**Price anchor: NEEDS_DATA.** A verified exact 25 February 2026 exchange close was not obtained. Conditional per-share values are provided as reproducible bridge sensitivities; no observed upside, market-implied multiple or stock-price target is stated. The [reverse-premium table](heidelberg-brevik/reverse-premium.csv) instead shows the cash earnings needed to add €0/1/2 per issued share above the embedded central reference.

## Historical capital, lifecycle returns and future value

The **NOK4.9bn gross construction forecast**, historical investor capital and future residual spending must remain distinct. Only future residual spending is deducted from forward project value. Actual lifecycle NPV/IRR additionally requires original payment dates, final project cost, capital grants, 2025 operating cash, tax shields and closure obligations. Neither the revised gross forecast nor the consolidated group grant line answers how much capital Heidelberg ultimately retained.

The [capital-recovery sensitivities](heidelberg-brevik/capital-recovery.csv) use hypothetical net construction capital of €0/100/200/300m, an explicit 1 January 2025 reference date and an assumed 8% required return. They compare required capital recovery at the cutoff with remaining future value, **not historical full-project NPV or IRR**. For example, central value of €65.86m falls €43.40m short of recovering hypothetical €100m compounded to the cutoff; the premium hurdle becomes €73.36/t. Unknown pre-cutoff operating cash and capital dates prevent an actual lifecycle conclusion.

## What changes the view

| Evidence gate | Upgrade / failure test | Model or investment consequence |
| --- | --- | --- |
| Premium invoices and committed offtake | Net realized premium and volume clear the recalculated hurdle across actual delivery conditions | Replace assumed premiums and sell-through; re-underwrite forward value. |
| Executed support waterfall | Eligible costs, remaining caps, retained returns and grant receipts reconcile without duplicate carbon/grant benefits | Replace the aid formula and retained-cash fractions together. |
| Capture, storage and assured attributes | Monthly physical volumes reconcile to cargo certificates and product allocation, including lifecycle deductions | Replace availability, storage yield and attribute constraint. |
| Capital and tax ledger | Final retained capital, residual spending, tax treatment and historic cash dates are documented | Calculate actual lifecycle NPV/IRR and required-return recovery. |
| Group and market baseline | Existing CCS forecasts, dated price, pension/NCI/JV values and balance movements reconcile | Assess observed security-level mispricing and action; avoid duplicated uplift. |

The next meaningful catalyst is disclosure that resolves these gates. No unverified hard catalyst date is assigned. The portfolio action remains **watchlist / wait for proof**, with no position-size recommendation or trade authority.

## Original five-year case retained

The original model and outputs remain unchanged at the same historical cutoff. Its central 2026–2030 PV is **€56.08m**, versus **−€47.55m / +€193.60m**. It excludes original construction expenditure and all post-2030 cash. Its €13.08/t premium hurdle is specific to that earlier five-year, already-net-cost specification; without retained carbon cash it is €46.50/t. Neither figure should be substituted for the extended finite-life hurdle.

The new €65.86m central result is not an updated forecast on the same old assumptions. It changes the operating specification, separates gross costs and grants, introduces independent capture/storage ramps, a first-year stub, cash lags, grant-cap exhaustion, residual capital, post-support costs and closure. Comparing the two values without those bridges would be misleading.

[Original inputs](heidelberg-brevik/inputs.json) · [Original calculations](heidelberg-brevik/model.py) · [Original annual cash flows](heidelberg-brevik/annual-cashflows.csv) · [Original synthetic example](SYNTHETIC_CASHFLOW_EXAMPLE.md)

## Reproduce and review

From the repository root, Python 3.10+ with no external packages:

```bash
python examples/heidelberg-brevik/model.py --check
python examples/heidelberg-brevik/forward_model.py --check
python -m unittest discover -s tests -p 'test_brevik*' -v
```

Both `--check` commands compare committed outputs without writing. To change the extension, edit `extended-inputs.json`, run `forward_model.py`, and reconcile this memo to its tables. Preserve factual classifications, update the cutoff only when introducing later evidence, and record outstanding dependencies. Economic tests cover grant exhaustion, receipt timing, physical limits, working-capital release, capital discounting, the issuer bridge and reverse premiums.

This analyst case remains separate from the workflow engine's [methodology-only source study](reports/source-study-packet.md), which correctly remains `NEEDS_DATA`. It does not self-attest human approval or certify investment readiness.
