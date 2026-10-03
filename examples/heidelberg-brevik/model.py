"""Reproduce a bounded real-issuer sensitivity; Python standard library only.

All amounts returned are EUR million except explicitly labelled tonnes/ratios.
Inputs separate reported evidence, management expectations and assumptions.
This model does not fetch evidence, approve research or value the whole issuer.
"""
from __future__ import annotations

import argparse
import csv
from datetime import date
import io
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def load_inputs():
    return json.loads((ROOT / "inputs.json").read_text(encoding="utf-8"))


def project(data, scenario, *, premium=None, net_opex=None, discount_rate=None):
    common = data["common_assumptions"]
    plan = data["management_expectations"]
    s = data["scenarios"][scenario]
    r = common["discount_rate"] if discount_rate is None else discount_rate
    p = s["incremental_premium_eur_per_cement_tonne"] if premium is None else premium
    o = s["net_ccs_opex_eur_per_captured_tonne"] if net_opex is None else net_opex
    if not (-1 < r) or not (0 <= s["realization_fraction"] <= 1):
        raise ValueError("Invalid discount rate or realization fraction")
    capacity = data["facts"]["capture_capacity_tonnes_per_year"]["value"]
    valuation_date = date.fromisoformat(data["valuation_date"])
    previous_wc = common["opening_premium_working_capital_eur_m"]
    rows = []
    for year, planned_volume, carbon_price in zip(
        plan["years"], plan["brevik_evozero_cement_tonnes"],
        plan["carbon_price_eur_per_tonne"], strict=True
    ):
        cement = planned_volume * s["realization_fraction"]
        capture = min(capacity, capacity * cement / common["capture_scaling_cement_tonnes"])
        premium_revenue = cement * p / 1e6
        carbon_cash = capture * carbon_price * s["retained_carbon_cash_fraction"] / 1e6
        cash_opex = capture * o / 1e6
        operating_surplus = premium_revenue + carbon_cash - cash_opex
        cash_tax = max(0, operating_surplus) * common["cash_tax_rate"]
        wc = premium_revenue * common["premium_revenue_working_capital_fraction"]
        delta_wc = wc - previous_wc
        previous_wc = wc
        capex = common["annual_incremental_capex_eur_m"]
        fcf = operating_surplus - cash_tax - capex - delta_wc
        years = (date(year, 12, 31) - valuation_date).days / 365.25
        if years <= 0:
            raise ValueError("Every cash flow must occur after the valuation date")
        rows.append(dict(
            scenario=scenario, year=year, cement_tonnes=cement,
            captured_tonnes=capture, premium_revenue_eur_m=premium_revenue,
            retained_carbon_cash_eur_m=carbon_cash, net_ccs_opex_eur_m=cash_opex,
            operating_surplus_eur_m=operating_surplus, cash_tax_eur_m=cash_tax,
            incremental_capex_eur_m=capex, delta_working_capital_eur_m=delta_wc,
            incremental_fcf_eur_m=fcf, years_from_valuation=years,
            present_value_eur_m=fcf / (1 + r) ** years,
        ))
    return rows


def window_pv(data, scenario, **kwargs):
    return sum(row["present_value_eur_m"] for row in project(data, scenario, **kwargs))


def break_even_premium(data, scenario, **kwargs):
    """Minimum non-negative premium giving non-negative five-year PV; not IRR."""
    if window_pv(data, scenario, premium=0, **kwargs) >= 0:
        return 0.0
    low, high = 0.0, 1000.0
    if window_pv(data, scenario, premium=high, **kwargs) < 0:
        raise ValueError("No premium break-even within the search range")
    for _ in range(80):
        middle = (low + high) / 2
        if window_pv(data, scenario, premium=middle, **kwargs) >= 0:
            high = middle
        else:
            low = middle
    return (low + high) / 2


def csv_text(rows):
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=list(rows[0]), lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow({key: round(value, 8) if isinstance(value, float) else value for key, value in row.items()})
    return output.getvalue()


