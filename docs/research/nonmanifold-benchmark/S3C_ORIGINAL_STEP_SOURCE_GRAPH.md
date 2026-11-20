# S3.C — Original STEP source-graph gate before native curved fitting

**Date:** 2026-11-15. **Research track only.** The upstream originals were inspected through the connected GitHub repository at immutable HexMe revision `8f00f02579037cc893042f2ee2c910b20e3fb1b0`. This analysis does not claim to run native OCCT conversion or APMesh meshing of the originals in the current runtime. No original STEP bytes are committed.

## Direct inspection of four original sources

The independent reference traversal resolves `ADVANCED_FACE` -> `FACE_BOUND` -> `EDGE_LOOP` -> `ORIENTED_EDGE` -> `EDGE_CURVE` -> master 3D `LINE`, including `SURFACE_CURVE` and `SEAM_CURVE` wrappers. It checks four topologically connected distinct vertices, convexity and source-point coplanarity. The original `EDGE_CURVE` identity (not coordinate proximity) determines incidence. A complex `RATIONAL_B_SPLINE_SURFACE` STEP entity is recognized without promoting it to a polynomial surface.

| Original source | Faces | Source graph planar quad candidates | Candidate-side uses | Distinct candidate source edges | Candidate-candidate shared edges (2 face uses) | Candidate-to-excluded face edges | Source open candidate edges |
|---|---:|---:|---:|---:|---:|---:|---:|
| M5 `i05o_m5.step` | 41 | 6 | 24 | 22 | 2 | 20 | 0 |
| S40 `i25o_s40.step` | 43 | 9 | 36 | 34 | 2 | 32 | 0 |
| S27 `i22o_s27.step` | 52 | 20 | 80 | 70 | 10 | 60 | 0 |
| M3 `i03o_m3.step` | 60 | 10 | 40 | 40 | 0 | 40 | 0 |
| **Total** | **196** | **45** | **180** | **166** | **14** | **152** | **0** |

**Key result:** the candidate patches alone are *not a complete model atlas*. Exactly 152 original edge identities of these candidate faces connect to non-admitted source faces. Such edges need original feature-curve compatible neighboring surfaces before an unqualified model claim. The 14 shared edges have two candidate incident source faces, and none is an original multi-sheet three-plus junction. This cohort remains a complex-*geometry* control, not external non-manifold generalization.

The 45 candidates match the counts in the prior independent native S1 audit, but numerical count equality is **not a bijective mapping from STEP `ADVANCED_FACE` IDs to native imported `TopoDS_Face` IDs**. That mapping must be established and independently audited before asserting the correct source-to-patch provenance.

Evidence JSON: [original_step_candidate_summary.json](evidence/s3c/original_step_candidate_summary.json), with pinned upstream Git blob SHA-1 identifiers and all 45 `ADVANCED_FACE` entity IDs; it contains no third-party coordinates or STEP model bodies. Raw STEP SHA-256 values are inherited from the separately documented S1 original-byte validation, **not recomputed in this source-graph connector inspection**.

### Reproducible local execution gate

Place original permitted files in an external `sources/` directory, unchanged, and execute from the repository root with CadQuery 2.8.0, OCP and NumPy available:

```sh
python docs/research/nonmanifold-benchmark/probes/s3c_step_source_gate.py --model M5 --sources /external/mambo/sources --output build/research-s3c/m5_step_graph.json
python docs/research/nonmanifold-benchmark/probes/s3c_original_batch.py --sources /external/mambo/sources --output build/research-s3c/originals --models M5 S40 S27 M3
python -m unittest discover -s docs/research/nonmanifold-benchmark/probes -p 'test_s3c_*.py' -v
```

The batch fails closed if an input is missing, has a changed SHA-256, disagrees with the native face inventory, or fails the independent partial BP audit. It records each failure rather than replacing it with fabricated mesh output. It makes separate source-graph, native-eligibility, derived BP and independent BP receipt files, but **does not** fit or connect the excluded curved, periodic or multiply-trimmed faces. Outputs are local research artifacts, not committed source geometry.

### Test scope and disposition

- 16 local S3.C directed tests executed: **15 PASS, 1 SKIP** (real original STEP files absent from this runtime). Positive controls cover six-face box, joined native atlas, three-oracle comparison, source-entity identities, two almost touching but topologically distinct solids, and real rejection handling. Negative controls cover a flipped `ORIENTED_EDGE`, invalid envelope, duplicate entity ID, nonplanar cylinder, triangular faces, hash mismatch, frozen inventory mismatch, missing files, and rational complex surface recognition.
- Source-text inspection was performed on four exact pinned upstream Git blobs, including S40's rational complex STEP surface. Original local CAD native import/conversion in this turn: **NOT RUN**.
- Combined S3.A/S3.B/S3.C local unit tests: **46 cases, 45 PASS, 1 SKIP**, without full production regression. Historical three-model CTest/scientific regression, accepted APMesh TRI/QUAD, shared-source feature curve fitting, continuous approximation error bounds and external 3+-sheet topology validation: **NOT RUN**.
- Redistribution rights review: OPEN. Source metadata declares Apache-2.0, but this does not constitute an independent per-file redistribution approval.

## Next scientific checkpoint: S3.D

Start with the 152 original candidate-to-excluded source edge identities. Prioritize M5's cone/cylinder/torus and S40's rational B-spline interfaces, matching canonical original feature curves **before** individual face approximations. Admit a bounded curved face only if its trim-domain correctness, original edge identity, shared-control compatibility and independent source geometric error can be demonstrated within a predeclared budget. Do not fill absent faces with arbitrary patches or count derived seams as original non-manifold evidence.
