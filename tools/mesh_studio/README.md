# APMesh Mesh Studio — headless S0/S1 starter

This project is isolated under `tools/mesh_studio/`, with no generator production changes.

## Initial research-safe deliverables

- Synthetic immutable V1 fixture corpus and standalone oracle in `fixtures/`.
- Scientific typed `MeshDocument` with source vertices, typed TRI/QUAD faces, per-corner UV and explicit patch/source provenance.
- Bounded Wavefront OBJ importer with distinct legacy APMesh counting dialect and synthetic JSON sidecars.
- Headless vector-only SVG figure generation using actual source UV coordinates. An SVG with raster data or active content fails audit.
- Regression against 10 known-valid and 6 deliberate-invalid synthetic cases, parser mutations and figure deterministic reproduction.

```sh
python tools/mesh_studio/fixtures/generate.py
python tools/mesh_studio/fixtures/validate.py
python -m unittest tools.mesh_studio.test_studio -v
python -m tools.mesh_studio.cli \
  tools/mesh_studio/fixtures/cases/synthetic_quad_aft_transition.obj \
  --svg build/mesh-studio/synthetic_hybrid_uv.svg
```

All generated synthetic results must remain explicitly labeled **SYNTHETIC**, not reported as output from the actual APMesh generator. The original source `P1` model, real all-quad algorithm, anisotropic generator, vector PDF, GUI and scientific multi-epoch comparison are *not* claimed by this S0/S1 starter.

A generic OBJ lacking UV is parsed for geometry, but is not silently projected to fake UV coordinates. The importer does not infer source curve topology or model-global welding from coincident XYZ positions.

## S1b: reproducible synthetic technique storyboards

The three new storyboards are **synthetic instructional scenes**, not a capture
of generator execution, nor results measured in the paper. They are standalone
SVG path/polygon/ellipse vector drawings and require no Qt/VTK/GPU:

```bash
python -m unittest tools.mesh_studio.test_studio tools.mesh_studio.test_storyboards -v
python -m tools.mesh_studio.fixtures.validate
python -m tools.mesh_studio.storyboard_cli all --output-dir figures/mesh_studio
```

The command generates:

- `hybrid_synthetic.svg`: six illustrated stages of the existing 1-QUAD/8-TRI fixture, including a separate biquadratic *synthetic* lift in the last panel; the quadtree and front stages are **simulated** rather than recorded AFT operations.
- `all_quad_synthetic.svg`: actual 2x2 quad-grid boundary incidence (8 boundary edges) compared with a **fixed** five-edge disk where conforming all-quad is impossible under stated assumptions; necessary, not sufficient, existence criterion.
- `anisotropy_synthetic.svg`: exact unit ellipses for the prescribed synthetic metrics `I` and `diag(16,1)`; no APMesh anisotropic adapter is claimed.

Each `.svg` has an adjacent `.audit.json` with SHA-256, panel count, provenance
and the mathematical control data. SVG passes the existing raster/active-content
check, but **no PDF/PGF/LaTeX export has been qualified**. PNG files included
with the release example are previews, not the publication originals.

The metric example uses `Metric2D` defined in `metric2d.py`; original field
frame, units, tensor source and rotation must be supplied when real APMesh
measurements eventually become available. Local geometry is not a proof of
continuous physical Jacobian validity. All-quad and tensor-driven adaptation
remain scientific development goals, not released generator modes.
