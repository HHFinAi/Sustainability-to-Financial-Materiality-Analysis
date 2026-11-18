import copy
import importlib.util
import json
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MOD=ROOT/"examples/climate-resilience/model.py"
spec=importlib.util.spec_from_file_location("resilience_fcf_model",MOD)
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
DOC=json.loads((ROOT/"examples/climate-resilience/inputs.json").read_text())

class TestResilienceFCF(unittest.TestCase):
    def test_every_case_stays_unverified(self):
        self.assertEqual(len(DOC["cases"]),3)
        self.assertTrue(all(module.evaluate(x)["status"]=="NEEDS_DATA" for x in DOC["cases"]))
    def test_funding_conversion_zero(self):
        case=copy.deepcopy(DOC["cases"][0])
        case["assumptions"]["funded_fraction"]=0
        self.assertEqual(module.evaluate(case)["recognized_revenue_m"],0)
    def test_fraction_out_of_bounds_rejected(self):
        case=copy.deepcopy(DOC["cases"][0])
        case["assumptions"]["supplier_award_share"]=1.2
        with self.assertRaises(module.ModelError): module.evaluate(case)
    def test_reverse_hurdle_increases_with_premium(self):
        case=copy.deepcopy(DOC["cases"][0])
        a=module.evaluate(case)["annual_fcf_required_by_hypothetical_premium_m"]
        case["assumptions"]["hypothetical_entry_price_premium_m"]+=10
        self.assertGreater(module.evaluate(case)["annual_fcf_required_by_hypothetical_premium_m"],a)
    def test_non_synthetic_results_are_blocked(self):
        case=copy.deepcopy(DOC["cases"][0])
        case["status"]="VERIFIED"
        with self.assertRaises(module.ModelError): module.evaluate(case)

if __name__=="__main__": unittest.main()
