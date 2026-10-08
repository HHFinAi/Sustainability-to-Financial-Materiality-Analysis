# Cooling investment: reproducible sensitivities

**Illustrative project arithmetic, not a Microsoft site forecast or share-price valuation.**
Baseline prepared 4 October 2026; underwriting extension prepared 8 October 2026. USD million unless stated otherwise.

Issuer underwriting: **NEEDS_DATA**. Scenario arithmetic: **COMPLETE**. [Named evidence gaps](inputs.json) remain unresolved.

Annual IT electricity: 613,200 MWh. Additional electricity: 12,264 MWh.
Assumed avoided direct cooling water: 183,960 m3/year.
Water bill saving: 0.551880; additional electricity cost: 0.981120 per year.

| Scenario | First operating-year incremental FCF | NPV | Break-even additional pre-tax benefit/year |
|---|---:|---:|---:|
| Reference: direct bills only | -0.1344 | -15.9020 | 3.1598 |
| Additional benefit $3m/year | 2.1156 | -0.8044 | 3.1598 |
| Electricity $120/MWh | -0.5024 | -18.3708 | 3.6504 |
| Water $5/m3 | 0.1415 | -14.0505 | 2.7919 |
| Incremental PUE 0.04 | -0.8703 | -20.8396 | 4.1409 |
| Capex +25%; commissioning +1 year | -0.0407 | -19.0027 | 4.0780 |
| No taxes or tax shields | -0.6792 | -19.5578 | 2.9147 |
| Capital allowances unavailable; tax remains 25% | -0.5094 | -18.4183 | 3.6598 |
| All cost deductions unavailable; tax remains 25% | -0.8172 | -20.4835 | 4.0702 |
| All cost deductions delayed 2 years; tax remains 25% | -0.8172 | -16.5556 | 3.2897 |

The hurdle is total recurring additional pre-tax benefit required for zero NPV. It is not extra benefit on top of an assumed amount.
Cash taxes on savings/benefits remain payable in deduction-unavailable/delayed rows. A two-year delay shifts deductions, including tax-only receipts after asset life; no expiry is assumed. All deductions are otherwise immediately usable against other taxable income. These are simplified tax scenarios, not conclusions about US tax law.
Commissioning delays postpone operating cash flows and tax depreciation, not initial capex. Delay holding costs remain excluded.

## Route A: protected existing workload

The single-event scenario assumes a 25% annual event probability, 48 disruption hours, 80% risk reduction, $0.05m/hour cash contribution after avoidable costs, and 25% workload recovery. None is an issuer observation.

| Reliability output | Value |
|---|---:|
| Expected avoided outage hours/year | 9.6000 |
| Expected avoided pre-tax cash loss/year | 0.3600 |
| Required expected avoided hours/year to clear cooling hurdle | 84.2621 |
| Required event probability at assumed 48-hour duration | 2.1943 |
| Required event duration at assumed 25% annual probability, hours | 421.3106 |
| Cooling plus reliability NPV | -14.0903 |

Probability feasibility: **OUTSIDE_PROBABILITY_RANGE**. A required probability above 1 rejects this duration/contribution combination; it is not a predicted probability. Recoverable/rerouted work is removed before loss valuation.

## Route B: separate new capacity

The added 10 MW has its own infrastructure, cooling, IT hardware, total facility electricity, non-power operating costs and working capital. Hardware is replaced at year 5. This route does not place gross expansion revenue in the existing cooling model's benefit input.

| Capacity output | Value |
|---|---:|
| Added revenue/year | 28.0000 |
| Added facility electricity MWh/year | 70,518.0000 |
| Added power / other operating costs/year | 5.6414 / 10.0000 |
| Initial infrastructure and cooling / IT hardware capex | 43.0000 / 60.0000 |
| Hardware replacement capex across project life | 60.0000 |
| Separate capacity-project NPV | -55.0477 |
| Standalone break-even revenue per fully utilized MW-year | 5.5710 |
| Break-even revenue per fully utilized MW-year including existing cooling | 6.0248 |
| Existing cooling plus separate capacity-project NPV | -70.9498 |
| Added MW required to offset existing cooling NPV at constant assumed unit economics | Not finite / unavailable |

At the reference revenue assumption the added project has negative NPV, so no positive amount of identically priced capacity clears the existing cooling hurdle. The break-even combined revenue above prices both capital commitments.

| Revenue per fully utilized MW-year | Separate capacity NPV | Cooling plus capacity NPV | Required added MW |
|---|---:|---:|---:|
| 4.00 | -55.0477 | -70.9498 | Not finite / unavailable |
| 6.00 | 15.0324 | -0.8697 | 10.5785 |
| 6.20 | 22.0404 | 6.1383 | 7.2150 |

No expansion value is attributable to water resilience until water design is shown to be a binding constraint. Linear scaling assumes unchanged prices, utilization, costs and capital intensity; power, demand, permitting and grid constraints may invalidate it. Reliability and expansion routes are not combined.

[Investment memo](README.md) · [Inputs and assumptions](inputs.json) · [Calculation](model.py) · [Machine-readable cash flows](results.json)
