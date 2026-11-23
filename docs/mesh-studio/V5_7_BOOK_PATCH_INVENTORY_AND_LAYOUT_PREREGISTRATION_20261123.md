# Mesh Studio V5.7 — original source Book patch-slot audit and pre-registered print layout

**Date:** 2026-11-23. **Status: original certified V5.2 source-artifact inspection completed; new editorial figures NOT GENERATED or qualified.** This documentation-only preregistration is based on original certified V5.3 source code `38e03cd1de260a1791a9cb6e176181067d4c94bb`, **not** on the large experimental Studio research PR, later supply-chain branches or `main`. No original AFT/Adapter/native C++ numerical rule, accepted TRI or original journal PDF has been altered.

## 1. Exact historical original scientific inputs reviewed

Downloaded and reopened the existing certified V5.3 original C++-source derived artifacts:
- [V5.2 original SVG/scene ZIP artifact #14762761649](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/45043785743/artifacts/14762761649), from successful [GitHub Actions #45043785743](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/45043785743). It contains `v52-native-accepted-uv-publication/{book,eistute}-accepted-step1-uv.svg`, `manifest.json` and original `r2720-native-accepted-scene.json`.
- [V5.3 original two-page true-vector PDF artifact #14762946308](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/45043785743/artifacts/14762946308). This **existing** PDF remains immutable historical evidence, originally 133,746 bytes, SHA256 `4b2e0d75fc306fbaf856bfc25c217758d1707604dfb2260f73fb0ddf966b74e7`. No new PDF is claimed here.

Reopened XML namespace-aware SVG trees, 28/4 source `<g>` panels, and independently recomputed exact raw SVG byte hashes:
- Book SVG: **1,980,092 bytes**, SHA256 `8d639313d8ade37fd4a8b0347fe5787d5d2db15296f0d3e6c6844e6abb39b248`;
- Eistute SVG: **536,961 bytes**, SHA256 `c3757577ddc6cc147a029303be4bbe60fa0a87e4063829257ef7f7d91764bd66`.

This is a **secondary audit of previously native-certified artifacts**; parsing the CI ZIP **does not itself recompile and reauthenticate the original C++ runtime**, certify arbitrary uploaded SVGs, or create a new accepted adaptive epoch. The original [V5.2 scientific provenance study](V5_2_ORIGINAL_ACCEPTED_NATIVE_TRI_VECTOR_RESULTS_20261120.md) and [V5.3 source/PDF audit](V5_3_ORIGINAL_ACCEPTED_TRI_VECTOR_PDF_RESULTS_20261122.md) define the original source-side controls.

## 2. Original observed per-slot counts and identity semantics

| Original accepted step-1 input | Source chart slots | Accepted TRI per slot | Original source sample markers per slot | Total TRI | Total point markers |
| --- | ---: | ---: | ---: | ---: | ---: |
| Book | **28** | **152 in every slot** | **13 in every slot** | **4,256** | **364** |
| Eistute | **4** | **292 in every slot** | **11 in every slot** | **1,168** | **44** |

**Crucial identity distinction:** in both original vector SVGs, every `<g>` chart reports `data-original-native-patch-id="0"`, whereas each group has a **different `data-original-patch-slot`** (Book 0..27 and Eistute 0..3). The native patch ID is not a globally unique patch-slot identifier in this representation. Therefore the valid source identity for a triangle is the **composite key `(accepted_step, patch_slot, element_slot, native_element_id)`**, alongside the original native node IDs and three original UV doubles. Do not collapse charts by `native-patch-id=0`, claim 28 distinct source-global native patch ID values, or infer physical C++ node welding from equal XYZ. The source-side raw NDJSON re-audit remains authoritative for native ownership.

**Scientific selection consequence:** all 28 Book patches have **exactly the same triangle count and point-marker count**, so selecting smallest/largest/median patch by these counts is meaningless; such a rule cannot justify scientific representativeness or geometric diversity.

## 3. Prospective, reproducible **editorial** recipes (not yet produced)

### Complete Book appendix (coverage, not LOD)

- Preserve the existing certified full 28-panel Book page *unchanged* as a source-attested overview.
- Propose a **seven-page, 2×2 panel** appendix, four original Book slots per page, ordered `[0,1,2,3]`, `[4,5,6,7]`, `[8,9,10,11]`, `[12,13,14,15]`, `[16,17,18,19]`, `[20,21,22,23]`, `[24,25,26,27]`. This gives exactly **608 original native TRI and 52 source sample markers per page**, **4,256 TRI/364 sample markers globally**, each composite face key and source patch slot **exactly once**.
- Render a new independent deterministic true-vector PDF at a target print size set by the venue/advisers; no arbitrary change to UV or physical C++ node identities. Reposition source-attested chart geometry and transform all native polygon paths/point markers consistently; preserve original sample/face/patch data attributes in an immutable page-inventory receipt. Do **not** pass a raster crop off as a vector illustration.
- Audit new actual PDF physical `MediaBox`, vector paths/filled triangles, embedded font bytes, no raster/XObjects/inline image, printed label size, title/legend hierarchy and every original source face/marker expected point. Do **not** claim label improvement before producing and measuring it.

### Small Book primary-paper example (source-order coverage only)

**Pre-register demonstration slots `[0,9,18,27]`** by rounding the four equally spaced endpoints of the ordered range 0..27. Every selected chart has 152 original TRI/13 original source markers; combined **608 TRI/52 markers**. This rule is *deterministic coverage of source slot order*, not proof of typical geometry, quality or statistical representativeness. Caption must state **"four evenly sampled source patch slots from the original 28-slot accepted TRI Book mesh"** and refer to the complete appendix for all 28. Do not call the subset "most representative" or extrapolate its metrics to the unshown 24 slots.

## 4. Required separate verification before calling an editorial output complete

1. A venue/adviser-approved role and physical layout: SIBGRAPI or journal guidelines, exact final column/page width, acceptable minimum font, strokes, panel/caption terminology, and whether primary text uses an example + appendix.
2. Same-run original C++ accepted step-1 raw postcommit NDJSON and source-side manifest revalidation **before** any regenerated figure (a matching SVG+manifest alone is insufficient source attestation).
3. Independent negative controls for repeated/missing patch slot, duplicated/missing compound face key, malformed/altered original native UV, forged source/LOD, incorrect marker identity/order, raster injection, missing font, altered physical print dimensions.
4. Quantitative print/editorial gate on the actual newly generated vector bytes; the historical Book 190×160 mm overview's smallest extracted font is **4.90 pt** and the historical Eistute 178×140 mm figure's is **6.67 pt**. Neither an arbitrary static label threshold nor the proposed layout is asserted as an official venue criterion.
5. Document the original scientific boundary in final captions: these figures show original C++ globally accepted **TRI step [1]** in **patch-local UV**, not physically welded multi-patch seams, continuous CAD error, all-QUAD/anisotropic solver improvement or two accepted geometric LOD epochs.

**Decision:** V5.7 inventory and objective editorial selection protocol are grounded in the actual original certified SVG artifact. **New publication-ready PDF/appendix output, reviewer signoff and venue typography are OPEN.** PR remains DRAFT. Main scientific R2.8 LOD qualification stays **BLOCKED**; original native algorithms, acceptance criteria, and previously archived V5.3 PDF are untouched.
