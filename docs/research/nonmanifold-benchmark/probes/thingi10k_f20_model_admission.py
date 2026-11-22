#!/usr/bin/env python3
"""Audit the frozen Thingi10K model cohort without admitting unexecuted benchmarks.

Inputs are provenance receipts, NOT an independently loaded original geometry.
No dataset downloads, mesh conversion, meshing or rights inference occur here.
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

LITERATURE_COHORT = {'QUADWILD_FIG29': 12, 'BADIA_FIG10_TABLE1': 11}
SHA_CHARS = frozenset('0123456789abcdef')


def fail_unless(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def csv_rows(path: Path, required: set[str]) -> dict[int, dict[str, str]]:
    fail_unless(path.is_file() and 0 < path.stat().st_size <= 1_000_000,
                f'Missing or oversized input CSV: {path.name}')
    with path.open('r', newline='', encoding='utf-8') as stream:
        reader = csv.DictReader(stream)
        fail_unless(required <= set(reader.fieldnames or []), f'CSV missing required columns: {path.name}')
        rows: dict[int, dict[str, str]] = {}
        for row in reader:
            model_id = int(row['thingi10k_file_id'])
            fail_unless(model_id > 0 and model_id not in rows, 'Duplicate/nonpositive model ID')
            rows[model_id] = row
        return rows


def read_invariants(path: Path) -> dict[int, dict]:
    fail_unless(path.is_file() and 0 < path.stat().st_size <= 1_000_000,
                'Missing/oversized raw STL topology audit')
    with path.open('r', encoding='utf-8') as stream:
        data = json.load(stream)
    fail_unless(data.get('audited_original_stl_files') == 7 and
                data.get('manifest_entries') == 23, 'F17 invariant summary denominator changed')
    inv = data['topology_invariants']
    fail_unless(isinstance(inv, dict) and len(inv) == 7, 'Expected seven source topology audits')
    return {int(k): v for k, v in inv.items()}


def is_sha(raw: str, width: int) -> bool:
    return len(raw) == width and set(raw) <= SHA_CHARS


def audit(sources_path: Path, literature_path: Path, topology_path: Path,
          paper_euler_path: Path) -> dict:
    sources = csv_rows(sources_path, {'thingi10k_file_id', 'literature_cohort',
        'raw_stl_audit_executed', 'source_stl_sha256', 'source_zip_git_blob_sha1',
        'source_zip_bytes', 'raw_euler_characteristic', 'conditional_source_surface_genus',
        'original_source_rights_independently_verified',
        'quadwild_reference_mesh_pair_verified', 'apmesh_mesh_generated'})
    literature = csv_rows(literature_path, {'thingi10k_file_id', 'literature_cohort',
        'published_quad_vertices', 'published_quad_faces', 'individual_license_status',
        'quad_result_pair_status', 'apmesh_pipeline_status'})
    paper_euler = csv_rows(paper_euler_path, {'thingi10k_file_id', 'source_euler_evidence',
        'published_quad_euler_if_closed_quad', 'published_output_euler_matches_source',
        'actual_quad_mesh_bytes_checked', 'matched_pair_verified', 'apmesh_quad_mesh_generated'})
    invariants = read_invariants(topology_path)
    fail_unless(len(sources) == len(literature) == 23 and sources.keys() == literature.keys(),
                'Source and literature 23-case denominators diverge')
    cohort_counts = Counter(r['literature_cohort'] for r in sources.values())
    fail_unless(cohort_counts == LITERATURE_COHORT, 'Original 12+11 cohort changed')
    fail_unless(set(paper_euler) == {k for k, r in sources.items()
                if r['literature_cohort'] == 'QUADWILD_FIG29'},
                'F18 paper rows do not match the original twelve QuadWild IDs')
    audited = {k for k, r in sources.items() if r['raw_stl_audit_executed'] == 'YES'}
    fail_unless(audited == invariants.keys(), 'Source manifest and seven raw audits disagree')

    cases = []
    for mid in sorted(sources):
        source, paper = sources[mid], literature[mid]
        fail_unless(source['literature_cohort'] == paper['literature_cohort'],
                    f'{mid}: contradictory literature cohorts')
        fail_unless(is_sha(source['source_zip_git_blob_sha1'], 40) and
                    int(source['source_zip_bytes']) > 0,
                    f'{mid}: absent source archive provenance')
        fail_unless(source['original_source_rights_independently_verified'] == 'NO' and
                    source['quadwild_reference_mesh_pair_verified'] == 'NO' and
                    source['apmesh_mesh_generated'] == 'NO',
                    f'{mid}: changed scientific claim needs an explicit new audit protocol')
        fail_unless(paper['individual_license_status'] == 'PER_ASSET_NOT_REVIEWED' and
                    paper['apmesh_pipeline_status'] == 'NOT_RUN',
                    f'{mid}: literature manifest experimental state changed')
        has_raw = mid in audited
        genus = None
        source_screen = 'RAW_STL_NOT_INDEPENDENTLY_AUDITED'
        if has_raw:
            inv = invariants[mid]
            fail_unless(is_sha(source['source_stl_sha256'], 64), f'{mid}: missing raw STL SHA-256')
            chi = int(source['raw_euler_characteristic'])
            fail_unless(chi == inv['source_mesh_euler_characteristic_raw'],
                        f'{mid}: source manifest Euler mismatch')
            if inv['closed_connected_orientable_surface_screen'] == 'COMBINATORIAL_PASS':
                genus = inv['applicable_genus']
                fail_unless(isinstance(genus, int) and genus >= 0 and chi == 2 - 2 * genus
                            and str(genus) == source['conditional_source_surface_genus'],
                            f'{mid}: genus and Euler certificate disagree')
                source_screen = 'ORIGINAL_RAW_STL_COMBINATORIAL_CLOSED_SURFACE_PASS'
            else:
                fail_unless(inv['applicable_genus'] is None and
                            source['conditional_source_surface_genus'] == '' and
                            inv.get('failed_conditions'),
                            f'{mid}: inadmissible source improperly assigned a genus')
                source_screen = 'RAW_STL_ADVERSARIAL_TOPOLOGY_NOT_A_CAD_JUNCTION_PROOF'
        else:
            fail_unless(source['source_stl_sha256'] == '' and
                        source['conditional_source_surface_genus'] == '' and
                        source['raw_euler_characteristic'] == '',
                        f'{mid}: unaudited original has invented geometry invariants')

        published_counts = None
        euler_comparison = 'NO_PUBLISHED_QUAD_REFERENCE'
        if mid in paper_euler:
            f18 = paper_euler[mid]
            fail_unless(all(f18[k] == 'false' for k in
                        ('actual_quad_mesh_bytes_checked', 'matched_pair_verified',
                         'apmesh_quad_mesh_generated')),
                        f'{mid}: F18 output availability changed')
            pv, pf = int(paper['published_quad_vertices']), int(paper['published_quad_faces'])
            fail_unless(pv > 0 and pf > 0 and
                        int(f18['published_quad_euler_if_closed_quad']) == pv - pf,
                        f'{mid}: paper V/F Euler precheck contradictory')
            published_counts = {'vertices': pv, 'quad_faces': pf}
            necessary_match = f18['published_output_euler_matches_source'] == 'true'
            if necessary_match:
                fail_unless(f18['source_euler_evidence'] in {
                    'DIRECT_RAW_STL_TOPOLOGY_AUDITED', 'CONDITIONAL_PINNED_CATALOG_ONLY'},
                    f'{mid}: conditional Euler match has no source basis')
                if has_raw:
                    fail_unless(genus is not None and
                                int(source['raw_euler_characteristic']) == pv - pf,
                                f'{mid}: raw source and published QUAD Euler mismatch')
            euler_comparison = ('NECESSARY_EULER_MATCH_RAW_SOURCE' if necessary_match and has_raw
                                else 'NECESSARY_EULER_MATCH_CATALOG_ONLY' if necessary_match
                                else 'NO_NECESSARY_EULER_MATCH_PROVED')
        if mid == 58012:
            fail_unless(has_raw and genus == 41 and
                        euler_comparison == 'NECESSARY_EULER_MATCH_RAW_SOURCE',
                        'Canopy #58012 reference pilot no longer satisfies frozen premises')
            role = 'REFERENCE_PAIR_ACQUISITION_FIRST'
        elif mid == 61394:
            fail_unless(has_raw and genus is None,
                        'Adversarial original STL #61394 topology changed')
            role = 'ADVERSARIAL_TOPOLOGY_CONTROL'
        elif source['literature_cohort'] == 'BADIA_FIG10_TABLE1' and genus is not None:
            role = 'SMALL_SOURCE_CONVERSION_PILOT' if genus <= 1 else 'HIGHER_GENUS_CONVERSION_STRESS'
        else:
            role = 'SOURCE_GEOMETRY_AUDIT_REQUIRED'
        cases.append({
            'model_id': mid,
            'cohort': source['literature_cohort'],
            'research_role': role,
            'source_archive_git_blob_sha1': source['source_zip_git_blob_sha1'],
            'original_raw_stl_sha256': source['source_stl_sha256'] if has_raw else None,
            'source_raw_stl_audited': has_raw,
            'source_topology_screen': source_screen,
            'source_genus_if_certified': genus,
            'reference_published_quad_counts': published_counts,
            'published_output_euler_screen': euler_comparison,
            'original_cad_curve_junction_proven': False,
            'four_sided_bezier_patch_domain_constructed': False,
            'original_author_quad_output_extracted': False,
            'input_output_preprocessing_correspondence_verified': False,
            'source_and_output_permissions_cleared': False,
            'independent_apmesh_tri_or_quad_executed': False,
            'fair_apmesh_vs_paper_comparison_admitted': False,
        })
    roles = Counter(x['research_role'] for x in cases)
    return {
        'schema': 'apmesh-thingi10k-f20-model-admission-matrix-v1',
        'status': 'CORPUS_TRIAGE_ONLY_NO_NEW_SCIENTIFIC_ADMISSION',
        'source_case_count': len(cases),
        'quadwild_literature_cases': cohort_counts['QUADWILD_FIG29'],
        'badia_literature_cases': cohort_counts['BADIA_FIG10_TABLE1'],
        'independently_audited_raw_stl_cases': len(audited),
        'audited_closed_surface_sources': sum(x['source_genus_if_certified'] is not None for x in cases),
        'audited_adversarial_sources': sum(x['source_topology_screen'] ==
            'RAW_STL_ADVERSARIAL_TOPOLOGY_NOT_A_CAD_JUNCTION_PROOF' for x in cases),
        'quadwild_raw_audited_euler_matches': sum(x['published_output_euler_screen'] ==
            'NECESSARY_EULER_MATCH_RAW_SOURCE' for x in cases),
        'quadwild_catalog_only_euler_matches': sum(x['published_output_euler_screen'] ==
            'NECESSARY_EULER_MATCH_CATALOG_ONLY' for x in cases),
        'priority_roles': dict(sorted(roles.items())),
        'scientifically_admitted_reference_output_pairs': 0,
        'source_to_bezier_patch_conversions_admitted': 0,
        'apmesh_matched_case_meshes_admitted': 0,
        'cases': cases,
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--sources', type=Path, required=True)
    ap.add_argument('--literature', type=Path, required=True)
    ap.add_argument('--source-invariants', type=Path, required=True)
    ap.add_argument('--published-euler', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args(argv)
    report = audit(args.sources, args.literature, args.source_invariants, args.published_euler)
    with args.output.open('x', encoding='utf-8') as stream:
        json.dump(report, stream, indent=2, sort_keys=True)
        stream.write('\n')
    print(json.dumps({key: val for key, val in report.items() if key != 'cases'}, indent=2))
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (ValueError, OSError, KeyError, TypeError, json.JSONDecodeError) as error:
        raise SystemExit(f'F20 CORPUS TRIAGE BLOCKED: {error}') from error
