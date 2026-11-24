# R3.C2 — Native partial-face contact splitting for T/Cross junctions

**Date:** 2026-11-15. **Status:** two bounded native-kernel source-recipe controls passed; complete R3 work package OPEN. **This is not an external G1/G2 admission.** The original APMesh C++ implementation, published `.bp` inputs, numerical policies, TRI and QUAD experiments were not changed or executed.

## Pinned source and scientific boundary

- Upstream: `fusion-energy/model_benchmark_zoo` revision `3a2e69fe62209e33a1e176d816609d69a2aebadc`.
- Pinned CadQuery source recipes: `src/model_benchmark_zoo/t_junction.py` (Git blob `5a6fa71cd7e1351a77f8a2015b6c5dcb08430f08`) and `src/model_benchmark_zoo/cross_junction.py` (Git blob `cdc49ab90604cb7a9290a05519464ffe7a099a60`). These Git blob SHA-1 identifiers are **not raw-file SHA-256**.
- Original code: [T-Junction](https://github.com/fusion-energy/model_benchmark_zoo/blob/3a2e69fe62209e33a1e176d816609d69a2aebadc/src/model_benchmark_zoo/t_junction.py), [Cross-Junction](https://github.com/fusion-energy/model_benchmark_zoo/blob/3a2e69fe62209e33a1e176d816609d69a2aebadc/src/model_benchmark_zoo/cross_junction.py).
- The original upstream package was **not executed**. Source default CAD constructors were mirrored locally, preserving separate source solid B-Reps. Their STEP files were generated and reimported as part of the local tests, but no original third-party STEP file was downloaded or admitted.
- `main` remains frozen to `f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94`. The experiments are isolated under `docs/research/nonmanifold-benchmark/` in draft PR #225.

## 1. Native kernel algorithm, evidence provenance and restrictions

The source input is a multi-body CadQuery assembly, not an already welded non-manifold surface graph. R3.C2 reconstructs a **bounded subset of its interface neighborhood**:

1. Keep main and arm solids separate. Identify source faces by their native face index and original body ID. Reject invalid source solids, penetrating positive-volume intersections and missing contacts.
2. For each intended main/arm contact, evaluate `BRepAlgoAPI_Common` on face pairs; accept an opposing-normal planar contact only when the smaller arm face lies **fully inside** the main face. Independently check source face distance using `BRepExtrema_DistShapeShape`; the input contact budget is **1e-12 source units**, separate from the **1e-8 output sewing tolerance**.
3. Use `BRepAlgoAPI_Cut` on the original host face, retaining the common contact subface and both residual wing faces. Require exactly two disconnected four-sided wing faces and native source area conservation. Reject hole, partial-overlap-on-both-faces, periodic and unbounded/complex trim cases rather than silently heal them.
4. Locate the arm's two exposed side faces through **original TopoDS edge/face incidence**, not a coordinate-based weld. Keep the paired host/arm face IDs on the common interface and the source face ID of each residual wing/arm exterior face.
5. Sew only these *five* source-derived four-sided faces per contact into a research surface complex; the source solids remain immutable. Collect the **actual** `TopoDS_IsSame` face-to-edge incidence graph after native sewing. Track `sewn_face_index` and the independent source-face provenance.
6. Parameterize each native rectangle by a planar bilinear map elevated to 16 bicubic poles. **Global BP control indices are interned by native TopoDS_Vertex/TopoDS_Edge identity**, including oriented interior edge samples, not by rounded coordinates. Per-face interior controls remain distinct. Four oriented control indices identify each common boundary.
7. Run a separate BP reader, de Casteljau evaluator, analytic native-rectangle oracle and Open CASCADE minimum-distance checks on each mapped source face. The independent audit rejects falsified source rights/meshing claims and corrupted control/side identity.

Native centroid signatures (rounded to nine decimal places) are used **only for checking which sewn face corresponds to which source-derived subface**, not to create or merge topological edges. This restricted mapping is not suitable for general CAD with geometrically repeated identical faces.

## 2. Measured T-Junction and Cross-Junction results

| Metric | T-Junction | Cross-Junction |
|---|---:|---:|
| Source solids | 2 | 3 |
| Original main-bar volume | 500 | 320 |
| Branch volumes | 250 | 128 each |
| Positive-area main/arm contacts | 1 | 2 |
| Contact subfaces + host wings + arm sides | 5 | 10 |
| All resulting faces planar quadrilaterals | Yes | Yes |
| Native TopoDS edges | 16 | 32 |
| Native edges with three distinct face users | 2 | 4 |
| Native edges with one face user | 14 | 28 |
| Valid assembled OCCT topology | Shell | Compound of two Shells |
| Bicubic BP patches (`p`, 16 indices each) | 5 | 10 |
| Unique indexed BP control vertices | 64 | 128 |
| Canonically shared 3-face BP side curves | 2 | 4 |
| Independent analytic BP samples | 245 | 490 |
| Native BRep interior face-distance samples | 125 | 250 |
| Max absolute analytic coordinate discrepancy | 3.552713678800501e-15 | 3.552713678800501e-15 |
| Max native BRep face distance | 1.3322676295501878e-15 | 0.0 |

**Area conservation:** In T-Junction, the host face has area 100; a 25-area interface and two 37.5-area wings cover it. In Cross-Junction each host face has area 80; a 16-area interface and two 32-area wings cover it. The exposed arm sides are area 50 each for T, and 32 each for Cross.

The two Cross-Junction contacts are at different Y planes and do **not** form one common four-way junction. Instead they produce four **separate triple-incidence edge curves**. The source code's CSG view may assign the same material to both arms, whereas this research sidecar intentionally preserves their **separate source body identities**. Material-interface consolidation is an open advisor decision.

**Important:** Standard sewing with `SetNonManifoldMode(False)` was observed also to retain triple edge incidences in these particular source split-face configurations. Therefore the sewing flag is **not used as evidence of success**; only native `TopoDS_IsSame` face-user multiplicity is accepted. This differs from the earlier four-sheet analytic case and must not be generalized without kernel/version-specific investigation.

## 3. Adversarial rejection and scientific interpretation

The bounded probe explicitly rejects or fails qualification for: source bodies separated by 1e-5, 1e-9, or 1e-10 (strict native source-distance gate, even when a fuzzy Boolean reports an overlap); overlapping-volume penetration of 0.01; branch height reduced to 80% (four-sided wing decomposition fails); source edge-only contact; branch face wider than the source host (both sides would need trimming); invalid or nonfinite dimensions; tampered BP with a recomputed SHA-256; corrupted side controls; invalid native BRep; false external-source admission; and false APMesh-mesh acceptance claims.

**Not supported:** arbitrary trimmed NURBS, curved partial-contact STEP, face holes, multiple arm contacts on the same original host face, imprecise/unverified units, arbitrary rotated faces, vertex-only junctions, nonmatching material-interface semantics, general-purpose patch fitting or topology healing. The 1e-12 source-distance and 1e-8 sewing bounds are experimental local thresholds, not universal geometric warranties.

## 4. Test results, reproducibility and stable hashes

Environment: Python 3.13.5; CadQuery 2.8.0; Open CASCADE through OCP 7.9.3.1; exact local source/test files. Commands executed:

```sh
python -m unittest discover -s docs/research/nonmanifold-benchmark/probes -p 'test_*.py' -v
python docs/research/nonmanifold-benchmark/probes/r3c2_native.py --case t_junction --output-dir build/research-r3c2
python docs/research/nonmanifold-benchmark/probes/r3c2_native.py --case cross_junction --output-dir build/research-r3c2
python docs/research/nonmanifold-benchmark/probes/r3c2_bp.py --case t_junction --output-dir build/research-r3c2
python docs/research/nonmanifold-benchmark/probes/r3c2_bp.py --case cross_junction --output-dir build/research-r3c2
python docs/research/nonmanifold-benchmark/probes/r3c2_audit.py --bp build/research-r3c2/t_junction.bp --sidecar build/research-r3c2/t_junction.sidecar.json --brep build/research-r3c2/t_junction_interface.brep
python docs/research/nonmanifold-benchmark/probes/r3c2_audit.py --bp build/research-r3c2/cross_junction.bp --sidecar build/research-r3c2/cross_junction.sidecar.json --brep build/research-r3c2/cross_junction_interface.brep
```

- The **19/19** new native-kernel/BP/adversarial unit tests passed in the local R3.C2 source directory.
- All **44/44** previous R2 and R3 planar/curved tests also passed in their existing research bundle, for **63/63 local tests across these two scopes**. This is NOT the project's production 75 CTest + Python regression and no APMesh execution was performed.
- Native STEP source assembly export/import for both cases preserved contact classification and reconstructed BP incidence. Native BRep output export/import preserved triple edges. Source shape face/edge/volume observations were unchanged before and after reconstruction.
- The four generated BP/sidecar/BRep/topology output categories were byte-identical over two independent local runs on each model.

| Artifact | T-Junction SHA-256 | Cross-Junction SHA-256 |
|---|---|---|
| BP input | `67679108f3d5cbef3886520f9eb47be2b3b0148a2df7efc95505f86a7be479b1` | `49f0880daadfc8ea0dd6ac685eeb2ec9aeb107dcb0d21205f03429e2198f1c68` |
| Source-provenance sidecar JSON | `cfd7eb9450591aa15d736d2da5adc3c934390e5cbd4e0264c1261b8d6d9992cf` | `e9fd120ddeada04accf33126b9b407553866bb683c65b18c350016d329dc7344` |
| Native reconstructed BRep | `1b52c82ee88fb2900344f18ed4eeb64df9b142126f9cd72f363e2639d9befcd5` | `48b2b4198ed2605cc5e14e5557db18b69cec128aa630747e25f5c2c67982d69e` |
| Source-to-subface graph JSON | `c0165c82475399664296114b2ee5c73b9aad8b9a4d7baa600d6d9f970531fa06` | `68e286c081993e76bc23df492b0ba7b898d8682ff57d7ecfd524ec2784370889` |

The BP and sidecar are author-generated research artifacts; they may be committed to the research directory. Full original third-party STEP files were NOT imported. Native BRep and visual PNG are delivered as separate local research artifacts, not as evidence of source ownership.

## 5. Stage disposition and next gate

**R3.C2 narrow control: PASS (two mirrored CAD recipes, source-derived partial four-sided decomposition, true native triple edge incidence and BP identity). Full R3: OPEN.** R4 has a bounded experimental precursor but no general CAD-to-BP tool. R5 TRI, QUAD/TRI, all-quad, anisotropy, historical regression and true external benchmark admission remain NOT RUN / BLOCKED.

Next: independent original-source rights/raw-hash review; extend partial face splitting to *both* faces and to non-rectangular/trimmed source surfaces with rigorous unsupported-case diagnostics; independent curve orientation/feature-graph oracles; controlled G1/G2 admission of one actual intended non-manifold original CAD asset. Only then consider full R4 and separate R5 meshing acceptance/regression. No review or merge authorized based solely on this control.
