"""Score only registered, dated operating observations; no network or fake outcomes."""
from __future__ import annotations
import argparse
from datetime import date
import hashlib
import json
import math
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]


def score(register, observations, as_of):
    cutoff = date.fromisoformat(register['frozen_on'])
    current = date.fromisoformat(as_of)
    if current < cutoff:
        raise ValueError('as-of precedes the prediction freeze')
    predictions = {p['id']: p for p in register['predictions']}
    if len(predictions) != len(register['predictions']) or not predictions:
        raise ValueError('empty or duplicate prediction IDs')
    for p in predictions.values():
        if not 0 <= p['probability'] <= 1 or p['operator'] not in ('>', '>='):
            raise ValueError('invalid probability or comparison')
        if not math.isfinite(p['threshold']):
            raise ValueError('nonfinite threshold')
    observed = {}
    for o in observations:
        if o['id'] not in predictions or o['id'] in observed:
            raise ValueError('unknown or duplicate observation')
        p = predictions[o['id']]
        if any(o[k] != p[k] for k in ('period', 'metric', 'unit')):
            raise ValueError('observation scope or unit mismatch')
        if isinstance(o['value'], bool) or not isinstance(o['value'], (float, int)) or not math.isfinite(o['value']):
            raise ValueError('nonfinite or nonnumeric observation')
        published, retrieved = date.fromisoformat(o['published_on']), date.fromisoformat(o['retrieved_on'])
        if not cutoff < published <= retrieved <= current:
            raise ValueError('observation must be after freeze and available by as-of')
        url = urlparse(o['source_url'])
        if url.scheme != 'https' or url.hostname not in p['allowed_source_hosts'] or not o['locator'] or not o['reviewer']:
            raise ValueError('issuer source, locator and reviewer required')
        outcome = int(o['value'] > p['threshold'] if p['operator'] == '>' else o['value'] >= p['threshold'])
        observed[o['id']] = {'id': o['id'], 'value': o['value'], 'outcome': outcome,
                              'brier_score': round((p['probability'] - outcome) ** 2, 8),
                              'naive_brier_score': .25, 'source_url': o['source_url']}
    rows = [observed[k] for k in predictions if k in observed]
    pending = [k for k in predictions if k not in observed]
    return {'as_of': as_of, 'frozen_on': register['frozen_on'], 'total_predictions': len(predictions),
            'scored_count': len(rows), 'pending': pending, 'events': rows,
            'mean_brier_score': round(sum(r['brier_score'] for r in rows) / len(rows), 8) if rows else None,
            'naive_mean_brier_score': .25 if rows else None,
            'status': 'PENDING' if not rows else ('PARTIAL' if pending else 'SCORED'),
            'scope': 'Operating hypotheses only; subjective probabilities, tiny correlated sample, no alpha claim.'}


def load():
    frozen = json.loads((ROOT / 'freeze.json').read_text())
    for name, expected in frozen['sha256'].items():
        path = (REPO / name).resolve()
        if not path.is_relative_to(REPO) or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError('frozen evidence or prediction bytes changed')
    return json.loads((ROOT / 'predictions.json').read_text()), json.loads((ROOT / 'observations.json').read_text())['observations']


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--check', action='store_true')
    p.add_argument('--as-of')
    args = p.parse_args()
    register, observations = load()
    as_of = args.as_of or register['frozen_on']
    # The archived cutoff is deliberately empty. Later observations belong to
    # a new dated view and must not overwrite the original pending snapshot.
    selected = [] if args.check else observations
    output = json.dumps(score(register, selected, as_of), indent=2, sort_keys=True, allow_nan=False) + '\n'
    if args.check:
        if args.as_of and args.as_of != register['frozen_on']:
            raise ValueError('--check reproduces only the frozen cutoff status')
        if output != (ROOT / 'STATUS.json').read_text():
            raise ValueError('archived cutoff status differs; preserve it and record later results separately')
        print('PASS: frozen bytes and archived empty cutoff status; later observations require a dated scoring run')
    else:
        print(output, end='')
