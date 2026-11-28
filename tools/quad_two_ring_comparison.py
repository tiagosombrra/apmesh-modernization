"""Compare adopted bounded and complete-two-ring jets on identical retained meshes.

This reports paired nodal differences, never a global curvature error or a
criterion for choosing a support, accepting a mesh or activating adaptation.
"""
import argparse
import csv
import json
import math
from pathlib import Path
import statistics

from quad_quadratic_curvature import measure_archive


# Existing independent numerical agreement budget, fixed before real measurement.
# Used only to distinguish reported changes from numerical ties, not acceptance.
NUMERICAL_TIE = 1e-7
IDENTITY = ('step', 'epoch', 'retry', 'domain_generation',
            'reference_tri_accepted', 'reason', 'scheme', 'file', 'sha256')


def distribution(values):
    return dict(count=len(values), median=statistics.median(values) if values else None,
                maximum=max(values) if values else None)


def paired_group(original, variant, boundary=None):
    pairs = [(a, b) for a, b in zip(original, variant)
             if boundary is None or a['boundary'] == boundary]
    coverage = dict(both_available=0, original_only=0, variant_only=0, neither=0)
    for a, b in pairs:
        key = ('both_available' if b['status'] == 'available' else 'original_only') if a['status'] == 'available' else (
            'variant_only' if b['status'] == 'available' else 'neither')
        coverage[key] += 1
    result = dict(nodes=len(pairs), coverage=coverage)
    available = [(a, b) for a, b in pairs if a['status'] == b['status'] == 'available']
    for channel in ('K', 'H'):
        key = f'abs_{channel}_difference'
        first, second = [a[key] for a, _ in available], [b[key] for _, b in available]
        changes = dict(improved=0, worsened=0, numerical_tie=0)
        for a, b in zip(first, second):
            if math.isclose(a, b, abs_tol=NUMERICAL_TIE, rel_tol=NUMERICAL_TIE):
                changes['numerical_tie'] += 1
            else:
                changes['improved' if b < a else 'worsened'] += 1
        result[channel] = dict(original=distribution(first), complete_two_ring=distribution(second),
                               paired_changes=changes)
    for name in ('scale', 'condition'):
        result[name] = dict(original=distribution([a[name] for a, _ in available]),
                            complete_two_ring=distribution([b[name] for _, b in available]))
    result['support_size'] = dict(original=distribution([len(a['support']) for a, _ in pairs]),
                                  complete_two_ring=distribution([len(b['support']) for _, b in pairs]))
    return result


def compare_reports(original, variant):
    if (original['inputs_sha256'] != variant['inputs_sha256'] or
            original['source'] != variant['source'] or
            variant.get('neighborhood_policy') != 'complete_two_ring'):
        raise ValueError('Jet comparison requires the same inputs and explicit variant')
    if len(original['stages']) != len(variant['stages']):
        raise ValueError('Jet comparison stage inventory differs')
    for report in (original, variant):
        if report['mixed_global_error'] is not None or report['accepted_mixed_epochs'] != 0:
            raise ValueError('Nodal comparison must not publish global/adaptive results')
    stages, rows = [], []
    for a, b in zip(original['stages'], variant['stages']):
        if any(a[k] != b[k] for k in IDENTITY) or a['nodes'] != b['nodes']:
            raise ValueError('Jet comparison changed snapshot identity or nodes')
        first, second = a['per_node'], b['per_node']
        if len(first) != len(second) or len(first) != a['nodes']:
            raise ValueError('Incomplete paired jet inventory')
        changed_support = 0
        for i, (old, new) in enumerate(zip(first, second)):
            if (old['node'] != i or new['node'] != i or new['ring'] != 2 or
                    old['boundary'] != new['boundary'] or
                    any(old[k] != new[k] for k in ('analytical_K', 'analytical_H'))):
                raise ValueError('Unpaired jet query or incorrect complete-ring policy')
            if old['support'] == new['support']:
                if {k: v for k, v in old.items() if k != 'ring'} != {k: v for k, v in new.items() if k != 'ring'}:
                    raise ValueError('Unchanged jet support changed numerical results')
            else:
                changed_support += 1
                if not set(old['support']).issubset(new['support']):
                    raise ValueError('Complete second ring dropped original samples')
            row = {k: a[k] for k in IDENTITY}
            row.update(node=i, boundary=old['boundary'], original_status=old['status'],
                       variant_status=new['status'], original_ring=old['ring'],
                       original_support='|'.join(map(str, old['support'])),
                       complete_two_ring_support='|'.join(map(str, new['support'])))
            for channel in ('K', 'H'):
                row.update({f'analytical_{channel}': old[f'analytical_{channel}'],
                            f'original_{channel}': old[channel], f'complete_two_ring_{channel}': new[channel],
                            f'original_abs_{channel}': old[f'abs_{channel}_difference'],
                            f'complete_two_ring_abs_{channel}': new[f'abs_{channel}_difference']})
            rows.append(row)
        stages.append(dict({k: a[k] for k in IDENTITY}, nodes=a['nodes'],
                           changed_support_nodes=changed_support,
                           original_coverage=a['coverage'], complete_two_ring_coverage=b['coverage'],
                           all_nodes=paired_group(first, second),
                           boundary=paired_group(first, second, True),
                           interior=paired_group(first, second, False)))
    return dict(schema='apmesh.quad.two_ring_comparison.v1', source=original['source'],
                inputs_sha256=original['inputs_sha256'], stages=stages,
                numerical_tie_budget=NUMERICAL_TIE, mixed_global_error=None, accepted_mixed_epochs=0,
                scope='Paired fixed-mesh nodal diagnostic only. Coverage losses are explicit; no support selection or estimator/global/adaptive adoption.'), rows


def compare_archive(archive, probe, output):
    output = Path(output)
    original = measure_archive(archive, probe, output)
    variant = measure_archive(archive, probe, output/'complete-two-ring', policy='complete_two_ring')
    result, rows = compare_reports(original, variant)
    result['probe_sha256'] = original['probe_sha256']
    result['independent_agreement_max'] = dict(original=original['independent_agreement_max'],
                                                complete_two_ring=variant['independent_agreement_max'])
    result['rejected_forgeries'] = original['rejected_forgeries'] + variant['rejected_forgeries']
    (output/'comparison.json').write_text(json.dumps(result, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    with (output/'comparison.csv').open('w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive', type=Path, required=True)
    parser.add_argument('--probe', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    report = compare_archive(args.archive, args.probe, args.output)
    print(json.dumps(dict(paired_stages=len(report['stages']), rejected_forgeries=report['rejected_forgeries'])))


if __name__ == '__main__':
    main()
