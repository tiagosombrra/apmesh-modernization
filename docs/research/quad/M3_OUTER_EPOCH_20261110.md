# M3-6a — scoped outer generator retry identity

**Integrated into research `quad-templates` via PR #191; not a physical QUAD generator.** Adds `OuterAttemptIdentity{session, epoch, global_retry}` as a trailing field to the existing four-field `PatchAttemptIdentity`, with backward-compatible unscoped defaults.

The research-only `GeneratorAdaptive::SetResearchUvCapture(hooks, session)` requires a nonzero caller-provided session namespace when hooks are installed. Each outer adaptive `retry` increments a per-instance monotonic epoch and passes it to `Adapter::SetResearchOuterAttempt` before generating its patch candidates. No process-global token registry, CLI option or default capture is introduced. The caller is responsible for unique session identifiers across distinct generator instances and independent runs; this API does **not** claim globally unique IDs without that input.

The Adapter enriches both serial retry-aware and OMP paths, in both `AttemptUvCapture` and `LocalSelectionEvent`, with the same scope inherited by the individual AFT. A direct Adapter research client may supply its own complete scope, or retain the legacy all-zero unscoped sentinel. Scope changes without installed research hooks are refused. When the hook registration is replaced, the old scope is cleared. Mixed-session/epoch patch candidate streams are rejected before publishing local decision records.

The actual one-patch native Adapter fixture now runs two normal captures with the same patch/step/local retry IDs and different outer epochs, plus an intentionally aborted capture with a third epoch. It requires the UV capture and local decision to agree on the epoch and validates preserved TRI behavior. Native pure contracts check invalid/incomplete scopes, mixed-epoch refusal, and four-field initializer compatibility.

**Limits:** the outer generator call path is compiled, but these fixtures are not a full hook-enabled `GeneratorAdaptive::Execute` with budget/acceptance retry outcomes. M3-6b must add explicit evaluated/committed/rejected global events after the real state transitions. OpenMP runtime races, full sanitizers, numeric point selection, UV->XYZ, boundary, multipatch and physical QUAD remain unqualified. The default CLI still fails closed for `quad_uv`. M1/M2/M3 remain partial.

**Gates:** exact-head Linux and Windows QUAD native 4/4 each, root 76/76 CTest, 527 Python, seven CLI rejections, `USE_OPENMP=1` compile and exact frozen Eistute/Book parity, then post-merge CI.

## Exact qualification and integration

[Actions #42813339493](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42813339493) completed SUCCESS on candidate `65a566c3...` with root 76/76 CTest, 527/527 Python tooling, GCC/MSVC QUAD 4/4 each and frozen Eistute/Book 5/4 exact reference comparisons. [PR #191](https://github.com/tiagosombrra/apmesh-modernization/pull/191) merged into research at `1f34cc31d7fef9f6a4427a9c7c0bfffaaf34d2eb`; post-merge [CI #42814238290](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42814238290) status at record: in_progress. See [M3-6a evidence](evidence/M3_OUTER_EPOCH_20261110.json).
