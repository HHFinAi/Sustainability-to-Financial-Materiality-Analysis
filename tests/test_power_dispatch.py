"""Hourly energy-adequacy pilot; deterministic physical checks only."""
import copy
import importlib.util
import math
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / "examples" / "ai-power-stack"
SPEC = importlib.util.spec_from_file_location("hourly_power_dispatch", HERE / "dispatch.py")
DISPATCH = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(DISPATCH)


class HourlyAdequacy(unittest.TestCase):
    def setUp(self):
        self.p = DISPATCH.load()

    def test_daily_trace_does_not_claim_annual_uptime(self):
        x = DISPATCH.simulate(self.p)
        self.assertEqual(x["hours_simulated"], 24)
        self.assertFalse(x["annual_uptime_inferred"])
        self.assertIsNone(x["npv_or_capital_value_usd_m"])
        self.assertGreater(x["unserved_mwh"], 0)
        self.assertTrue(all(r["ending_soc_mwh"] >= x["battery_reserve_floor_mwh"] - 1e-9
                            for r in x["hourly_balance"]))

    def test_generator_that_covers_peak_fills_all_hours(self):
        p = copy.deepcopy(self.p)
        p["dispatchable_generation_mw"] = 100
        p["battery_power_mw"] = 0
        p["battery_energy_mwh"] = 0
        p["battery_reserve_fraction"] = 0
        p["initial_soc_fraction"] = 0
        a = DISPATCH.simulate(p)
        self.assertAlmostEqual(a["unserved_mwh"], 0)
        self.assertEqual(a["trace_fraction_hours_fully_served"], 1)

    def test_strict_reserve_stops_free_battery_energy(self):
        p = copy.deepcopy(self.p)
        p["battery_reserve_fraction"] = 0.5
        p["initial_soc_fraction"] = 0.5
        a = DISPATCH.simulate(p)
        self.assertGreater(a["unserved_mwh"], 0)
        self.assertAlmostEqual(a["hourly_balance"][0]["served_by_battery_mwh"], 0)

    def test_hourly_load_balances(self):
        a = DISPATCH.simulate(self.p)
        for r in a["hourly_balance"]:
            self.assertAlmostEqual(
                r["load_mwh"],
                r["served_by_solar_mwh"] + r["served_by_generation_mwh"] +
                r["served_by_battery_mwh"] + r["unserved_mwh"]
            )

    def test_bad_physics_rejected(self):
        for key, val in (
            ("battery_roundtrip_efficiency", 1.1),
            ("battery_energy_mwh", -100),
            ("battery_reserve_fraction", True),
            ("initial_soc_fraction", 0.1),
            ("time_step_hours", 0),
        ):
            p = copy.deepcopy(self.p)
            p[key] = val
            with self.assertRaises(ValueError):
                DISPATCH.simulate(p)
        p = copy.deepcopy(self.p)
        p["hours"][0]["solar_available_mw"] = float("nan")
        with self.assertRaises(ValueError):
            DISPATCH.simulate(p)


if __name__ == "__main__":
    unittest.main()
