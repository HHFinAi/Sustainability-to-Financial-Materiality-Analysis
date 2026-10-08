"""Finite-life Brevik sensitivity with explicit cash boundaries; no network or dependencies.

All EUR amounts are millions except labelled per-tonne/per-share values.
This extends, rather than replaces, the original five-year model.
"""
from __future__ import annotations
import argparse
from copy import deepcopy
import csv
from datetime import date
import io
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def load_inputs():
    return json.loads((ROOT / 'extended-inputs.json').read_text(encoding='utf-8'))


def number(value, name, *, low=0, high=None):
    if isinstance(value, bool) or not isinstance(value, (float, int)) or not math.isfinite(value):
        raise ValueError(f'{name} must be a finite number')
    if value < low or (high is not None and value > high):
        raise ValueError(f'{name} outside permitted range')
    return value


def validate(data):
    a = data['assumptions']
    s = data['scenarios']
    for k in ('first_year', 'last_year', 'support_last_year', 'carbon_cash_timing_lag_years'):
        if isinstance(a[k], bool) or not isinstance(a[k], int):
            raise ValueError(f'{k} must be an integer')
    if a['last_year'] < a['first_year'] or a['first_year'] <= date.fromisoformat(data['valuation_date']).year - 1:
        raise ValueError('Invalid finite operating horizon')
    if not 0 <= a['carbon_cash_timing_lag_years'] <= 3:
        raise ValueError('Invalid cash timing lag')
    number(a['discount_rate'], 'discount_rate', low=0, high=1)
    for k in ('cash_tax_rate', 'premium_working_capital_fraction', 'eligible_fixed_cost_fraction', 'eligible_variable_cost_fraction', 'non_ets_share_of_stored_co2', 'non_ets_aid_cash_realization', 'operating_aid_above_threshold_share'):
        number(a[k], k, high=1)
    number(a['carbon_attribute_tonnes_per_tonne_premium_cement'], 'carbon_attribute_intensity', low=1e-9)
    for k in ('annual_sustaining_capex_eur_m', 'residual_capital_at_valuation_eur_m', 'closure_cost_2045_eur_m', 'opening_working_capital_eur_m', 'fixed_capture_cost_eur_m_per_full_year', 'capture_variable_cost_eur_per_tonne', 'transport_storage_cost_eur_per_stored_tonne_during_support', 'transport_storage_cost_eur_per_stored_tonne_after_support', 'operating_aid_threshold_eur_m_per_full_year', 'operating_aid_total_remaining_cap_eur_m', 'carbon_price_2026_eur_per_tonne', 'carbon_price_2030_eur_per_tonne', 'post_2030_cement_production_tonnes'):
        number(a[k], k)
    for k in ('post_2030_carbon_price_annual_growth', 'post_2030_premium_annual_growth'):
        number(a[k], k, low=-0.99, high=1)
    plan = data['commercial_plan']
    if plan['years'] != list(range(2026, 2031)) or len(plan['cement_production_tonnes']) != 5:
        raise ValueError('Commercial ramp must cover 2026–2030 exactly')
    for x in plan['cement_production_tonnes']:
        number(x, 'planned cement tonnes')
    for name, case in s.items():
        for k in ('cement_sell_through_fraction', 'steady_capture_availability', 'stored_fraction_of_captured', 'ets_cash_realization_fraction'):
            number(case[k], f'{name}.{k}', high=1)
        number(case['incremental_premium_eur_per_cement_tonne'], name+'.premium')
        if len(case['capture_availability_2026_to_2030']) != 5:
            raise ValueError('Capture ramp must cover five years')
        for x in case['capture_availability_2026_to_2030']:
            number(x, 'capture availability', high=1)
        for k in ('operating_grants_enabled', 'non_ets_aid_enabled'):
            if not isinstance(case[k], bool):
                raise ValueError(k+' must be boolean')
    for fact in data['facts'].values():
        number(fact['value'], 'reported fact')
    number(data['facts']['shares_post_january_2026_cancellation']['value'], 'shares', low=1)
    b = data['issuer_bridge']
    number(b['brevik_embedded_reference_fraction'], 'embedded fraction', high=1)
    for k in ('pension_debtlike_adjustment_fraction', 'nci_value_to_book_multiplier', 'jv_associate_value_to_book_multiplier'):
        number(b[k], k)
    for m in b['core_ev_to_2025_rcobd_multiples']:
        number(m, 'multiple', low=1e-9)
    if b['historical_price_eur'] is not None:
        raise ValueError('No verified historical quote is registered; adding one requires a dated source gate')
    return data


