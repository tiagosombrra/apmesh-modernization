# Mixed-fill continuity audit and live-pair delivery - 2026-11-17

Source6f4ef473b2d248548632d4e0f358f8eea4749f86, draft PR238; tree
56412019f9c1123464a262a1a33176f3a37a2e6f. Canonical entry3cf8d21, main ef40c0f,
frozen reference f6050ec. One work item: integrated mixed filling. This is an
opt-in research capability with finite qualification, not a scientific stage
closure, production adoption, independent approval or integration receipt.

## Audit findings and disposition

| Finding | Verified disposition |
| --- | --- |
| Real curves already reach native QUAD/AFT, but earlier pair CSVs were completed-output topology observations only | Retain that prior evidence. The new separate case selects pairs at actual original AFT triangle commits. |
| Native QUAD provenance previously assumed every QUAD came from a template leaf | Keep seed LeafPolygonOrigin separate from AFT-pair source face IDs; validate/export final paired-face origins. |
| UV shape can hide distortion on the physical surface | Implement the recorded S_XYZ<=1.5 experiment with existing UV and physical validity predicates; retain TRI when no admissible pair exists. |
| Choosing a local angle winner does not optimize the whole mesh | Retain sampled error increases and unchanged node counts. No global optimum, convergence or superior geometry claim. |
| The earlier analyzer/raw archives were local build artifacts | Add a tracked independent actual-OBJ/CSV decision replay and run it locally and in hosted Linux/Windows/sanitizer jobs. The old observation remains its original limited evidence. |
| Canonical and feature documents had an add/add conflict | Synchronize canonical3cf8d21 into the feature, preserving decisions and the implemented contract. Native/test inputs are unchanged by that reconciliation. |
| Architecture and hosted reviewed-config guards did not yet describe the new slice | Regenerate exact source inventory; add only the reviewed opt-in config. Preserve the failed gate/job and the unreviewed-config rejection. |
| Expanded header analysis exposed an older owning-snapshot warning | Express the independent snapshot with a range constructor. Keep the mutation contract and configured diagnostics. |
| Earlier pending-choice wording could cause another generic questionnaire | The user's delegated experimental choices remain the implementation basis. Formal advisor sign-off and general scientific adoption are not invented. |

## Capability delivered

Use `configs/quad/curved_patch_live_pairs.conf` with an explicitly enabled serial
experimental QUAD build. The new case is
`curved_bezier_live_pairs_vertex_mean_v1`. Previous QUAD cases and default TRI keep
their behavior. Original curves, quadtree/templates and AFT trajectory remain.

The selector evaluates already-emitted adjacent TRI alternatives when each new
TRI becomes owned by the original AFT. It checks positive UV corner determinants,
existing signed physical corner/split-normal validity, then S_XYZ<=1.5. Minimize
S; exact ties use physical edge ratio, current triangle edge order and stable
source IDs. Consume each TRI at most once. Retain valid TRI without an eligible
partner. This is incremental selection on the original TRI trajectory, not proof
of every historical contraction choice or a completed-mesh matching optimum.

Build a separate typed physical owner containing seed QUADs, paired QUADs and
retained TRI. Validate complete incidence/source/seam/disk before publication.
The injected prepublication failure preserves the previous nonempty owner,
observers and output. No two already-published physical TRI are mutated in place.
The per-step `_aft_source.obj`, live decision/stage CSVs and final OBJ provenance
make the source-to-final transformation independently reviewable.

## Measured result and tradeoff

The bounded source case produces the same33/281/797 nodes and original curve
partitions as before. Across three independently executed compiler profiles:

| Adapted step | Seed QUAD | Selected pairs | Final QUAD | Retained TRI | Reference outcome |
| --- | ---: | ---: | ---: | ---: | --- |
| 1 | 16 | 2 | 18 | 20 | accepted TRI reference |
| 2 | 242 | 0 | 242 | 66 | accepted TRI reference |
| 3 | 724 | 3 | 727 | 124 | accepted TRI reference |

Step2 retains TRI:42 union candidates fail UV validity and24 fail the physical
angular score. Step1 records15 UV rejections,6 shape rejections,2 selections and
1 already-consumed alternative; step3 records88/37/3/2. Zero selected pairs is
reported, not treated as a successful selected-pair observation.

