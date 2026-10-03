"""Incremental cooling economics; all project inputs are explicit analyst assumptions.

No network, model API, market feed or issuer loss forecast. Python 3.10+ standard
library. Run with --check to verify the checked-in results without writing files.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
NUMERIC = (
    "it_capacity_mw", "average_it_load_fraction", "hours_per_year",
    "avoided_cooling_water_l_per_it_kwh", "incremental_pue",
    "electricity_usd_per_mwh", "water_usd_per_m3", "incremental_capex_usd_m",
    "incremental_maintenance_usd_m_per_year", "asset_life_years",
    "discount_rate", "cash_tax_rate", "commissioning_delay_years",
    "capex_overrun_fraction", "additional_operating_benefit_usd_m_per_year",
)


def validate(p: dict[str, Any]) -> None:
    if p.get("classification") != "ANALYST_ASSUMPTIONS_NOT_ISSUER_GUIDANCE":
        raise ValueError("Project inputs must remain labelled analyst assumptions")
    if p.get("currency") != "USD" or p.get("money_unit") != "million":
        raise ValueError("This model requires USD million monetary inputs")
    for key in NUMERIC:
        value = p.get(key)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"Missing or nonnumeric input: {key}")
        if not math.isfinite(value) or value < 0:
            raise ValueError(f"Input must be finite and nonnegative: {key}")
    if not 0 < p["average_it_load_fraction"] <= 1:
        raise ValueError("Average IT load must lie in (0, 1]")
    if p["it_capacity_mw"] <= 0 or not 0 < p["hours_per_year"] <= 8784:
        raise ValueError("Invalid capacity or hours")
    if not 0 <= p["cash_tax_rate"] < 1:
        raise ValueError("Tax rate must lie in [0, 1)")
    if not 0 <= p["discount_rate"] <= 1:
        raise ValueError("Discount rate outside supported [0, 1] range")
    for key, minimum, maximum in (("asset_life_years", 1, 100),
                                  ("commissioning_delay_years", 0, 100)):
        if not isinstance(p[key], int) or not minimum <= p[key] <= maximum:
            raise ValueError(f"Invalid integer input: {key}")
    if p["incremental_capex_usd_m"] <= 0:
        raise ValueError("Positive incremental capex required")


def calculate(p: dict[str, Any]) -> dict[str, float]:
    validate(p)
    it_mwh = p["it_capacity_mw"] * p["average_it_load_fraction"] * p["hours_per_year"]
    extra_mwh = it_mwh * p["incremental_pue"]
    # MWh * 1000 kWh/MWh * litres/kWh / 1000 litres/m3.
    water_m3 = it_mwh * p["avoided_cooling_water_l_per_it_kwh"]
    power_cost = extra_mwh * p["electricity_usd_per_mwh"] / 1_000_000
    water_saving = water_m3 * p["water_usd_per_m3"] / 1_000_000
    operating_delta = water_saving - power_cost - p["incremental_maintenance_usd_m_per_year"]
    capex = p["incremental_capex_usd_m"] * (1 + p["capex_overrun_fraction"])
    depreciation = capex / p["asset_life_years"]
    tax = p["cash_tax_rate"]
    benefit = p["additional_operating_benefit_usd_m_per_year"]
    annual_fcf = (operating_delta + benefit) * (1 - tax) + depreciation * tax
    annuity = sum((1 + p["discount_rate"]) ** -(year + p["commissioning_delay_years"])
                  for year in range(1, p["asset_life_years"] + 1))
    hurdle = (capex / annuity - depreciation * tax) / (1 - tax) - operating_delta
    return {
        "it_mwh_per_year": it_mwh,
        "extra_electricity_mwh_per_year": extra_mwh,
        "avoided_direct_water_m3_per_year": water_m3,
        "extra_power_cost_usd_m_per_year": power_cost,
        "water_bill_saving_usd_m_per_year": water_saving,
        "direct_operating_delta_usd_m_per_year": operating_delta,
        "capex_usd_m": capex,
        "annual_incremental_fcf_usd_m": annual_fcf,
        "annuity_factor": annuity,
        "incremental_npv_usd_m": -capex + annual_fcf * annuity,
        "break_even_additional_pretax_benefit_usd_m_per_year": hurdle,
    }


def render(p: dict[str, Any]) -> str:
    cases = [
        ("Reference: direct bills only", {}),
        ("Additional benefit $3m/year", {"additional_operating_benefit_usd_m_per_year": 3.0}),
        ("Electricity $120/MWh", {"electricity_usd_per_mwh": 120.0}),
        ("Water $5/m3", {"water_usd_per_m3": 5.0}),
        ("Incremental PUE 0.04", {"incremental_pue": 0.04}),
        ("Capex +25%; commissioning +1 year", {"capex_overrun_fraction": 0.25, "commissioning_delay_years": 1}),
        ("No tax relief", {"cash_tax_rate": 0.0}),
    ]
    r = calculate(p)
    lines = ["# Cooling investment: reproducible sensitivities", "",
             "**Illustrative project arithmetic, not a Microsoft site forecast or share-price valuation.**",
             "All monetary values below are USD million unless stated otherwise.", "",
             f"Annual IT electricity: {r['it_mwh_per_year']:,.0f} MWh. Additional electricity: {r['extra_electricity_mwh_per_year']:,.0f} MWh.",
             f"Assumed avoided direct cooling water: {r['avoided_direct_water_m3_per_year']:,.0f} m3/year.",
             f"Water bill saving: {r['water_bill_saving_usd_m_per_year']:.6f}; additional electricity cost: {r['extra_power_cost_usd_m_per_year']:.6f} per year.",
             "", "| Scenario | Annual incremental FCF | NPV | Break-even additional pre-tax benefit/year |",
             "|---|---:|---:|---:|"]
    for name, overrides in cases:
        out = calculate({**p, **overrides})
        lines.append(f"| {name} | {out['annual_incremental_fcf_usd_m']:.4f} | {out['incremental_npv_usd_m']:.4f} | {out['break_even_additional_pretax_benefit_usd_m_per_year']:.4f} |")
    lines += ["", "Each row changes only the stated reference inputs. The hurdle is the total recurring additional pre-tax operating benefit needed for zero NPV, not an extra amount on top of any assumed benefit.",
              "Tax relief assumes immediately usable deductions; the no-tax row removes both tax charges and shields. Commissioning delay postpones operating flows and depreciation, but not initial capex. No delay holding costs are modeled.",
              "", "[Investment memo](README.md) · [Inputs and assumptions](inputs.json) · [Calculation](model.py)", ""]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inputs", type=Path, default=HERE / "inputs.json")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        p = json.loads(args.inputs.read_text(encoding="utf-8"))
        report = render(p)
        if args.check:
            if report != (HERE / "RESULTS.md").read_text(encoding="utf-8"):
                raise ValueError("RESULTS.md differs from calculations; inspect inputs and regenerate")
            print("PASS: checked-in results reproduce exactly")
        else:
            print(report, end="")
    except (OSError, ValueError, TypeError, KeyError) as exc:
        parser.exit(1, f"ERROR: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
