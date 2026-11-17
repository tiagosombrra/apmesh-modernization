# Mesh Studio R2.7.15 — native sampled shared-curve geometry, UV and node-ID audit

**Date:** 2026-11-17. **Research scope:** original real Eistute and Book
serial TRI accepted snapshots, with no scientific generator changes.
**Review:** draft PR #239; branch
`feature/mesh-studio-r27-bvh-20261116`, not `main`.

## Research question

R2.7.14 qualified the canonical original curve-to-patch **incidence
graph**. Sharing a source curve is not proof that generated TRI
interfaces use identical boundary samples, that their XYZ coincide,
or that their nodes share a physical allocation. R2.7.15 tests the
sampled boundary geometry and original **logical** native node IDs,
rather than promoting a source-curve graph into a physical welding
claim.

The original C++ `src/adapter/adapter.cpp` explicitly maps its four
local patch sides to UV equations `v=0`, `u=1`, `v=1`, `u=0`.
The source `PatchCoons::IsCurveReversed` flag maps local curve
parameter `t` to canonical `1-t` for reversed incidences. The
existing Adapter copies boundary samples into patch-local submeshes
while retaining their native node IDs; equal IDs may correspond to
**different C++ node objects**. In particular, `native_node_id`
is not evidence of global pointer sharing.

## Audited algorithm

`tools/mesh_studio/native_seam_samples.py` first revalidates the
**actual original native accepted** R2.7.12 retained NDJSON, original
source summary and all SHA-256 pins via independent existing parsers.
It does not consume OBJ face ordinals or synthesize faces.

For each canonical original source curve owned by more than one
source patch in the R2.7.14 graph, it:

1. Selects **real accepted TRI face edges** whose two source UV
   vertices lie on the corresponding original patch side, using an
   explicitly stated UV tolerance `1e-9` in normalized parameters.
2. Recovers canonical curve parameters using the native incidence
   orientation, and keeps the **original native node IDs and XYZ**.
   Repeated native IDs with inconsistent original per-corner UV/XYZ
   are rejected.
3. Builds the set of original local boundary edges. It independently
   reports repeated edges, zero-length-in-parameter edges, duplicated
   parameter nodes, missing endpoints, and incomplete/branched edge
   coverage. Recovered ordered chain must have endpoints near
   `t=0,1` and exactly the edges of consecutive recovered nodes.
4. Compares all pairs of distinct owning patches for equal sample
   counts, canonical parameter differences, original native logical
   node IDs and Euclidean XYZ displacement. The explicit XYZ rule is
   `distance <= 1e-9 + 1e-9*(local two-side XYZ bounding-box diagonal)`, not a
   proof that a common CAD curve has zero continuous error.
5. Marks `sampled_uv_xyz_logical_id_concordance_observed=true`
   **only when both native side chains are complete and all
   corresponding observed samples agree** within the declared
   tolerances. Missing/invalid chains remain nonconcordant and are
   recorded with diagnostics rather than omitted.
6. Emits exact observed counters and per-source-curve diagnostics.
   The output explicitly retains
   `physical_node_welding_certified=false`,
   `continuous_geometric_error_certified=false`,
   `cross_epoch_lineage_certified=false` and
   `scientific_lod_qualified=false`, regardless of sampled agreement.

Matching sampled **logical IDs, coordinates and UV** is valuable
evidence for conforming observed boundary discretizations. It does
**not** establish shared in-memory native pointers, globally welded
mesh topology, full nonmanifold sheet adjacency, analytically
continuous Bézier geometry, or cross-epoch face descent. A difference
in native node IDs with coincident XYZ is reported as an **ID
discrepancy**, not automatically repaired through coordinate welding.

## Test and native execution gates

`test_native_seam_samples.py` exercises synthetic fixtures only:
all four original UV side equations, direct/reversed incidence,
matching observations, deliberate XYZ drift, different native IDs
at equal XYZ, incomplete/duplicated boundary edges, inconsistent
native-ID geometry, tolerance limits and deterministic output.
These isolated tests are not scientific generator evidence.

The native-lineage CI job runs the real compiled serial Eistute/Book
GeneratorAdaptive first, captures exact original accepted source-face
NDJSON, rechecks bytes and source metadata, and then creates
`build/r2715-native-sampled-seams.json`. The 14-day GitHub Actions
artifact is named `mesh-studio-r2715-sampled-seams-<commit>`.
Numerical OFF/ON parity and independent Linux/Windows scientific
regressions continue to run without any source acceptance threshold
change.

Reproduce after real R2.7.12 native capture:

```bash
python -m unittest tools.mesh_studio.test_native_seam_samples -v

python -m tools.mesh_studio.native_seam_samples \
  --directory build/r2712-native-evidence \
  --output build/r2715-native-sampled-seams.json
```

**Admission rule:** mark this step PASS for *sampling audit execution*
only when its exact new CI source SHA, all four jobs, actual native
R2.7.15 report and denominator counters have been observed. A
successful audit is not automatically evidence that all native
seams are conforming. The numbers and any source discrepancies
must be reported separately.

