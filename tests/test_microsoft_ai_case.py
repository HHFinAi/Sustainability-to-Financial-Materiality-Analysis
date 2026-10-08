"""Arithmetic and controlled evidence-boundary tests, not validation of issuer forecasts."""
from __future__ import annotations

from copy import deepcopy
import importlib.util
import json
import hashlib
import subprocess
import sys
from pathlib import Path
import unittest
from unittest.mock import patch

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

    def test_tax_charge_remains_when_deductions_unavailable(self):
        p = {**self.p, "operating_deduction_fraction": 0,
             "depreciation_deduction_fraction": 0,
             "additional_operating_benefit_usd_m_per_year": 3}
        r = model.calculate(p)
        # $3m benefit and water savings are taxed, but costs receive no shield.
        expected = (3 + 0.55188) * 0.75 - 0.98112 - 0.25
        self.assertAlmostEqual(r["annual_incremental_fcf_usd_m"], expected)
        self.assertEqual(r["tax_deduction_present_value_usd_m"], 0)
        no_tax = model.calculate({**p, "cash_tax_rate": 0})
        self.assertGreater(no_tax["incremental_npv_usd_m"], r["incremental_npv_usd_m"])

    def test_capital_allowance_unavailable_keeps_operating_deductions(self):
        reference = model.calculate(self.p)
        no_capital = model.calculate({**self.p, "depreciation_deduction_fraction": 0})
        expected_lost_shield = 15 / 10 * 0.25 * reference["annuity_factor"]
        self.assertAlmostEqual(reference["incremental_npv_usd_m"] -
                               no_capital["incremental_npv_usd_m"], expected_lost_shield)

    def test_deduction_delay_shifts_all_shields_and_keeps_tail(self):
        old = model.calculate(self.p)
        p = {**self.p, "tax_deduction_delay_years": 2}
        r = model.calculate(p)
        yearly_shield = (0.98112 + 0.25 + 1.5) * 0.25
        self.assertAlmostEqual(r["tax_deduction_present_value_usd_m"],
                               old["tax_deduction_present_value_usd_m"] / 1.08**2)
        self.assertAlmostEqual(r["cash_flows"][-1]["incremental_fcf_usd_m"], yearly_shield)
        self.assertEqual(r["cash_flows"][-1]["year_from_initial_capex"], 12)
        self.assertLess(r["incremental_npv_usd_m"], old["incremental_npv_usd_m"])
        self.assertAlmostEqual(r["cash_flows"][1]["incremental_fcf_usd_m"],
                               0.55188 * 0.75 - 0.98112 - 0.25)

    def test_hurdle_reprices_all_deduction_policies_to_zero(self):
        for overrides in ({"depreciation_deduction_fraction": 0},
                          {"operating_deduction_fraction": 0, "depreciation_deduction_fraction": 0},
                          {"tax_deduction_delay_years": 2},
                          {"tax_deduction_delay_years": 2, "commissioning_delay_years": 1}):
            p = {**self.p, **overrides}
            hurdle = model.calculate(p)["break_even_additional_pretax_benefit_usd_m_per_year"]
            with self.subTest(overrides=overrides):
                self.assertAlmostEqual(model.calculate({**p, "additional_operating_benefit_usd_m_per_year": hurdle})["incremental_npv_usd_m"], 0, places=9)

    def test_reliability_expected_loss_and_impossible_probability(self):
        r = model.reliability(self.p)
        self.assertAlmostEqual(r["expected_avoided_outage_hours_per_year"], 0.25 * 48 * 0.8)
        self.assertAlmostEqual(r["expected_avoided_pretax_cash_loss_usd_m_per_year"], 0.36)
        self.assertGreater(r["required_event_probability_at_assumed_duration"], 1)
        self.assertEqual(r["break_even_feasibility_at_assumed_duration"], "OUTSIDE_PROBABILITY_RANGE")

    def test_reliability_duration_breakpoint_reprices_to_zero(self):
        r = model.reliability(self.p)
        p = {**self.p, "reliability": {**self.p["reliability"],
             "disruption_duration_hours": r["required_disruption_duration_hours_at_assumed_probability"]}}
        self.assertAlmostEqual(model.reliability(p)["cooling_plus_reliability_npv_usd_m"], 0, places=9)

    def test_recovered_work_does_not_create_loss_value(self):
        for override in ({"recoverable_workload_fraction": 1},
                         {"protected_cash_contribution_usd_m_per_hour": 0},
                         {"risk_reduction_fraction": 0}, {"annual_event_probability": 0}):
            p = {**self.p, "reliability": {**self.p["reliability"], **override}}
            r = model.reliability(p)
            with self.subTest(override=override):
                self.assertEqual(r["expected_avoided_pretax_cash_loss_usd_m_per_year"], 0)
                if "annual_event_probability" in override:
                    self.assertIsNone(r["required_disruption_duration_hours_at_assumed_probability"])
                    self.assertGreater(r["required_event_probability_at_assumed_duration"], 1)
                else:
                    self.assertIsNone(r["required_event_probability_at_assumed_duration"])
                    self.assertEqual(r["break_even_feasibility_at_assumed_duration"], "NO_FINITE_BREAKPOINT")

    def test_expansion_counts_full_power_capex_and_replacement_once(self):
        r = model.capacity_expansion(self.p)
        self.assertAlmostEqual(r["annual_added_revenue_usd_m"], 28)
        self.assertAlmostEqual(r["annual_added_total_facility_mwh"], 10 * 0.7 * 8760 * 1.15)
        self.assertAlmostEqual(r["cash_flows"][0]["incremental_fcf_usd_m"], -104.4)
        self.assertEqual(r["hardware_replacements"], [{"year_from_initial_capex": 5, "hardware_capex_usd_m": 60}])
        flows = {x["year_from_initial_capex"]: x["incremental_fcf_usd_m"] for x in r["cash_flows"]}
        self.assertAlmostEqual(flows[1] - flows[5], 60)
        self.assertAlmostEqual(flows[10] - flows[9], 1.4)
        self.assertIsNone(r["required_added_mw_to_offset_existing_cooling_npv_at_constant_unit_economics"])

    def test_expansion_revenue_breakpoints_reprice_both_commitments(self):
        r = model.capacity_expansion(self.p)
        for key, result_key in (
                ("break_even_revenue_usd_m_per_fully_utilized_mw_year", "capacity_project_npv_usd_m"),
                ("break_even_revenue_including_existing_cooling_usd_m_per_fully_utilized_mw_year", "cooling_plus_separate_capacity_npv_usd_m")):
            p = {**self.p, "capacity_expansion": {**self.p["capacity_expansion"],
                 "revenue_usd_m_per_fully_utilized_mw_year": r[key]}}
            with self.subTest(key=key):
                self.assertAlmostEqual(model.capacity_expansion(p)[result_key], 0, places=9)

    def test_profitable_capacity_required_mw_prices_existing_cooling(self):
        p = {**self.p, "capacity_expansion": {**self.p["capacity_expansion"],
             "revenue_usd_m_per_fully_utilized_mw_year": 6.2}}
        r = model.capacity_expansion(p)
        self.assertGreater(r["cooling_plus_separate_capacity_npv_usd_m"], 0)
        required = r["required_added_mw_to_offset_existing_cooling_npv_at_constant_unit_economics"]
        p = {**p, "capacity_expansion": {**p["capacity_expansion"], "added_it_capacity_mw": required}}
        self.assertAlmostEqual(model.capacity_expansion(p)["cooling_plus_separate_capacity_npv_usd_m"], 0, places=9)

    def test_expansion_does_not_change_existing_workload(self):
        before = model.calculate(self.p)
        p = {**self.p, "capacity_expansion": {**self.p["capacity_expansion"], "added_it_capacity_mw": 20}}
        self.assertEqual(model.calculate(p), before)
        a = model.analysis(p)
        self.assertNotIn("combined_reliability_and_expansion_npv_usd_m", a)

    def test_routes_reject_unattributed_generic_benefit(self):
        p = {**self.p, "additional_operating_benefit_usd_m_per_year": 3}
        for fn in (model.reliability, model.capacity_expansion):
            with self.subTest(fn=fn.__name__), self.assertRaises(ValueError):
                fn(p)

    def test_missing_issuer_data_is_not_closed_by_arithmetic(self):
        a = model.analysis(self.p)
        self.assertEqual(a["issuer_underwriting_status"], "NEEDS_DATA")
        self.assertEqual(a["scenario_arithmetic_status"], "COMPLETE")
        self.assertEqual(len(a["issuer_evidence_gaps"]), 6)
        with self.assertRaises(ValueError):
            model.analysis({**self.p, "issuer_evidence_gaps": []})

    def test_nested_inputs_reject_invalid_physics_probability_and_cycles(self):
        for section, key, value, fn in (
                ("reliability", "annual_event_probability", 1.01, model.reliability),
                ("reliability", "risk_reduction_fraction", float("nan"), model.reliability),
                ("reliability", "disruption_duration_hours", 9000, model.reliability),
                ("reliability", "protected_cash_contribution_usd_m_per_hour", True, model.reliability),
                ("capacity_expansion", "total_facility_pue", 0.5, model.capacity_expansion),
                ("capacity_expansion", "hardware_life_years", 3, model.capacity_expansion),
                ("capacity_expansion", "project_life_years", 10.5, model.capacity_expansion),
                ("capacity_expansion", "working_capital_fraction_of_revenue", 1.1, model.capacity_expansion)):
            p = {**self.p, section: {**self.p[section], key: value}}
            with self.subTest(section=section, key=key), self.assertRaises(ValueError):
                fn(p)
        for key, value in (("tax_deduction_delay_years", 2.5), ("operating_deduction_fraction", 1.1)):
            with self.subTest(key=key), self.assertRaises(ValueError):
                model.calculate({**self.p, key: value})

    def test_machine_results_reproduce_and_check_is_read_only(self):
        expected = json.loads((CASE / "results.json").read_text())
        self.assertEqual(model.analysis(self.p), expected)
        paths = [CASE / name for name in ("inputs.json", "RESULTS.md", "results.json", "model.py")]
        before = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
        run = subprocess.run([sys.executable, str(CASE / "model.py"), "--check"], capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual(before, {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in paths})

    def test_results_independent_of_python_builtin_float_sum_algorithm(self):
        # Python 3.12 changed builtin float summation. Emulate Python 3.10/3.11
        # accumulation and require model reports/cash flows to remain identical.
        def sequential_sum(values, start=0):
            total = start
            for value in values:
                total += value
            return total

        expected_results = model.analysis(self.p)
        expected_report = model.render(self.p)
        with patch.object(model, "sum", sequential_sum, create=True):
            self.assertEqual(model.analysis(self.p), expected_results)
            self.assertEqual(model.render(self.p), expected_report)

    def test_extension_keeps_original_financial_observation_periods(self):
        evidence = json.loads((CASE / "evidence.json").read_text())
        self.assertEqual(evidence["retrieved_on"], "2026-10-04")
        self.assertEqual(evidence["extensions"][0]["extension_date"], "2026-10-08")
        records = [r for r in evidence["records"] if r["source_id"] == "MS1"]
        self.assertEqual(len(records), 6)
        self.assertTrue(all(r["period"].startswith(("FY2023", "FY2024", "FY2025")) for r in records))
        self.assertEqual(evidence["extensions"][0]["issuer_underwriting_status"], "NEEDS_DATA")

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
