# Mesh Studio S5c — source-bound experiment ingestion and fail-closed provenance

**Date:** 2026-11-14. **Scope:** implementation-only changes under
`tools/mesh_studio/` and `docs/mesh-studio/` on
`feature/mesh-studio-fixture-first-20261114`. Historical source model and
production generator code remain read-only. This does not constitute a new
adaptive meshing algorithm or complete journal cross-technique experiment.

## Scientific contract

The new `apmesh.meshstudio.experiment_run.v1` manifest records:

- a unique run identity and typed topology/sizing policy;
- exact Git revisions, CI workflow run and artifact IDs, target platform;
- source model identity, with an **explicitly null** original model SHA when
  the model is built into source and no standalone source file exists;
- relative, bounded, SHA-256 authenticated source OBJ and generator report;
- metrics with immutable equation identity SHA, units, XYZ/UV reference frame,
  sampling rule and producer classification;
- ordered event identities, each bound to a geometry SHA, with separately
  represented rejected and staged candidates;
- an explicit evidence category: source generated, provisional or synthetic.

`tools/mesh_studio/schemas/experiment_run_v1.schema.json` is a structural
Draft 2020-12 JSON Schema. The executable `experiment_ingest.py` imposes the
stronger scientific checks and uses the **independent, exact-source P1 oracle**.
A JSON file's self-asserted claims are never sufficient to confer acceptance.

## Real measured geometry, without fabricated adaptation

The sole example manifest is
`tools/mesh_studio/fixtures/experiments/real_p1_pr217.json`, referencing the
already-committed and separately verified PR217 Linux CI artifact:

- source commit `d39bbc447f88e179c3c4ee674bd9309f59c18eed`;
- candidate `0999769722f128d887e1143c8ec1da67da627850`;
- Actions run `43588588497`; Linux artifact `14111372234`;
- OBJ SHA `cbf6cd6308ba54544d06c5d562c491eb7d43ddb216365e0e9d188fd3430295e0`;
- original generator report SHA
  `1ec6d5e698b6502f117b01d9fce9f2ce9e26048b82b97484da219b747ad908d2`;
- 69 owned nodes, 42 QUAD, 36 AFT TRI, 16 outer edges, 20 internal
  cross-type edges and 120 oriented physical subfacets.

The independent viewer computes and checks these three metric claims:

| Versioned metric ID | Value from original P1 | Units/frame/sampling |
| --- | ---: | --- |
| `p1_min_sampled_facet_normal_alignment_v1` | 0.9859299598139977 | dimensionless, XYZ, 120 facet centroids |
| `p1_max_source_xyz_component_error_v1` | 1.0408340855860843e-16 | original XYZ units unspecified, 69 mesh vertices |
| `triangle_mean_ratio_3d_v1` | 0.7681840384225347 | dimensionless, XYZ, 36 source AFT triangles |

These are **Studio-computed, independent geometric observations**, not
source-reported adaptation success, a continuous surface Jacobian certificate,
shared-source welding evidence or directly comparable TRI/QUAD score values.
The exact P1 run has one `CONTROLLED_NONADAPTIVE_OUTPUT`, zero accepted
adaptive epochs, no genuine source timing/hardware measurement and no
independent model input file SHA. It cannot enter a 3-by-2 factorial study.

## Hard failures, rather than permissive imports

Reject unknown schema fields/versions, duplicate JSON properties, NaN/Inf,
oversized input, unknown origins, unbounded files, absolute/relative
traversal paths, symlinks outside the root, altered OBJ/report hashes,
corrupted original receipt, forged CI revisions and artifact IDs, missing
mesh identity in an event, nonconsecutive event IDs, unsupported accepted
adaptive epoch, unqualified anisotropic claim, wrong TRI/QUAD inventory,
changed sampling/metric definition/frame/units, source value forgery and
incorrectly relabeled synthetic/real origin. The negative suite asserts
that invalid CLI input does not leave an output package.

Any real source without an available independent named oracle is emitted only
as `SOURCE_PROVISIONAL_NOT_SCIENTIFICALLY_QUALIFIED`; its reported values
are not upgraded to paper-ready scientific results. Matching model hashes
and common numerical definitions are **not sufficient** for paper-level
comparability without common source sites, measurement protocol, physical
units, acceptance rules and performance hardware when relevant. The future
comparison engine must review those constraints on genuine source traces.

## Reproduction

From the repository root:

```bash
python -m tools.mesh_studio.experiment_cli \
  tools/mesh_studio/fixtures/experiments/real_p1_pr217.json \
  --output-dir build/mesh-studio/s5c_real_p1

python -m unittest discover -s tools/mesh_studio -t . -p 'test_*.py' -v
python tools/mesh_studio/fixtures/validate.py
```

Outputs are deterministic, no-overwrite JSON:
`qualified_run.json` and `scientific_matrix.json`. The latter keeps all six
TRI / QUAD+TRI / all-QUAD by isotropic / anisotropic cells `NOT_AVAILABLE`,
and documents P1 as excluded. This is the correct state of the *available
certified source evidence*; it does not deny newer source research development
outside this frozen P1 artifact.

## S4b qualification remains pending

PySide6, PyVista and PyVistaQt are **not installed** in this environment.
Running the current Qt smoke explicitly exits with code 2 and no PASS receipt.
The Python/VTK headless tests are not a substitute for real widget startup,
Qt/VTK ABI, physical mouse picking, camera restore or Windows/Linux
open/close endurance. No hosted Studio CI or Qt GUI smoke is claimed.

## Review responsibilities and next branch work

- **Geometry scientist:** check original control net, UV/XYZ relation,
  nonplanar QUAD limitations, curve and patch incidence.
- **Numerical researcher:** confirm error metric equation hashes, common
  sampling/units, accepted versus staged/rejected timing and field origin.
- **Architect:** maintain independent CLI/domain path; Qt/VTK imports must
  remain optional.
- **Security/QA:** preserve bounded paths, SHA checks, anti-forgery controls,
  no code execution from external models, negative-case regression.
- **Publication reviewer:** keep data with real source IDs and explicit
  `NOT_AVAILABLE`; never imply P1 all-QUAD or anisotropic method data.

**Next:** S5d real multi-run source experiment ingest from future agreed,
source-instrumented adaptive traces; require independent same-source-site
oracles and metric protocols before numerical cross-method plots. Separately,
S4b remains dependent on a real Qt-enabled Windows/Linux smoke.
