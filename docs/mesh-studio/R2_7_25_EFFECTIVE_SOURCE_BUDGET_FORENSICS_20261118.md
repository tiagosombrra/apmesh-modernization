# Mesh Studio R2.7.25 — observability of effective source curve and patch budgets

**Research stage:** original compiled C++ native budget forensics. **Date:** 2026-11-18. **PR #239** remains draft, no merge to main, no release.

## Question

R2.7.24 independently confirmed that changing exactly one declared generation control per source model did **not** change either real source's original native accepted/rejected epoch sequence, 7 original Eistute acceptance-predicate records or 3 original Book predicate records. The genuine, still separate processes and postcommit accepted source IDs remained byte-identical to original article controls. That negative result alone cannot establish whether the changed control was ineffective, masked by stronger geometric rules, or affected uncommitted candidate details that were not captured in the R2.7.23 summary.

**R2.7.25 is an observational study, not a third parameter intervention.** It replays the unchanged two R2.7.24 generation treatments and two original article controls, under the same compiled serial C++ generator executable with a research-only, opt-in, read-only source trace. It measures budgets *before acceptance*, including attempts eventually rejected and restored. It does not reclassify them as accepted geometry.

## Exact source instruments

Under the compilation macro `AP_MESH_RESEARCH_NATIVE_LINEAGE` and the runtime flag `APMESH_RESEARCH_EFFECTIVE_BUDGETS=1`, the unchanged C++ source evaluates and prints:

- **R2725_ELEMENT_BUDGET**, one per real outer step/retry: stable mode, configured and effective policy intensity, nominal policy step-1 growth, configured step-1/step-2/step-3 element target growth, element target mode and budget-driven flag, previous element count, computed effective element-growth factor, and computed effective element target. These values are recorded before `AdaptCurve()`, after existing stable-mode damping and quality adjustments.
- **R2725_CURVE_BASE**, one per actual source curve/attempt (13 for Eistute; 85 for Book): prior sampled point count, whether the original curve budget branch is active, the configured step-N growth cap, its effective initial growth-based target, target after priority/sensitivity increments, independently computed geometric-spacing lower bound, the resulting pre-consistency target, and priority/sensitivity booleans.
- **R2725_CURVE_FINAL**, for the same original curve/attempt after existing patch-consistency and structural-cap rules and after the real original curve adaptation callback: pre-consistency count, post-consistency count, target submitted to the curve sampler, actual sample count and original consistency-adjustment flag. The flag may cover either consistency elevation or structural capping; its value alone must not be interpreted as strictly a cap reduction.

All three record kinds include original native step/retry/curve index, an explicit scientific-LOD exclusion and their own versioned schemas. There is no node welding, source-face relabeling, acceptance threshold change, or release-mode trace. The original C++ `score_ok || small_mesh_progress_override`, original postcommit scope and scientific result writing remain untouched.

## Immutable legacy source attestation

Only the specific predeclared seven R2.7.25 observer blocks are permitted on the **exact new C++ Git blob**; the immutable `native_epoch_bridge.py` verifier requires that removing those blocks reconstructs the **previous pinned R2.7.23 C++ observer byte-for-byte**, and removing that observer reconstructs the historical original accepted C++ source Git blob `e0d1edd28968a684edba1e6c11a72b54e07e283a`. An unrecognized C++ source blob, inserted branch mutation, missing observer, altered accept/reject expression or additional unrelated source change fails closed.

The default production/off C++ build must still produce numerical outputs **byte-identical** to the compiled original research-on run for all 38 original scientific output files. The real source acceptance sidecars, lineage, source SHA and C++ outcome ledger remain independently required by the existing CI. Observational C++ stderr is not itself a legitimate accepted adaptive epoch.

## Independent fail-closed interpretation

`native_effective_budget_audit.py` independently reads the original raw C++ stderr from the **same** original article controls and the two distinct single-factor processes, with matching compiled generator executable and source-model SHA-256. Each original R2.7.23 acceptance-gate event must match exactly one R2.7.25 element-budget record and the complete ordered set of 13/85 curve-base and curve-final witnesses. Duplicate native trace keys, incomplete curve sets, non-finite or out-of-bound values, inconsistent final targets, mixed attempt chronology and false scientific LOD claims are rejected.

The report separates:

1. Observed changes in the initial curve growth-target component, the target after consistency, and the actual final number of points.
2. Observed changes in the effective per-attempt total element target.
3. How often, among original controls only, geometric minimum and priority floor individually dominate the configured initial growth target.
4. Count of original curves flagged as consistency-adjusted or structurally capped, without claiming those mechanisms are the same.
5. Per-attempt values joined by the actual original native step/retry.