def prorata(year, valuation_date):
    start, end = date(year, 1, 1), date(year+1, 1, 1)
    if valuation_date >= end:
        raise ValueError('Operating flows precede valuation date')
    return (end - max(start, valuation_date)).days / (end-start).days


def project(data, scenario, *, premium=None):
    validate(data)
    a, s = data['assumptions'], data['scenarios'][scenario]
    val = date.fromisoformat(data['valuation_date'])
    premium = s['incremental_premium_eur_per_cement_tonne'] if premium is None else number(premium, 'premium')
    capacity = data['facts']['capture_capacity_tonnes_per_year']['value']
    previous_wc = a['opening_working_capital_eur_m']
    remaining_aid = a['operating_aid_total_remaining_cap_eur_m']
    delayed_ets, delayed_non_ets = {}, {}
    rows = []
    # The final receipt-only tail collects earned carbon cash; it has no extra operating life.
    for year in range(a['first_year'], a['last_year'] + a['carbon_cash_timing_lag_years'] + 1):
        operating = year <= a['last_year']
        fraction = prorata(year, val) if operating else 0.0
        supported = operating and year <= a['support_last_year']
        planned = data['commercial_plan']['cement_production_tonnes'][year-2026] if 2026 <= year <= 2030 else a['post_2030_cement_production_tonnes']
        availability = s['capture_availability_2026_to_2030'][year-2026] if 2026 <= year <= 2030 else s['steady_capture_availability']
        produced = planned * fraction
        captured = capacity * availability * fraction
        stored = captured * s['stored_fraction_of_captured']
        offered_sales = produced * s['cement_sell_through_fraction']
        # Assumed attribute intensity, not an observed engineering emissions factor.
        sold = min(offered_sales, stored/a['carbon_attribute_tonnes_per_tonne_premium_cement'])
        unmonetized = offered_sales-sold
        unit_premium = premium * (1+a['post_2030_premium_annual_growth']) ** max(0, year-2030)
        premium_cash = sold*unit_premium/1e6
        if year <= 2030:
            carbon_price = a['carbon_price_2026_eur_per_tonne'] + (a['carbon_price_2030_eur_per_tonne']-a['carbon_price_2026_eur_per_tonne']) * (year-2026)/4
        else:
            carbon_price = a['carbon_price_2030_eur_per_tonne'] * (1+a['post_2030_carbon_price_annual_growth']) ** (year-2030)
        eligible_ets = stored*(1-a['non_ets_share_of_stored_co2'])
        non_ets = stored*a['non_ets_share_of_stored_co2']
        gross_ets = eligible_ets*carbon_price/1e6
        ets_earned = gross_ets*s['ets_cash_realization_fraction']
        non_ets_earned = non_ets*carbon_price*a['non_ets_aid_cash_realization']/1e6 if supported and s['non_ets_aid_enabled'] else 0
        receipt_year = year+a['carbon_cash_timing_lag_years']
        delayed_ets[receipt_year] = delayed_ets.get(receipt_year, 0)+ets_earned
        delayed_non_ets[receipt_year] = delayed_non_ets.get(receipt_year, 0)+non_ets_earned
        ets_cash, non_ets_cash = delayed_ets.get(year, 0), delayed_non_ets.get(year, 0)
        fixed = a['fixed_capture_cost_eur_m_per_full_year']*fraction
        variable = captured*a['capture_variable_cost_eur_per_tonne']/1e6
        ts_unit = a['transport_storage_cost_eur_per_stored_tonne_during_support'] if supported else a['transport_storage_cost_eur_per_stored_tonne_after_support']
        ts = stored*ts_unit/1e6
        eligible_cost = fixed*a['eligible_fixed_cost_fraction']+variable*a['eligible_variable_cost_fraction']
        threshold = a['operating_aid_threshold_eur_m_per_full_year']*fraction
        grant_formula = min(eligible_cost, threshold) + max(0, eligible_cost-threshold)*a['operating_aid_above_threshold_share']
        grant = min(remaining_aid, grant_formula) if supported and s['operating_grants_enabled'] else 0
        remaining_aid -= grant
        cash_surplus = premium_cash+ets_cash+non_ets_cash+grant-fixed-variable-ts
        tax = max(0, cash_surplus)*a['cash_tax_rate']
        sustaining = a['annual_sustaining_capex_eur_m']*fraction
        closure = a['closure_cost_2045_eur_m'] if year == a['last_year'] else 0
        # The final operating year releases all premium-related WC; no stranded balance remains.
        wc = premium_cash*a['premium_working_capital_fraction'] if year < a['last_year'] else 0
        delta_wc = wc-previous_wc
        previous_wc = wc
        fcf = cash_surplus-tax-sustaining-closure-delta_wc
        time = (date(year,12,31)-val).days/365.25
        pv = fcf/(1+a['discount_rate'])**time
        rows.append(dict(scenario=scenario, year=year, future_year_fraction=fraction,
            cement_produced_tonnes=produced, cement_sold_premium_tonnes=sold,
            offered_premium_cement_unmonetized_tonnes=unmonetized, co2_captured_tonnes=captured,
            co2_stored_tonnes=stored, co2_eligible_ets_tonnes=eligible_ets,
            co2_non_ets_tonnes=non_ets, premium_cash_eur_m=premium_cash,
            gross_ets_value_earned_eur_m=gross_ets, retained_ets_value_earned_eur_m=ets_earned,
            retained_ets_cash_received_eur_m=ets_cash, non_ets_aid_earned_eur_m=non_ets_earned,
            non_ets_aid_cash_received_eur_m=non_ets_cash,
            gross_fixed_capture_cost_eur_m=fixed,gross_variable_capture_cost_eur_m=variable,
            transport_storage_cost_eur_m=ts, operating_grant_cash_eur_m=grant,
            remaining_assumed_operating_aid_cap_eur_m=remaining_aid,
            net_operating_cash_surplus_eur_m=cash_surplus,cash_tax_eur_m=tax,
            sustaining_capex_eur_m=sustaining, closure_cost_eur_m=closure,
            change_working_capital_eur_m=delta_wc, incremental_fcf_eur_m=fcf,
            present_value_eur_m=pv, years_from_valuation=time))
    return rows


