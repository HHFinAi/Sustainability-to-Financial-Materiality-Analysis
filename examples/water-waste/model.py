"""Reconstruct operating signals without conflating revenue, orders or margins."""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from public_case_support import value, run_cli


def calculate(inputs, s):
    v = lambda src, key, unit: value(s, src, key, unit)
    xrev = v('XYL_Q226', 'revenue', 'USD_m')
    orders = v('XYL_Q226', 'orders', 'USD_m')
    total = v('XYL_Q226', 'orders_total_change', 'USD_m')
    wss = v('XYL_Q226', 'orders_wss_change', 'USD_m')
    return {'prepared_on': inputs['prepared_on'],
            'xylem': {'revenue_usd_m': xrev, 'orders_usd_m': orders,
              'book_to_bill': round(orders / xrev, 6),
              'organic_revenue_growth_percent': v('XYL_Q226', 'organic_growth', 'percent_yoy_rounded'),
              'organic_order_growth_percent': v('XYL_Q226', 'orders_organic_growth', 'percent_yoy_rounded'),
              'wss_share_of_reported_order_increase_percent': round(wss / total * 100, 6),
              'reported_order_increase_wss_usd_m': wss, 'reported_order_increase_other_usd_m': total - wss,
              'adjusted_ebitda_margin_percent': v('XYL_Q226', 'margin', 'percent_sales')},
            'veralto': {'revenue_usd_m': v('VLTO_Q226', 'revenue', 'USD_m'),
              'group_core_growth_percent': v('VLTO_Q226', 'core_growth', 'percent_yoy'),
              'water_quality_core_growth_percent': v('VLTO_Q226', 'water_quality_core_growth', 'percent_yoy'),
              'adjusted_operating_margin_percent': v('VLTO_Q226', 'margin', 'percent_sales_adjusted_operating'),
              'q3_core_growth_guidance_midpoint_percent': (v('VLTO_Q226', 'q3_guidance_low', 'percent_yoy') + v('VLTO_Q226', 'q3_guidance_high', 'percent_yoy')) / 2},
            'wm': {'revenue_usd_m': v('WM_Q226', 'revenue', 'USD_m'),
              'reported_revenue_growth_percent': v('WM_Q226', 'revenue_growth', 'percent_yoy'),
              'core_price_percent': v('WM_Q226', 'core_price', 'percent'),
              'realized_yield_percent': v('WM_Q226', 'yield', 'percent'),
              'volume_percent': v('WM_Q226', 'volume', 'percent'),
              'volume_ex_wildfire_percent': v('WM_Q226', 'volume_ex_wildfire', 'percent'),
              'volume_comparator_difference_pp': round(v('WM_Q226', 'volume_ex_wildfire', 'percent') - v('WM_Q226', 'volume', 'percent'), 6),
              'adjusted_operating_ebitda_margin_percent': v('WM_Q226', 'margin', 'percent_sales_adjusted_operating_ebitda')}}


def render(d):
    x, v, w = d['xylem'], d['veralto'], d['wm']
    return f'''# Water and waste: operating evidence

Evidence available by 21 October 2026; latest reviewed observations are Q2 2026 releases.

| Issuer | Revenue ($m) | Growth signal | Margin: preserve definition |
|---|---:|---|---|
| Xylem | {x['revenue_usd_m']:.0f} | Revenue organic {x['organic_revenue_growth_percent']:.1f}%; orders organic {x['organic_order_growth_percent']:.1f}% | Adjusted EBITDA {x['adjusted_ebitda_margin_percent']:.1f}% |
| Veralto | {v['revenue_usd_m']:.0f} | Group core {v['group_core_growth_percent']:.1f}%; Water Quality core {v['water_quality_core_growth_percent']:.1f}% | Adjusted operating {v['adjusted_operating_margin_percent']:.1f}% |
| WM | {w['revenue_usd_m']:.0f} | Reported revenue {w['reported_revenue_growth_percent']:.1f}%; C&D volume {w['volume_percent']:.1f}% | Adjusted operating EBITDA {w['adjusted_operating_ebitda_margin_percent']:.1f}% |

Xylem's reported book-to-bill is {x['book_to_bill']:.2f}x. Water Solutions and Services accounts for {x['wss_share_of_reported_order_increase_percent']:.1f}% of the dollar order increase (${x['reported_order_increase_wss_usd_m']:.0f}m of ${x['reported_order_increase_wss_usd_m'] + x['reported_order_increase_other_usd_m']:.0f}m). That concentration makes conversion timing a stronger diligence question than a broad sector-demand extrapolation.

WM's core-price metric ({w['core_price_percent']:.1f}%) differs from realized yield ({w['realized_yield_percent']:.1f}%). Removing the prior wildfire comparator changes volume growth by {w['volume_comparator_difference_pp']:.1f} percentage points to {w['volume_ex_wildfire_percent']:.1f}%; this is not new demand. These measures do not sum to group reported revenue growth.

Veralto's Q3 group core-growth guidance midpoint is {v['q3_core_growth_guidance_midpoint_percent']:.1f}%. It is management guidance, not an observed result or our forecast. Group and segment measures are kept separate.

No valuation ranking is possible from these margins: accounting definitions, capital intensity and perimeter differ. See [investment questions](README.md) and [source register](sources.json).
'''


if __name__ == '__main__':
    run_cli(Path(__file__).parent, calculate, render)
