"""Original monthly infrastructure scenarios. Standard library; no network.

Run with --write to explicitly refresh results.json/RESULTS.md, or --check to
verify them without writes. Issuer underwriting remains NEEDS_DATA. The model
does not submit synthetic economics to the repository's research state machine.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
LABEL = "ILLUSTRATIVE_ASSUMPTIONS_NOT_ISSUER_ECONOMICS"


def validate(p):
    if p.get("classification") != LABEL or p.get("currency") != "USD" or p.get("money_unit") != "million":
        raise ValueError("Assumption classification and USD million units required")
    exempt = {"case_id", "prepared_on", "classification", "currency", "money_unit", "boundaries"}
    for key, value in p.items():
        if key in exempt:
            continue
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
            raise ValueError(f"Finite nonnegative input required: {key}")
    for key in ("horizon_months", "building_life_months", "cooling_life_months", "hardware_life_months", "hardware_tax_life_months",
                "grid_connection_life_months", "generation_life_months", "event_month"):
        if not isinstance(p[key], int) or p[key] < 1:
            raise ValueError(f"Positive integer required: {key}")
    if p["horizon_months"] > 600 or p["event_month"] > p["horizon_months"]:
        raise ValueError("Unsupported horizon or event month")
    for key in ("building_life_months", "cooling_life_months", "grid_connection_life_months", "generation_life_months"):
        if p[key] < p["horizon_months"]:
            raise ValueError("Non-hardware life must cover the modeled horizon; replacement is not modeled")
    for key in ("utilization", "cash_tax_rate", "recoverable_workload_fraction",
                "working_capital_fraction_of_annual_revenue", "land_sale_fraction", "building_sale_fraction",
                "hardware_sale_fraction_of_remaining_economic_cost"):
        if not 0 <= p[key] <= 1:
            raise ValueError(f"Fraction outside [0, 1]: {key}")
    if p["cash_tax_rate"] >= 1 or p["pue"] < 1 or p["it_capacity_mw"] <= 0 or p["utilization"] <= 0:
        raise ValueError("Invalid capacity, tax, utilization or PUE")
    if not 0 < p["hours_per_year"] <= 8784 or p["event_outage_hours"] > p["hours_per_year"] / 12:
        raise ValueError("Incident hours must fit one equal-length modeled month")
    if p["discount_rate"] > 1:
        raise ValueError("Discount rate outside [0, 1]")


def calculate(p, power="grid", delay_months=0):
    validate(p)
    if power not in {"grid", "gas"}:
        raise ValueError("Power must be grid or gas")
    if isinstance(delay_months, bool) or not isinstance(delay_months, int) or not 0 <= delay_months < p["horizon_months"]:
        raise ValueError("Delay must be an integer inside the common opportunity window")
    horizon = p["horizon_months"]
    operating_months = horizon - delay_months
    revenue_annual = p["it_capacity_mw"] * p["utilization"] * p["revenue_m_per_utilized_mw_year"]
    energy_annual = p["it_capacity_mw"] * p["utilization"] * p["pue"] * p["hours_per_year"]
    variable_power = (p["grid_power_usd_per_mwh"] if power == "grid" else
                      p["gas_usd_per_mmbtu"] * p["heat_rate_mmbtu_per_mwh"] +
                      p["generation_variable_om_usd_per_mwh"] +
                      p["generation_tco2_per_mwh"] * p["carbon_cost_usd_per_t"])
    fixed_power = 0 if power == "grid" else p["generation_fixed_om_m_per_year"]
    power_capex = p["grid_connection_capex_m"] if power == "grid" else p["generation_capex_m"]
    power_life = p["grid_connection_life_months"] if power == "grid" else p["generation_life_months"]
    initial = p["land_capex_m"] + p["building_capex_m"] + p["cooling_capex_m"] + power_capex + p["mitigation_capex_m"]
    wc = revenue_annual * p["working_capital_fraction_of_annual_revenue"]
    # Month m denotes an end-of-month cash date; hardware is bought at COD,
    # then at complete service-life boundaries before the next month operates.
    hardware_purchases = list(range(delay_months, horizon, p["hardware_life_months"]))
    rows = []
    for month in range(horizon + 1):
        active = month > delay_months
        elapsed = max(0, month - delay_months)
        revenue = revenue_annual / 12 if active else 0.0
        energy = energy_annual / 12 if active else 0.0
        outage = p["event_outage_hours"] if active and month == p["event_month"] else 0.0
        unrecovered_fraction = outage / (p["hours_per_year"] / 12) * (1 - p["recoverable_workload_fraction"])
        lost_revenue = revenue * unrecovered_fraction
        revenue -= lost_revenue
        energy *= (1 - unrecovered_fraction)
        power_cost = energy * variable_power / 1e6 + (fixed_power / 12 if active else 0)
        other_cost = p["other_opex_m_per_year"] / 12 if active else 0
        holding = p["holding_cost_m_per_month"] if 0 < month <= delay_months else 0
        incident = outage * p["event_service_credit_m_per_hour"] + (p["event_recovery_cost_m"] if outage else 0)
        depreciation = 0.0
        if active:
            # The vintage bought exactly at this month's end replaces the old
            # equipment for NEXT month's operation, not this month's allowance.
            operating_vintage = max(t for t in hardware_purchases if t < month)
            hardware_tax_age = month - operating_vintage
            hardware_depreciation = (p["hardware_capex_m"] / p["hardware_tax_life_months"]
                                     if hardware_tax_age <= p["hardware_tax_life_months"] else 0)
            depreciation = (p["building_capex_m"] / p["building_life_months"] +
                            p["cooling_capex_m"] / p["cooling_life_months"] +
                            power_capex / power_life + p["mitigation_capex_m"] / p["horizon_months"] +
                            hardware_depreciation)
        capex = initial if month == 0 else 0.0
        hardware = p["hardware_capex_m"] if month in hardware_purchases else 0.0
        capex += hardware
        wc_change = wc if month == delay_months else 0.0
        sale = decommission = taxable_gain = 0.0
        if month == horizon:
            land_sale = p["land_capex_m"] * p["land_sale_fraction"]
            building_sale = p["building_capex_m"] * p["building_sale_fraction"]
            building_book = p["building_capex_m"] * max(0, 1 - elapsed / p["building_life_months"])
            hardware_age = horizon - hardware_purchases[-1]
            hardware_book = p["hardware_capex_m"] * max(0, 1 - hardware_age / p["hardware_tax_life_months"])
            hardware_remaining_economic_cost = p["hardware_capex_m"] * max(0, 1 - hardware_age / p["hardware_life_months"])
            hardware_sale = hardware_remaining_economic_cost * p["hardware_sale_fraction_of_remaining_economic_cost"]
            sale = land_sale + building_sale + hardware_sale
            taxable_gain = max(0, land_sale - p["land_capex_m"]) + max(0, building_sale - building_book) + max(0, hardware_sale - hardware_book)
            decommission = p["decommission_cost_m"]
            wc_change -= wc
        ebitda = revenue - power_cost - other_cost - holding - incident
        taxable_income = ebitda - depreciation - decommission + taxable_gain
        cash_tax = max(0, taxable_income) * p["cash_tax_rate"]
        fcf = ebitda - cash_tax - capex - wc_change + sale - decommission
        discount = (1 + p["discount_rate"]) ** (-month / 12)
        rows.append({"month": month, "operating": active, "revenue_m": revenue,
                     "lost_revenue_m": lost_revenue, "power_cost_m": power_cost,
                     "other_opex_m": other_cost, "holding_cost_m": holding,
                     "incident_cost_m": incident, "depreciation_m": depreciation,
                     "cash_tax_m": cash_tax, "capex_m": capex, "hardware_capex_m": hardware,
                     "working_capital_change_m": wc_change, "asset_sale_m": sale,
                     "decommission_m": decommission, "fcf_m": fcf, "pv_m": fcf * discount})
    return {"classification": LABEL, "power": power, "delay_months": delay_months,
            "horizon_months": horizon, "operating_months": operating_months,
            "annual_revenue_before_incident_m": revenue_annual,
            "annual_facility_mwh_before_incident": energy_annual,
            "annual_power_cost_before_incident_m": energy_annual * variable_power / 1e6 + fixed_power,
            "initial_infrastructure_capex_m": initial, "hardware_purchase_months": hardware_purchases,
            "total_hardware_capex_m": p["hardware_capex_m"] * len(hardware_purchases),
            "holding_cost_total_m": p["holding_cost_m_per_month"] * delay_months,
            "npv_m": math.fsum(row["pv_m"] for row in rows), "cash_flows": rows}


def revenue_hurdle(p, power, delay):
    low, high = 0.0, 50.0
    def value(revenue):
        q = {**p, "revenue_m_per_utilized_mw_year": revenue}
        return calculate(q, power, delay)["npv_m"]
    if value(low) >= 0:
        return 0.0
    if value(high) < 0:
        return None
    for _ in range(80):
        mid = (low + high) / 2
        if value(mid) >= 0:
            high = mid
        else:
            low = mid
    return (low + high) / 2


def cancellation(p, cancel_month=12, infrastructure_recovery_fraction=0.30, exit_cost_m=20):
    """Conditional abandonment of grid case before hardware/WC commitment.

    Gross cash recoveries only; no tax-loss credit. This is a separate scenario,
    not a probability inferred from the project tracker.
    """
    validate(p)
    if not isinstance(cancel_month, int) or isinstance(cancel_month, bool) or not 0 <= cancel_month <= p["horizon_months"]:
        raise ValueError("Invalid cancellation month")
    if not 0 <= infrastructure_recovery_fraction <= 1 or not math.isfinite(exit_cost_m) or exit_cost_m < 0:
        raise ValueError("Invalid recovery or exit cost")
    infra = p["building_capex_m"] + p["cooling_capex_m"] + p["grid_connection_capex_m"] + p["mitigation_capex_m"]
    initial = p["land_capex_m"] + infra
    recovered = p["land_capex_m"] * p["land_sale_fraction"] + infra * infrastructure_recovery_fraction
    holding_pv = math.fsum(p["holding_cost_m_per_month"] / (1 + p["discount_rate"]) ** (m / 12) for m in range(1, cancel_month + 1))
    pv = -initial - holding_pv + (recovered - exit_cost_m) / (1 + p["discount_rate"]) ** (cancel_month / 12)
    return {"classification": LABEL, "cancel_month": cancel_month,
            "infrastructure_recovery_fraction": infrastructure_recovery_fraction,
            "exit_cost_m": exit_cost_m, "gross_recovery_m": recovered, "npv_m": pv,
            "hardware_and_working_capital_committed": False}


def build(p):
    reference = calculate(p)
    base = reference["npv_m"]
    timing = []
    for delay in (0, 6, 12, 24):
        for power in ("grid", "gas"):
            r = calculate(p, power, delay)
            timing.append({"power": power, "delay_months": delay, "npv_m": r["npv_m"],
                           "delta_to_grid_now_m": r["npv_m"] - base,
                           "revenue_hurdle_m_per_utilized_mw_year": revenue_hurdle(p, power, delay),
                           "holding_cost_total_m": r["holding_cost_total_m"]})
    axes = []
    definitions = [("Hardware life", "hardware_life_months", [36, 60, 84], "grid"),
                   ("Grid delivered power", "grid_power_usd_per_mwh", [60, 80, 120], "grid"),
                   ("Gas fuel", "gas_usd_per_mmbtu", [4, 6, 10], "gas"),
                   ("Hypothetical carbon cost", "carbon_cost_usd_per_t", [0, 50, 100], "gas"),
                   ("Building sale fraction", "building_sale_fraction", [0, 0.2, 0.4], "grid"),
                   ("One incident: outage hours", "event_outage_hours", [0, 4, 24, 72], "grid"),
                   ("Utilization", "utilization", [0.5, 0.7, 0.9], "grid")]
    for label, key, values, power in definitions:
        route_base = calculate(p, power)["npv_m"]
        for value in values:
            q = {**p, key: value}
            r = calculate(q, power)
            axes.append({"axis": label, "input": key, "value": value, "power": power,
                         "npv_m": r["npv_m"], "delta_to_same_power_reference_m": r["npv_m"] - route_base})
    early = calculate(p, "gas", 0)["npv_m"]
    threshold = next((d for d in range(min(25, p["horizon_months"])) if early >= calculate(p, "grid", d)["npv_m"]), None)
    residual = []
    for life in (36, 60, 84):
        for fraction in (0, 0.5, 1):
            q = {**p, "hardware_life_months": life, "hardware_sale_fraction_of_remaining_economic_cost": fraction}
            residual.append({"hardware_economic_life_months": life, "recovery_fraction": fraction,
                             "npv_m": calculate(q)["npv_m"]})
    return {"case_id": p["case_id"], "prepared_on": p["prepared_on"],
            "issuer_underwriting": "NEEDS_DATA", "arithmetic_status": "COMPLETE",
            "classification": LABEL, "scope": p["boundaries"], "reference_grid": reference,
            "reference_gas": calculate(p, "gas"), "timing_scenarios": timing,
            "one_factor_sensitivities": axes, "cancellation_scenarios": [cancellation(p, 12, r) for r in (0, 0.3, 0.6)],
            "hardware_life_resale_scenarios": residual,
            "first_grid_delay_month_where_gas_now_has_higher_npv": threshold}


def render(r):
    grid, gas = r["reference_grid"], r["reference_gas"]
    lines = ["# AI infrastructure: reproducible project scenarios", "",
             "**Original HHFinAi scenario model, 16 October 2026. USD million unless stated.**",
             "Illustrative assumptions; no Microsoft or other issuer's site returns are estimated. Issuer underwriting: **NEEDS_DATA**.", "",
             "## Decision-relevant results", "",
             f"The grid-now reference NPV is **${grid['npv_m']:.2f}m**; gas-now is **${gas['npv_m']:.2f}m**. In this assumption set, immediate gas generation first exceeds delayed grid NPV at a **{r['first_grid_delay_month_where_gas_now_has_higher_npv']}-month** grid delay (whole-month search within 0-24 months). This ranking assumes immediate gas availability and a fixed horizon with zero hardware resale; replacement boundaries can cause nonmonotonic results outside the displayed range. Gas-now is only narrowly positive, so no investment conclusion is robust to unverified costs.", "",
             f"Both serve an assumed 100 MW IT workload, 70% utilization and PUE 1.15: **{grid['annual_facility_mwh_before_incident']:,.0f} MWh/year**. Grid power costs ${grid['annual_power_cost_before_incident_m']:.2f}m/year; gas fuel, variable and fixed O&M cost ${gas['annual_power_cost_before_incident_m']:.2f}m/year before any scenario carbon charge.", "",
             "## Commissioning timing and capital recovery", "",
             "Common calendar end: month 120. Initial infrastructure is committed at month zero; hardware and working capital at commissioning. Delayed projects lose operating months and incur holding costs. The model does not grant every delayed project a fresh ten-year operating life.", "",
             "| Power | Delay months | NPV | Change vs grid now | Revenue hurdle / utilized MW-year | Holding costs |",
             "|---|---:|---:|---:|---:|---:|"]
    for v in r["timing_scenarios"]:
        hurdle = v["revenue_hurdle_m_per_utilized_mw_year"]
        lines.append(f"| {v['power']} | {v['delay_months']} | {v['npv_m']:.2f} | {v['delta_to_grid_now_m']:+.2f} | {hurdle:.3f} | {v['holding_cost_total_m']:.2f} |")
    lines += ["", "The hurdle is revenue at full utilization per MW-year, multiplied by the assumed utilization to obtain modeled sales. It is not a customer tariff or a reported issuer metric.", "",
              "## One-factor sensitivities", "", "Each row changes one input; other reference assumptions remain fixed. Changes are relative to the same power route with zero delay. These rows must not be added together.", "",
              "| Variable | Value | Power | NPV | Change vs route reference |", "|---|---:|---|---:|---:|"]
    for v in r["one_factor_sensitivities"]:
        lines.append(f"| {v['axis']} | {v['value']:g} | {v['power']} | {v['npv_m']:.2f} | {v['delta_to_same_power_reference_m']:+.2f} |")
    lines += ["", "Hardware-life scenarios change the economic cash replacement schedule while keeping the assumed tax-allowance life at 60 months. Tax deductions stop when equipment is disposed; no tax credit for an unrecovered basis is assumed. Accounting lives, tax allowances and economic replacement cycles are distinct.", "",
              "## Hardware horizon and residual-value challenge", "",
              "A fixed endpoint can penalize a recent replacement. The following recovery fractions apply to the final vintage's cost multiplied by its remaining economic-life fraction; they are not market resale observations. Any gain above tax basis is taxed. Earlier replaced vintages receive zero resale in every case.", "",
              "| Economic life months | Terminal recovery fraction | NPV |", "|---:|---:|---:|"]
    for v in r["hardware_life_resale_scenarios"]:
        lines.append(f"| {v['hardware_economic_life_months']} | {v['recovery_fraction']:.0%} | {v['npv_m']:.2f} |")
    lines += ["", "Replacement schedules create discontinuities outside the displayed delay range: moving a purchase beyond the common endpoint can increase modeled NPV even with a longer delay. The reported 0-24-month crossing is not a universal or monotone break-even rule. Use a longer horizon and independently supported resale/continuation values before underwriting an actual investment.", "",
              "The incident is a single conditional event in month 36, not an annual frequency. Lost sales remove the recoverable workload fraction; variable power savings, service credits and recovery spending are separate. No probability is inferred from industry surveys. A carbon-cost row is a hypothetical cost stress, not a claim that a jurisdiction imposes that price.", "",
              "## Conditional cancellation before hardware commitment", "",
              "| Month | Recovery of committed non-land infrastructure | Gross recovery | NPV |", "|---:|---:|---:|---:|"]
    for v in r["cancellation_scenarios"]:
        lines.append(f"| {v['cancel_month']} | {v['infrastructure_recovery_fraction']:.0%} | {v['gross_recovery_m']:.2f} | {v['npv_m']:.2f} |")
    lines += ["", "Cancellation assumes a $20m exit cost, land recovery at its assumed sale fraction, and no tax-loss credit. No hardware or working capital is committed. This is distinct from retiring an operating site, and it does not estimate Caledonia's actual sunk costs.", "",
              "## Boundaries and reproduction", "",
              "Positive project NPV does not establish stock upside. A calibrated issuer bridge requires site ownership, incremental demand, contracts, tax treatment, financing/lease recourse and the number of affected projects; market pricing and consensus are not modeled. No ESG discount-rate adjustment is added.", "",
              "Cash taxes apply only to positive monthly taxable income; no loss carryforward/refund is assumed. Capital allowances are simplified straight-line assumptions, not tax advice. Land/building/hardware disposal gains are taxed if above remaining basis; disposal losses receive no assumed relief. Cash flows are constant purchasing-power dollars, discounted at an assumed real 8%; no inflation, terminal multiple or grid-backup credit is included.", "",
              "```bash", "python examples/ai-infrastructure/model.py --check", "python -m unittest discover -s tests -p test_ai_infrastructure.py -v", "```", "",
              "[Investment memo](README.md) · [Assumptions](inputs.json) · [Monthly cash flows](results.json) · [Methods](METHODS.md) · [Primary evidence](evidence/PROJECT_TRACKER.md)"]
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    p = json.loads((HERE / "inputs.json").read_text())
    result = build(p)
    targets = {HERE / "results.json": json.dumps(result, indent=2, allow_nan=False) + "\n",
               HERE / "RESULTS.md": render(result)}
    if args.write:
        for path, content in targets.items():
            path.write_text(content, encoding="utf-8")
        print("Wrote scenario results; issuer underwriting remains NEEDS_DATA.")
    elif args.check:
        for path, content in targets.items():
            if not path.exists() or path.read_text(encoding="utf-8") != content:
                raise SystemExit(f"FAIL: stale/missing {path.name}; investigate before --write")
        print("PASS: monthly cash flows and sensitivity report match; no issuer calibration claimed.")
    else:
        print(render(result))


if __name__ == "__main__":
    main()
