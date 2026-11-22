# Mesh Studio V5.3 — preregistered source-accepted TRI article PDF recipe

**Registered before implementation**, 2026-11-22. This is an isolated **document/publication** continuation of V5.2; no new original C++ instrument, CAD algorithm, numerical acceptance threshold or VTK default changes are authorized.

## Question

Can the two true-vector V5.2 original Eistute and Book **globally accepted original TRI step-1 patch-local UV** SVGs be transformed into one reproducible, physically sized two-page, font-embedded **vector-only PDF**, with independently checked identities and no fabricated welded-node or LOD interpretations?

## Source/acceptance contract (must fail closed)

Input is only the **same-run** original compiled C++ accepted postcommit source evidence and source-bound V5.2 publication. In CI, run the existing original `native_accepted_scene` auditor on raw C++ accepted NDJSON, rederive the original V5.2 SVGs and their manifest, then build the PDF. Never trust a user-supplied SVG, browser preview, unverified standalone manifest, staged candidate or previously cached file as self-attesting source. The PDF builder must check original V5.2 SVG SHA, numeric UV double attributes, original source model+config+NDJSON SHA, figure patch/face/node keys, accepted step and unqualified flags by calling the already qualified V5.2 independent audit *before* PDF rendering.

## Exact visual and document protocol

- Fixed **two pages**: page 1 original Eistute figure **178 × 140 mm**, page 2 original Book figure **190 × 160 mm**, exactly matching the vetted V5.2 SVG's physical dimensions. Preserve separated local UV charts and source shared-curve sample **points**; no globally welded atlas.
- Translate only explicitly supported SVG primitive tags `rect`, `polygon`, `circle`, `text`, `g`, `title`, `desc` to PDF-native vector paths or text. Reject `image`, script, external link, shader, `foreignObject`, unexpected paths, CSS injection, href and namespaces. No page-sized raster image or screen capture.
- Use a single deterministic, locally bundled, PDF-embedded font (DejaVu from pinned research matplotlib) for searchable text. No CDN/system-dependent font lookup. Enforce fixed numeric units, no ambient creation timestamps, explicit ReportLab invariant mode and fixed page order.
- Preserve every one of the **1,168 Eistute and 4,256 Book original native triangle** polygons; no dropping/culling/normalization. Original face/source UV identities remain in the **independently reverified** V5.2 SVG/manifest and the accompanying new PDF recipe JSON; PDF geometry is independently compared to all 5,424 source face polygons by Cartesian path coordinate, plus expected counts of all 408 source sample markers. Do not pretend PDF page content by itself carries native C++ IDs in the shape object.
- PDF output `accepted-original-tri-uv-article.pdf` with stable SHA, companion `recipe.json` listing source and output hashes, per-model original source/config/NDJSON and V5.2 SVG hashes, dimensions, precise page/shape count, PDF library/revision, explicit `scientific_lod_qualified=false`, `native_welding_certified=false`, `continuous_geometric_error_bound_certified=false`.
- Independent audit opens the **actual PDF bytes** (not source code's intent) with two independent parser families `pypdf` for page box/resources/inline-image operators and `PyMuPDF` for native vector paths, actual page dimensions and font existence/embedding; verify every source face mapped PDF vector path against same-run audited original source UV polygon with physical coordinate tolerance well below printed resolution; verify no image XObject or inline raster, and no unexpected PDF extra pages and all source sample circle paths.
- Optional actual raster preview is a **validation-only render**, not included in delivered PDF.

## Adversarial tests and stop conditions

Positive deterministic exact-input rerender identical PDF/recipe bytes. Reject missing raw C++ acceptance evidence; modified original SVG or manifest SHA; forged second step/LOD; missing/duplicate/changed native face, node, UV or source curve sample; XML script/foreign content; damaged PDF vector geometry, raster XObjects, inline images, wrong page dimensions, missing embedded fonts or wrong document source digest. Python unit fixtures are synthetic **tests of protocol only**, not scientific original C++ observations. Same-run actual native CI must build/reopen the report, store a raw artifact, and independently execute PDF path auditing; do not declare success if actual C++ acceptance fails.

## Boundaries

A two-page research figure is **not** a published paper, proof of continuous CAD error, physically welded C++ source seam, anisotropic/all-QUAD comparison or scientific multilevel LOD. Original C++ source still has only globally accepted **step [1]** per original model, and R2.8 remains BLOCKED. PRs #239/#244 remain DRAFT/unmerged, no main merge/tag/release.

**Future after finite V5.3:** independent article-layout review, targeted review of PR #244, deterministic lockfile generation and CI-fast/scientific lane design. Do not open another redundant original C++ observer merely to add documentation.
