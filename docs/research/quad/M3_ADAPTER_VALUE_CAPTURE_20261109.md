# M3-3 provisional value-owned UV capture — implementation candidate

**Not a QUAD generator:** the CLI still rejects `MESH_ELEMENT_KIND=quad_uv`, and the normal TRI path never installs research hooks.

A new research-only `CaptureHooks` pair explicitly injects a source provider and a value sink. The provider may call `CaptureLeafPolygons` while the AFT owns the refined `Quadtree`, but the sink receives only `AttemptUvCapture` containing value-owned vertices, polygon index cycles, origins and counts; no tree or mesh owner pointers escape. `CaptureDisposition::PendingTriDecision` forbids pretending that the observation was accepted as a TRI candidate.

`Adapter::SetResearchUvCapture` installs the complete pair on a specific adapter (empty pair disables it; partial pair fails closed), and the shared `ConfigureAdvancingFront` binds it into each AFT on both `AdaptDomainOmp` and retry-aware `AdaptDomain::run_attempt`. The attempted capture carries `patch_index`, `adaptive_step`, `retry_index`, `local_attempt` (zero in the OMP path). The sink must itself be safe for concurrent invocations. Production CLI does not install hooks. Exceptions from a provider/sink propagate before TRI template publication; no partial snapshot is delivered after a provider failure.

Native tests exercise source lifetime separation, capture provenance, provisional disposition, missing-hook refusal, exception propagation, no-observer TRI behavior and isolation of successive attempts. The tests use the existing bounded real-AFT quadtree fixture; they do not assert that an attempt was ultimately accepted. The new adapter registration is compiled in the full TRI baseline and the two call sites are checked by code review.

**Gate:** require exact-head Linux GCC and Windows MSVC QUAD CTest, TRI 75 CTest, Python 527 and strict Eistute/Book parity before integration. The unchanged legacy mutable `Quadtree&` observer remains a caller contract, not a type-level const guarantee; full numeric point, boundary, UV->XYZ, multipatch, adaptation and memory safety are still unqualified.
