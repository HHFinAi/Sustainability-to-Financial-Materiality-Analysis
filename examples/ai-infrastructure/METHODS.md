# Model design, ownership and limits

This original case uses separate evidence, assumptions and calculation layers. Preparation: 16 October 2026. The [input file](inputs.json) is an **illustrative assumption set**. The [evidence register](evidence/sources.json) and [public-data register](public-data/SOURCES.md) establish only the observations identified there. No source-derived project return is claimed.

## Financial mechanics

The model has 121 cash dates, months 0-120. The horizon ends at the same calendar date for every alternative. A delay consumes the available commercial window. This is an opportunity-window comparison, not an estimate of the full life of a particular building.

- Month zero: land, buildings, cooling, route-specific power infrastructure and mitigation capex.
- Commissioning: hardware and working capital; first operating cash flow occurs one month later.
- Operations: constant real revenue, energy and other operating costs; no assumed growth or inflation. **8% is an assumed real discount rate**, not an estimated Microsoft WACC.
- Waiting: non-financing holding costs are charged monthly. Debt interest is excluded from unlevered cash flow and is not added on top of the discount rate.
- Replacement: hardware is repurchased at the end of each economic service cycle, only if a subsequent operating month remains. All earlier hardware receives zero resale. Replacement costs do not change with time.
- Tax: cash tax applies to positive monthly taxable income. Separate straight-line capital-allowance assumptions are used; economic replacement life does not change tax-allowance life. Deductions stop when an asset is retired. No loss carryforward, refund, unused-basis deduction, credits or actual statutory tax entitlement is assumed.
- End: working capital is released once; land/building sale proceeds and an optional final-hardware recovery are added, with retirement costs deducted. Gains above remaining basis are taxed; losses receive no assumed relief. No terminal earnings multiple or continuing-project value is added.

For each month, `FCF = revenue - operating costs - cash tax - capex - increase in working capital + sale proceeds - retirement costs`. `NPV = sum(FCF_month / (1 + real_discount_rate)^(month/12))`.

The tax calculation uses simplified real-dollar bases consistently within this hypothetical model. Actual tax depreciation is ordinarily governed by nominal-dollar law and conventions; a calibrated case must reconcile inflation, nominal tax basis and cash-tax capacity. The current model does not undertake that reconciliation.

## Asset boundaries

| Asset | Cost timing | Life/recovery treatment | What must be verified for an issuer |
|---|---|---|---|
| Land | Month zero | No depreciation; explicit sale fraction | Title, remediation, zoning and alternate use |
| Building | Month zero | Separate allowance life; sale fraction | Structural suitability, leasehold rights, capex mix |
| Cooling | Month zero | Separate allowance life; zero recovery | Thermal density, retrofit cost, energy/water trade-off |
| Grid or generation assets | Month zero | Route-specific capex and allowance life; zero recovery | Ownership, tariff, fuel contract, permits, grid-backup needs |
| IT hardware | Commissioning and replacement dates | Economic and tax lives separate; optional final recovery | Workload compatibility, economic yield, supplier and resale terms |

Non-hardware lives must cover the modeled horizon because their replacement is not implemented. This constraint is enforced. An impairment charge is not added as a separate cash loss if the economic cash-flow loss is already modeled. An accounting life is not proof of actual technological obsolescence.

## Who bears the financial effect?

The model assumes one hypothetical owner bears all modeled costs. The following is a diligence map, not a statement of Microsoft's actual contracts.

| Mechanism | Potential cost bearer | Contract/evidence needed before allocation |
|---|---|---|
| Power-price or fuel shock | Utility customer, generator owner, tenant | Delivered tariff, pass-through, fuel/PPA terms and hedges |
| Delayed commissioning | Developer, landlord, tenant or contractor | Rent commencement, termination rights, liquidated damages, spending schedule |
| Hardware obsolescence | Hardware owner or lessee | Purchase/lease scope, refresh obligations and residual guarantees |
| Cooling retrofit | Owner, operator or tenant | Landlord works, operating responsibility, performance warranties |
| Outage and customer loss | Service provider, tenant, insurer | Service credits, liability caps, insurance, rerouting and recovery |
| Site retirement | Landowner, operator or secured obligor | Lease reinstatement, remediation, decommissioning and security terms |

A colocation landlord's building exposure cannot be assigned a tenant's GPU replacement bill without evidence. A vendor's demand opportunity is also different from the operator's project return.

## Conditional incidents and common-mode risk

The incident scenario occurs once in month 36. It removes unrecovered workload from revenue and net variable electricity demand; fixed costs remain. Service credits and recovery spending are explicit. It does not forecast cyberattack incidence. NIST's OT guidance supplies a diligence framework for physical processes, not Microsoft-specific failure statistics.

Grid loss, cooling failure and cyber disruption may affect the same workload. Do not sum standalone sensitivities as independent losses. A combined scenario requires a joint event definition, workload-recovery assumptions and prevention of duplicate lost revenue. The model provides one conditional event, not a correlated Monte Carlo engine.

## Challenges to the reference result

**Horizon:** a replacement just before month120 is costly with zero resale, while the same replacement just beyond it is omitted. The supplementary recovery table exposes this boundary; delay can become nonmonotonic outside the featured 0-24-month range. Underwrite longer horizons and credible continuation values before using the result for capital allocation.

**Spending schedule:** all facility capital at month zero intentionally tests committed capital; staged spending would change timing losses. Hardware is just-in-time and therefore does not age before operation. Preordered hardware, cancellation penalties and idle obsolescence would require another schedule.

**Availability:** immediate gas commissioning assumes adequate turbines, fuel delivery, permits, reliability and redundancy. Those conditions are unverified. The six-month gas-delay row demonstrates the consequence of losing the assumed speed advantage.

**Demand and pricing:** utilization and revenue are independent analyst choices. No backlog, contract, model-training value or demand curve calibrates them. If a new site displaces existing capacity, group incremental benefit is smaller than site revenue.

**Real-world exit:** a recovery fraction is not a sale appraisal. Physical reuse, environmental obligations and commercial demand can differ by asset. Cancellation before hardware commitment is distinct from closing an operating campus.
