"""Validate actual accepted-step labels and unchanged final console scalars."""
import argparse
import json
import math
from pathlib import Path
import re

FIELDS = {'error', 'elementos', 'nos_gauss', 'nos_mean', 'quality_min', 'quality_mean',
          'poor_ratio', 'acceptance_score', 'retry', 'relaxation', 'max_delta',
          'queda_abs', 'queda_pct', 'queda_por_elemento', 'fator_crescimento_elementos',
          'erro_normalizado'}
ROW = re.compile(rb'^Erro no step_ (\d+) = ([^,]+), (.+)$')


def history_rows(raw):
    rows = []
    for line in raw.splitlines():
        if not line.startswith(b'Erro no step_ '):
            continue
        match = ROW.fullmatch(line)
        if match is None:
            raise ValueError('Malformed final accepted report row')
        pairs = [('error', match[2].decode('ascii'))]
        pairs.extend(tuple(piece.strip() for piece in item.split('=', 1))
                     for item in match[3].decode('ascii').split(','))
        if any(len(pair) != 2 for pair in pairs):
            raise ValueError('Malformed final accepted scalar')
        values = dict(pairs)
        if len(values) != len(pairs) or set(values) != FIELDS:
            raise ValueError('Missing or duplicated final accepted scalar')
        if not all(math.isfinite(float(value)) for value in values.values()):
            raise ValueError('Nonfinite final accepted scalar')
        rows.append({'step': int(match[1]), 'values': values})
    return rows


def validate(raw, accepted_steps, reference=None):
    if not accepted_steps or accepted_steps[0] != 0 or accepted_steps != sorted(set(accepted_steps)):
        raise ValueError('Missing, duplicated or unordered accepted-step ledger')
    rows = history_rows(raw)
    if not rows or [row['step'] for row in rows] != accepted_steps:
        raise ValueError('Final labels do not identify the actual accepted steps')
    if reference is not None:
        previous = history_rows(reference)
        if not previous or [row['values'] for row in previous] != [row['values'] for row in rows]:
            raise ValueError('Final accepted scalar output changed')
    return {'accepted_steps': accepted_steps, 'rows': len(rows),
            'scalar_fields': len(FIELDS) * len(rows)}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stdout', type=Path)
    parser.add_argument('--steps', nargs='+', type=int, required=True)
    parser.add_argument('--reference', type=Path)
    args = parser.parse_args()
    print(json.dumps(validate(args.stdout.read_bytes(), args.steps,
                              args.reference.read_bytes() if args.reference else None)))
