# M3-3 provisional value-owned UV capture — implementation candidate

**Not a QUAD generator:** the CLI still rejects `MESH_ELEMENT_KIND=quad_uv`, and the normal TRI path never installs research hooks.

A new research-only `CaptureHooks` pair explicitly injects a source provider and a value sink. The provider may call `CaptureLeafPolygons` while the AFT owns the refined `Quadtree`, but the sink receives only `AttemptUvCapture` containing value-owned vertices, polygon index cycles, origins and counts; no tree or mesh owner pointers escape. `CaptureDisposition::PendingTriDecision` forbids pretending that the observation was accepted as a TRI candidate.

`Adapter::SetResearchUvCapture` installs the complete pair on a specific adapter (empty pair disables it; partial pair fails closed), and the shared `ConfigureAdvancingFront` binds it into each AFT on both `AdaptDomainOmp` and retry-aware `AdaptDomain::run_attempt`. The attempted capture carries `patch_index`, `adaptive_step`, `retry_index`, `local_attempt` (zero in the OMP path). The sink must itself be safe for concurrent invocations. Production CLI does not install hooks. Exceptions from a provider/sink propagate before TRI template publication; no partial snapshot is delivered after a provider failure.

Native tests exercise source lifetime separation, capture provenance, provisional disposition, missing-hook refusal, exception propagation, no-observer TRI behavior and isolation of successive attempts. The tests use the existing bounded real-AFT quadtree fixture; they do not assert that an attempt was ultimately accepted. The new adapter registration is compiled in the full TRI baseline and the two call sites are checked by code review.

**Gate:** require exact-head Linux GCC and Windows MSVC QUAD CTest, TRI 75 CTest, Python 527 and strict Eistute/Book parity before integration. The unchanged legacy mutable `Quadtree&` observer remains a caller contract, not a type-level const guarantee; full numeric point, boundary, UV->XYZ, multipatch, adaptation and memory safety are still unqualified.

## CI closure and M3-3 integration — 2026-11-10

PR [#188](https://github.com/tiagosombrra/apmesh-modernization/pull/188) merged as `078301a27feaffda0a7ecd8d69de1f3ba0d4c71e` (source tree identical to reviewed candidate `b2ec2104...`). [Pre-merge CI #42729761791](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42729761791) passed all four jobs: QUAD GCC/MSVC each 4/4 CTest, strict TRI 75/75 CTest and 527/527 Python tooling, seven real-CLI negative controls, conditional `USE_OPENMP=1` syntax check, and Eistute/Book five/four scientific states with exact OBJ bytes, acceptance and boundary incidence. [Post-merge CI #42731206966](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42731206966) also passed all four jobs on the exact merged code SHA.

The original failure of `attempt_metrics_probe` after changing the one-argument `ConfigureAdvancingFront` signature and the subsequently exposed pre-existing OMP `AppendDomainDebugLog` omission are preserved in the PR discussion. The test oracle was not weakened. New opt-in `SetResearchUvCapture` never runs without explicit registration; events are marked **PendingTriDecision** and are not evidence of TRI acceptance or QUAD production. OMP full runtime concurrency, const safety and memory-denial/sanitizer campaigns remain unqualified.

**Next M3-4:** attach an independently typed local-attempt selection/outcome event (candidate vs locally selected vs superseded) to patch/step/retry/local-attempt identity. It must not claim global generator acceptance; no scientific centroid/polygon boundary/physical QUAD is selected.
