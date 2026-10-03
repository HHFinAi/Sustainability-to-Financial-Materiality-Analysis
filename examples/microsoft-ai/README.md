# Microsoft: what must water-resilient AI infrastructure earn?

**A real-issuer research context with an explicitly illustrative project model. Prepared 4 October 2026.** Financial context is FY2023–FY2025; the engineering disclosure is dated 9 December 2024. The linked stewardship assessment separately reviews Microsoft's 2026 responsible-AI disclosure. This is not a historical backtest, a current Microsoft financial forecast, or a valuation of a disclosed site.

## Research conclusion

**Direct water-bill savings do not justify the reference cooling investment.** The illustrative design needs approximately **$3.16m of additional recurring pre-tax operating benefit per year** to achieve zero incremental NPV at an assumed 8% discount rate. With direct water and energy bills alone, modeled NPV is **−$15.90m**. These results are conditional arithmetic, not evidence that Microsoft's investments destroy value.

The useful investment question is whether reliability, avoided disruption, or profitable capacity enabled by water resilience can clear that hurdle. A design can reduce direct cooling-water demand while increasing electricity use. Neither a lower water metric nor a larger AI capital budget establishes an attractive return.

[Results](RESULTS.md) · [Inputs](inputs.json) · [Model](model.py) · [Evidence register](evidence.json) · [Sources and challenges](SOURCES.md) · [Evaluation](EVALUATION.md) · [Proposed AI stewardship programme](https://github.com/HHFinAi/Stewardship-and-Controversy-Assessment/blob/main/examples/microsoft-ai/README.md)

## What the issuer evidence establishes

Microsoft's December 2024 engineering disclosure describes closed-loop cooling, continued administrative water use, a mixed existing fleet and an energy/PUE trade-off. Its deployment dates were expectations at publication, not confirmed operating results. **MS2 does not supply the project capex, site tariffs or resilience benefits needed to price the investment.** [MS2](SOURCES.md#ms2--engineering-disclosure)

The FY2025 cash-flow statement reports consolidated cash from operations of **$136.162bn** and cash additions to property and equipment of **$64.551bn**, compared with **$118.548bn** and **$44.477bn** in FY2024. The simple CFO-minus-cash-capex residual therefore changes from **$74.071bn to $71.611bn**. This is a calculation from group accounts, not an AI-only cash-flow measure, and not the project model's FCFF. It does not deduct acquisitions, financing-lease principal or an economic charge for stock compensation. [MS1](SOURCES.md#ms1--financial-baseline)

**Inference:** those boundaries matter more than labeling all group capital expenditure as AI investment. The group figures are scale context only; they do not calibrate the hypothetical cooling design.

## Counterfactual and model

Compare two cooling designs serving the **same assumed IT workload**. Hold underlying cloud revenue, IT hardware and non-cooling costs constant. The model measures only incremental cooling capex, avoided direct-water expense, additional electricity, maintenance and simplified cash taxes.

| Reference assumption | Value | Classification |
|---|---:|---|
| IT capacity / average load | 100 MW / 70% | Analyst assumptions; not a Microsoft site |
| Annual operating hours | 8,760 | Constant-load simplification |
| Avoided direct cooling-water intensity | 0.30 L per IT kWh | Scenario input, not a calibrated issuer observation |
| Incremental facility PUE | +0.02 | Analyst assumption |
| Electricity / water price | $80/MWh / $3/m3 | Illustrative tariffs |
| Incremental capex / maintenance | $15m / $0.25m annually | Analyst assumptions |
| Cooling-asset life / discount rate / tax | 10 years / 8% / 25% | Analyst assumptions, not issuer guidance |

All these inputs are editable in [inputs.json](inputs.json). The 0.30 intensity is not treated as verified site data: the wording of MS2's WUE definition and its footnote needs reconciliation before calibration.

Annual IT MWh = capacity × average load × hours. Extra electricity = IT MWh × incremental PUE. Avoided direct water in m3 = IT MWh × avoided litres per IT kWh. That last equality includes both the 1,000 kWh/MWh and 1,000 litres/m3 conversions.

Let **S** be recurring water-bill savings less incremental power and maintenance costs; **B** the additional recurring pre-tax operating benefit; **I** initial incremental capex; **D = I / asset life** annual tax depreciation; and **t** the assumed tax rate.

```text
Incremental annual FCFF = (S + B) × (1 − t) + D × t
Incremental NPV = −I + annual FCFF × discounted operating-year annuity
Break-even B = [I / annuity − D × t] / (1 − t) − S
```

The model assumes all deductions are immediately usable against other taxable income. There is no terminal value, working-capital change, financing flow or separate ESG discount-rate adjustment. Commissioning delays postpone operating cash flow and depreciation, not initial capex. Delay holding costs are excluded. A real case needs asset-specific tax, useful life, replacement spending and residual value.

## What changes the decision?

At the reference workload, avoided direct water is **183,960 m3/year**, but the assumed water saving of **$0.552m** is less than additional electricity cost of **$0.981m**, before maintenance. The model deliberately assigns **zero** unverified avoided-loss or growth benefit initially.

The additional-benefit hurdle rises to **$3.65m/year** at $120/MWh electricity and **$4.08m/year** with 25% higher capex and a one-year commissioning delay. Even $3m of recurring additional pre-tax benefit does not quite clear the reference hurdle. See [the complete sensitivities](RESULTS.md).

**Strongest contrary case:** the reference design may understate resilience or expansion benefits, overstate incremental PUE, or miss lower capital costs. Conversely, a site with reliable low-cost water may have little avoided-loss benefit; delays, operating restrictions or unusable tax shields may worsen economics. These are hypotheses to investigate, not assigned probabilities.

## Evidence gates and stewardship handoff

| Missing evidence | Why it changes underwriting | Proposed next step |
|---|---|---|
| Site-specific direct-water definitions and basin context | A fleet ratio cannot establish local scarcity or availability | Reconcile withdrawal, consumption, water source and operating periods |
| Realized energy trade-off and tariff allocation | Determines who pays and the incremental operating cost | Obtain comparable operating data and contracts for both designs |
| Incremental capex, useful life and replacements | Determines the capital-recovery hurdle | Separate cooling from IT hardware and ordinary expansion |
| Operational or expansion benefit | Determines whether the hurdle can be met | Establish a documented counterfactual; separate protected profit from added capacity |
| Asset ownership, financing and customer terms | Prevents shifting costs or benefits to the wrong entity | Map operator, tenant, supplier and lender cash flows |

The [linked programme](https://github.com/HHFinAi/Stewardship-and-Controversy-Assessment/blob/main/examples/microsoft-ai/README.md) converts these gaps into proposed questions and milestones. No issuer contact, reply or engagement success is represented.

## Contribution, reproducibility and review boundary

The original HHFinAi contribution is the incremental counterfactual, explicit break-even hurdle, unit and double-counting controls, source-scope challenges, and investment-to-engagement handoff. The implementation and narrative were prepared with AI assistance under Ed's portfolio-development brief. Independent human validation and workflow research approval are **not recorded**; publication is not approval to invest.

```bash
python examples/microsoft-ai/model.py --check
python examples/microsoft-ai/claim_checks.py
python -m unittest discover -s tests -p test_microsoft_ai_case.py -v
```

No network or model API is required. Read [what the evaluation does and does not establish](EVALUATION.md). Whole-company valuation, current market evidence and mandate fit remain outside this sample.
