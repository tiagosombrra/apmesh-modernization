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

## Certified original C++ source PDF — exact 4-job CI

**PASS at exact implementation code SHA `38e03cd1de260a1791a9cb6e176181067d4c94bb`**, [GitHub Actions #45043785743](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/45043785743) **4/4 SUCCESS**:

| Independently scoped CI lane | Outcome |
| --- | --- |
| Scientific regression Linux 24.04 | **548 tests executed, 4 expected environment/optional skips; PASS** |
| Scientific regression Windows 2022 | **548 tests executed, 10 expected skips; PASS** |
| Actual serial original C++ `GeneratorAdaptive` acceptance and numerical parity | **PASS** — real Eistute and Book postcommit source, genuine step-1 acceptance, all original retained identity/gate observer controls |
| Same-run source-native 2-page PDF export, raw-NDJSON re-audit, 5,424 original UV PDF vector path comparisons, 408 circle comparisons and PDF media/font/raster audit | **PASS** — source-faithful original C++ published figures |
| Hosted Chromium original accepted TRI visualization and negative browser contracts | **63 tests passed / 5 intentionally skipped; PASS**; **no physical workstation GPU/VRAM certification** |

**Reproducible exact PDF:** original accepted step-1 figures from each same-run independently source-validated C++/V5.2 artifact produce **133,746 bytes** with PDF SHA-256 `4b2e0d75fc306fbaf856bfc25c217758d1707604dfb2260f73fb0ddf966b74e7`. Native output is identical byte-for-byte to the independently locally verified PDF and across the **two separate earlier original C++ Eistute/Book V5.2** regenerations. The source V5.2 scene receipt/manifest stays run-specific where original C++ stderr hashes differ, but the displayed figure geometry and PDF remain identical. Recipe records **ReportLab 4.4.9**, stable invariant PDF, DejaVuSans font embedding, physical sizes, SVG aspect-preserving transform and source NDJSON/model/config/SVG/PDF hashes.

- [Original V5.3 CI PDF/recipe/manifest artifact #14762946308](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/45043785743/artifacts/14762946308): **114,064-byte original ZIP**, exact ZIP SHA-256 `1f8d206c978c29e3fc479299c1c0326e490bada79fef12a88584b5ca2fc8010a`. The raw native PDF inside remains SHA-256 `4b2e0d75fc306fbaf856bfc25c217758d1707604dfb2260f73fb0ddf966b74e7`; accompanying recipe SHA-256 `9b9c58ad948428366ca5804af6e364f3985ad16a01f240a136feffffae4f742e`.
- Exact same-run original postcommit C++ native sidecars and earlier source SVG figures are retained independently under the **same CI run SHA**, not substituted with an arbitrary old/native or model path. To prevent artifacts expiring from undermining reproducibility, the first-party research archive also combines these **same-run raw C++ records**, accepted original scene, SVGs, scientific PDF and JSON receipts into one **14-file self-contained original-source replay ZIP**, **897,442 bytes**, SHA-256 `18f16c32a862d870c23b6bbbb8498fbb7d51da871a202a010a2840055525a0c6`. Each of its 13 data entries was rehashed; it includes a Portuguese reproduction README and does not assert scientific LOD.
- The unmodified original 114,064-byte GitHub ZIP and the 897,442-byte complete replay bundle were saved into the existing **private** Google Drive `Doutorado/DOUTORADO_APMESH_ACOMPANHAMENTO/05_Experimentos_e_Resultados`. Both were downloaded back with matching original ZIP SHA-256. Personal Drive URLs are deliberately omitted from public repository source documents.
- **PDF delivery caveat:** some standalone PDF file-transfer/preview layers reserialize document bytes and can alter its SHA without changing displayed vector geometry. Do not treat such a reserialized preview PDF as byte-exact scientific output. Use the original **ZIP** above to recover/attest the untouched `accepted-original-tri-uv-article.pdf` and `recipe.json`.

### Recorded CI harness failure and bounded correction

Initial V5.3 source candidate [#45043363596](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/45043363596) **failed only the new native PDF creation step** with `ModuleNotFoundError: No module named 'reportlab'`: the original-native job had not historically needed PDF libraries because original V5.2 only used standard-library SVG output. An intermediate direct-requirements file commit [#45043707256](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/45043707256) similarly ran before the workflow was updated to install it. The actual source-native acceptance and Python scientific regressions had passed; there was no geometric/numerical failure. Added minimal fixed `requirements-native-pdf-ci.txt` (ReportLab, pinned matplotlib-font, pypdf, PyMuPDF) to the **native** workflow with pip cache, explicitly avoiding the large VTK/OpenGL stack. The final exact 4/4 run above re-executed the entire original source/CI with this correction. Original C++ model, threshold, accepted step and exported source TRI faces were unchanged.

**Review slice:** [DRAFT PR #245](https://github.com/tiagosombrra/apmesh-modernization/pull/245), exactly **6 changed files** against the frozen [V5.2 PR #244](https://github.com/tiagosombrra/apmesh-modernization/pull/244) review branch, not the production `main`. Monolithic experiment PR #239 remains DRAFT/unmerged. Only documentation is updated after the fully tested code SHA; no merge, tag, publish or release.

## Scientific interpretation and next work

These are **one globally accepted original TRI step per model**, not LOD pairs: no second accepted source epoch, physical cross-patch C++ node ownership/welding proof, continuous curved surface error bound, independent GPU workload, all-QUAD quality or anisotropic native evaluation is established. The PDF demonstrates **provenance-controlled publication of original accepted patch-local parameterization**, not geometric equivalence or convergence.

V5.3 original-source article PDF and the small six-file review slice are now **certified/completed for this bounded publication goal**. Next prioritize deterministic direct/transitive dependency locks, fast-vs-scientific CI lane separation, physical workstation validation and independent academic review of figure layout/legibility. No new instrument-only R2.7 stage or production merger is authorized.
