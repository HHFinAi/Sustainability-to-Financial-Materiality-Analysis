"""Hourly energy-adequacy *toy* simulation; not an annual uptime guarantee.

Dispatchable power is assumed available every simulated hour. Solar is net
AC power. Battery reserves are held strictly, even during shortfalls.
No prices, failure distributions, degradation or maintenance are modeled.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
CLASSIFICATION = "SYNTHETIC_HOURLY_DATA_NOT_A_SITE"


def numeric(value, label, *, positive=False):
    if type(value) not in (int, float) or not math.isfinite(value):
        raise ValueError(f"{label}: finite number required")
    if value < 0 or (positive and value <= 0):
        raise ValueError(f"{label}: invalid range")
    return float(value)


def load():
    return json.loads((HERE / "synthetic-hours.json").read_text(encoding="utf-8"))


def simulate(p):
    if p.get("classification") != CLASSIFICATION:
        raise ValueError("Hourly input must be explicitly synthetic")
    if p.get("time_step_hours") != 1 or type(p.get("time_step_hours")) is not int:
        raise ValueError("Only 1-hour intervals are supported")
    g = numeric(p.get("dispatchable_generation_mw"), "generation")
    power = numeric(p.get("battery_power_mw"), "battery power")
    energy = numeric(p.get("battery_energy_mwh"), "battery energy")
    reserve = numeric(p.get("battery_reserve_fraction"), "battery reserve")
    soc_frac = numeric(p.get("initial_soc_fraction"), "initial charge")
    rte = numeric(p.get("battery_roundtrip_efficiency"), "efficiency", positive=True)
    if not (0 <= reserve <= soc_frac <= 1 and 0 < rte <= 1):
        raise ValueError("Invalid reserve, SOC or efficiency")
    if energy == 0 and power != 0:
        raise ValueError("Battery capacity cannot be zero with nonzero battery power")
    trace = p.get("hours")
    if not isinstance(trace, list) or not 1 <= len(trace) <= 8760:
        raise ValueError("One to 8760 explicit hourly records required")
    minimum = reserve * energy
    soc = soc_frac * energy
    eta = math.sqrt(rte)
    total_unserved, charged, discharged, curtailed, served_hours = 0.0, 0.0, 0.0, 0.0, 0
    rows = []
    for i, item in enumerate(trace):
        if not isinstance(item, dict) or set(item) != {"load_mw", "solar_available_mw"}:
            raise ValueError(f"hour {i}: explicit load/solar required")
        load_mw = numeric(item["load_mw"], "load")
        solar_mw = numeric(item["solar_available_mw"], "solar")
        solar_load = min(load_mw, solar_mw)
        generator = min(g, load_mw - solar_load)
        short = load_mw - solar_load - generator
        battery_delivered = min(short, power, max(0.0, soc - minimum) * eta)
        soc -= battery_delivered / eta
        excess_solar = max(0.0, solar_mw - solar_load)
        # There is no simultaneous charge/discharge: no solar surplus exists
        # in an hour with unmet load under the stated dispatch priority.
        battery_charged = min(excess_solar, power, max(0.0, energy - soc) / eta)
        soc += battery_charged * eta
        unserved = max(0.0, short - battery_delivered)
        spill = max(0.0, excess_solar - battery_charged)
        if soc + 1e-9 < minimum or soc > energy + 1e-9:
            raise ArithmeticError("SOC violates battery physical bounds")
        if abs((solar_load + generator + battery_delivered + unserved) - load_mw) > 1e-8:
            raise ArithmeticError("Hourly energy conservation violated")
        if battery_delivered > 1e-9 and battery_charged > 1e-9:
            raise ArithmeticError("Simultaneous battery charge and discharge")
        total_unserved += unserved
        charged += battery_charged
        discharged += battery_delivered
        curtailed += spill
        if unserved <= 1e-9:
            served_hours += 1
        rows.append({
            "hour_index": i, "load_mwh": load_mw,
            "served_by_solar_mwh": solar_load,
            "served_by_generation_mwh": generator,
            "served_by_battery_mwh": battery_delivered,
            "charged_from_solar_mwh": battery_charged,
            "unserved_mwh": unserved, "curtailed_solar_mwh": spill,
            "ending_soc_mwh": soc,
        })
    return {
        "classification": CLASSIFICATION,
        "hours_simulated": len(rows),
        "trace_hours_fully_served": served_hours,
        "trace_fraction_hours_fully_served": served_hours / len(rows),
        "annual_uptime_inferred": False,
        "outage_probability_inferred": False,
        "npv_or_capital_value_usd_m": None,
        "battery_reserve_floor_mwh": minimum,
        "battery_final_soc_mwh": soc,
        "unserved_mwh": total_unserved,
        "battery_charge_energy_mwh": charged,
        "battery_discharge_to_load_mwh": discharged,
        "curtailed_solar_mwh": curtailed,
        "hourly_balance": rows,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = simulate(load())
    if args.check:
        assert result["annual_uptime_inferred"] is False
        assert result["npv_or_capital_value_usd_m"] is None
        assert result["hours_simulated"] == 24
        print("CHECK_OK: hourly mass balance, battery reserve and no inferred uptime/NPV")
    else:
        print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
