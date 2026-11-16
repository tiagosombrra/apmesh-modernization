# S3.H — Original M5 source-constrained cylindrical Bézier pilot

**Date:** 2026-11-16. **Classification:** isolated scientific investigation. No modification to the C++ production generator, Stage 3, QUAD branch, original comparators, or published benchmark claims.

## Research question and measured distinction

Can the two original MAMBO M5 cylindrical faces directly adjoining selected planar source faces be represented by **candidate** polynomial bicubic Bézier patches while retaining the same original generator `EDGE_CURVE`/`VERTEX_POINT` canonical identities and exact integer control-index equality across author-derived seams?

The answer is **yes in the bounded original STEP source-geometry/sampled-error scope**, for four or more sectors at a **pilot** absolute sampled-distance budget of 0.001 mm. The answer remains **unverified for the native imported trim, source-to-OCCT BRep correlation, full BP atlas, APMesh TRI/QUAD generation or continuous geometric-distance certification**.

The author-generated synthetic control was executed locally in CadQuery 2.8.0 / Open CASCADE. The original M5 source was independently inspected from pinned GitHub upstream text by a separate reference implementation; original M5 bytes were **not** imported into the local Open CASCADE runtime. The source geometry is not added to Git or redistributed.

## Fixed original references and explicit trim-arc reconstruction

- Upstream: `cgg-bern/hex-me-if-you-can`, revision `8f00f02579037cc893042f2ee2c910b20e3fb1b0`.
- Original: `original/i05o_m5.step`, upstream Git blob `d72e5e3cb3de9ebdec80253cfa9b57fa1b7132f7`.
- Raw source SHA-256 expected for a **later local execution**: `895f67c0669096b287077ac1bb56dad0e117cd96f78334d3129d783fd78b96cb`. In the connector-side reference calculation, this *raw byte* SHA was not recomputed; provenance is frozen upstream Git blob SHA-1 + revision. Local script must fail closed unless raw SHA-256 matches.
- M5 `ADVANCED_FACE #3493`, `CYLINDRICAL_SURFACE #423`, original generator `EDGE_CURVE #3497/#3473`, original circular boundaries `#406/#3522`. The two circle arcs have opposite face-loop orientation, with physical cylinder-axis sweep magnitude **2.102093169774461 rad**. Reference U start is approximately **5.243685823365 rad** and the selected signed sweep is negative.
- M5 `ADVANCED_FACE #3976`, `CYLINDRICAL_SURFACE #282`, original generators `#3954/#3982`, original circles `#261/#4005`. Magnitude **2.102093169774461 rad**; the selected source signed sweep is positive. Reference U start is approximately **3.141592653590 rad**.
- Both faces have radius **2 mm**, common generator span **15 mm**, exactly one source wire of two original `LINE` generators and two `CIRCLE` arcs.

**Critical disambiguation:** `ORIENTED_EDGE` direction, `EDGE_CURVE` `same_sense`, original `CIRCLE` axis frame, and 3D endpoint identities together reconstruct the directed circular sweep. The generator `PCURVE` constant-U coordinates independently check that sweep. The algorithm never chooses the smaller of the two possible arcs by default. A directed major arc (4 rad) is retained and tested separately on synthetic STEP.

## Source-original independent numerical results

A separate JS reference probe read the original STEP entities via the GitHub connector and evaluated a **cubic Hermite angular approximation** on 65 x 65 samples **per patch**, compared with the exact analytic cylinder equation. The angle and axial endpoints come from the original source only. Tangents at the angular ends use `radius * delta_angle / 3`. The predeclared **experimental sampled-error budget** was 0.001 mm; this is not an advisor-approved final scientific acceptance tolerance.

| Source M5 face | Segments/patches | Maximum sampled distance (mm) | Sample count | Pilot budget |
|---|---:|---:|---:|---|
| `#3493` | 2 | 0.006239877153 | 8,450 | FAIL |
| `#3493` | 4 | 0.000395427370 | 16,900 | PASS |
| `#3493` | 6 | 0.000078309235 | 25,350 | PASS |
| `#3976` | 2 | 0.006239877152 | 8,450 | FAIL |
| `#3976` | 4 | 0.000395427370 | 16,900 | PASS |
| `#3976` | 6 | 0.000078309235 | 25,350 | PASS |

The **smallest configuration tested** that meets this sampled pilot budget is **four patches per cylindrical face**, eight patches for the two faces together. This is not a global optimum claim, a continuous-distance certificate or a proof of acceptable mesh quality.

