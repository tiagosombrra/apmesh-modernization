#!/usr/bin/env python3
"""Execute a fail-closed, source-pinned original-CAD partial atlas research batch.

Do not treat a partial indexed BP, a rendered CAD figure, or a native sample
as a complete model or an accepted APMesh surface-mesh generation.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path

import cadquery as cq

from audit_original_cad_planar_atlas import audit as independent_audit
from original_cad_planar_atlas import SOURCES as NATIVE_SOURCES, build_atlas
from s3b_curved_source_screen import screen as native_screen
from s3c_step_source_gate import SOURCES as STEP_SOURCES, analyze


def run_one(model, source_path, output_dir, *, expected_digest, expected_faces=None,
            expected_candidates=None, provenance="PINNED_ORIGINAL"):
    """Require source bytes and three separate agreeing geometry/topology oracles."""
    raw = source_path.read_bytes()
    digest = sha256(raw).hexdigest()
    if digest != expected_digest:
        raise ValueError("Source file SHA-256 mismatch: cannot inherit pinned provenance")
    graph = analyze(raw.decode("utf8"), model=model, source_sha256=digest)
    if expected_faces is not None and graph["original_advanced_faces"] != expected_faces:
        raise ValueError("Original STEP face inventory differs from frozen reference")
    if expected_candidates is not None and graph["candidate_faces"] != expected_candidates:
        raise ValueError("Original STEP candidate inventory differs from frozen reference")
    original = cq.importers.importStep(str(source_path)).val()
    native = native_screen(original, model_id=model, raw_sha256=digest)
    if not native["source_valid_brep"]:
        raise ValueError("Imported source BRep is invalid")
    native_candidate = native["face_classification_histogram"].get("EXACT_PLANAR_QUAD_CANDIDATE", 0)
    if graph["original_advanced_faces"] != native["source_face_count"]:
        raise ValueError("Original source STEP/native BRep face counts disagree")
    if graph["candidate_faces"] != native_candidate:
        raise ValueError("Original source STEP/native BRep eligible counts disagree")
    out_dir = output_dir / model.lower()
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "source_graph.json").write_text(json.dumps(graph, indent=2, sort_keys=True) + "\n")
    (out_dir / "native_face_screen.json").write_text(json.dumps(native, indent=2, sort_keys=True) + "\n")
    status="NO_ELIGIBLE_PLANAR_FACES"
    independent = None
    native_manifest = None
    if native_candidate:
        bp, native_manifest = build_atlas(original, model, digest)
        if native_manifest["converted_face_count"] != native_candidate:
            raise ValueError("Converted planar count differs from independent eligibility screens")
        independent = independent_audit(original, bp, native_manifest, source_sha256=digest)
        if independent["validated_patches"] != native_candidate:
            raise ValueError("Independent BP audit did not cover all accepted planar candidates")
        (out_dir / "planar.partial.bp").write_text(bp, encoding="utf8")
        (out_dir / "planar.partial.json").write_text(json.dumps(native_manifest, indent=2, sort_keys=True)+"\n")
        (out_dir / "independent_audit.json").write_text(json.dumps(independent, indent=2, sort_keys=True)+"\n")
        status="PARTIAL_PLANAR_ATLAS_AUDITED"
    report={
        "schema":"apmesh-s3c-original-source-batch-v1",
        "model":model,"provenance":provenance,"source_raw_sha256":digest,
        "status":status,
        "step_face_count":graph["original_advanced_faces"],
        "native_face_count":native["source_face_count"],
        "step_candidate_faces":graph["candidate_faces"],
        "native_candidate_faces":native_candidate,
        "candidate_edge_neighbors":graph["candidate_edge_neighbors"],
        "converted_faces":0 if native_manifest is None else native_manifest["converted_face_count"],
        "excluded_faces":native["source_face_count"] if native_manifest is None else native_manifest["excluded_face_count"],
        "native_to_source_face_id_bijection":"NOT_ESTABLISHED",
        "original_shared_feature_curve_fitting":"NOT_RUN",
        "original_curved_surfaces_converted":"NOT_RUN",
        "complete_original_model_converted":False,
        "apmesh_tri_quad_generation":"NOT_RUN",
        "independent_audit":independent,
    }
    (out_dir/"s3c_result.json").write_text(json.dumps(report, indent=2, sort_keys=True)+"\n")
    return report


def run_batch(models, sources, output):
    if any(model not in STEP_SOURCES for model in models):
        raise ValueError("Unknown original source model")
    all_cases = {}
    success = True
    for model in models:
        filename, digest, faces, candidates = STEP_SOURCES[model]
        if NATIVE_SOURCES[model] != (filename, digest):
            raise ValueError("Source pin discrepancy between native and original STEP audit")
        p = sources / filename
        if not p.exists():
            all_cases[model] = {"status":"BLOCKED_MISSING_ORIGINAL_BYTES", "expected_file":filename}
            success = False
            continue
        try:
            report = run_one(model, p, output, expected_digest=digest,
                             expected_faces=faces, expected_candidates=candidates)
            all_cases[model] = {"status":report["status"],
                                "candidate_faces":report["step_candidate_faces"],
                                "converted_faces":report["converted_faces"],
                                "excluded_faces":report["excluded_faces"]}
        except Exception as error:
            all_cases[model] = {"status":"BLOCKED_FAILED_ORIGINAL_VALIDATION",
                                "failure_type":type(error).__name__,"failure":str(error)}
            success = False
    output.mkdir(parents=True,exist_ok=True)
    result={"schema":"apmesh-s3c-original-batch-receipt-v1",
            "source_model_directory":str(sources),
            "complete_original_models_converted":0,
            "apmesh_tri_quad_generation":"NOT_RUN",
            "all_requested_source_checks_completed":success,
            "models":all_cases}
    (output/"s3c_batch_summary.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sources",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--models",nargs="+",choices=STEP_SOURCES,default=list(STEP_SOURCES))
    args=parser.parse_args()
    result=run_batch(args.models,args.sources,args.output)
    print(json.dumps(result,indent=2,sort_keys=True))
    if not result["all_requested_source_checks_completed"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
