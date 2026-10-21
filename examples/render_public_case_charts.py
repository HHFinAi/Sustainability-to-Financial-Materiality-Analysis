"""Optional plotting dependency: matplotlib. Models and CI remain stdlib-only."""
from pathlib import Path
import argparse
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 11,
                     'svg.fonttype': 'none', 'svg.hashsalt': 'hhfinai-public-cases-20261021',
                     'axes.spines.top': False, 'axes.spines.right': False})


def render(preview=None):
    def data(name):
        return json.loads((ROOT / name / 'results.json').read_text())

    def save(fig, name, note):
        fig.text(.08, .025, note, fontsize=9, color='#526170')
        fig.tight_layout(rect=(0, .11, 1, 1))
        fig.savefig(ROOT / name / 'chart.svg', metadata={'Date': None})
        if preview:
            preview.mkdir(parents=True, exist_ok=True)
            fig.savefig(preview / (name + '.png'), dpi=120)
        plt.close(fig)

    d = data('battery-storage')
    fig, ax = plt.subplots(figsize=(10, 5.5))
    for reserve, color in [(0, '#267d8d'), (.25, '#17365d'), (.5, '#be6d20')]:
        rows = [x for x in d['sensitivities'] if x['reserve_fraction'] == reserve]
        ax.plot([x['cost_usd_per_kwh'] for x in rows], [x['required_net_spread_usd_per_mwh'] for x in rows], marker='o', color=color, label=f'{reserve:.0%} backup reserve')
    ax.axhline(d['reference']['net_dispatch_spread_usd_per_mwh'], color='#777777', ls='--', label='Assumed net dispatch margin')
    ax.set(title='Storage: backup reserve raises the dispatch hurdle', xlabel='Installed cost (constant 2025 USD/kWh)', ylabel='Required net margin (USD/MWh)')
    ax.set_ylim(0, 475)
    ax.legend(loc='upper left', frameon=False)
    save(fig, 'battery-storage', 'Sources: IRENA 2025 costs; 2025 ATB. Original ten-year scenario; 21 Oct 2026.\nPrice/dispatch/reserve assumptions are hypothetical. Not a site return forecast.')

    d = data('climate-staples')['issuers']
    fig, ax = plt.subplots(figsize=(10, 5.5))
    vals = [x['one_percent_sales_unmitigated_cost_profit_hit_percent'] for x in d]
    bars = ax.barh([x['issuer'] for x in d], vals, color='#267d8d')
    ax.bar_label(bars, fmt='%.2f%%', padding=5)
    ax.set(title='The same cost shock has different profit arithmetic', xlabel='Operating profit decline from extra cost equal to 1% of sales (%)', xlim=(0, 9))
    ax.invert_yaxis()
    save(fig, 'climate-staples', 'Sources: H1 2026 issuer releases; underlying/recurring margins differ in definition.\nCommon cost experiment, not an exposure estimate or climate-risk ranking. 21 Oct 2026.')

    d = data('water-waste')['xylem']
    fig, ax = plt.subplots(figsize=(10, 5.5))
    vals = [d['reported_order_increase_wss_usd_m'], d['reported_order_increase_other_usd_m']]
    bars = ax.barh(['Water Solutions\nand Services', 'Other segments\ncombined'], vals, color=['#17365d', '#7c9faa'])
    ax.bar_label(bars, fmt='$%.0fm', padding=5)
    ax.set(title='Xylem: 95.6% of the order increase came from WSS', xlabel='Q2 2026 year-on-year change in reported orders (USD millions)', xlim=(0, 1050))
    ax.invert_yaxis()
    save(fig, 'water-waste', 'Source: Xylem Q2 2026 release. Original contribution calculation; 21 Oct 2026.\nReported dollar change is distinct from organic growth; orders are not recognized revenue.')


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--preview-dir', type=Path)
    render(p.parse_args().preview_dir)
