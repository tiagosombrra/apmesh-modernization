# S3.B — Curved source feasibility and segmented bicubic cylinder control

**Research classification:** scientific feasibility only; source-original MAMBO/M5/S40/S27/M3 STEP runs NOT executed in this environment. No APMesh TRI or QUAD mesh was generated. No external non-manifold original was admitted.

## Bounded results

An author-constructed OCCT cylindrical face of radius 3 mm, height 4 mm, and 90-degree sector was interpolated by tensor-product bicubic polynomial Bézier controls using 4 x 4 native parameter samples. The independent surface check used de Casteljau at 9 x 9, 17 x 17, and 33 x 33 points for every segment, plus 49 native closest-face samples per segment. A second independent audit checked 35 x 35 source-parameter samples per patch and exact global integer control IDs on derived seams. Error values below are **maximum sampled point-to-point Euclidean distances**, not certified continuous Hausdorff bounds.

| Source-derived segments | Indexed BP controls | Explicitly shared derived seams | Maximum sampled error (mm) | Independent audit maximum (mm) | Prespecified absolute budget (mm) | Status |
|---:|---:|---:|---:|---:|---:|---|
| 1 | 16 | 0 | 0.0091380080 | 0.0090990560 | 0.01 | PASS in control scope |
| 2 | 28 | 1 | 0.0005830351 | 0.0005806302 | 0.001 | PASS in control scope |
| 4 | 52 | 3 | 0.00003662796 | 0.00003647813 | 0.0001 | PASS in control scope |
| 8 | 100 | 7 | 0.000002292198 | 0.000002282841 | 0.00001 | PASS in control scope |

A 1-patch control **FAILS** a predeclared 0.00001-mm absolute budget. Segment-level budgets are assessed without retuning. Derived seam control identity is explicit and cannot be inferred by proximity-based welding. The original quarter-cylinder boundary is a *local authored source*, not a MAMBO original, and the derived seam identities are not mislabeled as original STEP edge entities.

### Interpretation

Subdivision substantially reduces polynomial approximation error on this smooth, analytically parameterized case. It does NOT establish a continuous error bound, feature-curve compatibility across adjacent original CAD faces, a globally watertight BP atlas, or applicability to rational/trimmed S40 B-spline faces. Degree-3 collocation is not automatically an optimal minimax fit.

## Native source support/trim screen

`probes/s3b_curved_source_screen.py` independently records the original face type, native edge references (nondegenerate only), source per-face trimming wires, periodic axes, finite face UV bounds and rational B-spline weights/pole/degree/knots. It separates exact planar candidates, planar partition needs, rational splines, polynomial splines and analytic curved approximation needs. The M5 original has six documented degenerate TopoDS edges, so the report carries native all-edge and nondegenerate-edge counts separately; it is not a complete seam/topology proof.

For actual STEP inputs, **raw SHA-256 must match the frozen external source**, and assets must remain outside the Git repository. Run source face screen before selecting any fitting candidate. A source face with unsupported topology is rejected rather than silently healed.

## Reproduce

From the repository root, with CadQuery, OCP and NumPy installed:

```sh
python -m unittest discover -s docs/research/nonmanifold-benchmark/probes -p 'test_s3b_*.py' -v
python docs/research/nonmanifold-benchmark/probes/s3b_segmented_cylinder_atlas.py --segments 8 --absolute-budget-mm 0.00001 --relative-budget 0.01 --out-bp build/research-s3b/cylinder_8_segments.bp
```

The second command produces an indexed `.bp` and a JSON sidecar with an independent audit result. Original model screening (if original bytes were acquired separately):

```sh
python docs/research/nonmanifold-benchmark/probes/s3b_curved_source_screen.py --model S40 --sources /external/mambo/sources --output build/research-s3b/s40_curved_screen.json
python docs/research/nonmanifold-benchmark/probes/s3b_curved_source_screen.py --model M5 --sources /external/mambo/sources --output build/research-s3b/m5_curved_screen.json
```

For a *specific original* source cylindrical face, after source identity and trim inspection:

```sh
python docs/research/nonmanifold-benchmark/probes/s3b_cylindrical_bicubic_pilot.py --source-step /external/mambo/sources/i05o_m5.step --source-sha256 895f67c0669096b287077ac1bb56dad0e117cd96f78334d3129d783fd78b96cb --face-index FACE_ID --absolute-budget-mm 0.01 --relative-budget 0.01 --output build/research-s3b/m5_cylinder_face.bp
```

`FACE_ID` must be selected from the native screening report, not guessed. Original CAD per-face fitting has **NOT RUN**. A result outside budget is recorded as failure and cannot become admitted merely because a wider tolerance can be selected after the fact.

## Current gate and next work

- **Local test evidence:** S3.A directed 11/11; S3.B native screen/cylinder directed 11/11; derived segmented atlas directed 8/8 = 30/30 local controls, without the whole production suite.
- **Original CAD S3.B:** NOT RUN (original source files not available in this runtime); independent four-original acceptance and full curved decomposition remain open.
- **Scientific priority:** exact source model import and face-trim map on M5/S40; feature-curve-first decomposition; external original 3+-sheet B-Rep search remains a distinct blocker.
- **Integration:** draft research PR only; no merge until qualified exact-head checks and scientific review.