On the same24x24 cell-center UV grid, using independent Bernstein source values
and source-area-weighted physical RMS, step1 changes0.023406069100086815 to
0.023427760104983878, approximately+0.0927%; step2 is unchanged; step3 changes
0.007235566866455381 to0.00723557052535219, approximately+0.0000506%.
These are absolute source-coordinate errors and relative changes in this sampled
metric, not the existing curvature-estimator percentages, a continuous bound or
an adopted acceptance rule. Fewer elements do not establish better approximation.

## Executed gates on the delivery revision

- Exact6f4ef47 baseline:85/85 through validation_session delivery scope. Receipt
  build/validation-session/1794950586476829500-eb4b3a1e/report.json; the adapter
  itself does not certify scientific delivery or independent review.
- GNU13.3 Release, MSVC19.44 Debug and Clang18.1 ASan/UBSan with leak detection:
  actual real-curve source/reversed/negative cases, new live histories, five prior
  domain cases, fixed16, original/stable histories and nonempty rollback pass.
  Native added contracts include four shortcut/observer cases with one injected
  abort, seven shape/parameterization cases, three exact rank-tie contracts and
  three malformed live inputs. Old four-topology/five-invalid and six-source/
  three-reversed/54-negative outcomes remain.
- Independent replay verifies every actual alternative, geometry score/validity,
  ordering, disjoint consumption, final faces and OBJ origin IDs. Six forged
  source/cycle/score/final-face/generation/acceptance records are rejected.
- All40 previous OBJ per profile match exact7fc988d hashes. All12 new paired
  history OBJ match across profiles. All lineage/topology/status/selection fields
  agree; four MSVC S entries differ from GNU/Clang by at most4.440892098500626e-16.
  Other CSV bytes match. Preserve this distinction from byte-identical geometry.
- Current GNU frozen TRI comparison: Eistute5 and Book4 exact OBJ/acceptance with
  independently verified boundary coverage. Reference source/image/archive
  identities retained; no model/profile/tolerance changes.
- Configured LLVM22 analysis covers five touched TUs/header consumers. Four
  unchanged native TUs reuse exact-source0417a5a analysis; the affected test TU
  repeats on6f4ef47 with first-party headers and no line filter, with no visible
  first-party diagnostic. Retain configured non-user/check exclusions; no claim
  of a whole-repository diagnostic closure.
- Hosted run44179166105:4/4 SUCCESS on exact6f4ef47, including the new live audit
  in Linux, Windows and sanitizer jobs, full baseline and frozen TRI comparison.

Commands: `python tools/validation_session.py run --scope delivery --base 7fc988d`;
configured `cmake --build ... --target ap_mesh quad_real_boundary_source_contracts`;
`python tests/quad/test_live_pair_application.py --exe ... --directory ...`;
existing domain/fixed16/history runners; `tools/run_generation_case.py` and
`tools/verify_generation.py --require-boundary-coverage`. Exact argv/tool/flags,
source/input/output hashes and finite result scopes are in the portable receipt.
Raw native logs/archives remain local build/WSL artifacts.

## Retained failures and closure audit

Keep the initial transport reset; wrong forged-record exception catch; ambiguous
and undefined-legacy-method shortcut fixture build failures; formatter literal
reflow/PATH lookup failures; stale-inventory regression stop; document conflict;
expanded-header snapshot warning; and failed hosted run44178168367. That job
stopped on the new config allowlist before a reference comparison ran. The
specific reviewed asset and independent snapshot fix do not alter science or
disable the unreviewed-path guard. No identical failed campaign was blindly
retried; changed code/contracts or corrected explicit tooling preceded validation.

Code/owners, real and negative tests, source/provenance contracts, documentation,
scientific scope and the failure/coverage inventory were reviewed explicitly.
This closes the bounded implementation/qualification work for review; PR238
remains draft and unmerged. M1 center identity, full M5/1993 scope, isolated
topology-phase-only observer coverage, R3/M7 mixed accepted feedback, continuous
bilinear validity, Doxygen/full new-path CRT/denials, independent review and
post-integration exact-branch gates remain open. mixed_adaptive_epochs=0.

Next: independent review and research integration qualification of this package,
then actual mixed accepted-state/error feedback, then local curve/transition/
interior balancing. Do not replace that route with another global-factor sweep.

[Portable delivery receipt](evidence/MIXED_FILL_LIVE_PAIR_DELIVERY_20261117.json).
