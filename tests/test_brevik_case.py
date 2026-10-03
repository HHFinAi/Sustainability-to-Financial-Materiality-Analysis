"""Economic invariants and reproducibility for the Brevik portfolio case."""
import csv
from copy import deepcopy
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
CASE = ROOT / "examples" / "heidelberg-brevik"
spec = importlib.util.spec_from_file_location("brevik_model", CASE / "model.py")
model = importlib.util.module_from_spec(spec)
spec.loader.exec_module(model)


class BrevikCase(unittest.TestCase):
    def setUp(self):
        self.data = model.load_inputs()

    def test_committed_outputs_reproduce(self):
        for name, text in model.outputs(self.data).items():
            self.assertEqual((CASE / name).read_text(encoding="utf-8"), text, name)

    def test_no_capture_exceeds_nameplate(self):
        altered = deepcopy(self.data)
        altered["management_expectations"]["brevik_evozero_cement_tonnes"] = [1000000] * 5
        for row in model.project(altered, "upside"):
            self.assertLessEqual(row["captured_tonnes"], 400000)

    def test_losses_have_no_assumed_tax_refund(self):
        for row in model.project(self.data, "downside"):
            self.assertLess(row["operating_surplus_eur_m"], 0)
            self.assertEqual(row["cash_tax_eur_m"], 0)

    def test_break_even_and_cash_direction(self):
        for scenario in ("downside", "central_sensitivity"):
            premium = model.break_even_premium(self.data, scenario)
            self.assertAlmostEqual(model.window_pv(self.data, scenario, premium=premium), 0, places=8)
            self.assertLess(model.window_pv(self.data, scenario, premium=premium-1), 0)
            self.assertGreater(model.window_pv(self.data, scenario, premium=premium+1), 0)
        self.assertGreater(model.break_even_with_no_carbon(self.data), model.break_even_premium(self.data, "central_sensitivity"))

    def test_working_capital_is_change_not_balance(self):
        rows = model.project(self.data, "central_sensitivity")
        self.assertEqual(rows[-1]["delta_working_capital_eur_m"], 0)
        closing = rows[-1]["premium_revenue_eur_m"] * self.data["common_assumptions"]["premium_revenue_working_capital_fraction"]
        self.assertAlmostEqual(sum(row["delta_working_capital_eur_m"] for row in rows), closing)

    def test_dates_and_evidence_boundary(self):
        rows = model.project(self.data, "central_sensitivity")
        self.assertTrue(0 < rows[0]["years_from_valuation"] < 1)
        self.assertTrue(4 < rows[-1]["years_from_valuation"] < 5)
        with (CASE / "sources.csv").open(newline="", encoding="utf-8") as handle:
            sources = {row["id"]: row for row in csv.DictReader(handle)}
        for fact in self.data["facts"].values():
            self.assertIn(fact["source"], sources)
        self.assertIn(self.data["management_expectations"]["source"], sources)
        self.assertIn("no human approval", self.data["review_status"])


if __name__ == "__main__":
    unittest.main()
