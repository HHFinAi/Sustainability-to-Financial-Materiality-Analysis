"""November 2026 add-on: compare a 100-MW IT load using the frozen October engine.

No proprietary research is embedded. This is a model-of-assumptions, not a forecast.
Grid and gas retain the baseline case parameters; SOFC parameterizes the baseline
owned-gas-generation route. That deliberately shares tax, capex, horizon, hardware
replacement, working-capital, terminal and discounting conventions.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = HERE.parent / "ai-infrastructure"
CLASSIFICATION = "ILLUSTRATIVE_ANALYST_ASSUMPTIONS_NOT_ISSUER_ECONOMICS"
OVERRIDES = {
    "generation_capex_m", "generation_life_months",
    "heat_rate_mmbtu_per_mwh", "generation_variable_om_usd_per_mwh",
    "generation_fixed_om_m_per_year", "generation_tco2_per_mwh"
}
NAMES = {"grid", "gas", "sofc"}


def _original_engine():
    spec = importlib.util.spec_from_file_location("ai_infrastructure_base", BASE / "model.py")
    if spec is None or spec.loader is None:
        raise ValueError("October baseline model not found")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load():
    return (
        json.loads((BASE / "inputs.json").read_text(encoding="utf-8")),
        json.loads((HERE / "inputs.json").read_text(encoding="utf-8")),
    )


def _nonnegative(value, label):
    if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
        raise ValueError(f"{label}: finite nonnegative number required")
    return float(value)


def validate(base, config):
    if config.get("classification") != CLASSIFICATION:
        raise ValueError("Unambiguous illustrative classification required")
    if config.get("source_case") != "../ai-infrastructure/inputs.json":
        raise ValueError("Unexpected baseline reference")
    if base.get("classification") != "ILLUSTRATIVE_ASSUMPTIONS_NOT_ISSUER_ECONOMICS":
        raise ValueError("Unrecognized October baseline")
    if config.get("owner_boundary") != "campus_owner_pays_all_infrastructure_hardware_and_operating_costs":
        raise ValueError("Counterfactual requires matching owner boundaries")
    routes = config.get("routes")
    delays = config.get("route_default_delays_months")
    if not isinstance(routes, dict) or set(routes) != NAMES:
        raise ValueError("Exactly grid, gas and sofc routes required")
    if not isinstance(delays, dict) or set(delays) != NAMES:
        raise ValueError("Exactly three commissioning delays required")
    samples = config.get("sensitivity_delays_months")
    if (not isinstance(samples, list) or not samples
            or len(set(map(str, samples))) != len(samples)):
        raise ValueError("Unique delay-sensitivity list required")
    for name, route in routes.items():
        if not isinstance(route, dict) or set(route) != {"rated_mw", "availability_factor", "overrides"}:
            raise ValueError(f"{name}: unexpected capacity or override fields")
        rated = _nonnegative(route["rated_mw"], f"{name}.rated_mw")
        availability = _nonnegative(route["availability_factor"], f"{name}.availability_factor")
        if rated <= 0 or not 0 < availability <= 1:
            raise ValueError(f"{name}: invalid capacity screen")
        overrides = route["overrides"]
        if not isinstance(overrides, dict) or set(overrides) - OVERRIDES:
            raise ValueError(f"{name}: unauthorized economics override")
        if name != "sofc" and overrides:
            raise ValueError("October grid/gas economics must remain unchanged")
        if name == "sofc" and set(overrides) != OVERRIDES:
            raise ValueError("SOFC operating and owned-capital assumptions required")
        for field, value in overrides.items():
            _nonnegative(value, f"{name}.{field}")
        if name == "sofc":
            life = overrides["generation_life_months"]
            if type(life) is not int or life < base["horizon_months"]:
                raise ValueError("SOFC replacement is not modeled: life must cover horizon")
        d = delays[name]
        if type(d) is not int or not 0 <= d < base["horizon_months"]:
            raise ValueError(f"{name}: invalid commissioning delay")
    for d in samples:
        if type(d) is not int or not 0 <= d < base["horizon_months"]:
            raise ValueError("Invalid delay sensitivity")
    if not isinstance(config.get("exclusions"), list) or not config["exclusions"]:
        raise ValueError("Missing underwriting limitations")
    _original_engine().validate(base)


def one_route(base, config, name, delay=None):
    if name not in NAMES:
        raise ValueError("Unknown power route")
    validate(base, config)
    if delay is None:
        delay = config["route_default_delays_months"][name]
    if type(delay) is not int or not 0 <= delay < base["horizon_months"]:
        raise ValueError("Invalid commissioning delay")
    route = config["routes"][name]
    peak = base["it_capacity_mw"] * base["pue"]
    screened = route["rated_mw"] * route["availability_factor"]
    result = {
        "route": name,
        "delay_months": delay,
        "owner_boundary": config["owner_boundary"],
        "facility_peak_mw": peak,
        "screened_capacity_mw": screened,
        "capacity_screen_definition": config["firm_capacity_screen"],
        "screen_is_reliability_proof": False,
        "status": "ILLUSTRATIVE",
        "npv_m": None,
        "delta_to_grid_default_m": None,
    }
    if screened + 1e-9 < peak:
        result["status"] = "BLOCKED_INSUFFICIENT_CAPACITY"
        return result
    p = dict(base)
    p.update(route["overrides"])
    engine = _original_engine()
    backend = "grid" if name == "grid" else "gas"
    calculated = engine.calculate(p, power=backend, delay_months=delay)
    result.update({
        "npv_m": calculated["npv_m"],
        "annual_power_cost_m": calculated["annual_power_cost_before_incident_m"],
        "total_hardware_capex_m": calculated["total_hardware_capex_m"],
        "initial_infrastructure_capex_m": calculated["initial_infrastructure_capex_m"],
        "operating_months": calculated["operating_months"],
        "horizon_months": calculated["horizon_months"],
        "modeling_route": ("owned_sofc_proxy_using_parameterized_gas_branch"
                           if name == "sofc" else "unchanged_october_" + name),
    })
    return result


def build(base, config):
    validate(base, config)
    reference = {name: one_route(base, config, name) for name in sorted(NAMES)}
    grid = reference["grid"]["npv_m"]
    scenarios = []
    for name in sorted(NAMES):
        for month in config["sensitivity_delays_months"]:
            row = one_route(base, config, name, month)
            if grid is not None and row["npv_m"] is not None:
                row["delta_to_grid_default_m"] = row["npv_m"] - grid
            scenarios.append(row)
    for row in reference.values():
        if grid is not None and row["npv_m"] is not None:
            row["delta_to_grid_default_m"] = row["npv_m"] - grid
    return {
        "case_id": config["case_id"],
        "prepared_on": config["prepared_on"],
        "classification": CLASSIFICATION,
        "investment_decision": "NEEDS_DATA",
        "model_status": "ARITHMETIC_SCREEN_ONLY",
        "currency": base["currency"],
        "money_unit": base["money_unit"],
        "horizon_months": base["horizon_months"],
        "it_capacity_mw": base["it_capacity_mw"],
        "facility_peak_mw": base["it_capacity_mw"] * base["pue"],
        "owner_boundary": config["owner_boundary"],
        "reference": reference,
        "commissioning_delay_sensitivities": scenarios,
        "exclusions": config["exclusions"],
    }


def main():
    parser = argparse.ArgumentParser(description="Illustrative AI power-stack comparison")
    parser.add_argument("--write", action="store_true", help="write deterministic results.json")
    parser.add_argument("--check", action="store_true", help="validate and check invariants")
    args = parser.parse_args()
    base, config = load()
    result = build(base, config)
    if args.check:
        assert result["horizon_months"] == 120
        assert set(result["reference"]) == NAMES
        assert result["investment_decision"] == "NEEDS_DATA"
        assert all(x["npv_m"] is None or math.isfinite(x["npv_m"])
                   for x in result["commissioning_delay_sensitivities"])
        print("CHECK_OK: 3 routes, common cash-flow conventions, controlled capacity screens")
    if args.write:
        (HERE / "results.json").write_text(
            json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n",
            encoding="utf-8")
    elif not args.check:
        print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
