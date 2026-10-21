"""Normalized cost transmission, not a calibrated ENSO earnings forecast."""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from public_case_support import value, run_cli


def transmit(cogs_ratio, margin_ratio, a):
    for k in ('exposed_share_of_cogs', 'hedged_fraction', 'pass_through_fraction'):
        if not 0 <= a[k] <= 1:
            raise ValueError(f'invalid fraction {k}')
    for k in ('inventory_lag_months', 'pricing_lag_months', 'hedge_protection_months'):
        if not isinstance(a[k], int) or a[k] < 0:
            raise ValueError(f'invalid lag {k}')
    if not 0 < cogs_ratio < 1 or not 0 < margin_ratio < 1 - cogs_ratio:
        raise ValueError('inconsistent baseline margin')
    if a['months'] <= 0 or a['revenue_index'] <= 0 or a['price_elasticity'] < 0:
        raise ValueError('invalid baseline')
    unit_shock = (1 + a['commodity_price_shock']) * (1 + a['input_fx_shock']) - 1
    if a['commodity_price_shock'] <= -1 or a['input_fx_shock'] <= -1:
        raise ValueError('invalid price shock')
    cost_shocks = []
    for month in range(1, a['months'] + 1):
        unhedged = 1 - a['hedged_fraction'] if month <= a['hedge_protection_months'] else 1
        cost_shocks.append(0 if month <= a['inventory_lag_months'] else a['exposed_share_of_cogs'] * unit_shock * unhedged)
    monthly = []
    base = a['revenue_index'] / a['months']
    for t, shock in enumerate(cost_shocks):
        prior = t - a['pricing_lag_months']
        price = cogs_ratio * cost_shocks[prior] * a['pass_through_fraction'] if prior >= 0 else 0
        volume = 1 - a['price_elasticity'] * price
        if volume <= 0:
            raise ValueError('elasticity scenario implies nonpositive volume')
        sales = base * (1 + price) * volume
        cogs = base * cogs_ratio * (1 + shock) * volume
        other = base * (1 - cogs_ratio - margin_ratio)
        monthly.append({'month': t + 1, 'unit_cost_shock': shock, 'price_change': price,
                        'volume_index': volume, 'sales': sales, 'profit': sales - cogs - other})
    sales = sum(x['sales'] for x in monthly)
    profit = sum(x['profit'] for x in monthly)
    baseline_profit = a['revenue_index'] * margin_ratio
    return {'baseline_profit_index': round(baseline_profit, 6), 'scenario_sales_index': round(sales, 6),
            'scenario_profit_index': round(profit, 6),
            'profit_change_percent': round((profit / baseline_profit - 1) * 100, 6),
            'margin_change_bps': round((profit / sales - margin_ratio) * 10000, 6),
            'months': monthly}


def calculate(inputs, s):
    a = inputs['assumptions']
    dn_sales = value(s, 'DANO_H126', 'sales', 'EUR_m')
    dn_cogs = value(s, 'DANO_H126', 'cogs', 'EUR_m')
    rows = [
        ('Nestle', 1 - value(s, 'NESN_H126', 'gross_margin', 'percent_sales') / 100, value(s, 'NESN_H126', 'underlying_margin', 'percent_sales') / 100),
        ('Unilever', 1 - value(s, 'ULVR_H126', 'gross_margin', 'percent_sales') / 100, value(s, 'ULVR_H126', 'underlying_margin', 'percent_sales') / 100),
        ('Danone', dn_cogs / dn_sales, value(s, 'DANO_H126', 'recurring_margin', 'percent_sales') / 100)]
    results = []
    for name, c, m in rows:
        results.append({'issuer': name, 'cogs_ratio': round(c, 8), 'profit_margin': m,
                        'one_percent_sales_unmitigated_cost_profit_hit_percent': round(1 / m, 6),
                        'scenario': transmit(c, m, a)})
    reclass = value(s, 'DANO_H126', 'logistics_reclassified', 'EUR_m') + value(s, 'DANO_H126', 'industrial_costs_reclassified', 'EUR_m')
    alternative = transmit((dn_cogs - reclass) / dn_sales, rows[2][2], a)
    return {'prepared_on': inputs['prepared_on'], 'issuers': results,
            'danone_presentation_control': {'reclassified_costs_eur_m': reclass,
              'cogs_share_of_sales_reclassification_pp': round(reclass / dn_sales * 100, 6),
              'alternative_scenario': alternative,
              'meaning': 'Move disclosed reclassified costs back to fixed other expense, preserving baseline profit. Analytical presentation control, not restated issuer accounts or harmonized procurement exposure.'}}


def render(d):
    lines = ['# Climate-to-earnings: normalized sensitivity', '',
             '21 October 2026. Disclosed H1 2026 cost/profit structures; common hypothetical procurement assumptions. These are not company forecasts or relative climate-risk rankings.', '',
             '| Issuer | Starting profit margin | Profit hit from unmitigated cost = 1% of sales | Profit change under lagged scenario | Margin change (bp) |',
             '|---|---:|---:|---:|---:|']
    for x in d['issuers']:
        q = x['scenario']
        lines.append(f"| {x['issuer']} | {x['profit_margin']:.1%} | {x['one_percent_sales_unmitigated_cost_profit_hit_percent']:.2f}% | {q['profit_change_percent']:.2f}% | {q['margin_change_bps']:.1f} |")
    p = d['danone_presentation_control']
    lines += ['', f"Danone's disclosed EUR {p['reclassified_costs_eur_m']:.0f}m expense reclassification equals {p['cogs_share_of_sales_reclassification_pp']:.2f}% of H1 sales. Moving it back to other expense leaves starting profit unchanged but changes the hypothetical commodity scenario to {p['alternative_scenario']['profit_change_percent']:.2f}% profit growth.", '',
              'This sensitivity exposes why applying the same commodity percentage to differently defined COGS can create a false risk ranking. Neither treatment identifies actual commodity purchases. The 1%-of-sales cost experiment avoids that particular classification dependency, but still does not estimate exposure.', '',
              'Source margins have different non-GAAP definitions. No EPS, price target or present-value impact is claimed. See [method](README.md), [inputs](inputs.json) and [primary sources](sources.json).', '']
    return '\n'.join(lines)


if __name__ == '__main__':
    run_cli(Path(__file__).parent, calculate, render)
