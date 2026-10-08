# Microsoft: what must water-resilient AI infrastructure earn?

**Real-issuer context with illustrative project economics. Baseline prepared 4 October 2026; underwriting extension prepared 8 October 2026.** The FY2023–FY2025 accounts and December 2024 engineering disclosure remain the original financial/design baseline. The extension adds explicitly dated Phoenix design and basin evidence; it does not update the company forecast or treat earlier rollout expectations as achieved results.

## Research conclusion

**Direct water-bill savings do not justify the reference cooling investment.** Its unchanged illustrative inputs require **$3.16m/year** of additional pre-tax operating benefit to clear an 8% return hurdle; direct bills alone produce **−$15.90m NPV**. This conditional result does not establish a loss on Microsoft's actual investments.

The extension makes the missing benefit concrete. At an assumed $50,000/hour protected cash contribution and 25% workload recovery, the design must prevent **84.26 expected outage hours/year**. A 25%-probability, 48-hour event reduced by 80% prevents only 9.6 expected hours and supplies $0.36m/year of benefit. That duration would require a **219.43% event probability**, outside the supported probability range, to clear the hurdle. At the assumed 25% probability, the required event duration is 421.31 hours. These are breakpoints, not loss forecasts.

Expansion is a separate capital project. The illustrative added 10 MW includes infrastructure, cooling, IT hardware, recurring operating costs, working capital and a year-5 hardware replacement. It needs **$5.57m revenue per fully utilized MW-year** to break even alone, or **$6.02m** including recovery of the original cooling investment. This avoids treating gross new-capacity revenue as a free resilience benefit.

**Issuer underwriting remains NEEDS_DATA.** Public design and basin evidence establish a researchable counterfactual, not site-specific outage probabilities, commercial losses or investment returns.

