#!/usr/bin/env python3
"""Recalculate paper-only Euler prechecks from immutable research source files."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from thingi10k_f18_quad_reference_gate import published_rows, build_published_comparison

ROSTER_GIT_BLOB = '471461eb74027428253c6c3b00ef5b6097eea63d'
CATALOG_SLICE_GIT_BLOB = '0844dc91dd14fb640819c35103c8370abb5fa821'
F17_SEVEN_GIT_BLOB = '80ca4ef6ce2eda197e7c9cae635ec77d12d0d7e9'
CATALOG_GIT_BLOB = 'ac376cc8604436f9460cac39b5171ce8d99b2e74'


def pinned_git_blob(path: Path, expected: str) -> bytes:
    """Validate exact file bytes using the Git content-addressed blob contract."""
    if not path.is_file() or path.stat().st_size > 10_000_000:
        raise ValueError('Missing or oversized immutable research source')
    content = path.read_bytes()
    digest = hashlib.sha1(b'blob ' + str(len(content)).encode() + b'\0' + content).hexdigest()
    if digest != expected:
        raise ValueError(f'Research blob changed: {path.name}')
    return content


def recalculate(roster_path: Path, catalog_path: Path, f17_path: Path,
                *, expected_roster: str = ROSTER_GIT_BLOB,
                expected_catalog: str = CATALOG_SLICE_GIT_BLOB,
                expected_f17: str = F17_SEVEN_GIT_BLOB) -> dict:
    """Certify only 12 published numerical prechecks, not actual QUAD outputs."""
    pinned_git_blob(roster_path, expected_roster)
    blob = pinned_git_blob(catalog_path, expected_catalog)
    f17_blob = pinned_git_blob(f17_path, expected_f17)
    catalog = json.loads(blob)
    f17 = json.loads(f17_blob)
    if catalog.get('catalog_git_blob_sha1') != CATALOG_GIT_BLOB:
        raise ValueError('Wrong upstream 9,997-entry catalog identity')
    if len(catalog.get('source_records', [])) != 12:
        raise ValueError('Expected 12 original source records')
    pub = published_rows(roster_path)
    if catalog.get('frozen_quadwild_model_ids') != list(pub):
        raise ValueError('Catalog order does not match frozen paper IDs')
    if len(f17.get('raw_stl_audits', [])) != 7:
        raise ValueError('F17 independent source audit count changed')
    result = build_published_comparison(pub, catalog['source_records'], f17)
    matches = [x['file_id'] for x in result['cases'] if x['published_output_euler_compatible_with_source']]
    if matches != [58012, 67792, 81877, 94884]:
        raise ValueError('Unexpected source-vs-published conditional Euler match population')
    audited = [x for x in result['cases'] if
               x['source_euler_evidence'] == 'AUDITED_EXACT_COORDINATE_STL' and
               x['published_output_euler_compatible_with_source']]
    if [x['file_id'] for x in audited] != [58012]:
        raise ValueError('Unexpected actual raw STL topology evidence')
    result.update({
        'frozen_roster_git_blob_sha1': expected_roster,
        'frozen_catalog_slice_git_blob_sha1': expected_catalog,
        'frozen_seven_source_audits_git_blob_sha1': expected_f17,
        'individual_quad_output_file_sha256_verified': False,
        'actual_quadwild_archive_extracted': False,
        'source_vs_output_homeomorphism_demonstrated': False,
        'dataset_per_asset_rights_approved': False,
    })
    return result


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--published-csv', type=Path, required=True)
    parser.add_argument('--catalog-subset', type=Path, required=True)
    parser.add_argument('--f17-source-audits', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(argv)
    receipt = recalculate(args.published_csv, args.catalog_subset, args.f17_source_audits)
    # Exclusive creation is deliberate; never overwrite a previous evidence receipt.
    with args.output.open('x', encoding='utf-8') as stream:
        json.dump(receipt, stream, indent=2, sort_keys=True)
        stream.write('\n')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