**Independent blockers:** second genuinely accepted adaptive epoch per
original model, independently validated cross-epoch face/curve
ancestry, structural node welding/nonmanifold mesh-sheet proof,
continuous source-surface error bounds, real physical Windows GPU
present/RSS/VRAM measurements. Therefore R2.8 scientific LOD stays
**BLOCKED**, VTK picker stays default, experimental BVHs stay
opt-in/bounded, and PR #239 stays draft/unmerged. No generator
policy change, default-on switch, tag or release.

## Original native experiment: first qualification and negative result

[**GitHub Actions #44159057629**](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/44159057629)
at exact audited implementation `fcf345ff3870ce6239b7b693d900f409bbb68516`
finished **all four jobs SUCCESS**: original compiled C++ Eistute
and Book source capture, native raw NDJSON revalidation, R2.7.14
adjacency, new R2.7.15 seam audit, OFF/ON parity,
independent Linux and Windows Python regressions and Chromium suite.
The native scientific job's exact
`R2715_ORIGINAL_NATIVE_SAMPLED_SEAMS` log reports:

| Native original accepted step 1 | Source shared curves | Original patch-owner pairs checked | Strict sampled concordance |
| --- | ---: | ---: | ---: |
| Eistute (4 patches / 13 source curves) | 1 | 6 | **0 / 6** |
| Book (28 patches / 85 source curves) | 1 | 378 | **0 / 378** |

**Interpretation:** every comparison failed to satisfy **all**
conditions *simultaneously*. The aggregate alone does **not** identify
whether missing boundary edge-chain coverage, sampled canonical t,
XYZ displacement or logical native node-ID differences are responsible;
it is therefore invalid to infer a proven CAD discontinuity or a
physical nonmanifold welding defect merely from 0 concordant pairs.
The audited 4/28 patch original source-curve graph and original
native OFF/ON numerical file equality remained preserved.

The R2.7.15 follow-up adds source-hash-preserving, **independent
per-condition** counters, bounded failure examples and translation-
invariant XYZ tolerance using each sampled seam's original local
bounding-box diagonal instead of absolute world position. A second
CI run must qualify these diagnostics before identifying a cause.
This is an observational diagnostic refinement, not a new generator
or geometry algorithm. The scientific evidence is **negative for the
strict combined sampled-concordance hypothesis** in the initial
observed run, **not a proof that every pair differs geometrically**.

R2.8 remains BLOCKED; no main merge, tag, release, default BVH switch,
source geometry correction or C++ scientific policy change.


### Final R2.7.15 diagnostic qualification (2026-11-17)

[**All-four-jobs-success CI #44160223365**](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/44160223365)
at exact implementation source SHA
`2f9c36756a6ddd96b6f6b81afe01826b598de339`
passed the compiled original native serial generator/lineage audit,
Linux and Windows scientific regressions and real Chromium
contracts. The independently recompiled C++ OFF/ON control again
matched original scientific outputs Eistute **21/21** and Book
**17/17** by raw bytes.

The exact real original `R2715_SAMPLED_SEAM_FAILURE_BREAKDOWN`
native job marker isolates the disagreement:

| Measured condition on accepted native TRI step 1 | Eistute | Book |
| --- | ---: | ---: |
| Original shared-source-curve patch-owner comparisons | 6 | 378 |
| Full original UV boundary chains | **6 / 6** | **378 / 378** |
| Equal original sampled node counts | **6 / 6** | **378 / 378** |
| Canonical t within stated tolerance | **6 / 6** | **378 / 378** |
| Original XYZ within stated tolerance | **6 / 6** | **378 / 378** |
| Original *native logical* node IDs equal | **0 / 6** | **0 / 378** |
| Combined all-conditions concordance | **0 / 6** | **0 / 378** |
| Individual original source-patch side chains complete | **4 / 4** | **28 / 28** |
| Original per-patch seam sample count | **11** | **13** |
| Source-side structural edge diagnostic codes | **none** | **none** |

The first three logged pairwise examples for **each** model had
max paired canonical-t delta **0** and max paired XYZ delta **0.0**,
but the summary does not certify an exact-zero maximum for all
384 comparisons; it certifies all samples **within explicitly
declared tolerance**. In this original experiment **the only
pairwise criterion not passed is native logical ID equality**,
not a detected sampled geometric discontinuity. Source-oriented
XYZ/UV equivalence is not physical C++ node-pointer welding or
analytic surface continuity.

The source geometry is **not changed**. Native node IDs are **not
silently unified**. This supports R2.7.16's independent original
source-scoped seam-sample association, not a topology rewrite.
R2.8 remains BLOCKED because there is still just one accepted
native epoch per model, no verified descendant mapping and no
continuous geometric LOD bound. Physical Windows GPU/RSS/VRAM
qualification is a separate open task.