def outputs(data):
    all_rows, summaries = [], []
    denominator = data["facts"]["group_fcf_2025_eur_m"]["value"]
    for name in data["scenarios"]:
        rows = project(data, name)
        all_rows.extend(rows)
        summaries.append(dict(
            scenario=name, window_pv_eur_m=sum(r["present_value_eur_m"] for r in rows),
            fcf_2026_eur_m=rows[0]["incremental_fcf_eur_m"],
            fcf_2030_eur_m=rows[-1]["incremental_fcf_eur_m"],
            fcf_2030_pct_of_reported_group_2025_fcf=100 * rows[-1]["incremental_fcf_eur_m"] / denominator,
            break_even_premium_eur_per_cement_tonne=break_even_premium(data, name),
        ))
    grid = [dict(premium_eur_per_cement_tonne=p, net_ccs_opex_eur_per_captured_tonne=o,
                 window_pv_eur_m=window_pv(data, "central_sensitivity", premium=p, net_opex=o))
            for o in data["sensitivity_grid"]["net_ccs_opex_eur_per_captured_tonne"]
            for p in data["sensitivity_grid"]["premium_eur_per_cement_tonne"]]
    rate_grid = [dict(discount_rate=r, window_pv_eur_m=window_pv(data, "central_sensitivity", discount_rate=r))
                 for r in data["sensitivity_grid"]["discount_rates"]]
    lines = ["# Recomputed results", "", "Generated by `python examples/heidelberg-brevik/model.py`. All scenarios are conditional analyst sensitivities.", "",
             "| Scenario | 2026 incremental FCF (€m) | 2030 incremental FCF (€m) | 2026–30 PV (€m) | 2030 / FY2025 reported group FCF | Break-even premium (€/t cement) |",
             "|---|---:|---:|---:|---:|---:|"]
    for s in summaries:
        lines.append(f"| {s['scenario']} | {s['fcf_2026_eur_m']:.2f} | {s['fcf_2030_eur_m']:.2f} | {s['window_pv_eur_m']:.2f} | {s['fcf_2030_pct_of_reported_group_2025_fcf']:.2f}% | {s['break_even_premium_eur_per_cement_tonne']:.2f} |")
    lines += ["", "PV is discounted to 25 February 2026. It excludes terminal value and original construction expenditure; it is neither total project NPV nor issuer fair value. A zero premium hurdle means no premium is required for non-negative PV under that scenario; it does not mean PV itself is zero.", "", "## Central annual cash bridge (€m)", "",
              "| Year | Premium revenue | Retained carbon cash | Net CCS opex | Cash tax | Capex | Change in working capital | Incremental FCF |",
              "|---|---:|---:|---:|---:|---:|---:|---:|"]
    for row in project(data, "central_sensitivity"):
        keys = ["premium_revenue_eur_m", "retained_carbon_cash_eur_m", "net_ccs_opex_eur_m", "cash_tax_eur_m", "incremental_capex_eur_m", "delta_working_capital_eur_m", "incremental_fcf_eur_m"]
        lines.append(f"| {row['year']} | " + " | ".join(f"{row[k]:.2f}" for k in keys) + " |")
    lines += ["", "## Premium × uncovered operating cost: five-year PV (€m)", "", "All other central inputs remain fixed; columns are incremental premium per tonne of cement and rows are net CCS opex per tonne captured.", "",
              "| Net CCS opex | €20 premium | €40 premium | €60 premium | €80 premium | €100 premium |", "|---|---:|---:|---:|---:|---:|"]
    for o in data["sensitivity_grid"]["net_ccs_opex_eur_per_captured_tonne"]:
        lines.append(f"| €{o} | " + " | ".join(f"{g['window_pv_eur_m']:.2f}" for g in grid if g["net_ccs_opex_eur_per_captured_tonne"] == o) + " |")
    lines += ["", "## Discount-rate sensitivity", "", "| Analyst discount rate | Central five-year PV (€m) |", "|---|---:|"]
    lines += [f"| {r['discount_rate']:.0%} | {r['window_pv_eur_m']:.2f} |" for r in rate_grid]
    lines += ["", f"Setting the retained carbon cash fraction to zero (all other central inputs unchanged) gives a break-even premium of €{break_even_with_no_carbon(data):.2f}/t cement.", ""]
    return {"annual-cashflows.csv": csv_text(all_rows), "scenario-results.csv": csv_text(summaries),
            "sensitivity-results.csv": csv_text(grid), "RESULTS.md": "\n".join(lines)}


def break_even_with_no_carbon(data):
    from copy import deepcopy
    altered = deepcopy(data)
    altered["scenarios"]["central_sensitivity"]["retained_carbon_cash_fraction"] = 0
    return break_even_premium(altered, "central_sensitivity")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail if committed outputs differ; do not write")
    args = parser.parse_args()
    generated = outputs(load_inputs())
    for filename, content in generated.items():
        path = ROOT / filename
        if args.check:
            if not path.is_file() or path.read_text(encoding="utf-8") != content:
                raise SystemExit(f"Stale or missing result: {path.name}")
        else:
            path.write_text(content, encoding="utf-8")
    print("PASS: Brevik calculations reproduce" if args.check else "Wrote four Brevik result files")


if __name__ == "__main__":
    main()
