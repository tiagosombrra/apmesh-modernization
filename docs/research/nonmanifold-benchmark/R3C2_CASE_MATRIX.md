# R3.C2 bounded contact-case acceptance matrix

**Scope:** face-splitting and exact indexed bicubic interpolation of planar rectangles from *locally mirrored pinned CAD recipes*, using OCCT native topology. No external source-model admission or APMesh generation.

| Input / perturbation | Expected result | Evidence gate |
|---|---|---|
| T-Junction default source recipe | CONTROL_PASS | 1 contact, host area 100 = 25 + 37.5 + 37.5; 5 valid quads; native 2 triple edges; 5 BP patches |
| Cross-Junction default source recipe | CONTROL_PASS | 2 independent contacts, two 80 = 16 + 32 + 32 host areas; 10 valid quads; native 4 triple edges; 10 BP patches |
| Original source-mirror STEP roundtrip | CONTROL_PASS | 2 or 3 independent imported solids; source geometry/face contact, topological incidence and BP pass audit |
| Sewn native BRep roundtrip | CONTROL_PASS | Native TopoDS triple edge identities survive import; no flattened adjacent coordinate-only approximation |
| Gap 1e-5, 1e-9 or 1e-10 source units | NEGATIVE_PASS | Strict native distance gate rejects even when OCC fuzzy Booleans produce an area-overlap candidate |
| Overlapping solids, positive source volume 0.01 offset | NEGATIVE_PASS | Penetrating solids are not treated as a contact boundary |
| Branch Z height reduced to 80% | UNSUPPORTED_REJECTED | Host minus contact is no longer the required two complete rectangular wing faces |
| Arm face wider than host | UNSUPPORTED_REJECTED | Both source faces need generalized intersection and split; no hidden trimming |
| Edge-only source touch | UNSUPPORTED_REJECTED | No positive-area face contact |
| Nonfinite / nonpositive dimensions | INPUT_REJECTED | Source geometry construction guard |
| Corrupted indexed BP with updated digest | NEGATIVE_PASS | Independent polynomial geometry or source-ID check rejects |
| Wrong shared side reference/orientation | NEGATIVE_PASS | Exact BP vertex IDs and canonical side map mismatch |
| Wrong BRep/nonmatching native source | NEGATIVE_PASS | Independent native shape and area/geometry check |
| False external G2 approval or TRI accepted-stage claim | NEGATIVE_PASS | Scientific scope overclaim rejected |
| Curved/trimmed CAD partial contact, multiple interfaces per source face, material-tag consolidation | NOT_EVALUATED | Dedicated decomposition and scientific-source contracts required |

The actual CAD source is mirrored from `fusion-energy/model_benchmark_zoo@3a2e69fe62209e33a1e176d816609d69a2aebadc`. Source body identity is distinct from material identity (the two Cross arms are separate bodies but may carry the same material tag in the upstream CSG case). Small-dimensional tolerances are **screened case-specific thresholds**, not general sewing or approximation guarantees.
