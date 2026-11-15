# R3.C1 — curved shared-curve bicubic control (local proof)

**Date:** 2026-11-15. **Status:** bounded synthetic curved control PASSED; full R3 corpus and external model admission OPEN.
**Scope:** authored nonplanar cubic spine and four exact polynomial ruled bicubic surface sheets, not the CAD shape of the upstream three cuboids. This is a *controlled deformation of the R2 incidence pattern*, not a conversion of an original third-party B-Rep. No APMesh production source or historical article model was changed.

## 1. Geometry, topology and exact representability

A nonplanar cubic spatial centerline is explicitly specified for t in [0,1]:

    C(t) = (0.4*t*(1-t), 0.3*t*(1-t)*(2*t-1), -2.5+5*t)

The corresponding cubic Bernstein poles, in order, are:

    C0 = (0, 0, -2.5)
    C1 = (2/15, -0.1, -5/6)
    C2 = (2/15, +0.1, +5/6)
    C3 = (0, 0, +2.5)

The curve is regular because z'(t)=5. It is not a straight line or a planar constant-curvature proxy: the scalar triple product of its first three derivatives is nonzero (14.4), so the authored curve has nonzero torsion everywhere its Frenet curvature is nonzero.

For the four region-pair sheets (A/B, A/C, B/VOID, C/VOID), choose D in {(0,5),(-5,0),(5,0),(0,-5)}. The exact ruled surfaces are

    S_k(u,t) = C(t) + u*(Dx_k,Dy_k,0),  0 <= u,t <= 1.

For each sheet, bicubic control poles with i,j in {0,1,2,3} are exactly

    P_ij = C_j + (i/3)*(Dx_k,Dy_k,0).

This is degree elevation in u and is **exact over the continuous patch in exact real arithmetic** by polynomial Bernstein linear precision, rather than an approximate CAD fit. All four sheets are curved in the ambient 3D space and the common boundary is one **curved cubic**. This specific exactness statement does NOT extend to arbitrary CAD, trimmed surfaces or nonpolynomial inputs.

The indexed legacy BP grammar has exactly 52 distinct global control records, four 16-index patches and 13 distinct logical boundary curves. The four C0 control indices are [0,1,2,3]. Three patches traverse these in increasing t; patch P1 traverses them as [3,2,1,0], testing canonical orientation normalization without duplicating the curve controls. The sidecar preserves region and orientation metadata absent from the BP grammar.

## 2. Native Open CASCADE topology proof

The independent CAD artifact is built as four Geom_BezierSurface faces and sewn with BRepBuilderAPI_Sewing SetNonManifoldMode(True) at 1e-8 source units.

Actual local kernel observations:
- all four source curved faces and the sewn Shell validate in OCCT;
- 13 unique TopoDS edge identities with face-incidence histogram {1: 12, 4: 1};
- exactly one true TopoDS edge is incident on all four faces, checked with native IsSame;
- native BRep export and reimport preserve the same incidence histogram;
- ordinary manifold-mode sewing instead gives no four-incidence edge;
- displacing one face by 2e-5 source units, above 1e-8 sewing tolerance, destroys the four-way shared edge. This single bounded test is not a global tolerance-safety proof.

Relevant kernel API references:
- https://github.com/Open-Cascade-SAS/OCCT/blob/master/src/ModelingAlgorithms/TKTopAlgo/BRepBuilderAPI/BRepBuilderAPI_MakeFace.hxx
- https://github.com/Open-Cascade-SAS/OCCT/blob/master/src/ModelingAlgorithms/TKTopAlgo/BRepBuilderAPI/BRepBuilderAPI_Sewing.hxx

## 3. Independent analytic and native checks

Producer: probes/curved_bicubic_pilot.py. Independent BP grammar and de Casteljau evaluator: audit_analytic_bp.py; curved geometry and status auditor: probes/audit_curved_bicubic.py. Native geometry uses CadQuery + OCP.

