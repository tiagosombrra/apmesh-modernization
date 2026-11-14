# R1 — Model-level discovery and evidence gaps

**Date:** 2026-11-14. **Status:** first model-ID discovery inventory created; no model admitted.
**Register:** `candidate_register.csv`, 40 rows. Every row is a named individual source reference or upstream-documented corrupt file ID. Counts are exploration volume, not success or non-manifold coverage.

## Grounded discovery totals

| Source | Records | Evidence read | Current restrictions |
|---|---:|---|---|
| HexMe / cgg-bern | 29 | existence of original CAD file AND corresponding `meta/*o_*.yaml` in pinned upstream repository; file-level declared license | STEP/B-Rep/Gmsh GEO files have NOT been downloaded, hashed by SHA-256, topologically analyzed or converted |
| Fusion Energy model_benchmark_zoo | 6 | exact executable-example Python script and repository MIT license; descriptions of contacts/junctions | scripts were inspected but not executed, no STEP output exists in our study and actual welded/imprinted source topology is UNKNOWN |
| Thingi10K | 5 | upstream README explicitly identifies these model file IDs as corrupt/empty/unsupported OBJ semantics | negative test leads only; original files, their individual licenses and hashes not fetched |
| **Total** | **40** | source identifiers only | **0 accepted external APMesh models; 0 confirmed intended >=3-sheet non-manifold edges** |

The HexMe repository identifies **63 original CAD files**, not 63 APMesh-compatible patch complexes. Its metadata distinguishes public-domain and Apache-2.0 items from GrabCAD-terms models and an unknown-rights DLR model; upstream dataset MIT licensing must not be substituted for asset-specific CAD rights. Models imported from MAMBO into HexMe are **not independent benchmark geometries** if also collected separately from MAMBO (avoid duplicate counts).

Thingi10K's overall ~22% non-manifold rate is a dataset-level flag. It does not prove that any particular Thingi10K asset has an intended shared CURVE with >=3 sheets. Its five known corrupt items are adversarial-parser leads, not benchmark positives.

### Source repositories pinned for repeatable retrieval

- HexMe: https://github.com/cgg-bern/hex-me-if-you-can/tree/8f00f02579037cc893042f2ee2c910b20e3fb1b0 (original and per-file metadata).
- Model Benchmark Zoo: https://github.com/fusion-energy/model_benchmark_zoo/tree/3a2e69fe62209e33a1e176d816609d69a2aebadc (procedural CAD/CSG examples).
- Thingi10K README: https://github.com/Thingi10K/Thingi10K/blob/cbac53559cfade2c4ffb2ef1ae8cae88462eaed4/README.md (upstream errata, not raw files).
- Tangency Labs: https://github.com/tangency-labs/models/tree/57abdd6f71c4202fcda78d19dcfdb54dde80a7a9 (STEP, OBJ, STL and IGES folders have only README files; no candidate model supplied).
- ABC: https://deep-geometry.github.io/abc-dataset/ (B-Rep chunks and metadata; **no individual model/chunk extracted in R1**).
- MAMBO: https://gitlab.com/franck.ledoux/mambo (a geometry source; named MAMBO originals are already present inside HexMe; do not count twice).

## High-value investigation order (NOT approved candidate ranking)

1. `FUSION-three_touching_cuboids`: expected three-body contact / reported triple-edge challenge. First test if exported STEP has an explicit, topology-coherent three-sheet edge. If contact surfaces remain independent, it is a contact/imprinting challenge rather than a positive APMesh junction.
2. `FUSION-t_junction` and `FUSION-cross_junction`: multi-body contact and imprint cases; require source edge and sheet graph to prove >=3 incidence, not merely visual contact.
3. `HEXME-n13o_acute_line`, `HEXME-s07o_notch`, `HEXME-n01o_cross_cyls_sr`: sharp/curved feature geometry controls, not presumed non-manifold. In particular, the upstream 'two planes acute dihedral' is not itself a three-sheet shared-edge proof.
4. `HEXME-s09o_bridge`, `HEXME-n10o_qtorus_cyl`, `HEXME-i01o_m1`, `HEXME-i03o_m3`, `HEXME-i05o_m5`: CAD and MAMBO-backed controls for quality/segmentation. These are *not* automatically edge-non-manifold.
5. `FUSION-tangent_spheres`: a valuable point-contact, vertex-only adversarial/control example to prevent false positive classification.
6. `THINGI-ERRATA-49911/74463/286163/81313/77942`: parser failure controls; permissions and raw access must be assessed first.

`HEXME-i26o_gc_turbo_vol1`, `HEXME-i28o_gc_tire_1218`, `HEXME-i29o_bracket`: source metadata lists **GrabCAD Terms**. No copying/derivative distribution is authorized by this review. `HEXME-i31o_dlr_f6`: metadata license explicitly **Unknown - AIAA-DPW/DLR**. Rights BLOCKED pending explicit clearance.

## Critical caveats discovered

- Pinned paths and human-readable upstream metadata confirm **existence**, not geometry, topology, bounded converter fit, or redistribution rights.
- Exact STEP and GEO B-Rep semantics must be interrogated with a CAD kernel; Python example script behavior must be checked by actually generating STEP and preserving source/body identity. Scripts may require nontrivial runtime dependencies (OpenMC, CAD, DAGMC) not present in this research session.
- The `.bp` representation requires four-sided indexed bicubic Bezier control nets; a valid source CAD solid is not automatically representable as one or more admissible patches.
- All `raw_sha256` fields intentionally remain blank. Git revisions are provenance anchors, not substitutes for byte hashes of model assets.
- `candidate_register.csv` uses the conservative `DISCOVERED` state for all entries; metadata declarations are not independent license or topology reviews.

## Next R1->R2 handoff

1. Recheck pinned source paths and download policy; retrieve exact raw assets into a separate non-versioned workspace, or create reproducible acquisition instructions where permitted.
2. Compute raw SHA-256 and preserve the original file, any CAD export and normalization transformations separately.
3. Extract independent B-Rep face/edge use graph and mesh edge/vertex incidence, with explicit sheet IDs, shared-curve labels, trimmed-edge orientation and topology class.
4. Keep CAD geometry controls and prospective multi-body junctions distinct; report every rejected or inaccessible candidate and avoid post hoc replacing them with easy success cases.
5. Require signed G1/G2 review to promote models beyond `DISCOVERED`. No claim of an approved corpus is made in this report.

**R1 result:** discovery inventory documented, basic upstream file/metadata existence established, but exact-asset SHA256/license independent review and topological characterization are **OPEN**. This is a research handoff, not the R2 admission gate.