def forward_pv(data, scenario, **kwargs):
    return sum(r['present_value_eur_m'] for r in project(data, scenario, **kwargs))-data['assumptions']['residual_capital_at_valuation_eur_m']


def premium_for_pv(data, scenario, target):
    number(target, 'target PV', low=-1e12)
    if forward_pv(data,scenario,premium=0) >= target:
        return 0.0
    lo, hi = 0., data['reverse_targets']['premium_search_max_eur_per_tonne']
    if forward_pv(data,scenario,premium=hi) < target:
        raise ValueError('Target cannot be reached within the permitted premium range')
    for _ in range(80):
        middle = (lo+hi)/2
        if forward_pv(data,scenario,premium=middle) >= target:
            hi = middle
        else:
            lo = middle
    return (lo+hi)/2


def issuer_bridge(data, scenario, multiple):
    f,b=data['facts'],data['issuer_bridge']
    number(multiple,'multiple',low=1e-9)
    normalized_rcobd = f['group_rcobd_2025_eur_m']['value']-f['equity_accounted_result_2025_eur_m']['value']
    baseline_ev = normalized_rcobd*multiple
    embedded=forward_pv(data,b['brevik_embedded_reference_scenario'])*b['brevik_embedded_reference_fraction']
    replacement=forward_pv(data,scenario)
    debt=f['net_debt_2025_eur_m']['value']
    pension=f['pension_provisions_2025_eur_m']['value']*b['pension_debtlike_adjustment_fraction']
    nci=f['nci_book_equity_2025_eur_m']['value']*b['nci_value_to_book_multiplier']
    nonoperating=f['jv_associate_book_values_2025_eur_m']['value']*b['jv_associate_value_to_book_multiplier']
    ev=baseline_ev-embedded+replacement
    equity=ev-debt-pension-nci+nonoperating
    shares=f['shares_post_january_2026_cancellation']['value']/1e6
    return dict(scenario=scenario, core_ev_to_rcobd_multiple=multiple,
        normalized_rcobd_ex_equity_accounted_eur_m=normalized_rcobd, baseline_ev_eur_m=baseline_ev, embedded_brevik_reference_pv_eur_m=embedded,
        replacement_brevik_pv_eur_m=replacement, adjusted_ev_eur_m=ev,
        reported_net_debt_eur_m=debt, pension_debtlike_proxy_eur_m=pension,
        nci_value_proxy_eur_m=nci, jv_associate_value_proxy_eur_m=nonoperating,
        conditional_common_equity_eur_m=equity, issued_shares_m=shares,
        conditional_value_eur_per_share=equity/shares,
        brevik_variant_value_eur_per_share=(replacement-embedded)/shares)


