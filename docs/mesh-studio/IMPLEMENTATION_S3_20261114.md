# S3: verified integration with real source APMesh P1 output

**Scope:** Research-only Mesh Studio branch `feature/mesh-studio-fixture-first-20261114`. No production generator files have changed.

## Actual original source, not a made-up mesh

Original *source* PR [#217](https://github.com/tiagosombrra/apmesh-modernization/pull/217) merged at `d39bbc447f88e179c3c4ee674bd9309f59c18eed`. CI [43588588497](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43588588497) completed four successful jobs. The Linux artifact `14111372234` and Windows artifact `14111247733` were both downloaded from GitHub Actions and compared directly. The two `accepted.obj` files are **byte identical** with SHA-256 `cbf6cd6308ba54544d06c5d562c491eb7d43ddb216365e0e9d188fd3430295e0`.

The *unmodified* Linux `accepted.obj`, its original `report.json` (renamed to `generator_report.json` for clarity) and original corrupt controls are committed under `tools/mesh_studio/fixtures/real_p1/`. The original negative controls are an invalid vertex arity and invalid face arity, respectively. The associated source provenance is immutable and must remain distinguishable from the synthetic corpus.

## Integration and independent oracle

`p1_source_oracle.py` pins the known original `Models3d::ModelCurvaBezier` 4×4 Bernstein control net independently of the source object's OBJ positions and source report. It checks vertex-by-vertex UV → XYZ mapping, positive orientation of both QUAD facets, finite positive sampled source differential normals, original QUAD/TRI class labels, canonical indexed topology and the opposite-oriented seam. It **does not** inspect, alter or execute the active C++ QUAD algorithm.

| Observable | Expected original output | S3 result |
| --- | ---: | ---: |
| Physical nodes | 69 | 69 |
| QUAD interior | 42 | 42 |
| Native AFT TRI exterior | 36 | 36 |
| Quad/Tri shared seam edges | 20 | 20 |
| Outer source-boundary edges | 16 | 16 |
| Physically oriented facet triangles | 120 | 120 |
| Indexed complex components / Euler characteristic | 1 / 1 | 1 / 1 |
| TRI annular region boundary loops | 2 | 2 |

A separate S2 cell-quality pass computes an **explicitly Studio-defined TRI mean ratio** for 36 TRI elements, and does not pretend the curved QUADs have a planar scaled-Jacobian score. Original source normal alignment is qualified **at facet samples only**; whole-surface Jacobian, self-intersections, source-global patch welding, or multiple accepted adaptive epochs remain unqualified.

`real_p1_cli.py` creates reproducible `P1_real_hybrid_uv.svg`, `P1_real_hybrid_audit.json` and `P1_real_manifest.json`. The SVG contains the complete original 78 faces as vector polygons; no external SVG image, scripts or remote resources. It is a **source-derived vector UV view**, not a general three-dimensional occlusion-correct figure. It uses the same SVG renderer as the original S1 and is independently audited with `audit_svg`.

## Regression and source boundary

- Full original S0/S1/S1b/S2 and new S3 Python suite: **53 test methods passed**, including **12** new real P1 integration methods and the two original corrupt source artifacts. Negative mutation tests include wrong report/epochs/native AFT, wrong source SHA, modified source geometry, a class-mislabeled face and inverted seam orientation.
- V1 synthetic fixture corpus is untouched: **10 expected-valid, 6 expected-invalid, 8 fake epoch rows**.
- The generated SVG and JSON are deterministic and rerun byte-identically for the same source bytes.
- No new CI run for this exact Mesh Studio commit is claimed; tests were executed locally and re-run from an independently extracted source package. CI must be separately configured and qualified for this research branch.
- No C++ original full generator CTest was re-executed in the S3 integration. Its original passing CI is **source-generator evidence**, not a substitute for Studio regression.

## Future roadmap

S4: optional PyVista/Qt GUI viewer with synchronized UV/XYZ and typed cell picking; remain headless-first. S5: comparator/LaTeX paper figures. S6: reviewed opt-in real generator event recording in a separate source algorithm PR. These remain open; no all-QUAD or tensor-anisotropic generator implementation is inferred from this S3 output.
