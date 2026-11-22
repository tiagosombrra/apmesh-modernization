# Mesh Studio V5.3 — original accepted Eistute/Book two-page scientific vector PDF

**Date:** 2026-11-22. **Study scope:** reproduce actual source-accepted C++ TRI step-1, independently audited native UV vector paths, not scientific LOD. **Prospective method:** [V5.3 preregistration](V5_3_PREREGISTERED_ORIGINAL_NATIVE_TRI_VECTOR_PDF_20261122.md). PR #239 remains DRAFT/unmerged. Original C++ acceptance policy, CAD model inputs, source FFI and default VTK/BVH picking remain unchanged.

## Source chain and strict acceptance

Original compiled serial C++ `GeneratorAdaptive` emitted actual globally accepted postcommit native TRI `r2712-*.ndjson` for original Eistute and Book. V5.2 independently reopens that real C++ source, postcommit IDs, source patch/curve/corner identity and original C++ acceptance report, and exports per-patch native UV polygons as true SVG vector. V5.3 never reads an arbitrary uploaded file as proof of acceptance: `tools/mesh_studio/native_accepted_vector_pdf.py` **CLI unconditionally calls `audit_accepted_native_publication(original_directory, original_scene, v52_dir)` first**, which in turn rechecks original raw native NDJSON and independently regenerates every original SVG face/UV, before rendering or auditing the PDF.

The PDF preserves the actual accepted `(patch_slot, element_slot, native_element_id, native_node_id, UV)` geometry of the **5,424 original C++ TRI faces**, across **4 Eistute and 28 Book local UV patches**, with **44 + 364 original source-curve sampled corner markers**. Their identities and SHA receipts remain in the original C++ source/verified V5.2 SVG and the separate deterministic figure recipe; PDF paths are independently compared to each UV polygon's physical coordinate in the two pages. **A PDF path is not claimed to embed a persistent native C++ pointer, nor are the sampled markers welded nodes.**

## Physical publication output and method

| Real accepted original source | Figure page | Original TRI | Source UV panels | Sample markers | Page physical dimensions |
| --- | ---: | ---: | ---: | ---: | --- |
| Eistute | 1 | **1,168** | **4** | **44** | **178 × 140 mm** |
| Book | 2 | **4,256** | **28** | **364** | **190 × 160 mm** |

- PDF-native paths are rebuilt only from white/background patch rectangles, original `polygon` faces, source `circle` sample markers and searchable text in the **original accepted UV SVG**; no image/raster/scene screenshot is pasted into the document. Original per-triangle UV double attribute and source identity must first match the raw accepted C++ lineage under V5.2 audit.
- SVG's `xMidYMid meet` aspect-preserving transform is reproduced, accounting for figure page margins **without stretching patch UV**. Source polygon vertices and sampled node circle position/radius are checked against decoded PDF physical path geometry with **0.003 pt** tolerance.
- Explicit deterministic font `DejaVuSans` is loaded from the **pinned matplotlib package**, embedded/subset into both PDF pages, no external CDN or host font dependency. `ReportLab Canvas(invariant=1)` emits stable creation metadata and deterministic byte-exact PDF given the same original source SVG; the complete PDF and replayable `recipe.json` carry original source/file hashes.
- Independent PDF inspection uses **pypdf** to parse original PDF page boxes/resources and forbid inline image/external `Do` operations, plus **PyMuPDF** to inspect each actual path's vertices, source circle centers, native PDF font embedding, page dimensions, and absence of image XObjects. This is an inspection of **the emitted PDF**, not a count of input SVG polygon strings.
- Source PDF rendering locally from the already CI-certified original V5.2 same-run archive has produced **133,746 bytes**, PDF SHA-256 `4b2e0d75fc306fbaf856bfc25c217758d1707604dfb2260f73fb0ddf966b74e7`; independent local actual-PDF audit matched all **5,424 face paths** and **408 original marker paths**, both page sizes, one embedded source font per page and zero image XObjects/inline images. The source C++ archive's Eistute/Book raw NDJSON SHA matched **exactly** the V5.2 original accepted figure source claims. A second local rendering returned **identical PDF bytes and recipe**. This local validation is useful source-bound preflight, not a substitute for the complete newly compiled V5.3 CI.

## Reproducibility and negative controls

Generate only from the exact same-run `build/r2712-native-evidence` that qualified the source C++ figures:

```bash
python -m tools.mesh_studio.native_accepted_vector_pdf --mode export \
  --original-directory build/r2712-native-evidence \
  --scene build/r2720-native-accepted-scene.json \
  --v52-dir build/v52-native-accepted-uv-publication \
  --output-dir build/v53-original-native-vector-pdf

python -m tools.mesh_studio.native_accepted_vector_pdf --mode audit \
  --original-directory build/r2712-native-evidence \
  --scene build/r2720-native-accepted-scene.json \
  --v52-dir build/v52-native-accepted-uv-publication \
  --output-dir build/v53-original-native-vector-pdf
```

The independent `audit` phase reopens the raw C++ sources and source-native V5.2 SVG, rerenders the PDF to **byte equality**, and audits the actual 5,424 PDF face and 408 native marker paths. Synthetic unit fixtures only exercise the rejection logic: a missing raw C++ source, forged second accepted step/LOD, altered source SVG SHA, raster/executable SVG, missing source markers, raster PDF content, wrong PDF page sizes, extra false source-face graphics and added unembedded fonts must fail closed.

## CI qualification (honest status)

The exact V5.3 implementation includes `native_accepted_vector_pdf.py`, `test_native_accepted_vector_pdf.py`, and a same-run C++ workflow lane that invokes `--mode export` **and** `--mode audit` and archives the original source figure recipe/PDF. **Do not claim new CI success until all four jobs finish**. The previous [V5.2 native source qualification #44820514441](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/44820514441) remains independently 4/4 PASS but does not certify the later V5.3 code.

V5.3 new CI source implementation SHA is `517b0fa8f7ca0b8600cf05372a03e4034688a8fd`; [candidate Actions run #45043363596](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/45043363596). If any rejection or physical-source PDF mismatch occurs, preserve the negative in this report and correct only the defective scope; never silently change the original acceptance policy to make the publication succeed.

## Scientific interpretation and next work

These are **one globally accepted original TRI step per model**, not LOD pairs: no second accepted source epoch, physical cross-patch C++ node ownership/welding proof, continuous curved surface error bound, independent GPU workload, all-QUAD quality or anisotropic native evaluation is established. The PDF demonstrates **provenance-controlled publication of original accepted patch-local parameterization**, not geometric equivalence or convergence.

Once actual original-source V5.3 CI is green, focus on a reviewable documentation/figure PR slice, deterministic dependency locks and fast-versus-scientific CI lane plan. No new instrument-only R2.7 stage or production merger is authorized.
