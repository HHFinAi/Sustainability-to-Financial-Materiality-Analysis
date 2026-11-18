import importlib.util
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("resilience_primary_monitor",ROOT/"examples/climate-resilience/monitor.py")
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class TestPrimaryIssuerMonitor(unittest.TestCase):
    def setUp(self):
        self.rows={r["ticker"]:r for r in module.run()["results"]}
    def test_three_real_reporting_scopes(self):
        self.assertEqual(set(self.rows),{"TT","GEV","HEI.DE"})
        self.assertTrue(all(r["climate_attribution"]=="NEEDS_DATA" for r in self.rows.values()))
    def test_book_to_bill(self):
        self.assertEqual(self.rows["TT"]["reported_book_to_bill"],1.072)
        self.assertEqual(self.rows["GEV"]["reported_book_to_bill"],1.391)
    def test_organic_and_reported_orders_are_not_same(self):
        self.assertEqual(self.rows["GEV"]["organic_orders_yoy_pct_as_disclosed"],-9)
        self.assertGreater(self.rows["GEV"]["reported_orders_yoy_pct"],0)
    def test_company_margin_is_not_peer_comparable(self):
        self.assertAlmostEqual(self.rows["HEI.DE"]["rco_margin_pct"],19.98,places=1)
        self.assertTrue(all(r["do_not_cross_rank"] for r in self.rows.values()))

if __name__=="__main__": unittest.main()
