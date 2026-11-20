# Mesh Studio R2.7.16 — nonwelded original-native seam sample correspondences

**Date:** 2026-11-17. **Branch:** `feature/mesh-studio-r27-bvh-20261116`.
**PR:** #239, draft/unmerged.
**Scope:** original C++ serial accepted native TRI snapshots, read-only.

## Verified motivation

R2.7.14 actual compiled native Eistute/Book source observations have **one canonical
source curve incident to every patch** in each model: Eistute 4 patches
(6 owner pairs) and Book 28 patches (378 pairs).
The initial real R2.7.15 native run #44159057629 returned strict sampled
concordance **0/6 and 0/378**, but the subsequent independent R2.7.15
per-condition native log in run #44160223365 isolated the cause:

| Original native step 1 | Original boundary sample count per patch | Complete boundary chains | Canonical parameter matches | XYZ matches | Logical native IDs agree |
| --- | ---: | ---: | ---: | ---: | ---: |
| Eistute | 11 | 6/6 | 6/6 | 6/6 | **0/6** |
| Book | 13 | 378/378 | 378/378 | 378/378 | **0/378** |

Native report sample diagnostic rows show zero XYZ and canonical parameter
deltas for their first three examples; **do not generalize numerical
zero deviation across all 384 pairs from examples alone**. All 384
pairs passed the predeclared explicit tolerance gates, and all 32
individual patch-side edge chains were complete with no edge
diagnostics. The difference is in the original *logical native
node IDs* across patch-local copies, not in the sampled geometric
agreement in this experiment.

## Source-level explanation for the single divergent corner

The actual R2.7.15 original native records identify the canonical
shared original source curve as `source_curve_slot=3` on
**local patch edge 3** of every Eistute/Book patch; all incidences
have `reversed=false`. The **canonical `t=0` endpoint** is the
only seam sample whose logical native node ID differs across owner
patches. All other original samples have one shared logical ID
across patches, and the accepted native XYZ and canonical t are
exactly equal in the retained full pairwise R2.7.15 JSON.

The original serial C++ source offers a specific mechanism:
in `src/adapter/adapter.cpp`'s `AdaptDomain`, local edges 2/3
traverse `parameters_.rbegin()` to the element before
`parameters_.rend()`, **omitting their final local endpoint**
so that the boundary does not duplicate its first vertex.
`Boundary::close()` in `src/crab_mesh/aft/boundary.cpp` joins
the final edge-3 vertex to `first`, which was created on the
initial local edge 0, preserving that vertex's original copied
logical node ID. As `u=0,v=0` is incident to edge 0 and edge 3,
the resulting geometric point can be identical while its surviving
logical ID comes from each patch's edge-0 curve samples, rather
than the common edge-3 curve endpoint. This is a **source-level
mechanistic explanation consistent with the observations**, not
an independent instrumented runtime proof of pointer ownership.

There must be **no automatic global ID correction** based on this
finding. A subsequent source/ABI-focused observer can investigate
the actual corner owner and source-curve sample slot under real
accepted commits without modifying native acceptance, and must
preserve multi-sheet nonmanifold semantics.

## R2.7.16 hypothesis and construction

The source graph and native TRI per-face UV/XYZ/IDs support a
read-only source-scoped **sample association** at each accepted
snapshot without ever modifying original mesh identity. For each
real accepted step and original source curve, the tool
`tools/mesh_studio/native_seam_correspondence.py`:

1. Independently reruns R2.7.12 retained NDJSON + SHA-256 validation,
   R2.7.14 original source ownership graph and R2.7.15 native face-edge
   UV/XYZ/ID audit, **before** constructing any sample association.
2. Requires every patch-local side chain to be complete. Requires
   all pairwise owner comparisons to agree on source sample count,
   canonical parameter and XYZ within the R2.7.15 documented
   translation-invariant tolerance. If any condition fails,
   emits an **unqualified curve** and creates **zero** sample
   groups for it.
3. For a qualified source curve, constructs exactly one
   **read-only source sample group per original sampled curve
   ordinal**. Its reference consists of the real
   `(native_accepted_step, source_curve_slot, sample_ordinal)`
   namespace. It is **not** an original native node ID, an
   aliasing pointer, a global welded node nor a cross-epoch
   descendant. The group retains **every patch's original
   native_node_id, original XYZ and canonical t** without rewriting
   or deduplicating them.
4. Classifies each group as `same_native_logical_id_in_all_source_patches`,
   `different_native_logical_id_in_every_source_patch`, or
   `mixed_reused_native_logical_ids`. This is an identity
   comparison, not a new topological certification.
