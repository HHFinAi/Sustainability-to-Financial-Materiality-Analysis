"""Offline helpers for bounded public-evidence cases; no research approval."""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path


def load(folder):
    folder = Path(folder)
    inputs = json.loads((folder / 'inputs.json').read_text())
    register = json.loads((folder / 'sources.json').read_text())
    sources = {s['id']: s for s in register['sources']}
    if len(sources) != len(register['sources']):
        raise ValueError('duplicate source ID')
    cutoff = register['evidence_cutoff']
    for s in sources.values():
        if not s['url'].startswith('https://') or not s['locator']:
            raise ValueError('source requires HTTPS URL and locator')
        if s['publication_date'] > cutoff or s['retrieved_on'] > cutoff:
            raise ValueError('post-cutoff evidence')
        for item in s['metrics'].values():
            if not isinstance(item['value'], (float, int)) or not math.isfinite(item['value']):
                raise ValueError('non-finite evidence metric')
            if not item['unit'] or not item['kind']:
                raise ValueError('missing unit or claim type')
    return inputs, sources


def value(sources, source_id, key, unit):
    item = sources[source_id]['metrics'][key]
    if item['unit'] != unit:
        raise ValueError(f'unit mismatch: {source_id}/{key}')
    return item['value']


def dump(data):
    return json.dumps(data, indent=2, sort_keys=True, allow_nan=False) + '\n'


def run_cli(folder, calculate, render):
    parser = argparse.ArgumentParser(description='Recompute public-source facts and labelled scenarios offline.')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--write', action='store_true', help='Explicitly regenerate result artifacts')
    group.add_argument('--check', action='store_true', help='Compare against archived results without rewriting')
    args = parser.parse_args()
    folder = Path(folder)
    data = calculate(*load(folder))
    artifacts = {'results.json': dump(data), 'RESULTS.md': render(data)}
    if args.write:
        for name, text in artifacts.items():
            (folder / name).write_text(text, encoding='utf-8')
        print('WROTE: ' + ', '.join(artifacts))
    elif args.check:
        for name, text in artifacts.items():
            if (folder / name).read_text(encoding='utf-8') != text:
                raise ValueError(f'stale output: {name}')
        print('PASS: source schema, units and archived result reproduction')
    else:
        print(dump(data), end='')