def csv_text(rows):
    out=io.StringIO(newline='')
    w=csv.DictWriter(out,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader()
    for r in rows:
        w.writerow({k:round(v,8) if isinstance(v,float) else v for k,v in r.items()})
    return out.getvalue()


def outputs(data):
    validate(data)
    a=data['assumptions'];shares=data['facts']['shares_post_january_2026_cancellation']['value']/1e6
    embedded=forward_pv(data,data['issuer_bridge']['brevik_embedded_reference_scenario'])*data['issuer_bridge']['brevik_embedded_reference_fraction']
    cashflows,scenarios,bridge,reverse,capital=[],[],[],[],[]
    for name in data['scenarios']:
        rows=project(data,name);cashflows.extend(rows)
        v=forward_pv(data,name)
        scenarios.append(dict(scenario=name, operating_life_end_year=a['last_year'],
           support_assumed_end_year=a['support_last_year'], finite_life_forward_pv_eur_m=v,
           operating_pv_before_residual_capital_eur_m=v+a['residual_capital_at_valuation_eur_m'],
           residual_capital_eur_m=a['residual_capital_at_valuation_eur_m'],
           zero_forward_pv_premium_eur_per_tonne=premium_for_pv(data,name,0),
           fcf_2030_eur_m=next(r['incremental_fcf_eur_m'] for r in rows if r['year']==2030),
           fcf_2035_eur_m=next(r['incremental_fcf_eur_m'] for r in rows if r['year']==2035),
           finite_pv_per_issued_share_eur=v/shares))
        for multiple in data['issuer_bridge']['core_ev_to_2025_rcobd_multiples']:
            bridge.append(issuer_bridge(data,name,multiple))
        for target in data['reverse_targets']['incremental_value_eur_per_share']:
            target_pv=embedded+target*shares
            reverse.append(dict(scenario=name, variant_value_target_eur_per_share=target,
              required_project_pv_eur_m=target_pv,
              required_premium_eur_per_cement_tonne=premium_for_pv(data,name,target_pv)))
        # This is a capital-recovery stress, not historical NPV: historical2025 operating cash is absent.
        for k in data['lifecycle']['net_retained_construction_capital_eur_m_sensitivities']:
            required_at_cutoff=k*(1+a['discount_rate'])**((date.fromisoformat(data['valuation_date'])-date.fromisoformat(data['lifecycle']['capital_reference_date'])).days/365.25)
            capital.append(dict(scenario=name, assumed_net_retained_construction_capital_eur_m=k,
              required_capital_recovery_at_cutoff_eur_m=required_at_cutoff,
              remaining_value_less_required_capital_recovery_eur_m=v-required_at_cutoff,
              premium_to_recover_capital_plus_residual_eur_per_tonne=premium_for_pv(data,name,required_at_cutoff)))
    lines=['# Finite-life cash economics and issuer bridge','',
      'Generated by `python examples/heidelberg-brevik/forward_model.py`. Cutoff and discount date: **25 February 2026**. All outputs are conditional analyst sensitivities; readiness is **screen-grade / NEEDS_DATA** for contractual underwriting. The original five-year results remain unchanged.','',
      '## Future operating value','',
      '| Scenario |2026–2045 plus cash-receipt tail PV, after residual capital (€m)|2030 FCF (€m)|2035 FCF (€m)|Zero-forward-PV premium (€/t cement)|',
      '|---|---:|---:|---:|---:|']
    for s in scenarios:
        lines.append(f"|{s['scenario']}|{s['finite_life_forward_pv_eur_m']:.2f}|{s['fcf_2030_eur_m']:.2f}|{s['fcf_2035_eur_m']:.2f}|{s['zero_forward_pv_premium_eur_per_tonne']:.2f}|")
    lines+=['','There is no perpetual terminal value. Assumed operating aid expires after 2034 or earlier when its remaining cap is exhausted. Original construction spending is sunk for forward valuation; future residual capital is deducted once. Carbon cash earned by 2045 is collected in a receipt-only tail. The assumed cash-tax rule has no loss refund.','',
      '## Central annual waterfall: selected years (€m)','',
      '| Year | Cement sold (kt)|Captured CO₂ (kt)|Stored CO₂ (kt)|Premium cash|Retained ETS cash|Non-ETS aid cash|Gross capture cost|Operating aid|Transport/storage|FCF|',
      '|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
    for r in project(data,'central_sensitivity'):
        if r['year'] in (2026,2030,2034,2035,2045,2046):
            lines.append(f"|{r['year']}|{r['cement_sold_premium_tonnes']/1000:.2f}|{r['co2_captured_tonnes']/1000:.2f}|{r['co2_stored_tonnes']/1000:.2f}|{r['premium_cash_eur_m']:.2f}|{r['retained_ets_cash_received_eur_m']:.2f}|{r['non_ets_aid_cash_received_eur_m']:.2f}|{r['gross_fixed_capture_cost_eur_m']+r['gross_variable_capture_cost_eur_m']:.2f}|{r['operating_grant_cash_eur_m']:.2f}|{r['transport_storage_cost_eur_m']:.2f}|{r['incremental_fcf_eur_m']:.2f}|")
    lines+=['','Tax, sustaining capital, closure costs and working-capital changes are individually disclosed in [forward-cashflows.csv](forward-cashflows.csv). Fixed costs do not disappear when capture is lower. Sales and captured tonnes have separate ramps; the assumed carbon-attribute constraint can prevent offered premium sales from being monetized. Gross ETS value is not assumed equal to current cash receipts.','',
      '## Enterprise to common-equity bridge','',
      'FY2025 preliminary RCOBD of €4,679m includes €191.2m of equity-accounted income. The multiple is applied to €4,487.8m after removing that income; JV/associate value is then added separately. The 7/9/11× multiples are analyst valuation sensitivities, not market observations or peer calibration. Default embedded Brevik PV equals the central project sensitivity: it is removed before scenario value is substituted. Central project value therefore creates zero additional uplift to its own baseline.','',
      '| Scenario |Baseline EV / normalized RCOBD|Baseline EV (€m)|Embedded Brevik removed (€m)|Scenario Brevik added (€m)|Conditional equity (€m)|Conditional €/share|Brevik variant €/share|',
      '|---|---:|---:|---:|---:|---:|---:|---:|']
    for r in bridge:
        lines.append(f"|{r['scenario']}|{r['core_ev_to_rcobd_multiple']:.0f}×|{r['baseline_ev_eur_m']:.2f}|{r['embedded_brevik_reference_pv_eur_m']:.2f}|{r['replacement_brevik_pv_eur_m']:.2f}|{r['conditional_common_equity_eur_m']:.2f}|{r['conditional_value_eur_per_share']:.2f}|{r['brevik_variant_value_eur_per_share']:.2f}|")
    lines+=['',f"At 9× the bridge deducts reported net debt €{data['facts']['net_debt_2025_eur_m']['value']:.1f}m, pension debt-like proxy €{data['facts']['pension_provisions_2025_eur_m']['value']:.1f}m and NCI book-value proxy €{data['facts']['nci_book_equity_2025_eur_m']['value']:.1f}m; adds JV/associate book-value proxy €{data['facts']['jv_associate_book_values_2025_eur_m']['value']:.1f}m; divides by {shares:.6f}m post-cancellation issued shares. These book values are not appraised fair values. No separate cash or lease deduction is made on top of reported net debt.",'',
      '**Price comparison: NEEDS_DATA.** An exact25February 2026 exchange quote was not verified. No observed upside/downside, market-implied multiple or buy/sell conclusion is reported. Conditional per-share values cannot serve as a stock-price target without a reconciled group forecast, market anchor and fair-value adjustments.','',
      '## Reverse valuation: required premium','',
      '| Physical/cost scenario | Match embedded central PV (€/t)| Add €1 per issued share (€/t)| Add €2 per issued share (€/t)|',
      '|---|---:|---:|---:|']
    for name in data['scenarios']:
        lines.append('|'+name+'|'+'|'.join(f"{r['required_premium_eur_per_cement_tonne']:.2f}" for r in reverse if r['scenario']==name)+'|')
    lines+=['',f'€1 per issued share requires €{shares:.6f}m more project value than the embedded baseline. These breakpoints answer what must be earned; they do not assert customers will pay these premiums.','',
      '## Capital recovery versus lifecycle returns','',
      'The June 2025 Gassnova report publishes an autumn 2024 gross construction forecast of NOK4.9bn, versus the original NOK3.2bn estimate. It does not establish final actual expenditure or Heidelberg’s retained share. The 2023 amendment shifted overruns to Heidelberg for a larger potential return; applying the original aid percentage to the entire revised forecast would therefore be unsafe. The up-to-NOK150m startup grant is a contingent ceiling, with no verified receipt entered here.','',
      'Net retained capital of €0/100/200/300m is explicitly hypothetical. The model compounds that capital from 1 January 2025 to the valuation cutoff at the assumed 8% required return, then compares it with remaining finite-life cash value. This deliberately omits unknown 2025 operating cash and construction dates: it is a capital-recovery sensitivity, **not historical project NPV or IRR**.','',
      '| Scenario |Assumed net construction capital (€m)|Required recovery at cutoff (€m)|Remaining value less recovery (€m)|Premium to recover capital plus residual (€/t)|',
      '|---|---:|---:|---:|---:|']
    for r in capital:
        lines.append(f"|{r['scenario']}|{r['assumed_net_retained_construction_capital_eur_m']:.0f}|{r['required_capital_recovery_at_cutoff_eur_m']:.2f}|{r['remaining_value_less_required_capital_recovery_eur_m']:.2f}|{r['premium_to_recover_capital_plus_residual_eur_per_tonne']:.2f}|")
    lines+=['','**Evidence needed for actual lifecycle returns:** dated construction payments; capital and operating grant receipts; startup grant receipt; retained capital; 2025 operating cash; usable depreciation/loss shields; disposal and closure liabilities. See [evidence-gaps.json](evidence-gaps.json). No full-project return is certified.','']
    return {'forward-cashflows.csv':csv_text(cashflows),'forward-scenarios.csv':csv_text(scenarios),
        'issuer-bridge.csv':csv_text(bridge),'reverse-premium.csv':csv_text(reverse),
        'capital-recovery.csv':csv_text(capital),'FORWARD_VALUATION.md':'\n'.join(format_markdown(lines))}



def format_markdown(lines):
    """Keep table cells readable without changing any calculated values."""
    readable=[]
    replacements={
        'exact25February 2026':'exact 25 February 2026',
        'exact25 February2026':'exact 25 February 2026',
        'exact25 February 2026':'exact 25 February 2026',
        '25February2026':'25 February 2026',
        'at9×':'at 9×', 'life2045':'life 2045',
        'from1 January 2025':'from 1 January 2025',
        'Net retained capital of€':'Net retained capital of €',
        'originalNOK':'original NOK', 'ofNOK':'of NOK',
        'required recovery atcutoff':'required recovery at cutoff',
    }
    for line in lines:
        for old,new in replacements.items():
            line=line.replace(old,new)
        if line.startswith('|') and line.endswith('|'):
            line='| '+' | '.join(cell.strip() for cell in line[1:-1].split('|'))+' |'
        readable.append(line)
    return readable

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--check',action='store_true',help='Compare committed results without writing')
    args=p.parse_args()
    for name,content in outputs(load_inputs()).items():
        path=ROOT/name
        if args.check:
            if not path.is_file() or path.read_text(encoding='utf-8') != content:
                raise SystemExit('Stale or missing result: '+name)
        else:
            path.write_text(content,encoding='utf-8')
    print('PASS: finite-life Brevik outputs reproduce' if args.check else 'Wrote six finite-life Brevik result files')


if __name__=='__main__':
    main()
