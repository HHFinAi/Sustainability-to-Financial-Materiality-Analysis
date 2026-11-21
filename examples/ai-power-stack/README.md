# AI Power Stack: a common-horizon power choice for a hypothetical AI campus

**Original HHFinAi extension · 21 November 2026 · ILLUSTRATIVE model · Issuer/site underwriting: NEEDS_DATA.**

This adds a third, *solid-oxide fuel-cell (SOFC)* route to the existing October 16
[grid-versus-gas research case](../ai-infrastructure/README.md).
The model reuses the original 120-month, 100-MW IT workload engine instead of
forking it: its cash tax, hardware replacement, initial/terminal capital,
working capital, constant-USD discounting and fixed calendar horizon are
identical. No October input or result is edited.

## Question and counterfactual

Under a *single campus-owner economic boundary*, what changes if grid, gas or
SOFC infrastructure commissions 0, 6, 12 or 18 months after project start?
Compare net present value against the **grid route with a 12-month delay**,
not against an undisclosed reference. The user can edit the delay and
technology assumptions in [inputs.json](inputs.json).

The SOFC route is an explicitly labelled **parameterization of the baseline
owned-gas generator route**, not a manufacturer-specific quote, proprietary
fuel-cell physics simulator or actual Bloom Energy (BE) installation.
The SOFC numerical inputs (capital, heat rate, emissions, service/stack reserve
and capacity factor) are hypothetical HHFinAi analyst assumptions. We do *not*
import bank estimates as source data, and no 45Q tax credit or CCS benefit is
assumed.

## Capacity check and reliability limitation

IT load is 100 MW; PUE is 1.15; the screening peak is **115 MW**.
Each route supplies assumed *rated MW × availability factor*. Below 115 MW,
the model reports \`BLOCKED_INSUFFICIENT_CAPACITY\` and suppresses NPV.

**Do not interpret this as an N-1, reliability, uptime or firm-power certification.**
Actual capacity adequacy requires outage distributions, correlated failures,
interconnections, backup reserves and hourly dispatch. Those are **NEEDS_DATA**.
Similarly, SOFC stack replacement costs are represented only by a simplified
annual fixed O&M/service allowance; there is no explicit replacement schedule.

## Reproduce

From the Financial Materiality repository root:

~~~bash
python examples/ai-power-stack/model.py --check
python examples/ai-power-stack/model.py > /tmp/ai-power-stack.json
python examples/ai-power-stack/model.py --write
python -m unittest tests.test_ai_power_stack -v
~~~

The optional \`--write\` generates \`results.json\` locally; it does not fetch
new inputs or change the prior October research. Tests validate deterministic
economic invariants, *not* issuer contracts, physical plant performance or alpha.

## Source and investment boundaries

Research prompts: Morgan Stanley, *Clean Tech & Data Center Infrastructure –
SF Bus Tour Roundup*, 19 November 2026 (Bloom, Equinix, Pacific Fusion,
Redwood Materials). These insights motivate questions about time-to-power,
manufacturing scale and hybrid architectures, but **no proprietary report,
chart, benchmark or copied passage is included or redistributed**.
Independent public, dated issuer evidence is required to populate a real case.

Before ranking listed equities, obtain EPC/equipment bids, service/stack
replacement warranties, gas and interconnection terms, delivery milestones,
permitting, realistic availability profiles, load contracts and capital-owner
allocation. Grid/gas paths inherit assumptions from the original illustrative
case. The report does not provide enough verified data for an issuer-level DCF.

**Next implementation gate:** hourly solar/storage/backup dispatch to separate
energy adequacy from firm-power reliability, then an independent BE/EQIX
company-to-equity valuation bridge. Do not add a battery arbitrage NPV to
this after-tax project NPV without first reconciling basis, ownership and
cash-flow overlap.
