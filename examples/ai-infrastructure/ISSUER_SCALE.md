# How large is the project effect at issuer scale?

**Scale illustration only; not estimated Microsoft equity value or a stock target.** Prepared 16 October 2026.

The FY2026 consolidated source reports CFO of **$182,935m** and cash PP&E additions of **$115,948m**. Their difference is **$66,987m**. The cover reports **7,425,545,491 actual common shares on July 23, 2026**. These are dated group figures, not AI-only cash flows, current shares or the diluted EPS denominator. [Primary register](evidence/sources.json), MS-10K-FY2026; [typed metrics and locators](evidence/issuer_context.json).

The illustrative grid project's 12-month delay changes after-tax unlevered NPV by **$-183.77m** relative to immediate commissioning. Dividing by 7,425.545491 million dated shares gives **$-0.02475/share** for one hypothetical project. This division supplies scale; it does not establish a change in fair value.

| Hypothetical identical affected projects | Aggregate modeled NPV change, USDm | Change divided by dated shares, USD/share |
|---:|---:|---:|
| 1 | -183.77 | -0.02475 |
| 5 | -918.83 | -0.12374 |
| 10 | -1837.65 | -0.24748 |

The project counts are scenario choices. They are not derived from the six tracker records, which are neither a complete pipeline nor six verified unique campuses. Linear multiplication assumes independent identical project economics and no group capacity constraints, offsets, cannibalization or financing interaction.

## Evidence required for a genuine equity bridge

1. Verify which entity owns each asset, receives incremental cash flow and bears capex/leases/retirement obligations.
2. Replace hypothetical prices, utilization, timing, costs and real-dollar tax simplifications with issuer-specific economics.
3. Reconcile project financing, lease liabilities, tax capacity and any debt/ownership effects with group equity value; avoid deducting the same capex twice.
4. Identify affected project scale, displaced capacity and interactions with other investments.
5. Use a whole-company valuation, current shares, market price and consensus to determine whether the change is material and already reflected in expectations.

No market mispricing, target price or portfolio action is inferred. The group CFO-minus-cash-PP&E residual excludes other adjustments such as lease principal, acquisitions and an economic stock-compensation charge. We do not divide project NPV by annual CFO and label the result a cash-flow margin or return.

```bash
python examples/ai-infrastructure/issuer_scale.py --check
```
