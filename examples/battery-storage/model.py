"""Ten-year pre-tax storage hurdle; public benchmarks plus explicit scenarios."""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from public_case_support import value, run_cli


def storage_case(a, cost, efficiency, fom, reserve=None, years=None):
    reserve = a['backup_reserve_fraction'] if reserve is None else reserve
    years = a['years'] if years is None else years
    if not (0 <= reserve <= 1 and 0 < efficiency <= 1 and 0 <= fom < 1):
        raise ValueError('invalid physical or cost fraction')
    if min(cost, a['power_mw'], a['duration_hours'], a['cycles_per_year'], years) <= 0:
        raise ValueError('cost, capacity, cycles and horizon must be positive')
    if a['cycles_per_year'] * a['duration_hours'] * (1 + 1 / efficiency) > 8760:
        raise ValueError('cycle assumption exceeds conservative charging/discharging hour budget')
    if a['discount_rate_real'] <= -1 or not 0 <= a['terminal_recovery_fraction'] <= 1:
        raise ValueError('invalid discount/recovery assumption')
    energy = a['power_mw'] * a['duration_hours']
    capex = energy * 1000 * cost
    output = energy * a['cycles_per_year'] * (1 - reserve)
    spread = a['discharge_price_usd_per_mwh'] - a['charge_price_usd_per_mwh'] / efficiency
    annual_fom = capex * fom
    pv_factor = sum((1 + a['discount_rate_real']) ** -t for t in range(1, years + 1))
    recovery_pv = capex * a['terminal_recovery_fraction'] / (1 + a['discount_rate_real']) ** years
    cost_pv = capex + annual_fom * pv_factor - recovery_pv
    npv = output * spread * pv_factor - cost_pv
    hurdle = cost_pv / (output * pv_factor) if output else None
    return {
        'cost_usd_per_kwh': cost, 'reserve_fraction': reserve, 'years': years,
        'capacity_mwh': energy, 'initial_capex_usd_m': round(capex / 1e6, 6),
        'annual_discharge_mwh': round(output, 6),
        'net_dispatch_spread_usd_per_mwh': round(spread, 6),
        'required_net_spread_usd_per_mwh': round(hurdle, 6) if hurdle is not None else None,
        'npv_usd_m': round(npv / 1e6, 6),
        'additional_level_annual_benefit_for_break_even_usd_m': round(max(0, -npv / pv_factor) / 1e6, 6),
        'scope': 'pre-tax real unlevered; no merchant dispatch optimization, taxes, financing or issuer valuation'
    }


def calculate(inputs, sources):
    a = inputs['assumptions']
    cost = value(sources, 'IRENA2025', 'installed_cost', 'USD_2025/kWh')
    if a['duration_hours'] != value(sources, 'IRENA2025', 'duration', 'hours'):
        raise ValueError('global four-hour benchmark cannot be silently applied to another duration')
    eff = value(sources, 'ATB2025', 'roundtrip_efficiency', 'fraction')
    fom = value(sources, 'ATB2025', 'annual_fom', 'fraction_of_initial_capex')
    life = value(sources, 'ATB2025', 'lifetime', 'years')
    if a['years'] > life:
        raise ValueError('horizon exceeds supported maintained-capacity life')
    return {'prepared_on': inputs['prepared_on'], 'reference': storage_case(a, cost, eff, fom),
            'sensitivities': [storage_case(a, c, eff, fom, r) for c in a['site_cost_scenarios_usd_per_kwh'] for r in a['reserve_scenarios']],
            'fifteen_year_separate_horizon': storage_case(a, cost, eff, fom, years=life)}


def render(d):
    b = d['reference']
    lines = ['# Battery storage: computed hurdles', '',
             'Original calculations, 21 October 2026. Constant 2025 USD. Public benchmark costs plus labelled assumptions; not a quoted project return.', '',
             f"Reference: {b['capacity_mwh']:.0f} MWh; initial capex ${b['initial_capex_usd_m']:.2f}m; modeled NPV ${b['npv_usd_m']:.2f}m.", '',
             f"Required net dispatch margin: ${b['required_net_spread_usd_per_mwh']:.2f}/MWh, versus assumed ${b['net_dispatch_spread_usd_per_mwh']:.2f}/MWh after charging losses.", '',
             f"Equivalent additional annual benefit needed: ${b['additional_level_annual_benefit_for_break_even_usd_m']:.2f}m. This is a hurdle, not evidence that availability payments or avoided losses exist.", '',
             '| Installed cost ($/kWh) | Backup reserve | Required net spread ($/MWh) | NPV ($m) |',
             '|---:|---:|---:|---:|']
    for x in d['sensitivities']:
        lines.append(f"| {x['cost_usd_per_kwh']:.0f} | {x['reserve_fraction']:.0%} | {x['required_net_spread_usd_per_mwh']:.2f} | {x['npv_usd_m']:.2f} |")
    y = d['fifteen_year_separate_horizon']
    lines += ['', f"Separate 15-year sensitivity: required net spread ${y['required_net_spread_usd_per_mwh']:.2f}/MWh. This longer horizon is not interchangeable with the existing 10-year AI infrastructure comparison.", '',
              'FOM includes augmentation. No second degradation/replacement charge is added. Reserve reduces dispatchable energy; backup receives no invented revenue. See [method and interpretation](README.md) and [sources](sources.json).', '']
    return '\n'.join(lines)


if __name__ == '__main__':
    run_cli(Path(__file__).parent, calculate, render)
