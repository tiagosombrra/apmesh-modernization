"""Check actual caller stopping traces against retained accepted errors."""
import argparse
import json
import math
from pathlib import Path


def validate(rows):
    if not rows or rows[0]['event'] != 'accepted' or rows[-1]['event'] != 'function_end':
        raise ValueError('Missing accepted initialization or complete caller return')
    accepted = None
    guards = stops = rejections = 0
    thresholds = (rows[0]['epsilon'], rows[0]['tolerance'])
    for index, row in enumerate(rows):
        if (row['epsilon'], row['tolerance']) != thresholds:
            raise ValueError('Stopping thresholds changed during execution')
        if not all(math.isfinite(row[k]) for k in ('accepted_global', 'accepted_local_max', 'history_global', 'current_local_max')):
            raise ValueError('Nonfinite accepted error observation')
        if row['event'] == 'accepted':
            accepted = (row['step'], row['cached_global'], row['current_local_max'])
        elif row['event'] == 'accepted_error_control':
            # Explicit synthetic accepted-state controls are not solver results.
            accepted = (row['accepted_step'], row['history_global'], row['current_local_max'])
        if (row['accepted_step'], row['accepted_global'], row['accepted_local_max']) != accepted or row['history_global'] != accepted[1]:
            raise ValueError('Accepted error provenance differs from committed history')
        if row['event'] in ('guard_entry', 'rejected_restored', 'rejected_ready'):
            if row['current_local_max'] != accepted[2]:
                raise ValueError('Local accepted errors were not restored')
        if row['event'] == 'rejected_ready':
            rejections += 1
        if row['event'] == 'guard_entry':
            guards += 1
            expected = ('global_stop' if accepted[1] <= row['epsilon'] else
                        'local_stop' if accepted[2] <= row['tolerance'] else 'attempt_evaluated')
            following = next((r['event'] for r in rows[index + 1:] if r['event'] != 'growth_rejected'), None)
            if following != expected:
                raise ValueError('Guard did not select the retained accepted error with global-first priority')
        if row['event'] in ('global_stop', 'local_stop'):
            stops += 1
            expected_reason = ('target_error_reached' if row['event'] == 'global_stop' else
                               'local_error_threshold_reached')
            if index == 0 or rows[index - 1]['event'] != 'guard_entry':
                raise ValueError('Stop without a preceding guard')
            if index + 1 != len(rows) - 1 or rows[-1]['reason'] != expected_reason or rows[-1]['step'] != row['step']:
                raise ValueError('Stop label, step or terminal extent differs')
    if guards == 0 or stops > 1 or sum(r['event'] == 'function_end' for r in rows) != 1:
        raise ValueError('Missing guard coverage or duplicated completion')
    return {'guards': guards, 'stops': stops, 'rejections': rejections,
            'last_accepted_step': rows[-1]['accepted_step'], 'last_step': rows[-1]['step']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('trace', type=Path)
    args = parser.parse_args()
    print(json.dumps(validate([json.loads(line) for line in args.trace.read_text().splitlines()])))
