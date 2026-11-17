# Mesh Studio R2.7.14 — original accepted source-curve adjacency audit

**Date:** 2026-11-17. **Review:** draft PR #239 on isolated
`feature/mesh-studio-r27-bvh-20261116`, still unmerged.
**Scope:** inspect the already retained **real original native TRI accepted**
face/patch/curve snapshots from R2.7.12. No generator policy, OBJ
exporter, C++ numerical flow, web selector, LOD geometry or rendering
implementation is modified.

## Why this is a separate research gate

The real native post-commit sidecars already prove that individual TRI
faces belong to specific original source patches and report each patch's
four ordered source-curve incidences, canonical original curve slots,
native curve IDs, and original orientation flags.

**A shared original curve pointer is not evidence of welded physical
nodes.** Two neighboring surface sheets may share an original geometric
curve without sharing identical adapted boundary discretization or node
ownership. The former is **source topology**; the latter is **mesh
topology**. Likewise, a native element ID is snapshot-local until
cross-epoch descendant identity is established independently.

This stage therefore computes a read-only **source ownership graph**
without inventing cross-patch or cross-epoch geometric correspondences.

## Source-preserving execution contract

`tools/mesh_studio/native_source_adjacency.py`:

1. First re-runs R2.7.12's independent retained-evidence audit,
   including actual NDJSON byte SHA-256, source-bound acceptance summaries,
   all original patch/curve/face records, exact retained filenames and
   originally accepted model step numbers.
2. Reopens each authentic original accepted NDJSON, validates every
   record with the existing fail-closed native parser and checks its
   digest and step against the original retained native summary.
3. Indexes the **canonical source curve slot** to all observed
   `(patch_slot, edge_slot, reversed, native_curve_id)` incidences.
   The graph has one source curve row per original source registry curve.
4. Classifies each source curve as belonging to exactly one, exactly
   two, or three-or-more distinct source patches. Repeated incidences of
   the same curve inside a single patch are explicitly reported rather
   than silently counted as independent owners. Each pair of owners
   is recorded with its original shared curve slots.
5. Audits cross-patch native curve-ID consistency. The native curve's
   reported observer count is **recorded as a diagnostic discrepancy**
   where it differs from the observed distinct patch-owner count, since
   it is not an independent proof of welding or correct source topology.
6. Emits a source-hash-pinned JSON. Fields explicitly state
   `shared_curve_geometry_or_welded_node_continuity_verified=false`,
   `cross_epoch_face_curve_descendants_verified=false` and
   `scientific_lod_qualified=false`. No implicit identity matching
   by OBJ face ordinal, native face ID across steps, rounded XYZ,
   UV boundary proximity or patch display ID is allowed.

The Python unit suite `test_native_source_adjacency.py` contains
**synthetic contract tests only**, for a two-owner graph, a
three-owner source curve, within-patch curve repetition, observer-count
disagreement, conflicting original curve IDs, missing source slots and
deterministic ordering. They do **not** validate a scientific mesh
or qualify physical non-manifold topology.

The isolated native CI job now runs the graph audit only **after**
successfully running the original instrumented serial C++ Eistute and
Book generators and fully validating their retained byte-exact native
face/patch/curve sidecars. Its JSON receipt is a separate 14-day
Actions artifact, not a replacement for the original source evidence.

## Reproduction and expected evidence

After reproducing R2.7.12 native captures for both original models in
`build/r2712-native-evidence`:

```bash
python -m unittest tools.mesh_studio.test_native_source_adjacency -v

python -m tools.mesh_studio.native_source_adjacency \
  --directory build/r2712-native-evidence \
  --output build/r2714-source-adjacency.json
```

The original **model dimensions**, already source-verified by R2.7.12,
are Eistute 4 source patches / 13 source curves and Book 28 source
patches / 85 source curves. Each accepted snapshot must independently
report its source graph; **do not preassign a measured shared-curve or
nonmanifold count before the corresponding actual CI receipt exists**.

Scientific R2.8 admission remains **BLOCKED** independently of any
R2.7.14 graph result. Release requires real evidence for at least two
original native accepted adaptive epochs per model, certified
cross-epoch original face/patch/curve descendants, physically qualified
shared-curve discretization and welding/non-manifold sheet semantics,
continuous geometric error bounds, and a separate physical Windows GPU
present/RSS/VRAM performance campaign.

Keep VTK native as the default, both BVH selectors opt-in and bounded,
PR #239 draft/unmerged; do not change article configurations merely to
force an artificial second accepted step, merge, tag or release.

## Final exact original-native qualification (2026-11-17)

[**GitHub Actions #44153782458**](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/44153782458)
at exact implementation commit `60a1017e00e0660e7fb1948ad7367fc382f84b34`
finished **4/4 jobs SUCCESS**: Linux and Windows scientific
regressions, Chromium and serial native GeneratorAdaptive.
Its `native-lineage-optin` job ran Eistute and Book against the
**real original input configs**, independently verified full original
source face/patch/curve NDJSON and emitted
`R2714_ORIGINAL_SOURCE_ADJACENCY`. The retained original graph JSON
is Actions artifact
[#14360791421](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/44153782458/artifacts/14360791421),
configured for 14-day retention.

| Original native accepted snapshot | Source patches | Source curves | Curves owned by exactly two patches | Curves owned by 3+ patches | Distinct pair adjacencies |
| --- | ---: | ---: | ---: | ---: | ---: |
| Eistute accepted step 1 | **4** | **13** | **0** | **1** | **6** |
| Book accepted step 1 | **28** | **85** | **0** | **1** | **378** |

The direct original graph has **one source curve incident to every
patch** in each model (all 4 or all 28 patch-owner pairs), rather
than a set of ordinary two-patch seams. Those are **source curve
incidences**, not physical mesh-edge welding. The original real
native generator revalidated exactly one accepted TRI step for each:
Eistute **1,168 faces, 3 rejected/restored**; Book **4,256 faces,
2 rejected/restored**. The instrumented OFF/ON Eistute/Book original
scientific file parities also re-passed **21/21 and 17/17**, respectively.

**Decision:** R2.7.14 PASS for source incidence extraction on these
original accepted snapshots. It is **not** a physical nonmanifold
topology, welded-node, continuous geometry or cross-epoch LOD PASS.
The actual 3+-patch shared-source-curve finding motivates explicit
many-owner sampled side comparisons in R2.7.15.

No second accepted epoch, physical node pointer equality, certified
continuous source curve agreement or physical Windows GPU/RSS/VRAM
was produced. R2.8 remains BLOCKED; VTK remains default; PR #239
remains draft/unmerged, with no scientific C++ policy change.