Machine-readable source reference: [original_m5_cylinder_source_sampling.json](evidence/s3h/original_m5_cylinder_source_sampling.json).

## Construction and independent BP controls

`probes/s3h_source_cylinder_bp.py` implements source-bounded reconstruction of a single eligible cylindrical four-edge face. For each original generator, all four Bézier controls retain the **same canonical source-entity keys** used by S3.D: `vertex:<original-id>` at endpoints and `edge:<original-EDGE_CURVE-id>:1/2` in the interior. This is canonical **naming**, not a proven shared global index with the separate *native* planar partial BP produced in S3.A; the cross-atlas merge is a later gate.

For each author-derived angular partition seam, the two neighboring patches use the identical global BP control vertex IDs. Approximate interior controls are generated from source-cylinder angular Hermite tangents, never welded by proximity. The BP itself is written in the existing indexed polynomial bicubic grammar; it is not a mesh.

The independent checker reparses the STEP, recomputes original arc orientation, generator identities, and angular bounds, checks shared integer seam identities, verifies exact original generator boundary values, and evaluates BP surfaces using an independent de Casteljau function at 35 x 35 samples per patch against the analytic source cylinder. Adversarial tests cover source/manifest hash mismatch, forged original control keys, forged circle entity ID, forged patch inventory, tampered BP and a too-small fixed segment budget.

**Local native synthetic STEP experiment:** source face `ADVANCED_FACE #17` (generated within this execution) with 2.102093169774461-rad arc, radius 2 mm and axial length 15 mm. Approximate independent maximum sampled distances: 2 sectors 0.006239877152 mm (FAIL), 4 sectors 0.000395427370 mm (PASS), 6 sectors 0.000078309235 mm (PASS). One file with four candidate BP patches and a machine-readable independent audit was generated successfully. It is a **synthetic control**, not the original M5 model.

## Reproduce and explicit original-only gates

Run locally with Python, CadQuery and OCP; use first-party probe dependencies in the same directory.

```sh
python -m unittest discover -s docs/research/nonmanifold-benchmark/probes -p 'test_*.py' -v
python docs/research/nonmanifold-benchmark/probes/s3h_source_cylinder_bp.py \
  --source-step /external/mambo/sources/i05o_m5.step \
  --model M5 --face-ids 3493 3976 --sectors 4 \
  --absolute-budget-mm 0.001 --output build/research-s3h/m5-cylinder
```

The script verifies the pinned raw SHA-256, exact source curve IDs, source PCURVE constant-U, oriented arc span, generator canonical controls, and independent sampled budget **before** writing the source-derived partial BP files. A failed face prevents the entire batch from being labeled successful. To enable the original-directed unit gate, set `APMESH_MAMBO_SOURCE_DIR` to the external directory containing `i05o_m5.step`. No rights-unverified STEP original is included in source control.

**Actual local research suite:** 115 discovered; 109 PASS; 6 SKIP (all require absent original industrial STEP sources); 0 FAIL. This includes 19 new S3.H directed checks: 18 PASS + 1 original-M5 SKIP. This is not the full C++ production science regression and not an exact-head remote CI gate.

## Open scientific and integration gates

1. **Original native**: import byte-pinned M5 STEP through CadQuery / Open CASCADE, establish original `ADVANCED_FACE`/`EDGE_CURVE` ↔ `TopoDS_Face`/`TopoDS_Edge` and UV trim equivalence, and rerun S3.E–S3.H for both original source faces; rejection is not silently repaired.
2. **Cross-atlas control identity**: integrate the source-original generator controls with the partial native planar BP under a proven STEP ↔ native bijection. Equal coordinates without proven identity must not be counted as shared topological controls.
3. **Continuous geometric correctness**: audit trimmed-domain membership, self-intersections, continuity at all neighboring patches and a certified continuous distance bound or explicit validated surrogate.
4. **Original industrial model completeness**: the other 39 M5 source faces, S40 split-/multi-trim B-splines, cones and tori still need independent model-specific decomposition gates; the current two-cylinder partial BP is not complete M5.
5. **Mesh and publication**: only a fully independently admitted source-to-BP atlas can proceed to historical APMesh TRI acceptance, then conditional QUAD/anisotropic comparisons. External original 3+-sheet nonmanifold source evidence remains a distinct open blocker. Draft PR #225 must not be merged without advisor alignment and exact-head required gates.