5. Retains original accepted source-sidecar SHA, measured maximum
   pairwise sampled XYZ and parameter differences, all original
   memberships, and explicit negative certification booleans for
   C++ physical node welding, continuous analytic geometry and
   cross-epoch LOD ancestry.

This research representation can later drive an optional STUDIO
nonmanifold seam inspector. It must **not** be used to silently
rewrite original native connectivity, to triangulate or weld the
original N-sheet interface, to claim a true geometric LOD bound,
or to insert a fabricated global unique node identifier into
scientific output.

## Test and CI

The unit suite `test_native_seam_correspondence.py` has seven
synthetic tests for matched and differing native logical IDs,
XYZ mismatch refusal, incomplete boundary refusal, snapshot-local
reference, source SHA preservation and deterministic derivation.
They are parser/algorithm tests only, **not source mesh evidence**.

The isolated native CI job first compiles the **original** serial
GeneratorAdaptive in its opt-in observational build, executes
Eistute and Book, revalidates their raw original post-commit
NDJSON, and emits a 14-day artifact
`mesh-studio-r2716-nonwelded-correspondence-<sha>`.
Linux/Windows scientific regressions and Chromium UI controls
remain independent; R2.7.13 numerical OFF/ON parity remains required.

```bash
python -m unittest tools.mesh_studio.test_native_seam_correspondence -v

python -m tools.mesh_studio.native_seam_correspondence \
  --directory build/r2712-native-evidence \
  --output build/r2716-native-correspondence.json
```

**Qualification:** the R2.7.16 source-scoped associations are not
experimental PASS until their exact new CI SHA, four job outcomes,
authentic native counts, source pins and output receipt are observed.
Source graph concordance is not certified welded mesh topology.
One accepted native step per model remains insufficient for cross-
epoch LOD; no accepted step is manufactured merely for the report.

**Unchanged exclusions:** R2.8 scientific LOD BLOCKED; VTK native
picker default; bounded BVHs opt-in only; no generator policy
adjustment, automatic node welding, main merge, release or tag.
Physical Windows GPU-present/RSS/VRAM measurements remain open.

## Original native R2.7.16 evidence and durable archive (2026-11-17)

The corrected [CI #44162179260](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/44162179260)
at source SHA `f550ad2453b803b2452710a51c7b93bcacc98ba5`
has now finished **ALL FOUR JOBS SUCCESS**: original compiled serial
GeneratorAdaptive native lineage/correspondence and real OFF/ON
numerical parity, Linux scientific regression (**295 tests run,
4 optional skips**), Windows scientific regression (**295 tests run,
10 environment skips**), and actual Chromium (**42 passed**, with
its existing optional exclusions). The earlier unsuccessful run
#44161087523 failed only on one synthetic unit fixture keyword
argument; the corrected real native and browser CI both passed.
This is actual final workflow success, not an inferred browser result.

The real native original source-epoch R2.7.16 acceptance receipt
states:

| Model | Native accepted step | Original shared source curve | Patches sharing curve | Read-only sample groups | All-patch same native logical IDs | Different IDs at every patch |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Eistute | 1 | slot 3 | 4 | **11** | **10** | **1** |
| Book | 1 | slot 3 | 28 | **13** | **12** | **1** |

Every qualified group retains its full original patch-slot and
native logical node ID membership; there are **no invented global
mesh IDs**. The full original report's source-verified per-curve
max sampled canonical-t and XYZ discrepancies were **both exactly
zero**, on the tested original native acceptance step 1.
The only different-ID sample is canonical `t=0`, shared-source
local edge slot 3, with `reversed=false` on all original patches.

GitHub Actions R2.7.16 report artifact
[#14362709606](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/44162179260/artifacts/14362709606)
was downloaded and stored in the authenticated **personal**
`Doutorado/DOUTORADO_APMESH_ACOMPANHAMENTO/05_Experimentos_e_Resultados`
research folder. The Google Drive file was downloaded again;
its bytes and original Actions ZIP are **SHA-256-identical**:
`a5a84da0bc1148e043e016eaa4ace835c9e48fceea8e1ba1aba3cf4e9a17b826`
(4,576 ZIP bytes). The original per-model native NDJSON SHA pins
inside the report begin Eistute `3fa505b9283d7666` and
Book `292b0b5ccc399711`, matching the archived original
post-commit accepted-source snapshots. No private Drive URL
is disclosed in the public repository.

This is a **native source-scoped sampled correspondence PASS**,
not a physical node-welding, continuous analytic curve agreement,
cross-epoch face/curve ancestry or scientific LOD PASS. The initial
unit regression failure was a test fixture invocation error and
not a native numerical or geometric instability. Keep R2.8 blocked,
VTK default, BVH experimental modes opt-in, and PR draft/unmerged.
