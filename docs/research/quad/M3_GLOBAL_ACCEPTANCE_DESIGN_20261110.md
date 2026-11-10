# M3-6 — Correlating local TRI choices with global acceptance (source audit)

**Status:** technical design, NOT an implemented global event API or positive QUAD generator. The code described below is read from research `quad-templates` after PR #190; line numbers are navigational and must be rediscovered if modified.

## Three distinct decision levels

1. **Provisional UV Quadtree capture**: `research/quad/adapter_capture.h` produces `AttemptUvCapture` with `CaptureDisposition::PendingTriDecision`, a source-independent polygon snapshot. This has no approval semantics.
2. **Local Adapter TRI selection**: M3-4 emits `LocalSelectionEvent`: `SelectedForAdapterReturn`, `Superseded`, or `GenerationFailed`. It describes the result of one `Adapter::AdaptDomain` call, which can itself retry several times before returning a `SubMesh`. It does **not** imply that the outer adaptive generator accepts the patch or step.
3. **Global GeneratorAdaptive acceptance**: the outer adaptive attempt constructs a candidate `MeshAdaptive` over patches, evaluates error, budget, quality and consistency, then either *commits* it as the accepted state or restores the previously accepted state. The global outcome must be separately recorded **only after the real state transition**.

## Actual generator source boundaries

- `src/generator/generator_adaptive.cpp` ~2817–2885: at each adaptive step the serial implementation retains a previous accepted `MeshAdaptive` and creates `AcceptedMeshScope`. `accepted_step` starts false.
- ~3066: the **outer generator retry** variable `retry` is looped over; ~3109–3110 the previous accepted geometry/curve state is restored before generating the next candidate.
- ~3138–3161: the serial branch calls `GeneratorAdaptive::AdaptDomain`; the latter invokes `adapter_.AdaptDomain` near ~4484, with a separate patch-level `local_retry` identifier and *another* `local_attempt` internal to Adapter. Do not equate these integer IDs with the outer retry without an explicit correlation ID.
- ~3230–3264: an element-budget rejection uses `continue` **inside the outer retry loop** after recording candidate metrics, before the final accepted/rejected branch; ~3266–3303 similarly continues on excessive element growth. Audit events only at the final branch would therefore **miss these rejected outer retry candidates**.
- ~3567–3583: accepted candidate commits via `accepted_scope.Commit()` in serial, sets `accepted_retry_attempt=retry` and breaks the retry loop.
- ~3600–3692: if no outer retry was accepted, the generator follows the rejected-step path, writes diagnostic output and acceptance logs, restores `restore_geometry_submeshes` and `restore_curve_snapshots` ~3669–3670, and might advance to another step for logging or terminate.
- ~3694–3815: the accepted path records accepted metrics and publishes the acceptance log. A successful local Adapter result is **not sufficient** for this stage.

## Mandatory provenance redesign before claiming end-to-end correlation

The existing M3-3 identity `PatchAttemptIdentity{patch_index, adaptive_step, retry_index, local_attempt}` is only unique in the context of its Adapter invocation. The outer generator may run that same patch identity several times in distinct **global retries** while changing budgets, and its internal patch candidate `local_retry` can be reused. Therefore no global/local join by the current four fields alone is sound.

Introduce a scoped generation **attempt/epoch token** (or explicit `outer_retry` plus an invocation ordinal) propagated from `GeneratorAdaptive` through `Adapter` into the value-only capture and local-decision event. Preserve the existing four-field legacy APIs for M3-3/M3-5 probes through explicit defaults/overloads and negative tests. Confirm stable identity across serial, OMP and independently scheduled patches before using the token. Do not invent a join retrospectively or infer it from chronological callback arrival.

## Preferred bounded implementation sequence

1. **M3-6a identity:** add optional outer generator retry/attempt epoch to the research-only `PatchAttemptIdentity`; instrument only explicitly enabled research hooks. Test two generator invocations with identical patch/step/local retry identifiers and distinct outer tokens; preserve original Adapter fixture and default CLI.
2. **M3-6b event semantics:** define value-only `GlobalAttemptOutcome` events distinguishing (a) budget retry, (b) element-growth retry, (c) step committed to accepted mesh, and (d) step rejected after rollback. For events emitted before a potentially throwing mutation, label them *attempt evaluation*, not committed. For final events, observe after the actual state transition, not before.
3. **M3-6c reporting safety:** choose a deliberately isolated research event buffer with an explicit error/loss status. Do not let a thrown observer silently turn a successfully committed TRI step into a failed generator, and do not swallow a callback error as a false positive. Avoid a hidden process-global logger or unordered cross-thread event stream.
4. **M3-6d real scenario:** run an opt-in, bounded single-patch case with the outer GeneratorAdaptive controlling acceptance and rejection, correlating local events to the outer epoch. Use an acceptance/rejection oracle that exercises both outcomes without changing the frozen production policy. Evaluate a separate OpenMP concurrency case later, not as proof from syntax-only compilation.

## Mandatory admission gates

The currently qualified M3-5 suite has **76 root CTest** (historical 75 plus the real-Adapter fixture), **527 tooling Python**, **seven CLI denials** and **four QUAD native CTest each** under Linux GCC and Windows MSVC, with frozen Eistute (5 states) / Book (4 states) OBJ, acceptance-field and boundary-incidence identity. Maintain all gates on the **exact** candidate commit and repeat post-merge. Preserve failed runs and original oracles. Change only explicitly reviewed production source paths and update the SHA-256 source inventory if needed. `main` is out of scope.

## Scientific stop conditions

An accepted **TRI** generator step is neither an accepted QUAD patch nor proof of M1 historical numerical point selection. No physical UV-to-XYZ QUAD, full boundary, multipatch synchronization, iterative QUAD adaptation or full allocator/sanitizer proof is implied. Default CLI `MESH_ELEMENT_KIND=quad_uv` remains fail-closed. Milestones M1, M2 and M3 remain PARTIAL pending their independent admission criteria.

## Evidence

- [PR #190](https://github.com/tiagosombrra/apmesh-modernization/pull/190), tested source head `67a4ceb58af09d48ba86fa964b51efaae0c660cc`, merged research head `536c94009ea8b6a3a613886dfdf93314f94c91f6`.
- [Exact head pre-merge CI #42808140065](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42808140065): 76/76 CTest, 527/527 Python, Linux/MSVC QUAD 4/4 each and Eistute/Book scientific parity.
- [Post-merge CI #42809300817](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42809300817); its actual final conclusion must be inspected separately before claiming closure.
- [M3-5 evidence](evidence/M3_REAL_ADAPTER_FIXTURE_20261110.json).
