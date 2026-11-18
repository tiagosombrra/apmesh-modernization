# Per-stage geometry error and element quality

Date: 2026-11-18. Engineering-only reporting addition to draft [PR240](https://github.com/tiagosombrra/apmesh-modernization/pull/240),
exact source `9ca6deb35878f2b491ac27c908534936cfc55ca8`.
Native algorithm/configuration inputs are unchanged from `b3d2fbc`.
See the [compact evidence](evidence/GENERATION_RESULT_METRICS_20261118.json).

The user requests visible error and element quality at every generation step.
`tools/quad_generation_metrics.py` now measures each original TRI and QUAD/TRI
OBJ/UV output at steps0-3 and writes `results.md`, `metrics.csv`, `elements.csv`
and `metrics.json`. The article-application checker invokes reporting on new
histories; the Blender viewer writes or verifies the report before display.
Actual face IDs and source hashes bind every per-element value to its output.

## Meaning and limits

Geometry RMS uses576 common UV sample sites, the independent original Bernstein
surface, source-Jacobian area weights, linear TRI and inverse-bilinear QUAD
interpolation. RMS and maximum distance use model coordinate units. These are
sampled geometry diagnostics, not continuous bounds or solution-error estimates.

TRI area-Q is `4*sqrt(3)*area/sum(edge_length_squared)` in physical XYZ; an
equilateral triangle has1. QUAD quality is the minimum signed corner scaled
Jacobian using analytic source normals. Orthogonal aligned corners have1, but
an elongated rectangle can also have1. Display minimum angles and maximum edge
ratios alongside it. Keep both scales separate; do not average TRI Q with QUAD J.
Absent QUAD is N/A, not zero. Native TRI logged quality is a different original
metric and remains separately identified in JSON and above TRI Blender panels.

The original adaptive curvature error remains explicitly a TRI reference,
joined by exact step/retry/count identity. The mixed adaptive estimator remains
unimplemented and is null/N/A, including step0. This report does not alter any
acceptance, smoothing, source nodes, element selection or stopping policy.
The reporting source currently supports only `builtin:curva_bezier`.

## Measured results

| Step | Scheme | Nodes | TRI | QUAD | Geometry RMS | Geometry max | TRI reference curvature error |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | TRI | 5 | 4 | 0 | 0.07671967 | 0.3398609 | 0.314848 |
| 0 | QUAD_TRI | 5 | 4 | 0 | 0.07671967 | 0.3398609 | 0.314848 |
| 1 | TRI | 17 | 24 | 0 | 0.02648736 | 0.08992172 | 0.139436 |
| 1 | QUAD_TRI | 33 | 8 | 24 | 0.02366862 | 0.09094211 | 0.139436 |
| 2 | TRI | 78 | 144 | 0 | 0.014652 | 0.04337308 | 0.0538754 |
| 2 | QUAD_TRI | 281 | 52 | 249 | 0.0117036 | 0.04014871 | 0.0538754 |
| 3 | TRI | 223 | 430 | 0 | 0.009310312 | 0.03963429 | 0.0303172 |
| 3 | QUAD_TRI | 797 | 102 | 738 | 0.007262102 | 0.03224427 | 0.0303172 |

TRI area-Q and QUAD corner J are separate diagnostic scales; both have ideal reference1.
Corner J does not measure aspect ratio or continuous bilinear validity; inspect the edge ratio too.

| Step | Scheme | TRI Q min | TRI Q mean | QUAD J min | QUAD J mean | Minimum angle (deg) | Maximum edge ratio |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | TRI | 0.845991 | 0.8663829 | N/A | N/A | 43.70282 | 1.445866 |
| 0 | QUAD_TRI | 0.845991 | 0.8663829 | N/A | N/A | 43.70282 | 1.445866 |
| 1 | TRI | 0.7148837 | 0.8778737 | N/A | N/A | 29.75731 | 1.992988 |
| 1 | QUAD_TRI | 0.719132 | 0.7789288 | 0.5119564 | 0.8774299 | 28.55142 | 4.595718 |
| 2 | TRI | 0.2908076 | 0.8161307 | N/A | N/A | 9.976283 | 4.923397 |
| 2 | QUAD_TRI | 0.135358 | 0.4910054 | 0.3944663 | 0.8997611 | 4.824379 | 9.239147 |
| 3 | TRI | 0.04652305 | 0.8044304 | N/A | N/A | 1.70921 | 5.3054 |
| 3 | QUAD_TRI | 0.03981139 | 0.3875739 | 0.328431 | 0.9831509 | 1.336672 | 8.703204 |

Per-element values and source face IDs are in elements.csv; full definitions, native logged TRI quality, source hashes and stage identity are in metrics.json.
These observations do not change acceptance, smoothing, node placement or the generator.

The decreasing geometric RMS coexists with worsening worst elements: final
global minimum angles are1.71deg TRI and1.34deg mixed. Those global values are
not the earlier straight-boundary-only8.11deg audit. Higher density and different
source smoothing preclude an equal-cost or causal QUAD-benefit claim.

## Reproduction and Blender

```powershell
python tools/quad_generation_metrics.py --archive <prefix.steps> --output <new-directory>
python -W error::ResourceWarning tests/quad/test_generation_metrics.py
python tools/validation_session.py run --scope delivery
```

Local results: `build/quad-article-front-20261118/results-with-metrics/`.
`QUAD_TRI_errors_and_quality.blend` contains the analytic model, all eight actual
meshes with numeric labels, eighteen native TRI/QUAD/source-polygon panels below,
and the prior actual-commit animation. A second comparison scene colors actual
faces by their respective quality metric: red low, green near1. Identical vertex
coordinates and face indices are checked across comparison scenes. Blender5.3
GUI and the complete rendered comparison were inspected; prior blend untouched.

Five analytic/scope controls cover ideal TRI/QUAD, elongated rectangle, reversed
and collapsed faces, missing mixed metrics, initial native-row mapping, foreign
archive paths and native-count mismatch. All pass with ResourceWarning as error.
Exact-head local baseline85/85 passes; its report still says delivery_eligible=false.
Python compilation, five-file whitespace and diff checks pass. Existing-archive
replay verifies191 commits and eight forged traces; this read-only local replay
does not reexecute rollback. All six adapted geometry rows reproduce the earlier
comparison within relative1e-12/absolute1e-14 and all eight counts agree.

Exact hosted [run44296219310](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/44296219310)
passes all four checks, including frozen TRI science. GNU, MSVC and sanitizer
fresh article histories each verify191 commits, eight forgeries and rollback.
The new five reporting controls execute on both hosted operating systems.
No local native rebuild or regeneration was needed for unchanged native inputs.

Retain bounded development failures in the evidence: CSV ResourceWarning fixed
with scoped file lifetimes; outer scene-wrapper logging NameError after successful
artifact creation; initial cropped preview repaired only in the new artifact.
No hidden native rerun. Prior WSL publication failures remain unresolved.

## Closure and next action

Code/report identity, analytical tests, original acceptance contracts, diagnostic
definitions, actual render and remote checks are audited for this addition.
No source algorithm or scientific technique changes. Reporting does not repair
the [article-conformance gaps](ARTICLE_CONFORMANCE_REVALIDATION_20261118.md).
Keep PR240 draft: next restore documented contour-clearance classification with
its failing witness, then actual mixed smoothing/effective controls and explicit
M1 centroid disposition. Independent review, local failure disposition, historical
oracles, full CRT and exact research-integration/post-merge gates remain open.
The roadmap sequencing and modernization history are unchanged.
