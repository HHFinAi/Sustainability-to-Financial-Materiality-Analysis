# Worked example — Sustainability-to-Financial-Materiality Analysis Agent

**SYNTHETIC / RESEARCH_ONLY. All company, portfolio, instrument and outcome values are fictional. No capital should be deployed from this example.**

## Investment-relevant observation
The scenario reduces annual free cash flow by **USD 3.609 million**. Revenue declines by USD 2.030 million; incremental EBIT declines by USD 1.812 million. At a 25% usable tax rate, the operating cash-flow effect is USD −1.359 million, before USD 2 million incremental capex and USD 250,000 working capital.

## Reproduce the arithmetic
From the repository root:
```bash
python -m sf_agent calc --operation cashflow_bridge --arguments examples/calculation-arguments.json
```

### Inputs
```json
{
  "revenue": 100000000,
  "volume_change": -0.03,
  "price_change": 0.01,
  "contribution_margin": 0.4,
  "incremental_opex": 1000000,
  "incremental_capex": 2000000,
  "incremental_working_capital": 250000,
  "tax_rate": 0.25
}
```

### Recomputed result
```json
{
  "revenue_change": -2029999.9999999984,
  "ebit_change": -1811999.9999999995,
  "after_tax_operating_change": -1358999.9999999995,
  "free_cashflow_change": -3608999.9999999995
}
```

## What the result does not establish
This is a one-period stress, not an issuer forecast or target price. Before acting, reconcile the baseline model, identify price pass-through and tax usability, specify financing and terminal effects, obtain current market evidence and apply the mandate.

## Diligence handoff
Fictional industrial issuer: stress supply disruption and energy costs without adding a separate unexplained ESG discount-rate penalty.

Register source-backed inputs, contrary evidence, material data gaps and the investment constraints before replacing this illustrative result with actual research. Unit, boundary, timing, attribution and legal judgments are not supplied by arithmetic alone. No human research approval is recorded for this example.
