# AI infrastructure: when does earlier capacity justify extra capital?

**Original HHFinAi research | 16 October 2026 | Primary-source issuer evidence plus an illustrative financial model.**

**Research judgment: underwrite the delivery advantage and who pays for it.** Earlier commissioning can justify expensive power infrastructure, but the value disappears if the alternative also waits, demand cannot fill the capacity, or hardware replacement consumes the return. This case supports **further project diligence**, not a Microsoft stock recommendation. No mispricing or market-implied expectation is established.

[Financial sensitivities](RESULTS.md) · [Primary-data analysis](public-data/RESULTS.md) · [Project/policy tracker](evidence/PROJECT_TRACKER.md) · [Source challenges](SOURCE_CHALLENGES.md) · [Methods and ownership](METHODS.md) · [What changed](UPDATE_2026-10-16.md)

## Three findings to investigate

1. **Speed can be worth more than the electricity-price difference.** In a hypothetical 100 MW case, grid-now NPV is **$175.65m** and gas-now NPV **$1.29m**. A 12-month grid delay produces **-$8.12m**, while delaying the gas case six months produces **-$93.46m**. Immediate gas first exceeds delayed grid in the 12th month of the 0-24-month comparison. The result is conditional on assumptions, fixed horizon and residual values; a narrow positive NPV is not an investment margin of safety. [Reproducible model](model.py), [inputs](inputs.json).
2. **A company can have operating, prospective and abandoned projects simultaneously.** Microsoft's June 2026 release reports its first Mount Pleasant facility operational and the second under construction; its October 2025 Caledonia update says it would not proceed with that site. These observations support separate operating, delay and cancellation questions. They supply neither a cancellation probability nor site profitability. [Dated source register](evidence/sources.json), IDs MS-MP-20260623 and MS-CALEDONIA-20251010.
3. **Regional power inflation is an exposure screen.** Our calculation from EIA's consistent annual observations gives 2020-2025 price CAGR of **5.07% nationally**, **4.85% in Virginia** and **3.59% in Texas**. Customer mix and other determinants remain unresolved; the figures cannot identify a data-center demand effect or price an individual utility contract. [Calculation and source cells](public-data/RESULTS.md).

## What the primary evidence changes

Microsoft's Wisconsin disclosure describes a mixed cooling design and infrastructure prepayment; neither establishes measured savings or the price and recourse terms of a utility contract. Its Atlanta architecture describes a two-storey layout and grid resilience substituting for traditional backup arrangements for the GPU fleet. That is a useful counterexample to assuming every AI campus needs the same building or captive-power design. [Sources](evidence/sources.json): MS-WI-DESIGN-20250918; MS-ATL-20251112.

The policy register reads the actual Texas letter and New York executive order. It distinguishes scope, application status, thresholds and release conditions. Neither policy is applied to the Wisconsin/Georgia projects in this tracker. A power-source choice does not by itself establish a permit exemption. [Policy records](evidence/policies.json).

## The counterfactual

Compare the **same assumed workload** served by grid electricity or dedicated gas generation over a **common 120-month calendar opportunity**. Facility capex is committed at month zero. Hardware and working capital are paid at commissioning. Delay reduces operating time and adds holding costs. Hardware replacement, separate tax-allowance lives, asset recovery, retirement costs and a conditional operational incident are explicit. The hypothetical gas route is **not attributed to a Microsoft campus**.

All project economics are analyst assumptions. Source facts remain in separate evidence files and do not silently populate the model. The [original water-resilience case](../microsoft-ai/README.md) and its October 4/8 results remain intact.

## What would change the assessment?

| Evidence | Model consequence | Research response |
|---|---|---|
| Binding, affordable power and delivery terms | Replace price, capital allocation and commissioning assumptions | Recalculate route ranking and return hurdle |
| Customer commitments and genuinely incremental demand | Replace utilization, revenue and recovery assumptions | Test whether capacity earns an adequate return |
| Scoped permits and completion milestones | Revise delay/cancellation branches | Re-underwrite the specific phase, not every campus |
| Equipment economics and resale evidence | Replace replacement cycles and terminal values | Challenge capital recovery across a longer horizon |
| Responsibility for outages, credits and recovery | Allocate conditional losses to the right counterparty | Update the affected cash-flow line only |

## Contrary case and valuation boundary

Reliable grid supply, workload flexibility and strong customer commitments could make expensive local generation unnecessary. Conversely, a genuinely scarce delivery window may justify it. We have not verified the contracts needed to choose either conclusion for Microsoft.

The [issuer-scale illustration](ISSUER_SCALE.md) uses dated consolidated financials and actual shares only to show scale. It is not a whole-company DCF, share-price target or claim of upside. Ownership, lease financing, displaced demand and current market expectations remain open. Proposed engagement questions are available in the [stewardship handoff](https://github.com/HHFinAi/Stewardship-and-Controversy-Assessment/tree/main/examples/ai-infrastructure); no contact or issuer response is claimed.

Supporting notes define [water and land evidence gates](https://github.com/HHFinAi/Nature-and-Biodiversity-Investment-Agent/tree/main/examples/ai-infrastructure), [asset-life and transition-plan questions](https://github.com/HHFinAi/Transition-Plan-Credibility-Assessment/tree/main/examples/ai-infrastructure), and [climate mechanisms with equity/credit boundaries](https://github.com/HHFinAi/climate-investment-ai-agent-in-equity-and-bond-markets/tree/main/examples/ai-infrastructure).

## Reproduce and inspect

```bash
python examples/ai-infrastructure/model.py --check
python examples/ai-infrastructure/public-data/analysis.py --check
python examples/ai-infrastructure/check_case.py
python -m unittest discover -s tests -p test_ai_infrastructure.py -v
```

Python 3.10+ standard library; no network needed for frozen-data calculations. [Open issues](open_issues.json) and [validation scope](VALIDATION.md) distinguish arithmetic completion from issuer underwriting. AI assistance was used; no independent human approval, measured research productivity or investment alpha is claimed. Original analysis and code are published; no third-party research report, chart or proprietary universe is reproduced.
