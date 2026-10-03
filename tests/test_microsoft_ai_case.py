"""Arithmetic and controlled evidence-boundary tests, not validation of issuer forecasts."""
from __future__ import annotations

from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import unittest

CASE = Path(__file__).resolve().parents[1] / "examples" / "microsoft-ai"


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


model = load_module("hhfinai_cooling_example", CASE / "model.py")
checks = load_module("hhfinai_claim_example", CASE / "claim_checks.py")


class MicrosoftAIExampleTests(unittest.TestCase):
    def setUp(self):
        self.p = json.loads((CASE / "inputs.json").read_text(encoding="utf-8"))

    def test_physical_units(self):
        r = model.calculate(self.p)
        self.assertAlmostEqual(r["it_mwh_per_year"], 613200)
        self.assertAlmostEqual(r["extra_electricity_mwh_per_year"], 12264)
        self.assertAlmostEqual(r["avoided_direct_water_m3_per_year"], 183960)

    def test_bills(self):
        r = model.calculate(self.p)
        self.assertAlmostEqual(r["extra_power_cost_usd_m_per_year"], 0.98112)
        self.assertAlmostEqual(r["water_bill_saving_usd_m_per_year"], 0.55188)
        self.assertAlmostEqual(r["direct_operating_delta_usd_m_per_year"], -0.67924)

    def test_tax_bridge(self):
        r = model.calculate(self.p)
        self.assertAlmostEqual(r["annual_incremental_fcf_usd_m"], -0.13443)

    def test_break_even_reprices_to_zero(self):
        r = model.calculate(self.p)
        p = {**self.p, "additional_operating_benefit_usd_m_per_year":
             r["break_even_additional_pretax_benefit_usd_m_per_year"]}
        self.assertAlmostEqual(model.calculate(p)["incremental_npv_usd_m"], 0, places=9)

    def test_zero_discount(self):
        r = model.calculate({**self.p, "discount_rate": 0.0})
        self.assertEqual(r["annuity_factor"], 10)
        self.assertAlmostEqual(r["incremental_npv_usd_m"], -16.3443)

    def test_delay_hurdle(self):
        old = model.calculate(self.p)
        new = model.calculate({**self.p, "commissioning_delay_years": 1})
        self.assertGreater(new["break_even_additional_pretax_benefit_usd_m_per_year"],
                           old["break_even_additional_pretax_benefit_usd_m_per_year"])

    def test_capex_counted_once(self):
        p = {**self.p, "cash_tax_rate": 0.0,
             "avoided_cooling_water_l_per_it_kwh": 0.0,
             "incremental_pue": 0.0, "incremental_maintenance_usd_m_per_year": 0.0}
        self.assertEqual(model.calculate(p)["incremental_npv_usd_m"], -15.0)

    def test_reject_nonfinite_boolean_and_missing(self):
        for value in (float("nan"), float("inf"), True, "80", None, -1):
            with self.subTest(value=value), self.assertRaises(ValueError):
                model.calculate({**self.p, "electricity_usd_per_mwh": value})

    def test_reject_bad_ranges_and_classification(self):
        for key, value in (("cash_tax_rate", 1), ("average_it_load_fraction", 1.1),
                           ("asset_life_years", 10.5), ("commissioning_delay_years", -1),
                           ("money_unit", "billion"), ("classification", "REPORTED_FACT")):
            with self.subTest(key=key), self.assertRaises(ValueError):
                model.calculate({**self.p, key: value})

    def test_checked_in_report(self):
        self.assertEqual(model.render(self.p), (CASE / "RESULTS.md").read_text(encoding="utf-8"))

    def test_financial_scope_bridge(self):
        records = json.loads((CASE / "evidence.json").read_text())["records"]
        values = {r["id"]: r["value"] for r in records}
        fcf25 = values["MS1-cash_from_operations-2025"] - values["MS1-cash_additions_to_property_and_equipment-2025"]
        fcf24 = values["MS1-cash_from_operations-2024"] - values["MS1-cash_additions_to_property_and_equipment-2024"]
        self.assertEqual((fcf25, fcf24, fcf25-fcf24), (71611, 74071, -2460))

    def test_engineered_metadata_cases(self):
        records = json.loads((CASE / "evidence.json").read_text())["records"]
        result = checks.evaluate(records)
        self.assertEqual((result["case_count"], result["passed"]), (48, 48))
        self.assertFalse(result["llm_accuracy_measured"])

    def test_unknown_source_and_missing_field(self):
        record = json.loads((CASE / "evidence.json").read_text())["records"][0]
        claim = deepcopy(record)
        claim["source_id"] = "missing-source"
        claim.pop("period")
        self.assertEqual(set(checks.check_claim(claim, record)), {"source_id", "period"})


if __name__ == "__main__":
    unittest.main()
