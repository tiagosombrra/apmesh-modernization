# S3.E — Fail-closed source-entity-to-native-BRep interface correspondence

**Date:** 2026-11-16. **Scope:** isolated scientific research, no production/QUAD changes.

## Question and evidence boundary

Can an originally referenced STEP `ADVANCED_FACE`/`EDGE_CURVE` planar-candidate boundary be correlated **uniquely** with its imported Open CASCADE `TopoDS_Face`/`TopoDS_Edge`, including a native adjacent cylindrical face, without proximity welding or inferring unproved global BRep identity?

A new bounded correlator `probes/s3e_native_feature_bijection.py` conservatively tests local candidate boundaries in the *same immutable source STEP* and a native Open CASCADE import. It compares planar convex four-edge face loops, ordered 3D source vertices up to cyclic/reversed correspondence, global TopoDS identity, native `LINE` side edges, incident face owners, neighbor support type, source/native edge length and an independently audited planar BP subset. It rejects any ambiguous candidate face or source/native identity collision; it never merges distinct native entities solely by coordinate distance. A source SHA-256 digest must match the original bytes; known MAMBO models additionally enforce pinned raw digests and face/candidate inventories. Checksums on reports are only integrity metadata: independent recomputation from source/native geometry is the verification gate.

### Synthetic BRep execution — actually run

A test-constructed **half cylinder** (radius 3 mm; height 4 mm) has four valid native faces. OCCT STEP export and fresh import preserve one admitted planar four-edge candidate and four original STEP candidate-to-excluded edge interfaces:

| Evidence | Measured result |
|---|---:|
| STEP faces / imported native faces | 4 / 4 |
| Uniquely matched eligible planar faces | 1 |
| Matched source-original straight edges to excluded faces | 4 |
| Matched planar-to-cylinder native adjacency | 2 |
| Matched planar-to-excluded-planar native adjacency | 2 |
| Exact native source curve identities mapped into partial BP patch | 4 |
| Independently audited partial BP patches | 1 |
| Excluded faces not represented by patches | 3 |
| Original M5/S40 native runs | **NOT RUN** |
| Native cylinder patches | **NOT RUN** |
| Accepted APMesh TRI/QUAD generation | **NOT RUN** |

The independent source-line curve audit is also run before any partial BP data are written. The `source_neighbor_advanced_face_ids_verified` field is **false**: checking a native *adjacent face's surface type and native edge identity* does **not** establish a full STEP excluded-neighbor `ADVANCED_FACE`↔`TopoDS_Face` mapping. Full cross-face surface parameterization, p-curves, shared cubic control nets, periodics and rational B-splines are separate gates.

**Ambiguity controls:** translated source/native shape, coincident-but-distinct solids, modified STEP vertex, forged checksum with modified native edge, mismatched cylinder/plane support and substituted M5 source are rejected. All tests use author-constructed local synthetic CAD; no original STEP geometry is redistributed.

### Current suite and environment

`python -m unittest discover -s .../probes -p 'test_*.py' -v`: **67 discovered, 64 passed, 3 explicitly skipped, 0 failed** (including 12 S3.E cases, 11 pass + 1 original-asset skip). Existing 55 tests from S3.A–S3.D still pass or skip with the same reasons as previously reported. Full production regression: **NOT RUN**. Original MAMBO STEP bytes are not mounted in the local container, and direct container network resolution of `github.com` failed. The connector previously verified upstream pinned original STEP *source text*; that is not a native import in the current runtime.

## Reproduce: four-original native gate

Install environment dependencies and place original allowed STEP bytes in a separate external directory. Do not add third-party originals to Git until their distribution rights are verified. From the repository root:

```sh
python -m unittest discover -s docs/research/nonmanifold-benchmark/probes -p 'test_*.py' -v
python docs/research/nonmanifold-benchmark/probes/s3e_native_feature_bijection.py \
  --source-step /external/mambo/sources/i05o_m5.step --model M5 \
  --output build/research-s3e/m5
python docs/research/nonmanifold-benchmark/probes/s3e_native_feature_bijection.py \
  --source-step /external/mambo/sources/i25o_s40.step --model S40 \
  --output build/research-s3e/s40
```

For an *unpublished synthetic* STEP, `--model SYNTHETIC --expected-sha256 <the actual raw SHA-256>` is required. The output directory is populated only after every required screen and independent audit succeeds. Outputs are `source_feature_curves.json`, `independent_source_curve_audit.json`, `native_correspondence.json`, `independent_correspondence.json`, `planar.partial.bp`, `partial_atlas.json`, `independent_partial_bp_audit.json`.

## Next conditional gates (S3.F)

1. Run S3.E on original M5 and S40 with the pinned SHA-256 values. Treat any ambiguity or native-source discrepancy as a blocked result, not as a success.
2. Independently establish source excluded-face IDs ↔ imported native neighbor face identity, including cylindrical 2D p-curves and wire orientation. Do not infer global face bijection from candidate-face matching alone.
3. For the 4 M5 and 12 S40 candidate-to-cylinder interfaces (44 across all four CAD controls), fit *neighbor face regions* under fixed budgets with the already-admitted source linear cubic feature constraints. Verify native CAD geometric residuals and identical shared global control indices, including after splitting.
4. Only after compatible partial atlases, attempt TRI generator execution with its existing acceptance status and independent output diagnostics. QUAD or anisotropy benchmarking remains downstream; no original external true non-manifold positive has been admitted.

**Release status:** research PR #225 remains draft; no merge and no changes to production C++ or main.
