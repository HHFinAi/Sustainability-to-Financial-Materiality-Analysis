"""November 2026 power-stack extension tests; does not validate issuer economics."""
import importlib.util
import json
import math
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / "examples" / "ai-power-stack"
SPEC = importlib.util.spec_from_file_location("ai_power_stack", HERE / "model.py")
MODEL = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODEL)


class PowerStackTest(unittest.TestCase):
    def setUp(self):
        self.base, self.config = MODEL.load()

    def test_all_routes_share_ownership_horizon_and_load(self):
        results = MODEL.build(self.base, self.config)
        self.assertEqual(results["investment_decision"], "NEEDS_DATA")
        self.assertEqual(results["facility_peak_mw"], 115)
        self.assertEqual(results["horizon_months"], 120)
        self.assertEqual(set(results["reference"]), {"grid", "gas", "sofc"})
        self.assertTrue(all(row["horizon_months"] == 120 for row in results["reference"].values()))
        self.assertTrue(all(row["screen_is_reliability_proof"] is False
                            for row in results["reference"].values()))

    def test_october_grid_gas_economics_unchanged(self):
        engine = MODEL._original_engine()
        for name in ("grid", "gas"):
            delay = self.config["route_default_delays_months"][name]
            expected = engine.calculate(self.base, power=name, delay_months=delay)["npv_m"]
            self.assertAlmostEqual(MODEL.one_route(self.base, self.config, name)["npv_m"], expected)

    def test_sofc_uses_same_cashflow_engine(self):
        route = MODEL.one_route(self.base, self.config, "sofc")
        p = dict(self.base, **self.config["routes"]["sofc"]["overrides"])
        expected = MODEL._original_engine().calculate(
            p, power="gas", delay_months=self.config["route_default_delays_months"]["sofc"])
        self.assertAlmostEqual(route["npv_m"], expected["npv_m"])
        self.assertEqual(route["total_hardware_capex_m"], expected["total_hardware_capex_m"])
        self.assertIn("proxy", route["modeling_route"])

    def test_inadequate_capacity_blocks_npv(self):
        config = json.loads(json.dumps(self.config))
        config["routes"]["sofc"]["rated_mw"] = 100
        row = MODEL.one_route(self.base, config, "sofc")
        self.assertEqual(row["status"], "BLOCKED_INSUFFICIENT_CAPACITY")
        self.assertIsNone(row["npv_m"])

    def test_missing_economic_assumptions_and_bad_inputs_fail(self):
        for changed in (
            ("grid", "availability_factor", 1.1),
            ("grid", "availability_factor", True),
            ("sofc", "rated_mw", -1),
            ("sofc", "rated_mw", float("nan")),
        ):
            name, field, val = changed
            config = json.loads(json.dumps(self.config))
            config["routes"][name][field] = val
            with self.assertRaises(ValueError):
                MODEL.validate(self.base, config)
        config = json.loads(json.dumps(self.config))
        del config["routes"]["sofc"]["overrides"]["generation_fixed_om_m_per_year"]
        with self.assertRaises(ValueError):
            MODEL.validate(self.base, config)

    def test_delay_changes_npv_and_reference_is_consistent(self):
        early = MODEL.one_route(self.base, self.config, "grid", 0)
        late = MODEL.one_route(self.base, self.config, "grid", 18)
        self.assertGreater(early["npv_m"], late["npv_m"])
        results = MODEL.build(self.base, self.config)
        self.assertAlmostEqual(results["reference"]["grid"]["delta_to_grid_default_m"], 0)
        self.assertEqual(len(results["commissioning_delay_sensitivities"]), 12)

    def test_generation_fuel_cost_deteriorates_value(self):
        config = json.loads(json.dumps(self.config))
        before = MODEL.one_route(self.base, config, "sofc")["npv_m"]
        config["routes"]["sofc"]["overrides"]["heat_rate_mmbtu_per_mwh"] += 4
        after = MODEL.one_route(self.base, config, "sofc")["npv_m"]
        self.assertTrue(math.isfinite(before))
        self.assertLess(after, before)

    def test_no_tax_credit_or_unverified_availability_inferred(self):
        result = MODEL.build(self.base, self.config)
        self.assertEqual(result["model_status"], "ARITHMETIC_SCREEN_ONLY")
        self.assertIn("No CCS or 45Q benefit", result["exclusions"])
        self.assertTrue(all(x["screen_is_reliability_proof"] is False
                            for x in result["commissioning_delay_sensitivities"]))


if __name__ == "__main__":
    unittest.main()
