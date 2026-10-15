# AI infrastructure: reproducible project scenarios

**Original HHFinAi scenario model, 16 October 2026. USD million unless stated.**
Illustrative assumptions; no Microsoft or other issuer's site returns are estimated. Issuer underwriting: **NEEDS_DATA**.

## Decision-relevant results

The grid-now reference NPV is **$175.65m**; gas-now is **$1.29m**. In this assumption set, immediate gas generation first exceeds delayed grid NPV at a **12-month** grid delay (whole-month search within 0-24 months). This ranking assumes immediate gas availability and a fixed horizon with zero hardware resale; replacement boundaries can cause nonmonotonic results outside the displayed range. Gas-now is only narrowly positive, so no investment conclusion is robust to unverified costs.

Both serve an assumed 100 MW IT workload, 70% utilization and PUE 1.15: **705,180 MWh/year**. Grid power costs $56.41m/year; gas fuel, variable and fixed O&M cost $57.95m/year before any scenario carbon charge.

## Commissioning timing and capital recovery

Common calendar end: month 120. Initial infrastructure is committed at month zero; hardware and working capital at commissioning. Delayed projects lose operating months and incur holding costs. The model does not grant every delayed project a fresh ten-year operating life.

| Power | Delay months | NPV | Change vs grid now | Revenue hurdle / utilized MW-year | Holding costs |
|---|---:|---:|---:|---:|---:|
| grid | 0 | 175.65 | +0.00 | 5.719 | 0.00 |
| gas | 0 | 1.29 | -174.35 | 6.196 | 0.00 |
| grid | 6 | 82.00 | -93.65 | 5.958 | 12.00 |
| gas | 6 | -93.46 | -269.11 | 6.476 | 12.00 |
| grid | 12 | -8.12 | -183.77 | 6.226 | 24.00 |
| gas | 12 | -184.64 | -360.29 | 6.788 | 24.00 |
| grid | 24 | -178.27 | -353.92 | 6.867 | 48.00 |
| gas | 24 | -356.81 | -532.45 | 7.534 | 48.00 |

The hurdle is revenue at full utilization per MW-year, multiplied by the assumed utilization to obtain modeled sales. It is not a customer tariff or a reported issuer metric.

## One-factor sensitivities

Each row changes one input; other reference assumptions remain fixed. Changes are relative to the same power route with zero delay. These rows must not be added together.

| Variable | Value | Power | NPV | Change vs route reference |
|---|---:|---|---:|---:|
| Hardware life | 36 | grid | -570.55 | -746.20 |
| Hardware life | 60 | grid | 175.65 | +0.00 |
| Hardware life | 84 | grid | 196.18 | +20.53 |
| Grid delivered power | 60 | grid | 249.19 | +73.54 |
| Grid delivered power | 80 | grid | 175.65 | +0.00 |
| Grid delivered power | 120 | grid | 28.35 | -147.30 |
| Gas fuel | 4 | gas | 67.57 | +66.28 |
| Gas fuel | 6 | gas | 1.29 | +0.00 |
| Gas fuel | 10 | gas | -131.33 | -132.62 |
| Hypothetical carbon cost | 0 | gas | 1.29 | +0.00 |
| Hypothetical carbon cost | 50 | gas | -90.81 | -92.10 |
| Hypothetical carbon cost | 100 | gas | -182.90 | -184.20 |
| Building sale fraction | 0 | grid | 138.59 | -37.06 |
| Building sale fraction | 0.2 | grid | 175.65 | +0.00 |
| Building sale fraction | 0.4 | grid | 212.70 | +37.06 |
| One incident: outage hours | 0 | grid | 175.65 | +0.00 |
| One incident: outage hours | 4 | grid | 174.29 | -1.36 |
| One incident: outage hours | 24 | grid | 173.43 | -2.21 |
| One incident: outage hours | 72 | grid | 171.39 | -4.26 |
| Utilization | 0.5 | grid | -386.56 | -562.20 |
| Utilization | 0.7 | grid | 175.65 | +0.00 |
| Utilization | 0.9 | grid | 736.87 | +561.22 |

Hardware-life scenarios change the economic cash replacement schedule while keeping the assumed tax-allowance life at 60 months. Tax deductions stop when equipment is disposed; no tax credit for an unrecovered basis is assumed. Accounting lives, tax allowances and economic replacement cycles are distinct.

## Hardware horizon and residual-value challenge

A fixed endpoint can penalize a recent replacement. The following recovery fractions apply to the final vintage's cost multiplied by its remaining economic-life fraction; they are not market resale observations. Any gain above tax basis is taxed. Earlier replaced vintages receive zero resale in every case.

| Economic life months | Terminal recovery fraction | NPV |
|---:|---:|---:|
| 36 | 0% | -570.55 |
| 36 | 50% | -477.92 |
| 36 | 100% | -385.28 |
| 60 | 0% | 175.65 |
| 60 | 50% | 175.65 |
| 60 | 100% | 175.65 |
| 84 | 0% | 196.18 |
| 84 | 50% | 275.58 |
| 84 | 100% | 343.07 |

Replacement schedules create discontinuities outside the displayed delay range: moving a purchase beyond the common endpoint can increase modeled NPV even with a longer delay. The reported 0-24-month crossing is not a universal or monotone break-even rule. Use a longer horizon and independently supported resale/continuation values before underwriting an actual investment.

The incident is a single conditional event in month 36, not an annual frequency. Lost sales remove the recoverable workload fraction; variable power savings, service credits and recovery spending are separate. No probability is inferred from industry surveys. A carbon-cost row is a hypothetical cost stress, not a claim that a jurisdiction imposes that price.

## Conditional cancellation before hardware commitment

| Month | Recovery of committed non-land infrastructure | Gross recovery | NPV |
|---:|---:|---:|---:|
| 12 | 0% | 20.00 | -588.03 |
| 12 | 30% | 183.50 | -436.64 |
| 12 | 60% | 347.00 | -285.25 |

Cancellation assumes a $20m exit cost, land recovery at its assumed sale fraction, and no tax-loss credit. No hardware or working capital is committed. This is distinct from retiring an operating site, and it does not estimate Caledonia's actual sunk costs.

## Boundaries and reproduction

Positive project NPV does not establish stock upside. A calibrated issuer bridge requires site ownership, incremental demand, contracts, tax treatment, financing/lease recourse and the number of affected projects; market pricing and consensus are not modeled. No ESG discount-rate adjustment is added.

Cash taxes apply only to positive monthly taxable income; no loss carryforward/refund is assumed. Capital allowances are simplified straight-line assumptions, not tax advice. Land/building/hardware disposal gains are taxed if above remaining basis; disposal losses receive no assumed relief. Cash flows are constant purchasing-power dollars, discounted at an assumed real 8%; no inflation, terminal multiple or grid-backup credit is included.

```bash
python examples/ai-infrastructure/model.py --check
python -m unittest discover -s tests -p test_ai_infrastructure.py -v
```

[Investment memo](README.md) · [Assumptions](inputs.json) · [Monthly cash flows](results.json) · [Methods](METHODS.md) · [Primary evidence](evidence/PROJECT_TRACKER.md)
