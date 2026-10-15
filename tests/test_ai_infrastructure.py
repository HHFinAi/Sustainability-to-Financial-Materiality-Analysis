"""Economic invariants for the original fixed-horizon infrastructure model."""
import importlib.util
import json
import math
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
CASE = ROOT / "examples/ai-infrastructure"
SPEC = importlib.util.spec_from_file_location("ai_infrastructure", CASE / "model.py")
MODEL = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODEL)


class InfrastructureTest(unittest.TestCase):
    def setUp(self):
        self.p = json.loads((CASE / "inputs.json").read_text())

    def test_it_load_is_not_facility_load(self):
        r = MODEL.calculate(self.p)
        self.assertAlmostEqual(r["annual_facility_mwh_before_incident"], 705180)
        self.assertAlmostEqual(r["annual_power_cost_before_incident_m"], 56.4144)

    def test_hardware_and_wc_only_at_commissioning(self):
        r = MODEL.calculate(self.p, delay_months=12)
        self.assertEqual(r["hardware_purchase_months"], [12, 72])
        self.assertEqual(r["cash_flows"][0]["hardware_capex_m"], 0)
        self.assertEqual(r["cash_flows"][12]["hardware_capex_m"], 600)
        self.assertEqual(r["cash_flows"][12]["revenue_m"], 0)
        self.assertGreater(r["cash_flows"][13]["revenue_m"], 0)

    def test_common_horizon_loses_operating_months(self):
        r = MODEL.calculate(self.p, delay_months=24)
        self.assertEqual(r["operating_months"], 96)
        self.assertEqual(r["cash_flows"][-1]["month"], 120)
        self.assertEqual(r["holding_cost_total_m"], 48)
        self.assertLess(r["npv_m"], MODEL.calculate(self.p)["npv_m"])

    def test_replacement_is_cash_cost_and_no_terminal_purchase(self):
        p = {**self.p, "hardware_life_months": 36}
        r = MODEL.calculate(p)
        self.assertEqual(r["hardware_purchase_months"], [0, 36, 72, 108])
        self.assertEqual(r["total_hardware_capex_m"], 2400)
        self.assertEqual(r["cash_flows"][-1]["hardware_capex_m"], 0)

    def test_cash_tax_never_creates_unusable_loss_refund(self):
        p = {**self.p, "revenue_m_per_utilized_mw_year": 0}
        r = MODEL.calculate(p, delay_months=12)
        self.assertTrue(all(x["cash_tax_m"] >= 0 for x in r["cash_flows"]))
        self.assertEqual(sum(x["cash_tax_m"] for x in r["cash_flows"]), 0)

    def test_zero_discount_npv_equals_cash_sum(self):
        r = MODEL.calculate({**self.p, "discount_rate": 0})
        self.assertAlmostEqual(r["npv_m"], math.fsum(x["fcf_m"] for x in r["cash_flows"]))

    def test_revenue_hurdle_really_clears_npv(self):
        for power, delay in (("grid", 0), ("grid", 24), ("gas", 6)):
            hurdle = MODEL.revenue_hurdle(self.p, power, delay)
            p = {**self.p, "revenue_m_per_utilized_mw_year": hurdle}
            self.assertAlmostEqual(MODEL.calculate(p, power, delay)["npv_m"], 0, places=7)

    def test_gas_cost_components_not_grid_bill(self):
        r = MODEL.calculate(self.p, "gas")
        self.assertAlmostEqual(r["annual_power_cost_before_incident_m"], 705180 * (6 * 9 + 14) / 1e6 + 10)
        p = {**self.p, "grid_power_usd_per_mwh": 999}
        self.assertAlmostEqual(MODEL.calculate(p, "gas")["npv_m"], r["npv_m"])

    def test_incident_once_and_recovery_excluded_from_lost_sales(self):
        p = {**self.p, "event_outage_hours": 24}
        r = MODEL.calculate(p)
        affected = [x for x in r["cash_flows"] if x["incident_cost_m"]]
        self.assertEqual(len(affected), 1)
        self.assertEqual(affected[0]["month"], 36)
        self.assertAlmostEqual(affected[0]["lost_revenue_m"], 434 / 8760 * 24 * 0.5)
        self.assertLess(r["npv_m"], MODEL.calculate(self.p)["npv_m"])

    def test_fully_recoverable_workload_has_no_lost_sales(self):
        p = {**self.p, "event_outage_hours": 24, "recoverable_workload_fraction": 1,
             "event_service_credit_m_per_hour": 0, "event_recovery_cost_m": 0}
        self.assertAlmostEqual(MODEL.calculate(p)["npv_m"], MODEL.calculate(self.p)["npv_m"])

    def test_wc_released_exactly_once(self):
        r = MODEL.calculate(self.p, delay_months=6)
        flows = [x["working_capital_change_m"] for x in r["cash_flows"]]
        self.assertAlmostEqual(sum(flows), 0)
        self.assertEqual(len([x for x in flows if x != 0]), 2)

    def test_terminal_hardware_recovery_only_on_remaining_life(self):
        p = {**self.p, "hardware_life_months": 36, "hardware_sale_fraction_of_remaining_economic_cost": 0.5}
        last = MODEL.calculate(p)["cash_flows"][-1]
        # Last replacement at month 108: 12 of 36 months consumed.
        self.assertAlmostEqual(last["asset_sale_m"], 20 + 80 + 600 * (1 - 12/36) * 0.5)

    def test_economic_life_does_not_change_tax_allowance_life(self):
        p = {**self.p, "hardware_life_months": 84}
        r = MODEL.calculate(p)
        # The original vintage is fully tax-depreciated after month60, but
        # remains in service until month84. The replacement starts month85.
        d = [x["depreciation_m"] for x in r["cash_flows"]]
        self.assertAlmostEqual(d[60] - d[61], 600/60)
        self.assertAlmostEqual(d[85] - d[84], 600/60)

    def test_cancel_does_not_commit_hardware(self):
        a = MODEL.cancellation(self.p)
        b = MODEL.cancellation({**self.p, "hardware_capex_m": 900})
        self.assertEqual(a["npv_m"], b["npv_m"])
        self.assertFalse(a["hardware_and_working_capital_committed"])

    def test_replacement_crossing_terminal_boundary_is_disclosed_discontinuity(self):
        before = MODEL.calculate(self.p, delay_months=59)
        at = MODEL.calculate(self.p, delay_months=60)
        self.assertEqual(before["hardware_purchase_months"], [59, 119])
        self.assertEqual(at["hardware_purchase_months"], [60])
        self.assertGreater(at["npv_m"], before["npv_m"])

    def test_retired_tax_basis_does_not_generate_automatic_refund(self):
        # Replacing after36months leaves tax basis; month36 has only the normal
        # 60-month allowance, not an extra disposal-loss deduction.
        p = {**self.p, "hardware_life_months": 36}
        r = MODEL.calculate(p)
        self.assertAlmostEqual(r["cash_flows"][36]["depreciation_m"], r["cash_flows"][35]["depreciation_m"])
        self.assertAlmostEqual(r["cash_flows"][37]["depreciation_m"], r["cash_flows"][35]["depreciation_m"])

    def test_terminal_disposal_gain_is_taxed(self):
        no_gain = MODEL.calculate({**self.p, "building_sale_fraction": 0.5})
        gain = MODEL.calculate({**self.p, "building_sale_fraction": 1.0})
        self.assertAlmostEqual(gain["cash_flows"][-1]["cash_tax_m"] - no_gain["cash_flows"][-1]["cash_tax_m"], 200 * 0.25)

    def test_invalid_probability_like_fractions_and_dates_rejected(self):
        for change in ({"utilization": 1.1}, {"pue": 0.9}, {"cash_tax_rate": 1},
                       {"event_outage_hours": 1000}, {"hardware_life_months": True},
                       {"gas_usd_per_mmbtu": float("nan")}, {"building_life_months": 12}):
            with self.assertRaises(ValueError):
                MODEL.calculate({**self.p, **change})
        with self.assertRaises(ValueError):
            MODEL.calculate(self.p, delay_months=120)


if __name__ == "__main__":
    unittest.main()
