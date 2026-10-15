"""Bounded project-to-issuer scale arithmetic; never a share-price target."""
import argparse
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def render():
    evidence = json.loads((HERE / "evidence/issuer_context.json").read_text())
    model = json.loads((HERE / "results.json").read_text())
    m = evidence["metrics"]
    shares = m["common_shares_outstanding"]["value"] / 1e6
    if m["common_shares_outstanding"]["unit"] != "shares" or shares <= 0:
        raise ValueError("Actual share denominator and units required")
    cfo = m["cash_from_operations"]["value"]
    capex = m["cash_property_equipment_additions"]["value"]
    if cfo - capex != m["cfo_less_cash_property_equipment_additions"]["value"]:
        raise ValueError("Issuer cash-flow arithmetic mismatch")
    base = model["reference_grid"]["npv_m"]
    delayed = next(x for x in model["timing_scenarios"] if x["power"] == "grid" and x["delay_months"] == 12)["npv_m"]
    delta = delayed - base
    lines = ["# How large is the project effect at issuer scale?", "",
             "**Scale illustration only; not estimated Microsoft equity value or a stock target.** Prepared 16 October 2026.", "",
             f"The FY2026 consolidated source reports CFO of **${cfo:,.0f}m** and cash PP&E additions of **${capex:,.0f}m**. Their difference is **${cfo-capex:,.0f}m**. The cover reports **{m['common_shares_outstanding']['value']:,.0f} actual common shares on July 23, 2026**. These are dated group figures, not AI-only cash flows, current shares or the diluted EPS denominator. [Primary register](evidence/sources.json), MS-10K-FY2026; [typed metrics and locators](evidence/issuer_context.json).", "",
             f"The illustrative grid project's 12-month delay changes after-tax unlevered NPV by **${delta:.2f}m** relative to immediate commissioning. Dividing by {shares:,.6f} million dated shares gives **${delta/shares:.5f}/share** for one hypothetical project. This division supplies scale; it does not establish a change in fair value.", "",
             "| Hypothetical identical affected projects | Aggregate modeled NPV change, USDm | Change divided by dated shares, USD/share |", "|---:|---:|---:|"]
    for n in (1, 5, 10):
        lines.append(f"| {n} | {n*delta:.2f} | {n*delta/shares:.5f} |")
    lines += ["", "The project counts are scenario choices. They are not derived from the six tracker records, which are neither a complete pipeline nor six verified unique campuses. Linear multiplication assumes independent identical project economics and no group capacity constraints, offsets, cannibalization or financing interaction.", "",
              "## Evidence required for a genuine equity bridge", "",
              "1. Verify which entity owns each asset, receives incremental cash flow and bears capex/leases/retirement obligations.",
              "2. Replace hypothetical prices, utilization, timing, costs and real-dollar tax simplifications with issuer-specific economics.",
              "3. Reconcile project financing, lease liabilities, tax capacity and any debt/ownership effects with group equity value; avoid deducting the same capex twice.",
              "4. Identify affected project scale, displaced capacity and interactions with other investments.",
              "5. Use a whole-company valuation, current shares, market price and consensus to determine whether the change is material and already reflected in expectations.", "",
              "No market mispricing, target price or portfolio action is inferred. The group CFO-minus-cash-PP&E residual excludes other adjustments such as lease principal, acquisitions and an economic stock-compensation charge. We do not divide project NPV by annual CFO and label the result a cash-flow margin or return.", "",
              "```bash", "python examples/ai-infrastructure/issuer_scale.py --check", "```"]
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    text = render()
    target = HERE / "ISSUER_SCALE.md"
    if args.write:
        target.write_text(text)
    elif args.check:
        if not target.exists() or target.read_text() != text:
            raise SystemExit("FAIL: issuer scale table is stale; investigate before --write")
        print("PASS: dated denominator and hypothetical scaling; no equity target claimed")
    else:
        print(text)