[Results](RESULTS.md) · [Inputs](inputs.json) · [Model](model.py) · [Cash flows](results.json) · [Evidence register](evidence.json) · [Sources](SOURCES.md) · [Evaluation](EVALUATION.md) · [Proposed AI stewardship programme](https://github.com/HHFinAi/Stewardship-and-Controversy-Assessment/blob/main/examples/microsoft-ai/README.md)

## What the issuer evidence establishes

The original engineering source describes closed-loop cooling, continued administrative water use, mixed existing designs and an energy/PUE trade-off. Its rollout dates are expectations stated on 9 December 2024. It does not disclose project economics. [MS2](SOURCES.md#ms2--engineering-disclosure)

FY2025 consolidated cash from operations of $136.162bn less cash additions to property and equipment of $64.551bn leaves a simple $71.611bn residual, compared with $74.071bn in FY2024. This group-account calculation is scale context; it is neither AI-only expenditure nor project FCFF. It does not deduct acquisitions, financing-lease principal or an economic stock-compensation charge. [MS1](SOURCES.md#ms1--financial-baseline)

## Dated extension: Phoenix design and basin counterfactual

| Evidence | Registered observation | Underwriting implication |
|---|---|---|
| West US 3 announcement, 15 June 2021 [MS4](SOURCES.md#ms4--arizona-design-history-extension) | Arizona cooling was described as using outside air below 85°F and evaporation above it; availability zones have independent cooling infrastructure | Existing redundancy/rerouting must be considered before pricing an avoided outage |
| Arizona fact sheet, internally dated December 2024 [MS5](SOURCES.md#ms5--arizona-design-specific-disclosure-extension) | Existing facilities use direct evaporative cooling; new facilities are planned with air-cooled chillers and closed-loop direct-to-chip cooling | Establishes two design archetypes; does not identify a matched before/after site |
| ADWR Phoenix AMA model FAQs, 2023 release [MS6](SOURCES.md#ms6--basin-context-extension) | The regional groundwater model projects unmet groundwater demand over a 100-year horizon; already approved water-supply certificates are not rescinded | Basin exposure warrants checking water delivery/source contracts; it cannot be converted into annual datacenter outage probability |

These sources were reviewed for this extension on 8 October 2026. The Arizona PDF's publication date comes from its internal footer, not the older directory in its URL. The government observation is explicitly the 2023 model release; it is not represented as the latest basin projection or a finding about a particular Microsoft permit. No matched campus, supplier, tariff, source-water mix or curtailment history has been verified.

**Counterfactual:** compare evaporative and closed-loop/mechanical designs for an identical assumed 100 MW workload under the same local delivery conditions. Weather, redundancy, water rights, power and workload must be matched. The fleet WUE value is not a Phoenix site coefficient. Separate initial fill and administrative water from recurring cooling consumption; pumping/replenishment or returning water does not itself establish avoided business loss.

## Route A: preserve an existing workload

The original physical/cash-flow assumptions remain: 100 MW, 70% average load, 8,760 hours; avoided direct-water intensity 0.30 L/IT-kWh; incremental PUE +0.02; electricity $80/MWh; water $3/m3; cooling capex $15m and incremental maintenance $0.25m/year; 10-year life, 8% discount rate and 25% tax. They are analyst assumptions, not Microsoft site inputs. Avoided direct water is 183,960 m3/year; savings of $0.552m are below extra electricity expense of $0.981m, before maintenance.

```text
Expected avoided pre-tax loss = annual event probability × event hours
                              × risk-reduction fraction
                              × protected cash contribution per hour
                              × (1 − recoverable workload fraction)
Required expected avoided hours = annual pre-tax benefit hurdle
                                / nonrecoverable cash contribution per hour
```

The event model allows at most one water-linked event per year. Protected contribution is after costs avoided during shutdown; it is not gross revenue. Remove workload rerouted to other regions or recovered later, and assign costs/benefits to the party actually bearing them. The reduction fraction requires a causal water-design link; compound heat/power failures may persist after cooling redesign. No event probability, duration, recovery fraction or contribution has been inferred from the basin model.

## Route B: add profitable capacity

The capacity route compares a new 10 MW project against **no new project**. It has its own assumed $43m infrastructure/cooling capex, $60m initial IT hardware, $60m year-5 hardware replacement and $1.4m initial working capital. At 70% billable utilization and $4m revenue per fully utilized MW-year, annual revenue is $28m; total facility power costs $5.64m and other operating costs $10m/year. Those costs include assumed maintenance, people/network and other non-power site costs; none is calibrated to an issuer campus.

The reference capacity NPV is −$55.05m, so adding more capacity with those same economics cannot fund the existing cooling investment. The results also show $6.00m and $6.20m revenue sensitivities; the latter produces positive combined NPV after both capital commitments. Pricing, utilization, marginal power, site permits, demand and replacement assumptions must support such a case before calling it profitable.

The original 100 MW cash flows stay fixed. New workload uses **total** facility PUE and carries all its own infrastructure/hardware cash outlays; its revenue is not also entered as the old design's benefit. Reliability and growth outputs are separate routes and are not added together. Even a positive capacity-project NPV is not attributable to water resilience unless cooling/water availability is shown to bind capacity expansion. No extra ESG discount-rate adjustment is used.

## Tax and timing controls

The original “No tax relief” sensitivity was misleadingly named: a zero tax rate removes both tax charges and shields. It is now labeled **“No taxes or tax shields.”** Genuine deduction-unavailable cases retain the 25% cash tax on savings/benefits while removing capital allowances or all cost deductions. A separate two-year delayed-deduction case retains tax charges and moves shields later, including tax-only receipts after asset life. All other deductions are assumed usable against other taxable income; no deduction expiry or actual US tax entitlement is asserted.

Cooling capex is paid once at time zero. Commissioning delays move operating cash flows and depreciation, not the initial outlay. The expansion project depreciates infrastructure/cooling over ten years and hardware over two five-year cycles, includes replacement cash spending once, and releases working capital at the end. Zero residual asset value is assumed. Financing flows, delay holding costs, supply-chain water and a whole-company equity bridge remain outside this example.

## Evidence gates and stewardship handoff

| Missing evidence | Decision affected | Proposed verification |
|---|---|---|
| Matched campus/design, water source and delivery contract | Whether a local water problem can affect this workload | Identify counterpart designs and their legal/physical delivery conditions |
| Metered direct-water definitions and realized PUE | Correct quantity, denominator and energy/water trade-off | Match IT load, weather, withdrawal/consumption and administrative use |
| Cooling capex, useful life, replacements and tax treatment | Capital recovery and timing | Obtain cooling-specific bids, lifecycle costs and asset ownership |
| Water-linked events and protected unrecovered contribution | Whether reliability clears the 84.26-hour breakpoint | Review event logs, rerouting/recovery, contractual loss allocation and marginal contribution |
| Incremental demand and water as binding capacity constraint | Whether positive growth value is caused by redesign | Verify customer pricing/utilization, grid permits and all new hardware/infrastructure costs |

The [linked stewardship programme](https://github.com/HHFinAi/Stewardship-and-Controversy-Assessment/blob/main/examples/microsoft-ai/README.md) converts gaps into proposed questions and milestones. No issuer contact, reply or engagement success is represented.

## Reproducibility and review boundary

```bash
python examples/microsoft-ai/model.py --check
python examples/microsoft-ai/claim_checks.py
python -m unittest discover -s tests -p test_microsoft_ai_case.py -v
```

The read-only check compares both the rendered report and machine-readable annual cash flows with committed results. Tests cover physical units, tax charges/shields and timing, benefit breakpoints, replacement spending, double-counting controls, missing issuer data and invalid inputs. They establish arithmetic and explicit controls, not issuer data truth or causal validity. The original contribution is the counterfactual, breakpoints and investment-to-engagement handoff. AI assistance was used; independent human approval and live workflow research approval are not recorded. Publication is not approval to invest. See the separate [evaluation](EVALUATION.md).