Measured on Python 3.13.5, CadQuery 2.8.0, cadquery-ocp 7.9.3.1.1:
- 12 newly added curved controls passed; **44/44 combined R2 plus planar/curved R3 tests passed** on the local research source bundle, using the exact source bytes corresponding to the staged Git blobs;
- 324 patch parameter samples (81 per patch) checked with independent **power-basis** analytic S_k (not producer's poles);
- maximum absolute difference = **8.881784197001252e-16** (numerical screen limit 2e-12);
- 256 interior analytic samples compared with native BRep face distance (minimum over the four faces to avoid relying on shell iteration order);
- maximum native BRep distance = **8.95090418262362e-16** (numerical screen limit 1e-8);
- one reversed local parameter orientation recovered without changing the four common global control vertex IDs;
- corrupted shared-index references with a recalculated SHA-256, off-curve geometry, reversed orientation metadata and false claims of approved TRI generation are rejected;
- an exact nonrational cubic case with Cx(t) perturbed by 0.05*sin(2*pi*t) is explicitly rejected as **nonpolynomial in the fixed parameter t**: its fourth derivative at t=1/4 is nonzero, whereas a cubic polynomial's fourth derivative vanishes. Approximation, parameter changes and segmentation are NOT evaluated by that test.

These are finite numerical observations plus the preceding algebraic exactness argument; sample errors do not certify arbitrary CAD Hausdorff error.

## 4. Reproduction, checksums and artifact identity

From repository root:

    python docs/research/nonmanifold-benchmark/probes/curved_bicubic_pilot.py --out-dir build/research-r3-curved
    python docs/research/nonmanifold-benchmark/probes/audit_curved_bicubic.py --bp build/research-r3-curved/four_sheet_curved.bp --sidecar build/research-r3-curved/four_sheet_curved.sidecar.json --brep build/research-r3-curved/four_sheet_curved.brep
    python -m unittest discover -s docs/research/nonmanifold-benchmark/probes -p "test_*.py" -v
    python docs/research/nonmanifold-benchmark/probes/render_curved_r3.py --output build/research-r3-curved/curved_gallery.png

The .bp fixture is committed as fixtures/four_sheet_curved.bp. Native BRep and metadata JSON are generated from the script and delivered in a separate local ZIP; no unlicensed CAD source files are committed.

Two local production runs generated byte-identical files with SHA-256:

| Generated file | SHA-256 |
|---|---|
| four_sheet_curved.bp | b1b6610b63f10dfe91e84fc8de85d8cbb8b9bdb50a7b0ecdbc95efd89b64fdd4 |
| four_sheet_curved.sidecar.json | 03ffe6ef55c34f6d0f559ef9e34b04c0ae6c8caf4dec69c9dbe498a83deb9514 |
| four_sheet_curved.brep | b1a4b350574f23f1aac73d17bd822a78ea2ad9abd411ea34d258fe2929b99d14 |
| native_curved_report.json | 74a9c533945d33d4d1a028e25de0b8bee24e601e52706cb8b1329d9b62a6ea06 |

Checked local Git blob SHA identities for exact source text staged remotely:
- curved_bicubic_pilot.py: 92e98e777e90c4b3ad66b0fb730b2356dca1ec19
- audit_curved_bicubic.py: 74243a7a7ae72900eb3e481997b3e9103b2b5f47
- test_curved_bicubic.py: 93e4c2e8d60d423b34cf00d09b6e9ce67d91569f
- render_curved_r3.py: b60d97ae776b6db6ddccc12f0b8efff071372879
- fixtures/four_sheet_curved.bp: 398bef93f78368c3b41a90e4e8ca433e00ba5aa0

No native production CTest/Python regression, APMesh generation, accepted/rejected-stage trace, external source model G1/G2 signoff, or TRI/QUAD/all-quad/anisotropic comparison was executed. No GPU or general-purpose CAD import/decomposition is claimed.

## 5. Closure decision and hard next gates

**R3.C1 controlled curved analytic case: PASS**, with 12 direct tests and the combined 44-case local suite. **Full R3 work package: OPEN.** This is the second supported analytic BP fixture (first planar, now curved), not a second externally admitted candidate.

Next sequence:
1. R3.C2: source-derived bounded four-sided CAD face decomposition including partial-curve overlaps and independent source-unit/trim checks. Reject unsupported trimming/hole/periodic cases by evidence.
2. Validate exact canonical curve identity before fitting side surfaces. Enforce a declared geometry budget with sampled convergence and negative controls before any approximate fitting claim.
3. Keep the future general R4 reverse converter in a separate experimental subsystem. Do not reinterpret a synthetic BP writer as verified CAD-to-BP conversion.
4. Only start R5 APMesh TRI qualification after model admission and frozen source/binary/config evidence; then run exact accepted/rejected stages, historical 75 CTest plus current Python gates, and independent boundary incidence.
5. Require scientific advisor review of material-interface/VOID choices and extension of published claims.

No stage merge or scientific generalization is authorized by this bounded proof.
