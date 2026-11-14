# Mesh Studio S0/S1 — first executable delivery

**Status:** initial isolated, headless source implementation; source-generator production untouched.

## Executed local regression (2026-11-14)

- Re-generated the original V1 corpus using `python tools/mesh_studio/fixtures/generate.py`.
- Audited the corpus using `python tools/mesh_studio/fixtures/validate.py`: 10 valid fixtures, 6 deliberate failures, 8 synthetic experiment rows.
- Verified unchanged deterministic fixture manifest SHA-256 `dccd142254b17401f2f0c5c5f31b67483fb82f8e2f83e2e68ef1ab248a638ccc`.
- Ran `python -m unittest tools.mesh_studio.test_studio -v`: 7 test methods covering all 16 fixture cases, standard separate `v/vt` OBJ indices including relative indexes, strict legacy headers/counts, malicious face and nonfinite mutants, and SVG deterministic/pure-vector audits.
- Executed `python -m tools.mesh_studio.cli tools/mesh_studio/fixtures/cases/synthetic_quad_aft_transition.obj --svg <output>` and audited 1 QUAD/8 TRI/8 vertices and nine vector polygons; the resulting figure has visible SYNTHETIC provenance.
- Previewed the actual SVG visually with CairoSVG to inspect layout; PNG preview is a derived inspection artifact, not the SVG export format.

## Scope distinctions

S0 corpus and S1 import/UV vector render are functional for synthetic fixtures. Generic OBJ without `vt` is accepted as geometry but cannot masquerade as source UV; a missing sidecar does not fabricate curve IDs or patch-local physical identity. The legacy adapter checks exact original APMesh count rows and fails when global face IDs do not match a local vertex table; no implicit reindexing is performed. Other formats (VTU/MSH), curved-source metrics, actual generator P1 runtime import, Technique Storyboard, true-vector PDF/PGF, PySide6 GUI, all-quad and tensor anisotropy remain unimplemented.

A passing S0/S1 fixture audit is not independent certification of the underlying APMesh generators or of real model acceptance. Keep the existing research baseline `main` and `quad-templates` unchanged; the next gate is real P1 OBJ import plus camera-locked six-panel simulated Technique Storyboard, with separate scientific source provenance.

## Reproduce

```sh
python tools/mesh_studio/fixtures/generate.py
python tools/mesh_studio/fixtures/validate.py
python -m unittest tools.mesh_studio.test_studio -v
python -m tools.mesh_studio.cli \
  tools/mesh_studio/fixtures/cases/synthetic_quad_aft_transition.obj \
  --svg build/mesh-studio/synthetic_hybrid_uv.svg
```
