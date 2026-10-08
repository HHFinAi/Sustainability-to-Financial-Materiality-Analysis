"""Independent economic checks for the finite-life Brevik extension."""
from copy import deepcopy
from datetime import date
import importlib.util
import math
from pathlib import Path
import subprocess
import sys
import unittest

CASE = Path(__file__).resolve().parents[1] / 'examples' / 'heidelberg-brevik'
spec=importlib.util.spec_from_file_location('brevik_forward',CASE/'forward_model.py')
model=importlib.util.module_from_spec(spec)
spec.loader.exec_module(model)


class BrevikForwardCase(unittest.TestCase):
    def setUp(self):
        self.data=model.load_inputs()

    def test_issued_share_bridge_removes_equity_accounted_income(self):
        r=model.issuer_bridge(self.data,'central_sensitivity',9)
        normalized=4679-191.2
        # These independently sourced figures include both pension maturities.
        self.assertAlmostEqual(r['normalized_rcobd_ex_equity_accounted_eur_m'],normalized)
        self.assertAlmostEqual(r['baseline_ev_eur_m'],normalized*9)
        equity=normalized*9-5715-(569.3+54.9)-1136.3+(1646.4+650.1)
        self.assertAlmostEqual(r['conditional_common_equity_eur_m'],equity)
        self.assertAlmostEqual(r['conditional_value_eur_per_share'],equity/176.365065)

    def test_embedded_project_substitution_prevents_a_second_uplift(self):
        central=model.issuer_bridge(self.data,'central_sensitivity',9)
        self.assertEqual(central['adjusted_ev_eur_m'],central['baseline_ev_eur_m'])
        self.assertEqual(central['brevik_variant_value_eur_per_share'],0)
        upside=model.issuer_bridge(self.data,'upside',9)
        self.assertAlmostEqual(upside['adjusted_ev_eur_m']-central['adjusted_ev_eur_m'],
            model.forward_pv(self.data,'upside')-model.forward_pv(self.data,'central_sensitivity'))

    def test_gross_cost_grant_formula_and_cumulative_exhaustion(self):
        r=model.project(self.data,'central_sensitivity')[0]
        frac=310/365
        eligible=8*frac+400000*.65*frac*70/1e6
        threshold=10*frac
        expected=threshold+.75*(eligible-threshold)
        self.assertAlmostEqual(r['operating_grant_cash_eur_m'],expected)
        altered=deepcopy(self.data)
        altered['assumptions']['operating_aid_total_remaining_cap_eur_m']=1
        rows=model.project(altered,'central_sensitivity')
        self.assertEqual(rows[0]['operating_grant_cash_eur_m'],1)
        self.assertAlmostEqual(sum(r['operating_grant_cash_eur_m'] for r in rows),1)
        self.assertTrue(all(r['operating_grant_cash_eur_m']==0 for r in rows[1:]))
        self.assertTrue(all(r['remaining_assumed_operating_aid_cap_eur_m']>=0 for r in rows))

    def test_carbon_receipt_tail_collects_earned_cash_once(self):
        rows=model.project(self.data,'central_sensitivity')
        self.assertEqual(rows[0]['retained_ets_cash_received_eur_m'],0)
        self.assertAlmostEqual(sum(r['retained_ets_value_earned_eur_m'] for r in rows),
            sum(r['retained_ets_cash_received_eur_m'] for r in rows))
        self.assertAlmostEqual(sum(r['non_ets_aid_earned_eur_m'] for r in rows),
            sum(r['non_ets_aid_cash_received_eur_m'] for r in rows))
        tail=rows[-1]
        self.assertEqual(tail['year'],2046)
        self.assertEqual(tail['co2_captured_tonnes'],0)
        self.assertEqual(tail['cement_sold_premium_tonnes'],0)
        self.assertEqual(tail['operating_grant_cash_eur_m'],0)
        self.assertGreater(tail['retained_ets_cash_received_eur_m'],0)
        self.assertEqual(tail['sustaining_capex_eur_m'],0)

    def test_support_expiry_changes_earned_aid_not_prior_receipts(self):
        rows={r['year']:r for r in model.project(self.data,'central_sensitivity')}
        self.assertEqual(rows[2035]['non_ets_aid_earned_eur_m'],0)
        self.assertGreater(rows[2035]['non_ets_aid_cash_received_eur_m'],0)
        self.assertEqual(rows[2036]['non_ets_aid_cash_received_eur_m'],0)
        self.assertGreater(rows[2035]['transport_storage_cost_eur_m'],0)
        self.assertEqual(rows[2034]['transport_storage_cost_eur_m'],0)

    def test_physical_boundary_and_sale_capture_independence(self):
        changed=deepcopy(self.data)
        changed['scenarios']['central_sensitivity']['cement_sell_through_fraction']=.1
        orig=model.project(self.data,'central_sensitivity')
        new=model.project(changed,'central_sensitivity')
        self.assertEqual(orig[0]['co2_captured_tonnes'],new[0]['co2_captured_tonnes'])
        self.assertLess(new[0]['cement_sold_premium_tonnes'],orig[0]['cement_sold_premium_tonnes'])
        changed['assumptions']['carbon_attribute_tonnes_per_tonne_premium_cement']=3
        for r in model.project(changed,'central_sensitivity'):
            self.assertLessEqual(r['co2_stored_tonnes'],r['co2_captured_tonnes'])
            self.assertLessEqual(r['co2_captured_tonnes'],400000)
            self.assertLessEqual(r['cement_sold_premium_tonnes']*3,r['co2_stored_tonnes']+1e-8)
            self.assertAlmostEqual(r['co2_eligible_ets_tonnes']+r['co2_non_ets_tonnes'],r['co2_stored_tonnes'])

    def test_future_only_stub_and_working_capital_release(self):
        rows=model.project(self.data,'central_sensitivity')
        self.assertAlmostEqual(rows[0]['future_year_fraction'],310/365)
        self.assertTrue(0<rows[0]['years_from_valuation']<1)
        self.assertAlmostEqual(sum(r['change_working_capital_eur_m'] for r in rows),0)
        self.assertLess(next(r for r in rows if r['year']==2045)['change_working_capital_eur_m'],0)

    def test_manual_zero_production_loss_cashflow_and_residual_capital_once(self):
        d=deepcopy(self.data);a=d['assumptions'];s=d['scenarios']['downside']
        a['last_year']=2026;a['carbon_cash_timing_lag_years']=0
        a['fixed_capture_cost_eur_m_per_full_year']=10
        s['capture_availability_2026_to_2030']=[0]*5
        rows=model.project(d,'downside')
        frac=310/365
        cashflow=-10*frac-5*frac-20
        time=(date(2026,12,31)-date(2026,2,25)).days/365.25
        expected=cashflow/(1.08**time)-10
        self.assertEqual(rows[0]['cash_tax_eur_m'],0)
        self.assertAlmostEqual(model.forward_pv(d,'downside'),expected)
        a['residual_capital_at_valuation_eur_m']=20
        self.assertAlmostEqual(model.forward_pv(d,'downside'),expected-10)

    def test_reverse_premium_matches_independent_one_share_target(self):
        embedded=model.forward_pv(self.data,'central_sensitivity')
        target=embedded+176.365065
        p=model.premium_for_pv(self.data,'central_sensitivity',target)
        self.assertAlmostEqual(model.forward_pv(self.data,'central_sensitivity',premium=p),target,places=7)
        self.assertLess(model.forward_pv(self.data,'central_sensitivity',premium=p-1),target)
        self.assertGreater(model.forward_pv(self.data,'central_sensitivity',premium=p+1),target)

    def test_invalid_economic_inputs_rejected(self):
        for key,value in [('cash_tax_rate',1.1),('discount_rate',float('nan')),
                          ('carbon_attribute_tonnes_per_tonne_premium_cement',0),
                          ('operating_aid_total_remaining_cap_eur_m',-1),
                          ('carbon_cash_timing_lag_years',1.5)]:
            d=deepcopy(self.data);d['assumptions'][key]=value
            with self.assertRaises(ValueError,msg=key):model.project(d,'central_sensitivity')
        d=deepcopy(self.data);d['issuer_bridge']['historical_price_eur']=200
        with self.assertRaises(ValueError):model.project(d,'central_sensitivity')

    def test_read_only_check_and_all_committed_outputs(self):
        names=model.outputs(self.data)
        before={n:(CASE/n).read_bytes() for n in names}
        subprocess.run([sys.executable,str(CASE/'forward_model.py'),'--check'],check=True,capture_output=True)
        for n,text in names.items():
            self.assertEqual((CASE/n).read_text(),text,n)
            self.assertEqual((CASE/n).read_bytes(),before[n],n)


if __name__=='__main__':unittest.main()
