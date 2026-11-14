# Mesh Studio synthetic fixture corpus (research-safe)

This folder contains **only synthetic model examples**, not measured original APMesh research results. Every JSON case has `synthetic: true`, its own visible warning, a SHA-256 of the paired OBJ, expected element counts and expected acceptance/diagnostic. The examples include manifold TRI/QUAD, an interior QUAD/exterior TRI transition, an analytically warped polynomial Bezier-representable patch, patch-local fans of 2, 3, 4 and 28 incident sheets, and deliberate negative cases. The 8 experiment rows are invented solely to test accepted/rejected and non-monotone plotting logic.

Run from the repository root (Python standard library only):

```sh
python tools/mesh_studio/fixtures/generate.py
python tools/mesh_studio/fixtures/validate.py
```

Expected audit: `fixture_audit=PASS valid=10 negative=6 total=16 experiment_rows=8 synthetic_only=true`. The current validator is an **initial independent fixture-contract test**, not an end-to-end qualification of a future production OBJ importer, Qt render path or export backend. Do not quietly update reference counts or diagnostics to make failing tests pass.

Manifest SHA-256 after deterministic generation: `dccd142254b17401f2f0c5c5f31b67483fb82f8e2f83e2e68ef1ab248a638ccc`.

The `fan4` and `fan28` cases deliberately represent separate patch-local physical vertex sets around a shared *logical* source curve. They are NOT geometric proofs of advisor-approved sheet pairings or interpatch physical welding. The `synthetic_concave_uv` fixture uses a physically convex square with intentionally concave UV coordinates to isolate the P0 admission error. Do not substitute synthetic source derivatives for real PatchBezier control-net evaluations.
