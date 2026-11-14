"""Reproducibly qualify and render the actual PR217 controlled P1 mesh."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from .import_obj import import_obj
from .p1_source_oracle import qualify_p1, bezier, _cross
from .quality_analysis import analyze_mesh
from .svg_figure import audit_svg, render_uv_svg


def _json(value: dict) -> str:
    return json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def execute(obj: Path, report: Path, output_directory: Path) -> dict:
    """Create a deterministic real-source audit; never overwrite a prior result."""
    if output_directory.exists():
        raise FileExistsError("output_directory_already_exists")
    document = import_obj(obj, auto_sidecar=False)
    generator_report = json.loads(report.read_text(encoding="utf-8"))
    provenance = qualify_p1(document, generator_report)
    # The exact original Bezier control-net source is audited independently.
    quality = analyze_mesh(document, source_normal=lambda u,v:
                           _cross(bezier(u,v)[1], bezier(u,v)[2]))
    tri = quality["measures"]["triangle_mean_ratio_3d_v1"]
    planar = quality["measures"]["planar_quad_min_scaled_jacobian_3d_v1"]
    if tri is None or tri["count"] != 36 or planar is not None:
        raise ValueError("real_p1_metric_scope_changed")
    if any(cell["physical_orientation"] != "POSITIVE_AT_FACET_SAMPLES_ONLY"
           for cell in quality["cells"]):
        raise ValueError("real_p1_physical_orientation_changed")
    if sum(cell["quad_relative_planarity"] is not None and
           cell["planar_quad_min_scaled_jacobian"] is None
           for cell in quality["cells"] if cell["element_type"] == "quad") != 42:
        raise ValueError("real_p1_quad_planarity_changed")

    output_directory.mkdir(parents=True,exist_ok=False)
    svg = output_directory / "P1_real_hybrid_uv.svg"
    figure = render_uv_svg(document,svg,width_mm=155,height_mm=120)
    vector = audit_svg(svg, expected_faces=78)
    figure["vector_audit"] = vector
    figure["source_evidence_kind"] = provenance["evidence_kind"]
    figure["scientific_limit"] = "Single fixed-sampling curved source patch; no adaptive epochs"
    summary = {
        "schema":"apmesh.meshstudio.p1_real_integration.v1",
        "evidence_kind":"REAL_SOURCE_CI_ARTIFACT_NOT_SYNTHETIC",
        "source_provenance":provenance,
        "real_mesh_quality":{
            "triangle_mean_ratio_3d_v1":tri,
            "planar_quad_min_scaled_jacobian_3d_v1":None,
            "planar_quad_count_evaluated":0,
            "original_nonplanar_quads":42,
            "physical_orientation":"POSITIVE_AT_SAMPLED_FACETS_ONLY",
            "source_global_jacobian_certified":False,
        },
        "figure":figure,
        "generator_report_sha256":_sha(report),
        "warnings":[
            "OBJ groups QUAD/TRI_AFT classify cells, not distinct source patches",
            "Original all-quad and anisotropic generator output not present",
            "No accepted mixed adaptation epochs; single bounded source P1 run",
            "Metric scores from Studio are not source-emitted measured values",
            "True-vector UV figure does not prove 3D mesh continuous validity",
        ],
    }
    (output_directory/"P1_real_hybrid_audit.json").write_text(_json(summary),encoding="utf-8")
    # Return an independently inspectable manifest without nondeterministic paths.
    manifest={"schema":"apmesh.meshstudio.p1_figure_manifest.v1",
              "source_obj_sha256":document.source_sha256,
              "svg_sha256":_sha(svg),
              "audit_json_sha256":_sha(output_directory/"P1_real_hybrid_audit.json"),
              "synthetic":False,"published_as_adaptive_epoch":False}
    (output_directory/"P1_real_manifest.json").write_text(_json(manifest),encoding="utf-8")
    return manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify and render the original controlled P1 source mesh")
    root = Path(__file__).parent / "fixtures" / "real_p1"
    parser.add_argument("--obj",type=Path,default=root/"accepted.obj")
    parser.add_argument("--report",type=Path,default=root/"generator_report.json")
    parser.add_argument("--output-dir",required=True,type=Path)
    args = parser.parse_args(argv)
    print(json.dumps(execute(args.obj,args.report,args.output_dir),sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
