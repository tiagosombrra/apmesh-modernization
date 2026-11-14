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
