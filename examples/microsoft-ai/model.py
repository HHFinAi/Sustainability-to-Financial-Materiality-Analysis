"""Illustrative cooling, resilience and separate capacity economics.

No network or issuer loss forecast. Python 3.10+ standard library. --check reads
and verifies committed reports without writing files. Missing issuer evidence
remains NEEDS_DATA even when scenario arithmetic can be completed.
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
    "operating_deduction_fraction", "depreciation_deduction_fraction",
    "tax_deduction_delay_years",
)
RELIABILITY = (
    "annual_event_probability", "disruption_duration_hours",
    "risk_reduction_fraction", "protected_cash_contribution_usd_m_per_hour",
    "recoverable_workload_fraction",
)
CAPACITY = (
    "added_it_capacity_mw", "average_billable_load_fraction",
    "revenue_usd_m_per_fully_utilized_mw_year", "total_facility_pue",
    "infrastructure_capex_usd_m_per_mw", "cooling_capex_usd_m_per_mw",
    "hardware_capex_usd_m_per_mw", "nonpower_operating_cost_usd_m_per_mw_year",
    "hardware_life_years", "project_life_years", "commissioning_delay_years",
    "working_capital_fraction_of_revenue",
)


def nonnegative(p: dict[str, Any], keys: tuple[str, ...]) -> None:
    for key in keys:
        value = p.get(key)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"Missing or nonnumeric input: {key}")
        if not math.isfinite(value) or value < 0:
            raise ValueError(f"Input must be finite and nonnegative: {key}")


def integer(p: dict[str, Any], key: str, lo: int, hi: int) -> None:
    if isinstance(p[key], bool) or not isinstance(p[key], int) or not lo <= p[key] <= hi:
        raise ValueError(f"Invalid integer input: {key}")


def validate(p: dict[str, Any]) -> None:
    if p.get("classification") != "ANALYST_ASSUMPTIONS_NOT_ISSUER_GUIDANCE":
        raise ValueError("Project inputs must remain labelled analyst assumptions")
    if p.get("currency") != "USD" or p.get("money_unit") != "million":
        raise ValueError("This model requires USD million monetary inputs")
    nonnegative(p, NUMERIC)
    if not 0 < p["average_it_load_fraction"] <= 1:
        raise ValueError("Average IT load must lie in (0, 1]")
    if p["it_capacity_mw"] <= 0 or not 0 < p["hours_per_year"] <= 8784:
        raise ValueError("Invalid capacity or hours")
    if not 0 <= p["cash_tax_rate"] < 1:
        raise ValueError("Tax rate must lie in [0, 1)")
    if not 0 <= p["discount_rate"] <= 1:
        raise ValueError("Discount rate outside supported [0, 1] range")
    for key in ("operating_deduction_fraction", "depreciation_deduction_fraction"):
        if not 0 <= p[key] <= 1:
            raise ValueError(f"Deduction fraction must lie in [0, 1]: {key}")
    integer(p, "asset_life_years", 1, 100)
    integer(p, "commissioning_delay_years", 0, 100)
    integer(p, "tax_deduction_delay_years", 0, 100)
    if p["incremental_capex_usd_m"] <= 0:
        raise ValueError("Positive incremental capex required")


def calculate(p: dict[str, Any]) -> dict[str, Any]:
    validate(p)
    it_mwh = p["it_capacity_mw"] * p["average_it_load_fraction"] * p["hours_per_year"]
    extra_mwh = it_mwh * p["incremental_pue"]
    water_m3 = it_mwh * p["avoided_cooling_water_l_per_it_kwh"]
    power_cost = extra_mwh * p["electricity_usd_per_mwh"] / 1_000_000
    water_saving = water_m3 * p["water_usd_per_m3"] / 1_000_000
    costs = power_cost + p["incremental_maintenance_usd_m_per_year"]
    operating_delta = water_saving - costs
    capex = p["incremental_capex_usd_m"] * (1 + p["capex_overrun_fraction"])
    depreciation = capex / p["asset_life_years"]
    tax = p["cash_tax_rate"]
    receipts = water_saving + p["additional_operating_benefit_usd_m_per_year"]
    annual_before_shields = receipts * (1 - tax) - costs
    annual_shield = tax * (costs * p["operating_deduction_fraction"] +
                          depreciation * p["depreciation_deduction_fraction"])
    flows: dict[int, float] = {0: -capex}
    for operating_year in range(1, p["asset_life_years"] + 1):
        year = operating_year + p["commissioning_delay_years"]
        flows[year] = flows.get(year, 0.0) + annual_before_shields
        shield_year = year + p["tax_deduction_delay_years"]
        flows[shield_year] = flows.get(shield_year, 0.0) + annual_shield
    annuity = sum((1 + p["discount_rate"]) ** -(year + p["commissioning_delay_years"])
                  for year in range(1, p["asset_life_years"] + 1))
    deduction_annuity = annuity / (1 + p["discount_rate"]) ** p["tax_deduction_delay_years"]
    shield_pv = annual_shield * deduction_annuity
    hurdle = (capex + costs * annuity - shield_pv) / ((1 - tax) * annuity) - water_saving
    return {
        "it_mwh_per_year": it_mwh,
        "extra_electricity_mwh_per_year": extra_mwh,
        "avoided_direct_water_m3_per_year": water_m3,
        "extra_power_cost_usd_m_per_year": power_cost,
        "water_bill_saving_usd_m_per_year": water_saving,
        "direct_operating_delta_usd_m_per_year": operating_delta,
        "capex_usd_m": capex,
        "annual_incremental_fcf_usd_m": flows[1 + p["commissioning_delay_years"]],
        "annuity_factor": annuity,
        "tax_deduction_present_value_usd_m": shield_pv,
        "incremental_npv_usd_m": sum(fcf / (1 + p["discount_rate"]) ** year for year, fcf in flows.items()),
        "break_even_additional_pretax_benefit_usd_m_per_year": hurdle,
        "cash_flows": [{"year_from_initial_capex": y, "incremental_fcf_usd_m": flows[y]} for y in sorted(flows)],
    }


def reliability(p: dict[str, Any]) -> dict[str, Any]:
    validate(p)
    q = p.get("reliability")
    if not isinstance(q, dict):
        raise ValueError("Missing reliability scenario inputs")
    if q.get("classification") != "ANALYST_ASSUMPTIONS_NOT_ISSUER_GUIDANCE":
        raise ValueError("Reliability inputs must remain labelled analyst assumptions")
    nonnegative(q, RELIABILITY)
    for key in ("annual_event_probability", "risk_reduction_fraction", "recoverable_workload_fraction"):
        if not 0 <= q[key] <= 1:
            raise ValueError(f"Fraction must lie in [0, 1]: {key}")
    if q["disruption_duration_hours"] > p["hours_per_year"]:
        raise ValueError("Disruption duration exceeds annual hours")
    if q.get("event_model") != "AT_MOST_ONE_WATER_LINKED_EVENT_PER_YEAR":
        raise ValueError("Reliability scenario requires the explicit single-event model")
    if p["additional_operating_benefit_usd_m_per_year"] != 0:
        raise ValueError("Set generic additional benefit to zero before using explicit routes")
    reference = calculate(p)
    hurdle = max(0.0, reference["break_even_additional_pretax_benefit_usd_m_per_year"])
    net_per_hour = q["protected_cash_contribution_usd_m_per_hour"] * (1 - q["recoverable_workload_fraction"])
    avoided_hours = q["annual_event_probability"] * q["disruption_duration_hours"] * q["risk_reduction_fraction"]
    benefit = avoided_hours * net_per_hour
    risk_weighted_duration = q["disruption_duration_hours"] * q["risk_reduction_fraction"] * net_per_hour
    required_hours = 0.0 if hurdle == 0 else (hurdle / net_per_hour if net_per_hour else None)
    required_probability = 0.0 if hurdle == 0 else (hurdle / risk_weighted_duration if risk_weighted_duration else None)
    duration_slope = q["annual_event_probability"] * q["risk_reduction_fraction"] * net_per_hour
    required_duration = 0.0 if hurdle == 0 else (hurdle / duration_slope if duration_slope else None)
    after = calculate({**p, "additional_operating_benefit_usd_m_per_year": benefit})
    return {
        "classification": "ILLUSTRATIVE_CALCULATION_NOT_ISSUER_LOSS_FORECAST",
        "expected_avoided_outage_hours_per_year": avoided_hours,
        "nonrecoverable_cash_contribution_usd_m_per_hour": net_per_hour,
        "expected_avoided_pretax_cash_loss_usd_m_per_year": benefit,
        "required_expected_avoided_hours_per_year": required_hours,
        "required_event_probability_at_assumed_duration": required_probability,
        "required_disruption_duration_hours_at_assumed_probability": required_duration,
        "break_even_feasibility_at_assumed_duration": "NO_FINITE_BREAKPOINT" if required_probability is None else ("OUTSIDE_PROBABILITY_RANGE" if required_probability > 1 else "WITHIN_ASSUMED_RANGE"),
        "cooling_plus_reliability_npv_usd_m": after["incremental_npv_usd_m"],
    }


def capacity_expansion(p: dict[str, Any]) -> dict[str, Any]:
    validate(p)
    g = p.get("capacity_expansion")
    if not isinstance(g, dict):
        raise ValueError("Missing capacity scenario inputs")
    if g.get("classification") != "ANALYST_ASSUMPTIONS_NOT_ISSUER_GUIDANCE":
        raise ValueError("Capacity inputs must remain labelled analyst assumptions")
    nonnegative(g, CAPACITY)
    if g["added_it_capacity_mw"] <= 0 or not 0 < g["average_billable_load_fraction"] <= 1 or g["total_facility_pue"] < 1:
        raise ValueError("Invalid added capacity, billable load or total facility PUE")
    if not 0 <= g["working_capital_fraction_of_revenue"] <= 1:
        raise ValueError("Working-capital fraction outside [0, 1]")
    integer(g, "hardware_life_years", 1, 100)
    integer(g, "project_life_years", 1, 100)
    integer(g, "commissioning_delay_years", 0, 100)
    if g["hardware_life_years"] > g["project_life_years"] or g["project_life_years"] % g["hardware_life_years"]:
        raise ValueError("Supported capacity case requires whole hardware cycles within project life")
    if p["additional_operating_benefit_usd_m_per_year"] != 0:
        raise ValueError("Set generic additional benefit to zero before using explicit routes")
    mw = g["added_it_capacity_mw"]
    load = g["average_billable_load_fraction"]
    revenue = mw * load * g["revenue_usd_m_per_fully_utilized_mw_year"]
    it_mwh = mw * load * p["hours_per_year"]
    facility_mwh = it_mwh * g["total_facility_pue"]
    power = facility_mwh * p["electricity_usd_per_mwh"] / 1_000_000
    other_costs = mw * g["nonpower_operating_cost_usd_m_per_mw_year"]
    infrastructure = mw * (g["infrastructure_capex_usd_m_per_mw"] + g["cooling_capex_usd_m_per_mw"])
    hardware = mw * g["hardware_capex_usd_m_per_mw"]
    if infrastructure + hardware <= 0:
        raise ValueError("Capacity expansion must include positive capital spending")
    wc = revenue * g["working_capital_fraction_of_revenue"]
    depreciation = infrastructure / g["project_life_years"] + hardware / g["hardware_life_years"]
    tax = p["cash_tax_rate"]
    costs = power + other_costs
    flows: dict[int, float] = {0: -(infrastructure + hardware + wc)}
    replacements = []
    for n in range(1, g["project_life_years"] + 1):
        year = n + g["commissioning_delay_years"]
        flows[year] = flows.get(year, 0.0) + revenue * (1 - tax) - costs
        deduction_year = year + p["tax_deduction_delay_years"]
        flows[deduction_year] = flows.get(deduction_year, 0.0) + tax * (
            costs * p["operating_deduction_fraction"] + depreciation * p["depreciation_deduction_fraction"])
        if n % g["hardware_life_years"] == 0 and n < g["project_life_years"]:
            flows[year] -= hardware
            replacements.append({"year_from_initial_capex": year, "hardware_capex_usd_m": hardware})
    last_year = g["project_life_years"] + g["commissioning_delay_years"]
    flows[last_year] += wc
    rate = p["discount_rate"]
    annuity = sum((1 + rate) ** -(n + g["commissioning_delay_years"]) for n in range(1, g["project_life_years"] + 1))
    npv = sum(v / (1 + rate) ** y for y, v in flows.items())
    # WC scales with revenue; subtract its initial outlay less discounted release.
    revenue_pv_slope = (1 - tax) * annuity - g["working_capital_fraction_of_revenue"] * (1 - (1 + rate) ** -last_year)
    if revenue_pv_slope <= 0:
        raise ValueError("After-tax revenue present value must exceed working-capital funding drag")
    revenue_without_npv = revenue - npv / revenue_pv_slope
    cooling_npv = calculate(p)["incremental_npv_usd_m"]
    per_mw_npv = npv / mw
    required_added_mw = 0.0 if cooling_npv >= 0 else (-cooling_npv / per_mw_npv if per_mw_npv > 0 else None)
    return {
        "classification": "ILLUSTRATIVE_SEPARATE_CAPACITY_PROJECT_NOT_ISSUER_FORECAST",
        "added_it_capacity_mw": mw, "annual_added_revenue_usd_m": revenue,
        "annual_added_it_mwh": it_mwh, "annual_added_total_facility_mwh": facility_mwh,
        "annual_added_power_cost_usd_m": power, "annual_other_operating_cost_usd_m": other_costs,
        "initial_infrastructure_and_cooling_capex_usd_m": infrastructure,
        "initial_hardware_capex_usd_m": hardware, "initial_working_capital_usd_m": wc,
        "hardware_replacements": replacements, "capacity_project_npv_usd_m": npv,
        "break_even_annual_revenue_usd_m": revenue_without_npv,
        "break_even_revenue_usd_m_per_fully_utilized_mw_year": revenue_without_npv / (mw * load),
        "cooling_plus_separate_capacity_npv_usd_m": cooling_npv + npv,
        "break_even_annual_revenue_including_existing_cooling_usd_m": revenue - (npv + cooling_npv) / revenue_pv_slope,
        "break_even_revenue_including_existing_cooling_usd_m_per_fully_utilized_mw_year": (revenue - (npv + cooling_npv) / revenue_pv_slope) / (mw * load),
        "required_added_mw_to_offset_existing_cooling_npv_at_constant_unit_economics": required_added_mw,
        "cash_flows": [{"year_from_initial_capex": y, "incremental_fcf_usd_m": flows[y]} for y in sorted(flows)],
    }


def analysis(p: dict[str, Any]) -> dict[str, Any]:
    gaps = p.get("issuer_evidence_gaps")
    if not isinstance(gaps, list) or not gaps or not all(isinstance(x, str) and x.strip() for x in gaps):
        raise ValueError("This case must retain named unresolved issuer evidence gaps")
    return {
        "case_id": p["case_id"], "extension_date": p["extension_date"],
        "issuer_underwriting_status": "NEEDS_DATA", "scenario_arithmetic_status": "COMPLETE",
        "issuer_evidence_gaps": gaps,
        "fixed_workload_cooling": calculate(p), "fixed_workload_reliability": reliability(p),
        "separate_added_capacity": capacity_expansion(p),
        "aggregation_boundary": "Reliability and expansion are separate routes. No combined resilience-and-growth NPV or issuer valuation is asserted.",
    }


def render(p: dict[str, Any]) -> str:
    cases = [
        ("Reference: direct bills only", {}),
        ("Additional benefit $3m/year", {"additional_operating_benefit_usd_m_per_year": 3.0}),
        ("Electricity $120/MWh", {"electricity_usd_per_mwh": 120.0}),
        ("Water $5/m3", {"water_usd_per_m3": 5.0}),
        ("Incremental PUE 0.04", {"incremental_pue": 0.04}),
        ("Capex +25%; commissioning +1 year", {"capex_overrun_fraction": 0.25, "commissioning_delay_years": 1}),
        ("No taxes or tax shields", {"cash_tax_rate": 0.0}),
        ("Capital allowances unavailable; tax remains 25%", {"depreciation_deduction_fraction": 0.0}),
        ("All cost deductions unavailable; tax remains 25%", {"operating_deduction_fraction": 0.0, "depreciation_deduction_fraction": 0.0}),
        ("All cost deductions delayed 2 years; tax remains 25%", {"tax_deduction_delay_years": 2}),
    ]
    a = analysis(p)
    r, q, g = a["fixed_workload_cooling"], a["fixed_workload_reliability"], a["separate_added_capacity"]
    def show(value: Any, decimals: int = 4) -> str:
        return "Not finite / unavailable" if value is None else f"{value:,.{decimals}f}"
    lines = ["# Cooling investment: reproducible sensitivities", "",
             "**Illustrative project arithmetic, not a Microsoft site forecast or share-price valuation.**",
             "Baseline prepared 4 October 2026; underwriting extension prepared 8 October 2026. USD million unless stated otherwise.", "",
             "Issuer underwriting: **NEEDS_DATA**. Scenario arithmetic: **COMPLETE**. [Named evidence gaps](inputs.json) remain unresolved.", "",
             f"Annual IT electricity: {r['it_mwh_per_year']:,.0f} MWh. Additional electricity: {r['extra_electricity_mwh_per_year']:,.0f} MWh.",
             f"Assumed avoided direct cooling water: {r['avoided_direct_water_m3_per_year']:,.0f} m3/year.",
             f"Water bill saving: {r['water_bill_saving_usd_m_per_year']:.6f}; additional electricity cost: {r['extra_power_cost_usd_m_per_year']:.6f} per year.",
             "", "| Scenario | First operating-year incremental FCF | NPV | Break-even additional pre-tax benefit/year |",
             "|---|---:|---:|---:|"]
    for name, overrides in cases:
        out = calculate({**p, **overrides})
        lines.append(f"| {name} | {out['annual_incremental_fcf_usd_m']:.4f} | {out['incremental_npv_usd_m']:.4f} | {out['break_even_additional_pretax_benefit_usd_m_per_year']:.4f} |")
    lines += ["", "The hurdle is total recurring additional pre-tax benefit required for zero NPV. It is not extra benefit on top of an assumed amount.",
              "Cash taxes on savings/benefits remain payable in deduction-unavailable/delayed rows. A two-year delay shifts deductions, including tax-only receipts after asset life; no expiry is assumed. All deductions are otherwise immediately usable against other taxable income. These are simplified tax scenarios, not conclusions about US tax law.",
              "Commissioning delays postpone operating cash flows and tax depreciation, not initial capex. Delay holding costs remain excluded.",
              "", "## Route A: protected existing workload", "",
              "The single-event scenario assumes a 25% annual event probability, 48 disruption hours, 80% risk reduction, $0.05m/hour cash contribution after avoidable costs, and 25% workload recovery. None is an issuer observation.",
              "", "| Reliability output | Value |", "|---|---:|",
              f"| Expected avoided outage hours/year | {show(q['expected_avoided_outage_hours_per_year'])} |",
              f"| Expected avoided pre-tax cash loss/year | {show(q['expected_avoided_pretax_cash_loss_usd_m_per_year'])} |",
              f"| Required expected avoided hours/year to clear cooling hurdle | {show(q['required_expected_avoided_hours_per_year'])} |",
              f"| Required event probability at assumed 48-hour duration | {show(q['required_event_probability_at_assumed_duration'])} |",
              f"| Required event duration at assumed 25% annual probability, hours | {show(q['required_disruption_duration_hours_at_assumed_probability'])} |",
              f"| Cooling plus reliability NPV | {show(q['cooling_plus_reliability_npv_usd_m'])} |",
              "", f"Probability feasibility: **{q['break_even_feasibility_at_assumed_duration']}**. A required probability above 1 rejects this duration/contribution combination; it is not a predicted probability. Recoverable/rerouted work is removed before loss valuation.",
              "", "## Route B: separate new capacity", "",
              "The added 10 MW has its own infrastructure, cooling, IT hardware, total facility electricity, non-power operating costs and working capital. Hardware is replaced at year 5. This route does not place gross expansion revenue in the existing cooling model's benefit input.",
              "", "| Capacity output | Value |", "|---|---:|",
              f"| Added revenue/year | {show(g['annual_added_revenue_usd_m'])} |",
              f"| Added facility electricity MWh/year | {show(g['annual_added_total_facility_mwh'])} |",
              f"| Added power / other operating costs/year | {show(g['annual_added_power_cost_usd_m'])} / {show(g['annual_other_operating_cost_usd_m'])} |",
              f"| Initial infrastructure and cooling / IT hardware capex | {show(g['initial_infrastructure_and_cooling_capex_usd_m'])} / {show(g['initial_hardware_capex_usd_m'])} |",
              f"| Hardware replacement capex across project life | {show(sum(x['hardware_capex_usd_m'] for x in g['hardware_replacements']))} |",
              f"| Separate capacity-project NPV | {show(g['capacity_project_npv_usd_m'])} |",
              f"| Standalone break-even revenue per fully utilized MW-year | {show(g['break_even_revenue_usd_m_per_fully_utilized_mw_year'])} |",
              f"| Break-even revenue per fully utilized MW-year including existing cooling | {show(g['break_even_revenue_including_existing_cooling_usd_m_per_fully_utilized_mw_year'])} |",
              f"| Existing cooling plus separate capacity-project NPV | {show(g['cooling_plus_separate_capacity_npv_usd_m'])} |",
              f"| Added MW required to offset existing cooling NPV at constant assumed unit economics | {show(g['required_added_mw_to_offset_existing_cooling_npv_at_constant_unit_economics'])} |",
              "", "At the reference revenue assumption the added project has negative NPV, so no positive amount of identically priced capacity clears the existing cooling hurdle. The break-even combined revenue above prices both capital commitments.",
              "", "| Revenue per fully utilized MW-year | Separate capacity NPV | Cooling plus capacity NPV | Required added MW |", "|---|---:|---:|---:|"]
    for unit_revenue in (4.0, 6.0, 6.2):
        growth = capacity_expansion({**p, "capacity_expansion": {**p["capacity_expansion"], "revenue_usd_m_per_fully_utilized_mw_year": unit_revenue}})
        lines.append(f"| {unit_revenue:.2f} | {growth['capacity_project_npv_usd_m']:.4f} | {growth['cooling_plus_separate_capacity_npv_usd_m']:.4f} | {show(growth['required_added_mw_to_offset_existing_cooling_npv_at_constant_unit_economics'])} |")
    lines += ["", "No expansion value is attributable to water resilience until water design is shown to be a binding constraint. Linear scaling assumes unchanged prices, utilization, costs and capital intensity; power, demand, permitting and grid constraints may invalidate it. Reliability and expansion routes are not combined.",
              "", "[Investment memo](README.md) · [Inputs and assumptions](inputs.json) · [Calculation](model.py) · [Machine-readable cash flows](results.json)", ""]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inputs", type=Path, default=HERE / "inputs.json")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        p = json.loads(args.inputs.read_text(encoding="utf-8"))
        report = render(p)
        results = json.dumps(analysis(p), indent=2, allow_nan=False) + "\n"
        if args.check:
            if report != (HERE / "RESULTS.md").read_text(encoding="utf-8"):
                raise ValueError("RESULTS.md differs from calculations; inspect inputs and regenerate")
            if results != (HERE / "results.json").read_text(encoding="utf-8"):
                raise ValueError("results.json differs from calculations; inspect inputs and regenerate")
            print("PASS: checked-in reports and cash flows reproduce exactly; issuer underwriting remains NEEDS_DATA")
        else:
            print(report, end="")
    except (OSError, ValueError, TypeError, KeyError, IndexError) as exc:
        parser.exit(1, f"ERROR: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
