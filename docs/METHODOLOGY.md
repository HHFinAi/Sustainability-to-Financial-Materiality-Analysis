# Methodology and model boundaries

Scenario arithmetic is not a forecast. Financial materiality and impact materiality are separate; no universal ESG premium or automatic ESG score-to-WACC conversion.

## Analytical outputs
- Issue-to-financial-driver map
- Incremental cash-flow bridge and valuation sensitivity
- Separate equity and credit implications
- Catalysts, downside and thesis breakers

## Calculation library
The implementation is in `sf_agent/analytics.py`; generic helpers are in `sf_agent/maths.py`. Every exposed operation has argument-unit and result-unit metadata and is callable with `python -m sf_agent calc`. Arguments are not sourced automatically. See the operation inventory below, the worked example and domain regression tests.

### Financial-materiality calculations
`cashflow_bridge` calculates revenue × ((1+volume shock) × (1+price shock) − 1), incremental EBIT = revenue change × contribution margin − incremental opex, and incremental free cash flow = EBIT change × (1−tax) − incremental capex − incremental working capital. It assumes a constant incremental contribution margin, usable tax effects, no depreciation timing and no second-round responses. Model additions must address these limitations.

`incremental_dcf` discounts annual incremental free cash flows starting in year 1. Optional terminal value is final-year incremental cash flow × (1+g)/(r−g), discounted from year N; r must exceed g. Terminal persistence is an explicit assumption, not evidence. `equity_bridge` subtracts debt and minority claims and adds cash to EV, dividing by positive shares; a negative residual is not floored and is not an equity-option valuation. `scenario_expected_value` requires aligned scenario values and nonnegative probabilities summing to one. Probabilities are supplied, not model-estimated.


## Evidence status
Causal and legal interpretations remain human judgments. The software is not a complete implementation or certification of the referenced standards. Read the exact applicable original documents; the dated source register gives the verification scope. Proposed changes and future validation dates must not be applied retrospectively or represented as current law.
