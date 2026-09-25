"""Original HHFinAi domain arithmetic tests; all numbers are synthetic."""
import copy, math, random, unittest
from sf_agent.analytics import *
from sf_agent.validation import DataError

class Materiality(unittest.TestCase):
    def test_cashflow_no_shock(self):
        r=cashflow_bridge(100,0,0,.4,0,0,0,.25);self.assertEqual(r['free_cashflow_change'],0)
    def test_cashflow_bridge(self):
        r=cashflow_bridge(100000000,-.03,.01,.4,1000000,2000000,250000,.25)
        self.assertAlmostEqual(r['revenue_change'],-2030000);self.assertAlmostEqual(r['free_cashflow_change'],-3609000)
    def test_volume_below_minus_one(self):
        with self.assertRaises(DataError):cashflow_bridge(100,-1.1,0,.4,0,0,0,.25)
    def test_margin_bounded(self):
        with self.assertRaises(DataError):cashflow_bridge(100,0,0,1.4,0,0,0,.25)
    def test_dcf_one_year(self):self.assertAlmostEqual(incremental_dcf([11],.1,0,False)['enterprise_value_delta'],10)
    def test_terminal_rate_guard(self):
        with self.assertRaises(DataError):incremental_dcf([10],.02,.03,True)
    def test_terminal_value(self):
        r=incremental_dcf([10],.1,0,True);self.assertAlmostEqual(r['enterprise_value_delta'],100)
    def test_dcf_bool_required(self):
        with self.assertRaises(DataError):incremental_dcf([10],.1,0,1)
    def test_equity_bridge(self):self.assertEqual(equity_bridge(100,10,30,5,5)['per_share_residual'],15)
    def test_equity_negative_residual_not_floored(self):self.assertLess(equity_bridge(100,0,150,0,10)['per_share_residual'],0)
    def test_scenario_probability_sum(self):
        with self.assertRaises(DataError):scenario_expected_value([10,20],[.2,.2])
    def test_scenario_expected(self):self.assertEqual(scenario_expected_value([10,20],[.4,.6]),16)
    def test_scenario_mismatched(self):
        with self.assertRaises(DataError):scenario_expected_value([10],[.5,.5])

if __name__=='__main__':unittest.main()
