# QUAD state, implementation and plan audit — 2026-11-13

## Verdict and pinned scope

The implementation has made substantial engineering progress, but the research
branch is not a complete application QUAD generator. Keep PR #214 draft. Return
the next delivery to the existing R2/R3 critical path rather than treating more
original-TRI observations as completed QUAD adaptation.

Audited feature: `7cd5014936a417565415d736bad40dc70deb35df`; canonical checkpoint:
`7486e8ee9d2064593a502a84e4c189ccba5c6dd2`; unchanged main:
`f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94`. Concurrent canonical advancement
from `ff4d83e` to `7486e8e` was retained. The primary checkout remains the older
`bb50b16`; it was not reset or silently advanced. Findings below refer to the
pinned feature unless a canonical document is explicitly named.

## Findings

1. **High — physical QUAD convexity admission is incorrect.**
   `research/quad/physical_quadrilateral_adaptive.cpp:73` checks only the two
   triangles along diagonal 0–2. The exact planar UV/XYZ example
   `[(0,0), (1,0), (0.25,0.25), (0,1)]`, normal `(0,0,1)`, passes both
   determinants (`0.25`) although the turn at corner 2 is `-0.5`.
   A native GCC C++17 reproduction compiled the actual feature source and
   returned **exit 1**, exposing the missing rejection:
   `CONCAVE_QUAD_ADMITTED area=0.25 angle_at_reflex_corner=2.2143`.
   The constructor's diagnostic promises concavity rejection; `acos` also
   supplies the smaller angle for this reflex corner. Existing ownership
   negatives omit this input. This does not establish that the 32 exported
   patches contain concave elements; it establishes an admission-contract bug.

2. **High — original TRI epochs do not implement QUAD adaptive history.**
   The canonical roadmap requires mixed-element history in R3 and QUAD history
   in M7. `tests/quad/generator_outcome_probe.cpp:1030` counts genuine original
   TRI commits. Detached QUAD/TRI charts are not subsequently accepted and
   adapted as mixed history. Production adjacency still enumerates positions
   1–3 (`src/curvature/adjacent.cpp:20`). Eistute's three TRI commits and Book's
   one commit are useful source prerequisites, not a passed QUAD M7 gate.

3. **High — the live application R2 contract is still open.**
   `src/application/run_application.cpp:42` refuses `quad_uv`. The full chart
   probe explicitly reports `actual_production_AdaptDomain_tree=0`,
   `scientifically_approved_global_mesh=0` and no interpatch welding
   (`tests/quad/full_source_patch_stage_probe.cpp:2620`). No successful live
   `ap_mesh --config` QUAD run has been demonstrated. The canonical corrected
   critical path explicitly excludes new high-valence sheet pairing from the
   first delivery; a controlled curved manifold patch can close R2 without
   inventing valence-4/28 scientific decisions.

4. **Medium — current documentation and evidence identities diverge.**
   Canonical STATE records R2c20 completed, while its JSON still has a pending
   status / `native_result:null` and the dashboard says code in CI. R2c19's
   top-level identity still names the first source/run while the corrective
   qualified identity is nested later. STATE is about 588 kB with many
   competing “Active checkpoint” sections; the roadmap is about 125 kB.
   Preserve chronology in SESSION_LOG, but establish one concise current state.
   The research README also claims production sources are unchanged, although
   the feature modifies nine `src/include` files. Distinguish source identity
   from measured default-TRI behavioral parity.

5. **Medium — review scope and terminology need a finite boundary.**
   At the earlier canonical `ff4d83e` pin, the direct comparison to the feature
   spans 114 feature commits /89 files, about 12,246 added and 7,279 removed
   lines. GitHub's PR merge-base display uses a different base; do not mix the
   counts. The measured charts contain 512 QUAD and 1,456 TRI, approximately
   26% QUAD by element count. Use “mixed QUAD/TRI” unless a dominance metric is
   explicitly defined. Hosted artifacts expire; locally retained files and
   their hashes are required for durable replay.

## What is actually implemented and checked

| Scope | Current evidence | Remaining limit |
| --- | --- | --- |
| UV / quadtree | Real leaves, 2:1 signatures, typed QUAD emitter, shared IDs and native tests | General numerical/adversarial qualification |
| Physical patch | Native Bezier lift, four-node element, owned QUAD/AFT interface and detached staging | Convexity defect, native sanitizers, live publication |
| Original model charts | 4 Eistute +28 Book detached charts; 1,744 nodes, 512 QUAD +1,456 TRI | No accepted global connected mixed model |
| R2c21 | Exact push source `5ed7fdd`, run43532144224, all four jobs successful; downloaded topology/mesh/science artifacts | Local indexed patch scope; no scientific sheet approval |
| Local replay | Same downloaded OBJ checked again: 32/32 patches and seven negative controls; result matches artifact semantically | Existing verifier replay, not independent scientific review |
| R2c22 | Exact push7cd5014, run43539017852, all four jobs subsequently completed successfully | Does not cover the newly exposed concavity input or live application QUAD |
| Default TRI | Default selection retained; explicit QUAD refusal; frozen parity evidence available | Production source identity with main is false |
| M7 | Genuine original TRI source commits observed | No two accepted mixed-element epochs |

The source-bound adviser packets still contain no approved high-valence sheet
policy. Literal 1993 equivalence remains distinct from the already named
experimental point rules. Neither geometric coincidence nor a successful
checker authorizes welding. The existing remote policy records scoped owner
authorization for public-runner CI; this audit launched no hosted workflow.

## Recommended finite sequence

1. Repair physical convexity rejection in one bounded change. Preserve this
   failing input, cover all cyclic corners and rotations/reversals, retain
   observer rollback, valid element behavior and the original input contracts.
2. Close **R2** on one controlled curved manifold patch: live explicit opt-in,
   actual typed QUAD interior and original AFT exterior TRI, original boundary,
   independent UV/XYZ/orientation checks and failed-publication rollback.
3. Close **R3** using that same mixed mesh as history for at least two accepted
   epochs. Dispatch curvature, quality, export, cloning and acceptance by element
   type; preserve exact default TRI evidence.
4. Resume R4 model-wide trials, M6 approved sheet ownership and M8 comparative
   experiments after these functional contracts. Keep historical-method,
   all-QUAD, Hermite and anisotropy choices in their own approved scopes.

This sequence refines execution of the existing roadmap; it grants no new
scientific policy and does not remove required exact-head or memory gates.

## Reproduction and retained observations

[Compact evidence](evidence/STATE_PLAN_AUDIT_20261113.json) records hashes,
remote run identities, source-bound native concavity failure and downloaded
artifacts. Raw commands/stdout/stderr are retained at
`build/quad-audit/session-20261113/` in the primary Windows checkout. The native
concavity reproduction links unchanged previously qualified Node/Element/Point/
Vector engine objects; it does not qualify the entire current application.

The original Windows validation environment check failed for missing tools and
its plans lacked a configured baseline. Initial document review caught a Windows
writer LF-to-CRLF conversion; the edited files were explicitly restored to their
original LF convention before checking again. A separate WSL clone successfully
qualified the environment and configured the canonical checkpoint. Required
documentation-checkpoint regression is recorded separately against its exact
commit. No source fix, application QUAD run, sanitizer campaign, new model study
or merge is part of this audit. The known concavity failure blocks algorithmic
admission regardless of a passing unrelated baseline.
