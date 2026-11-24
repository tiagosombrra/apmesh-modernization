# R2 partial topological screen — explicit edge incidence versus geometric contact

**Status:** PARTIAL SCREEN / G2 NOT PASSED. Date: 2026-11-14.
**Baseline main:** `f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94`.
**Pinned HexMe:** `cgg-bern/hex-me-if-you-can@8f00f02579037cc893042f2ee2c910b20e3fb1b0`.
**Pinned Fusion Energy:** `fusion-energy/model_benchmark_zoo@3a2e69fe62209e33a1e176d816609d69a2aebadc`.

## Evidence boundaries

We examined the original UTF-8 STEP text of HexMe files from their pinned GitHub revision, using a limited reference-graph traversal: ADVANCED_FACE -> FACE_BOUND/FACE_OUTER_BOUND -> EDGE_LOOP -> ORIENTED_EDGE -> EDGE_CURVE. Each edge incidence counts **distinct face entity IDs**, not oriented uses within the same face. This does not independently validate CAD geometry, sewing, source-unit scale, coincident but distinct edges, source license or suitability for bicubic APMesh patches. No raw model asset has been copied into the repository, and no raw-file SHA-256 has been independently recorded.

Separately, we inspected the pinned Fusion Energy `cadquery_assembly()` definitions and **manually mirrored their default geometries locally** using CadQuery. That experiment is not an execution of the upstream package. The mirror's face-edge topological identity was checked using OCP `IsSame`, and geometric segment coincidence was grouped by exact rounded endpoints (9 decimal places). This cannot detect partial overlapping segments and is not a substitute for a source-independent topology oracle.

## Eight structurally traversable original STEP sources

| HexMe original | STEP advanced faces | STEP edge curves | Incidence 1 | Incidence 2 | Incidence >=3 | Interpretation |
|---|---:|---:|---:|---:|---:|---|
| i01o_m1.step (MAMBO M1) | 42 | 114 | 0 | 114 | 0 | No explicit 3+ user |
| i03o_m3.step (MAMBO M3) | 60 | 169 | 10 | 159 | 0 | Ten single-face edge references; native CAD review |
| i10o_simp.step | 11 | 26 | 0 | 26 | 0 | No explicit 3+ user |
| s09o_bridge.step (MAMBO) | 27 | 84 | 42 | 42 | 0 | Mixed shell-based/open-shell entities; native CAD review |
| n10o_qtorus_cyl.step (MAMBO) | 12 | 33 | 21 | 12 | 0 | Repeated within-face loop use; native CAD review |
| n11o_limit_cycle.stp | 6 | 11 | 0 | 11 | 0 | No explicit 3+ user |
| s11o_cube_cyl.stp | 8 | 14 | 0 | 14 | 0 | No explicit 3+ user |
| s12o_cube_rounded_1.stp | 26 | 48 | 0 | 48 | 0 | No explicit 3+ user |

Additional **incomplete** case: `s16o_torus.stp` contains one ADVANCED_FACE with a VERTEX_LOOP and no explicit EDGE_CURVE; the screen reports an unresolved bound. Zero counted edges here **does not** imply a valid topology or a complete audit. These STEP results are screening observations, not claims that the CAD models are globally manifold.

## Five pinned-source CadQuery geometry mirrors

Local environment: Python 3.13.5, CadQuery 2.8.0, OCP 7.9.3.1. All dimensions follow pinned upstream default parameter values.

| Mirrored source | Solids | OCP faces | OCP topological edges | Max topological face incidence | Geometrically coincident full segments across bodies |
|---|---:|---:|---:|---:|---:|
| three_touching_cuboids | 3 | 18 | 36 | 2 | 7 |
| t_junction | 2 | 12 | 24 | 2 | 0 (whole endpoints only) |
| cross_junction | 3 | 18 | 36 | 2 | 0 (whole endpoints only) |
| two_touching_cuboids | 2 | 12 | 24 | 2 | 4 |
| tangent_spheres | 2 | 2 | 2 OCP seams | 1 | 0 |

