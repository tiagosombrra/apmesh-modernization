# M3-4 — local attempt decisions, distinct from QUAD capture and global acceptance

**Status:** candidate feature branch, native/scientific CI pending. No physical QUAD generated.

The M3-3 `AttemptUvCapture` still has `CaptureDisposition::PendingTriDecision`. M3-4 introduces a separate, optional `CaptureHooks::local_selection_sink` callback with `LocalSelectionEvent` values. Its three exclusive kinds are `SelectedForAdapterReturn`, `Superseded` and `GenerationFailed`. The identity carries the same `patch_index`, `adaptive_step`, `retry_index` and `local_attempt` used by the original UV event. The original TRI candidate status string is copied unchanged.

The retry-aware `Adapter::AdaptDomain` records each local attempt's generation success and status only when a sink is installed; after all retry/fallback decisions are finished, it publishes a classification of **every attempted local candidate**, with exactly one selected if `best.success`. `Adapter::AdaptDomainOmp`, which has no local structural retry in this path, publishes one selected local attempt only after a generated TRI `SubMesh` is fully constructed. These events are **not** scientific/global acceptance, which remains the responsibility of the outer `GeneratorAdaptive` later in the pipeline. An earlier UV capture could exist without a matching local selection on exceptional early exits; no success is invented in those cases.

Before dispatching any decisions, `PublishLocalSelections` rejects duplicate local IDs, nonexistent selected IDs, selecting a failed candidate and an unselected stream containing successful candidates. Invalid inputs emit no partial events. A downstream sink exception may still interrupt delivery after prior events; it aborts the opt-in research execution and is not claimed transactionally safe across downstream observers.

No CLI installs any capture or decision sink. This is a bounded, explicitly injected research audit interface only: it does not alter `MESH_ELEMENT_KIND=quad_uv` rejection, point-policy requirements, TRI acceptance thresholds, output, 3D mapping or patch topology.

**Required qualification:** native Linux GCC/MSVC QUAD contracts, all 75 TRI CTest/527 Python tooling, seven CLI denials, optional OMP syntax compilation and exact Eistute/Book five/four-state OBJ/acceptance/boundary parity. M1/M2/M3 remain partial pending scientific decisions and positive QUAD generation.

## Qualified pre-merge and merged research candidate

PR [#189](https://github.com/tiagosombrra/apmesh-modernization/pull/189) merged at `1ce8bdc967367714ee780ee52077115252fd465c` with exact reviewed tree `a8891ee1f0419f7af2c7e0e22e66d2d84760ac2e`. [Pre-merge CI #42785252030](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42785252030) finished SUCCESS: Linux and MSVC QUAD 4/4 native tests, TRI 75/75 CTest, tooling Python 527/527, CLI denials 7/7, conditional OpenMP syntax and Eistute/Book 5/4 state exact scientific parity. Post-merge [Actions #42786259118](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42786259118) remained queued at checkpoint.

**Not yet qualified:** a hook-enabled real Adapter retry/selection fixture, full OpenMP runtime safety, global generator acceptance, a numerical interior point or complete physical QUAD mesh. See [M3-4 evidence](evidence/M3_LOCAL_SELECTION_20261110.json).
