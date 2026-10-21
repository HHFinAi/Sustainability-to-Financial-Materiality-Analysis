"""Economic invariants and release reproduction; not evidence of source truth."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'examples'))
from public_case_support import load, value


def module(relative):
    spec = importlib.util.spec_from_file_location(relative.replace('/', '_'), ROOT / relative)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class PublicCases(unittest.TestCase):
    def test_archived_results_reproduce(self):
        for case in ('battery-storage', 'climate-staples', 'water-waste'):
            with self.subTest(case=case):
                p = subprocess.run([sys.executable, f'examples/{case}/model.py', '--check'], cwd=ROOT, capture_output=True, text=True)
                self.assertEqual(p.returncode, 0, p.stdout + p.stderr)

    def test_storage_hurdle_closes_npv(self):
        m = module('examples/battery-storage/model.py')
        i, s = load(ROOT / 'examples/battery-storage')
        a = i['assumptions']
        r = m.storage_case(a, 140, .85, .04)
        b = dict(a, discharge_price_usd_per_mwh=r['required_net_spread_usd_per_mwh'] + a['charge_price_usd_per_mwh'] / .85)
        self.assertAlmostEqual(m.storage_case(b, 140, .85, .04)['npv_usd_m'], 0, places=5)

    def test_reserve_and_cost_worsen_hurdle(self):
        m = module('examples/battery-storage/model.py')
        a = load(ROOT / 'examples/battery-storage')[0]['assumptions']
        low = m.storage_case(a, 140, .85, .04, reserve=0)
        high = m.storage_case(a, 220, .85, .04, reserve=.5)
        self.assertGreater(high['required_net_spread_usd_per_mwh'], low['required_net_spread_usd_per_mwh'])
        all_backup = m.storage_case(a, 140, .85, .04, reserve=1)
        self.assertIsNone(all_backup['required_net_spread_usd_per_mwh'])
        self.assertEqual(all_backup['annual_discharge_mwh'], 0)
        self.assertLess(all_backup['npv_usd_m'], 0)

    def test_storage_rejects_duration_and_impossible_dispatch(self):
        m = module('examples/battery-storage/model.py')
        i, s = load(ROOT / 'examples/battery-storage')
        i['assumptions']['duration_hours'] = 2
        with self.assertRaises(ValueError): m.calculate(i, s)
        a = dict(i['assumptions'], duration_hours=4, cycles_per_year=2000)
        with self.assertRaises(ValueError): m.storage_case(a, 140, .85, .04)

    def test_no_commodity_shock_preserves_profit(self):
        m = module('examples/climate-staples/model.py')
        a = load(ROOT / 'examples/climate-staples')[0]['assumptions']
        a['commodity_price_shock'] = 0
        result = m.transmit(.6, .15, a)
        self.assertEqual(result['scenario_sales_index'], 100)
        self.assertEqual(result['scenario_profit_index'], 15)

    def test_full_hedge_and_lags_have_economic_effect(self):
        m = module('examples/climate-staples/model.py')
        a = load(ROOT / 'examples/climate-staples')[0]['assumptions']
        protected = dict(a, hedged_fraction=1, hedge_protection_months=12)
        self.assertEqual(m.transmit(.6, .15, protected)['profit_change_percent'], 0)
        immediate = m.transmit(.6, .15, dict(a, pricing_lag_months=0))
        delayed = m.transmit(.6, .15, a)
        self.assertGreater(immediate['scenario_profit_index'], delayed['scenario_profit_index'])
        self.assertTrue(all(x['unit_cost_shock'] == 0 for x in delayed['months'][:3]))

    def test_danone_presentation_changes_sensitivity_not_baseline(self):
        m = module('examples/climate-staples/model.py')
        d = m.calculate(*load(ROOT / 'examples/climate-staples'))
        actual = d['issuers'][2]['scenario']
        control = d['danone_presentation_control']['alternative_scenario']
        self.assertEqual(actual['baseline_profit_index'], control['baseline_profit_index'])
        self.assertLess(actual['scenario_profit_index'], control['scenario_profit_index'])

    def test_units_cannot_be_silently_substituted(self):
        _, s = load(ROOT / 'examples/water-waste')
        with self.assertRaises(ValueError): value(s, 'XYL_Q226', 'revenue', 'USD_billion')

    def test_water_contributions_reconcile(self):
        m = module('examples/water-waste/model.py')
        d = m.calculate(*load(ROOT / 'examples/water-waste'))
        x = d['xylem']
        self.assertEqual(x['reported_order_increase_wss_usd_m'] + x['reported_order_increase_other_usd_m'], 912)
        self.assertEqual(d['wm']['volume_comparator_difference_pp'], 1.4)


class ProspectiveEvaluation(unittest.TestCase):
    def setUp(self):
        self.m = module('evaluation/prospective-research/score.py')
        self.r, self.obs = self.m.load()
        self.o = {'id': 'VLTO-2026Q3', 'period': '2026Q3', 'metric': 'group_core_sales_growth',
                  'unit': 'percent_yoy', 'value': 4.5, 'published_on': '2026-10-29',
                  'retrieved_on': '2026-10-30', 'source_url': 'https://investors.veralto.com/test-fixture',
                  'locator': 'Synthetic test fixture, not an observation', 'reviewer': 'TEST_ONLY'}

    def test_empty_outcomes_do_not_become_zero_accuracy(self):
        d = self.m.score(self.r, [], '2026-10-21')
        self.assertEqual(d['scored_count'], 0)
        self.assertIsNone(d['mean_brier_score'])
        self.assertIsNone(d['naive_mean_brier_score'])
        self.assertEqual(len(d['pending']), 3)

    def test_score_and_tie_follow_registered_operator(self):
        d = self.m.score(self.r, [self.o], '2026-10-30')
        self.assertEqual(d['scored_count'], 1)
        self.assertEqual(d['events'][0]['outcome'], 1)
        self.assertAlmostEqual(d['mean_brier_score'], .45 ** 2)
        r = copy.deepcopy(self.r)
        r['predictions'][1]['operator'] = '>'
        self.assertEqual(self.m.score(r, [self.o], '2026-10-30')['events'][0]['outcome'], 0)

    def test_rejects_leakage_and_wrong_metric(self):
        for replacement in ({'published_on': '2026-10-21'}, {'retrieved_on': '2026-11-01'},
                            {'unit': 'fraction'}, {'metric': 'water_quality_core_sales_growth'},
                            {'value': float('nan')}, {'source_url': 'https://example.com/outcome'}):
            with self.subTest(replacement=replacement):
                with self.assertRaises(ValueError): self.m.score(self.r, [dict(self.o, **replacement)], '2026-10-30')

    def test_duplicate_outcomes_cannot_inflate_sample(self):
        with self.assertRaises(ValueError): self.m.score(self.r, [self.o, self.o], '2026-10-30')

    def test_cutoff_snapshot_and_freeze(self):
        expected = json.loads((ROOT / 'evaluation/prospective-research/STATUS.json').read_text())
        self.assertEqual(self.m.score(self.r, [], '2026-10-21'), expected)


if __name__ == '__main__': unittest.main()