In `three_touching_cuboids`, there is a geometrically coincident segment between (0,0,-2.5) and (0,0,2.5) belonging to **three bodies**, giving six face-edge uses (two per body). However, the unmodified B-Reps retain distinct edges for their separate solids; **no topological edge is incident to three faces in the unmodified assembly**. The mirrored assembly's exported STEP contains 18 ADVANCED_FACE and 36 EDGE_CURVE, all with two distinct face uses. Thus this is a high-value **contact / imprint feasibility lead**, not an already-compatible non-manifold APMesh patch complex.

T- and cross-junction assemblies include partial face/edge contacts that are missed by a full-endpoint coincidence detector; zero such matches is *not* evidence of no contact. Tangent spheres are a point-contact/periodic-seam control, not a positive edge-junction case. The mirrored STEP for tangent spheres exposed two unresolved vertex-loop bounds and no EDGE_CURVE.

## Reproducible probes and local tests

Isolated experimental code (not linked to the production build):
- `probes/step_structural_screen.py`: bounded STEP entity reference screen (standard library).
- `probes/test_step_structural_screen.py`: adversarial unit tests for true 3-face edge, 2-face edge, coincident-but-distinct edge IDs, VERTEX_LOOP, duplicate entity and invalid input.
- `probes/export_source_mirror.py`: CadQuery assembly export with the pinned models' default geometry.
- `probes/cadquery_contact_probe.py`: OCP topological identity and endpoint-coincidence comparison.

```sh
python -m unittest discover -s docs/research/nonmanifold-benchmark/probes -p "test_*.py" -v
python docs/research/nonmanifold-benchmark/probes/export_source_mirror.py --output-dir build/research-r2
python docs/research/nonmanifold-benchmark/probes/cadquery_contact_probe.py
python docs/research/nonmanifold-benchmark/probes/step_structural_screen.py path/to/permitted_model.step
```

The locally executed prototype STEP screen passed **6/6** adversarial tests and five mirrored models were constructed and screened. **The exact committed Git revision has not been re-executed as a suite**, and no APMesh CMake, CTest, Python regression or generation command has been run in this phase. These limited prototype checks are not CI qualification or model admission.

## R2 scientific decisions

1. Do **not** classify HexMe/MAMBO CAD files as non-manifold positives based on their benchmark name, complexity or a single screenshot.
2. Prioritize `three_touching_cuboids` as a *candidate for explicit junction reconstruction*; create a source-to-interface/sheet graph first, not tolerance-based welding.
3. Keep `t_junction` and `cross_junction` as partial-overlap and feature-split challenges, and `tangent_spheres` as a point-contact negative control.
4. Preserve source body and interface identities when choosing which coincident internal boundary faces are retained; a physical contact does not uniquely prescribe an APMesh patch graph.
5. Before moving any case to G2 PASS: retrieve authorized raw assets; hash bytes (SHA-256); use a CAD kernel for true edge, face, shell, body, trimming, imprint and geometric intersection topology; establish declared intended 3+ incident surface sides; run an independent checker; document legal rights and thresholds.
6. Conversion to .bp, APMesh TRI generation, historical regressions and future QUAD/anisotropic claims remain separately blocked until their gates are measured.

**Disposition:** R2 partial structural and contact evidence obtained; **0 externally validated 3+-sheet non-manifold APMesh models**, **0 converted models**, **0 generator claims**. No source algorithm or historical experimental artifact changed.

## R2 native kernel follow-on

A separate, measured source-recipe mirror and native STEP round-trip now reconstruct four candidate surface sheets around a central three-body contact, with explicit source-edge separation and 15 local adversarial tests. See [R2_NATIVE_INTERFACE_PROOF.md](R2_NATIVE_INTERFACE_PROOF.md). This result does NOT approve G2, validate an external model, convert BP, or qualify the APMesh generator.
