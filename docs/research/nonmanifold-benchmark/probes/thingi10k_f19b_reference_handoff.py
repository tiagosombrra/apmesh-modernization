#!/usr/bin/env python3
"""Cross-check F17/F19/F18 local receipts without admitting a scientific QUAD pair.

No network I/O, asset writes, topology repair, remeshing or rights inference occurs.
An independently licensed and provenance-verified author reference is still required.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path, PurePosixPath
import re

AUTHOR_ARCHIVE_URL = 'https://www.quadmesh.cloud/thingi10k-quad-dataset.zip'
MAX_REFERENCE_BYTES = 250_000_000
SHA256 = re.compile(r'[0-9a-f]{64}\Z')


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def read_json(path: Path) -> dict:
    require(path.is_file() and path.stat().st_size <= 1_000_000, 'Missing/oversized receipt')
    with path.open('r', encoding='utf-8') as stream:
        data = json.load(stream)
    require(isinstance(data, dict), 'Receipt must be an object')
    return data


def read_csv(path: Path) -> list[dict]:
    require(path.is_file() and path.stat().st_size <= 1_000_000, 'Missing/oversized manifest')
    with path.open(newline='', encoding='utf-8') as stream:
        rows = list(csv.DictReader(stream))
    require(rows and 'thingi10k_file_id' in rows[0], 'Manifest lacks model IDs')
    ids = [int(row['thingi10k_file_id']) for row in rows]
    require(len(ids) == len(set(ids)), 'Duplicate model ID in manifest')
    return rows


def sha256_file(path: Path) -> str:
    require(path.is_file() and 0 < path.stat().st_size <= MAX_REFERENCE_BYTES,
            'Missing, empty or oversized extracted output')
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for piece in iter(lambda: stream.read(1 << 20), b''):
            digest.update(piece)
    return digest.hexdigest()


def check(model_id: int, source_manifest: Path, literature_manifest: Path,
          extraction_receipt: Path, topology_receipt: Path, actual_output: Path) -> dict:
    """Check identity, hashes, literature counts and claimed topology without admission."""
    require(model_id > 0, 'Invalid model ID')
    sources = read_csv(source_manifest)
    papers = read_csv(literature_manifest)
    require(len(sources) == 23, 'Expected the original frozen 23-case source cohort')
    require(sum(row.get('literature_cohort') == 'QUADWILD_FIG29' for row in papers) == 12,
            'Expected twelve original QuadWild literature cases')
    source_rows = [row for row in sources if int(row['thingi10k_file_id']) == model_id]
    paper_rows = [row for row in papers if int(row['thingi10k_file_id']) == model_id]
    require(len(source_rows) == len(paper_rows) == 1, 'Case not in both source and literature rosters')
    source, paper = source_rows[0], paper_rows[0]
    require(source['literature_cohort'] == paper['literature_cohort'] == 'QUADWILD_FIG29',
            'Case has no published QuadWild reference')
    require(source['raw_stl_audit_executed'] == 'YES', 'Source raw STL has not been audited')
    source_sha = source['source_stl_sha256']
    require(isinstance(source_sha, str) and SHA256.fullmatch(source_sha) is not None,
            'Missing pinned original STL SHA-256')
    require(len(source['source_zip_git_blob_sha1']) == 40, 'Missing original ZIP Git blob identity')
    expected_v = int(paper['published_quad_vertices'])
    expected_f = int(paper['published_quad_faces'])
    require(expected_v > 0 and expected_f > 0, 'Missing published QUAD counts')
    extraction = read_json(extraction_receipt)
    topology = read_json(topology_receipt)
    require(extraction.get('schema') == 'apmesh-quadwild-f19-range-index-v1',
            'Not an F19 remote ZIP extraction receipt')
    require(extraction.get('status') == 'ONE_ORIGINAL_OUTPUT_MEMBER_EXTRACTED_NOT_PAIR_VERIFIED',
            'F19 receipt does not attest extraction of one member')
    require(extraction.get('original_thin_archive_url') == AUTHOR_ARCHIVE_URL,
            'F19 source is not the frozen authors archive URL')
    require(extraction.get('thingi10k_file_id') == model_id,
            'F19 receipt belongs to another model ID')
    require(extraction.get('source_output_pair_verified') is False and
            extraction.get('matched_published_quad_output') is False,
            'F19 flags contradict the unadmitted acquisition contract')
    member = extraction.get('selected_member')
    require(isinstance(member, str) and member and not member.startswith('/') and
            '..' not in member.split('/') and '\\' not in member,
            'Unsafe or missing ZIP member name')
    require(PurePosixPath(member).suffix.lower() in {'.obj', '.npz'} and
            re.search(r'(?<![0-9])' + str(model_id) + r'(?![0-9])', member) is not None,
            'Member is not an OBJ/NPZ for the exact model ID')
    members = extraction.get('candidate_members')
    require(isinstance(members, list) and sum(
        isinstance(entry, dict) and entry.get('name') == member for entry in members) == 1,
        'Selected member is not unique in the acquired ZIP index')
    saved_path = extraction.get('output_local_file')
    require(isinstance(saved_path, str) and Path(saved_path).resolve() == actual_output.resolve(),
            'Current reference output is not the F19 extracted file')
    digest = sha256_file(actual_output)
    require(extraction.get('selected_member_original_sha256') == digest,
            'Actual file SHA-256 disagrees with original extracted member')
    require(extraction.get('selected_member_original_bytes') == actual_output.stat().st_size,
            'Actual file byte length disagrees with extraction receipt')
    require(topology.get('file_id') == model_id, 'F18 inspected a different model ID')
    require(topology.get('actual_quad_sha256') == digest,
            'F18 inspected a different output file hash')
    require(topology.get('original_stl_sha256') == source_sha,
            'F18 original STL SHA-256 differs from frozen F17 identity')
    require(topology.get('reference_pair_accepted_for_fair_comparison') is False,
            'F18 receipt incorrectly claims pair admission')
    raw = topology.get('raw_quad_topology')
    require(isinstance(raw, dict), 'F18 topology audit absent')
    v, f = raw.get('vertices'), raw.get('quad_faces')
    require(isinstance(v, int) and not isinstance(v, bool) and v > 0 and
            isinstance(f, int) and not isinstance(f, bool) and f > 0,
            'F18 output V/F counts invalid')
    counts_match = (v, f) == (expected_v, expected_f)
    require(topology.get('published_vertex_face_counts_match') is counts_match,
            'F18 paper-count parity flag disagrees with independent roster')
    valid_topo = (raw.get('closed_connected_orientable_combinatorial') is True and
                  raw.get('singular_vertex_links') == 0 and
                  raw.get('orientation_conflicts') == 0 and
                  raw.get('face_components') == 1 and
                  raw.get('genus_if_valid') is not None)
    require(topology.get('reference_topology_screen_passed') is (counts_match and valid_topo),
            'F18 topology screening flag conflicts with recorded topology')
    genus = source.get('conditional_source_surface_genus')
    genus_match = bool(valid_topo and genus and int(genus) == raw.get('genus_if_valid'))
    precheck = bool(counts_match and valid_topo and genus_match)
    return {
        'schema': 'apmesh-thingi10k-f19b-cross-stage-handoff-v1',
        'model_id': model_id,
        'status': ('LOCAL_REFERENCE_PRECHECK_PASS_PROVENANCE_AND_RIGHTS_OPEN' if precheck
                   else 'LOCAL_REFERENCE_PRECHECK_MISMATCH_OR_INCOMPLETE'),
        'f17_original_stl_sha256': source_sha,
        'f17_original_zip_git_blob_sha1': source['source_zip_git_blob_sha1'],
        'f19_selected_original_member': member,
        'f19_actual_extracted_member_sha256_verified': digest,
        'f19_remote_archive_full_sha256_independently_verified': False,
        'f18_raw_quad_topology_claim_cross_checked': True,
        'published_counts': {'vertices': expected_v, 'faces': expected_f},
        'actual_counts': {'vertices': v, 'faces': f},
        'published_count_parity': counts_match,
        'source_output_euler_genus_necessary_precheck': genus_match,
        'independent_author_input_to_output_pair_provenance_verified': False,
        'per_asset_source_and_output_redistribution_rights_cleared': False,
        'paper_quality_metrics_independently_recomputed': False,
        'apmesh_matched_input_tri_quad_executed': False,
        'scientific_reference_pair_admitted': False,
        'comparison_with_apmesh_permitted': False,
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--model-id', type=int, required=True)
    ap.add_argument('--source-manifest', type=Path, required=True)
    ap.add_argument('--literature-manifest', type=Path, required=True)
    ap.add_argument('--f19-extraction-receipt', type=Path, required=True)
    ap.add_argument('--f18-topology-receipt', type=Path, required=True)
    ap.add_argument('--actual-quad', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args(argv)
    receipt = check(args.model_id, args.source_manifest, args.literature_manifest,
                    args.f19_extraction_receipt, args.f18_topology_receipt, args.actual_quad)
    with args.output.open('x', encoding='utf-8') as stream:
        json.dump(receipt, stream, indent=2, sort_keys=True)
        stream.write('\n')
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (ValueError, OSError, json.JSONDecodeError) as error:
        raise SystemExit(f'F19B HANDOFF BLOCKED: {error}') from error