**An unchanged output despite a changed configuration is evidence that this specific treatment did not change the observed downstream variable.** It is not by itself proof of universal parameter redundancy, geometric identity of rejected candidates, statistical generality, or correct cross-epoch ancestry.

The report is anchored to the exact source C++ stderr hashes, original input model hashes, same compiled research executable, R2.7.24 source-independent per-treatment audit, and full 38-file OFF/ON parity. Synthetic negative unit-test traces are only validation fixtures, not experimental mesh measurements.

## CI protocol

The `native-lineage-optin` job first compiles and independently verifies original real C++ Eistute and Book article source replay, original accepted TRI per-face sidecars, R2.7.23 acceptance predicates and original 38-file OFF/ON parity. It then executes the same two preregistered R2.7.24 source-sensitive trials with the additional read-only R2.7.25 flag. The independent R2.7.24 auditor remains mandatory, followed by the new effective-budget auditor, which retains a source-SHA-scoped 14-day JSON artifact. Linux, Windows and actual hosted Chromium jobs remain independent regression gates; hosted Chromium is **not a certified physical Windows GPU present/RSS/VRAM benchmark**.

## Preliminary original native observations — independent C++ audit passed

The first source-observation native job in
[Actions #44413831478](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/44413831478)
**passed the compiled C++ native source and independent R2.7.25
budget audit**, but that earlier workflow failed a **synthetic Windows
negative-test error-code expectation**, so it is **not a full 4/4 CI
certification**. The source artifact
[original effective-budget audit #14479206683](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/44413831478/artifacts/14479206683)
was independently inspected against both raw original and
trial C++ stderr archives and their source SHA. Its observations
must be reproduced by the final corrected workflow before full
R2.7.25 certification is declared.

| Actual original evidence | Eistute, 7 attempts × 13 curves | Book, 3 attempts × 85 curves |
| --- | ---: | ---: |
| Source curve-attempt witnesses | **91** | **255** |
| Configured control changed in genuine C++ observation | Curve step-N cap **4→2** in all 91 witnesses | Intensity **0.02→0.01** in all 3 element-budget witnesses |
| Changed initial curve growth target | **0** | **0** |
| Changed post-consistency curve target | **0** | **0** |
| Changed final real sampled curve point count | **0** | **0** |
| Changed effective per-step element target | **0** | **0** |
| Geometric floor strictly above initial growth target (original) | **78/91** | **0/255** |
| Original consistency or structural adjustment flag | **54/91** | **0/255** |

**Eistute:** `budget_driven=1`, `element_target_mode=1`;
configured step-N curve growth cap really changes from 4 to 2, but
the growth-component point targets remain byte-for-byte the same
observed integer sequence (11 or 21). That is direct evidence
that the decreased cap did not bind *that observed component*
in these exact attempts, not proof that the parameter can never
matter. At every step 2, 3 and 4 source retry, the actual
geometric-spacing floor strictly exceeds this initial growth
component for all 13 original curves. The original structural
consistency path flags 54 of the 91 curve-attempt witnesses.
The largest recorded initial geometric floor is 131 points,
whereas the final actual source curve counts in these
observations never exceed 20. These records expose how
later source-specific constraints can dominate intermediate
curve budgets; they do **not** establish any newly accepted
adaptive epoch.

**Book:** `budget_driven=0`, `element_target_mode=0`, and the
actual curve point-budget branch is **inactive** for all 255
curve-attempt witnesses. The input intensity changes from
0.02 to 0.01, changing nominal
`policy_step1_growth` from 1.16 to 1.08,
but the actual C++ element growth values remain **1.8**
(steps 1 and 2) and **1.5** (step 3), from the separately
configured original element-growth path; the
`effective_target_elements` remain **112, 4256, 4256**.
The trial thus changed a *computed nominal parameter* but
did not engage the budget-driven element target path under
Book's original research-debug configuration. The original
curve samples and accepted TRI sidecar bytes remain unchanged.

These results are observations from **specific real original
source-controlled generator runs**, not general statistical
conclusions or independent geometry error/LOD validation.
**R2.8 remains BLOCKED**.

## Status and next research decision

**Implementation prepared. Empirical numerical findings must be read from the exact passing native C++ and independent R2.7.25 audit artifacts; do not invent which floor dominates before the new source capture runs.** Even if some geometric target or actual curve sampling changes, the true original postcommit accepted step counts remain the only admission criterion for genuine native epochs. R2.8 remains **BLOCKED** pending at least two accepted commits in one actual source-model/run, verified original source face/curve descendants and a continuous geometric approximation-error bound. No merging, tagging, publishing, or alteration of acceptance policy.
