# S3.F — First-ring original STEP face identity from source-anchored native edges

**Date:** 2026-11-16. **Classification:** isolated scientific research, no C++ production changes or QUAD merge.

## Question

S3.E established source-to-native correspondence for eligible planar faces and original boundary edges, including their native adjacent face's support *type*. S3.F asks whether original excluded-neighbor `ADVANCED_FACE` **entity IDs**, rather than just a support type, can be assigned to the adjacent `TopoDS_Face` *injectively* from those certified original `EDGE_CURVE` anchors.

## Method and admission gates

The standalone `probes/s3f_first_ring_native_faces.py`:

1. Requires an immutable source STEP SHA-256 and the S3.E candidate/edge certificate; original M5/S40/S27/M3 are checked against pinned hashes before native import.
2. Independently **recomputes** the S3.E certificate from the original STEP text and imported BRep; it does not accept an arbitrary JSON claim.
3. Checks that each source neighbor face really contains the same original `EDGE_CURVE` exactly once, and the corresponding native neighbor face contains the mapped `TopoDS_Edge` exactly once by `IsSame`, not by coordinate welding.
4. Checks that the source and native adjacent supports agree, every anchored original edge is unique, all anchors assigned to one original neighbor face map to the **same** native face, and distinct source faces map to distinct native faces.
5. Recomputes all S3.F output fields from source/native geometry before writing four JSON receipts; failures write no success artifacts.

A source first-ring face ID is a **bounded topological assignment by anchored edges**. It does not certify every boundary of that face, NURBS/trim parameterization, a full original CAD representation, or an APMesh-generated mesh.

## Executed synthetic control

An author-constructed Open CASCADE half cylinder (radius 3 mm, height 4 mm) is exported to STEP and imported again. Source-anchored first-ring face mapping returns:

| Check | Measured |
|---|---:|
| Original STEP `ADVANCED_FACE` / imported native faces | 4 / 4 |
| S3.E eligible planar source-native face matches | 1 |
| Distinct excluded neighbors uniquely identified via original edges | 3 |
| Excluded native cylindrical face IDs identified | 1 |
| Excluded native planar face IDs identified | 2 |
| Direct original edge anchors verified | 4 |
| Multiple anchors on same cylinder consistently mapped | 2 |
| Original source faces outside this first ring | 0 |
| Recompute audit | PASS |
| Complete curved-face geometry audit | **NOT ESTABLISHED** |
| Original M5/S40 native run | **NOT RUN** |
| APMesh TRI/QUAD accepted mesh | **NOT RUN** |

A separate six-face box control maps its six planar candidates without adding fictitious excluded neighbors. Negative controls reject altered original text, native transforms, forged first-ring records even with recomputed checksums, source SHA mismatch and substitutes for pinned original M5 or S40.

## Source-only original MAMBO/HexMe first-ring prediction

A read-only traversal of the **previously verified original STEP `EDGE_CURVE` graph** at upstream revision `8f00f02579037cc893042f2ee2c910b20e3fb1b0` identifies how many original excluded-neighbor source IDs would become in-scope *if* the corresponding native S3.E prerequisite passes. This is **not** an OCCT-native run of these models. The source-only evidence lives in `evidence/s3f/original_step_first_ring_prediction.json`.

| Model | Source faces | Planar candidate faces | Direct excluded first-ring source faces | Source faces outside first ring | Distinct original anchored interfaces | First-ring excluded planar / cylindrical faces |
|---|---:|---:|---:|---:|---:|---:|
| M5 | 41 | 6 | 7 | 28 | 20 | 5 / 2 |
| S40 | 43 | 9 | 18 | 16 | 32 | 10 / 8 |
| S27 | 52 | 20 | 14 | 18 | 60 | 10 / 4 |
| M3 | 60 | 10 | 23 | 27 | 40 | 8 / 15 |

Only the original pinned STEP entity text was read through the GitHub connector; its upstream Git blob IDs are in the receipt. The original raw STEP SHA-256 hashes from S1 were *not recomputed* during this connector-only prediction. No third-party original STEP geometry is checked into this branch.

**Important interpretation:** Source adjacency reachability does not guarantee that the native kernel preserves exactly the source face graph. Ambiguity, split/merged faces, removed edges, periodic seam multiplicity, altered support type or unacceptable trim topology all *block* the native certificate. Report a failure rather than silently re-sewing entities or accepting only a subset.

## Reproduce when original input files are available

From the repository root with CadQuery 2.8.0 and OCP 7.9.3.1 available, use the separate source directory:

```sh
python -m unittest discover -s docs/research/nonmanifold-benchmark/probes -p 'test_*.py' -v
python docs/research/nonmanifold-benchmark/probes/s3f_first_ring_native_faces.py \
  --source-step /external/mambo/sources/i05o_m5.step --model M5 \
  --output build/research-s3f/m5
python docs/research/nonmanifold-benchmark/probes/s3f_first_ring_native_faces.py \
  --source-step /external/mambo/sources/i25o_s40.step --model S40 \
  --output build/research-s3f/s40
```

`M5` and `S40` need **the original bytes**, not a synthetic proxy. Each refuses a mismatched SHA before producing success artifacts. Do not commit upstream geometry without verifying redistribution rights.

## Test accounting and next gate

Local directed unit test discovery after S3.F: **80 cases / 76 PASS / 4 SKIP / 0 FAIL**, including 13 S3.F cases (12 PASS, 1 explicit original-asset SKIP). The full production regression suite was **NOT RUN**, and no original MAMBO native BRep files were available to this execution environment. Original STEP source graphs were inspected externally, but not imported locally.

The next gate is to obtain legally accessible, byte-exact originals locally and run S3.E and S3.F *for real*, recording any failed identity associations. Only afterward should research attempt constrained cylindrical-neighbor patches with exact shared boundary controls and independently validated geometric error. True external non-manifold 3+-incident originals remain a separate outstanding scientific gate.
