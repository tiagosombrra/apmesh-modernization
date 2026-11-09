# M3-2 — Refined Quadtree observation in the live AFT execution (2026-11-09)

**Status:** PR [#187](https://github.com/tiagosombrra/apmesh-modernization/pull/187) merged into `quad-templates`; exact PR head CI passed in scope; post-merge CI [#42690813905](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42690813905) in_progress_at_checkpoint. This is an **opt-in observer seam**, not a physical or complete QUAD generator.

## Implemented

`AdvancingFront::SetRefinedQuadtreeObserver(RefinedQuadtreeObserver)` accepts a synchronous `std::function<void(Quadtree&)>`. If installed, `AdvancingFront::execute` invokes it exactly after successful `quadtree->refineAccordingToNeighbors()` and before TRI `makeTemplateBasedMesh()`. Without a callback it follows the original TRI code path without additional allocations/calls. `MESH_ELEMENT_KIND=quad_uv` in the production CLI remains explicitly blocked by M3-1 before global runtime state is changed.

The test exercises an actual closed-boundary `AdvancingFront` using a **test-only** depth cap of three levels. Its active observer invokes the integrated `CaptureLeafPolygons` without choosing points or emitting any QUAD. The callback deliberately throws; the test requires one invocation at the correct stage, no prematurely published TRI template objects, and safe exception propagation/destruction. A disabled-observer case runs and produces a real TRI mesh.

## Native and scientific evidence

- Exact reviewed head `cd5825c19d976be0b9197428d8e77cc79b51c897`, [GitHub Actions run #42689321763](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42689321763): **four jobs SUCCESS**.
- Linux GCC QUAD 4/4 CTest and Windows MSVC QUAD 4/4 CTest, each including `quad.refined_observer.contracts`.
- Serial TRI baseline 75/75 CTest, 527/527 Python tooling and seven/ seven existing M3-1 real-CLI denial cases.
- Independent Eistute (five states) and Book (four states) reference comparison: byte-identical OBJ output, equivalent accepted/rejected decisions and verified boundary-incidence coverage.
- The merge commit `43809cd03578eb03cdfb76b9b150a040ebf13288` is a two-parent merge with the **exact same tree** as the reviewed head. Modernization `main` is unchanged at `f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94`.

## Failed prefix retained

The first synthetic test used an unrestricted null-curve boundary and provoked a 30-second Linux timeout and an MSVC crash on the former candidate; the original CI source-diff guard also rejected the unlisted AFT paths. The fix was **only** a depth cap inside the test fixture and an explicit review-scope whitelist update; the actual production quadtree refinement policy and scientific oracles were not modified. The previous failed/cancelled runs remain accessible.

## Non-claims and open gate

The callback receives legacy mutable `Quadtree&`. **Read-only is a caller contract and verified behavior for the tested bridge**, not a C++ `const` guarantee. It cannot retain a tree pointer beyond the synchronous call and must not mutate/rewire source owners. Future integration should prefer value-owned immutable capture and narrow the observer API.

No centroid/interior-point rule was approved, and the CLI does not generate QUAD output. Boundary leaves remain excluded from the current UV bridge; the existing standalone disk validator and later physical/multipatch/adaptation milestones are unchanged. Full ASan/LSan/CRT and allocation-fault campaigns remain unqualified.

**Next:** close the exact merged-commit CI gate, then implement M3-3: value-only patch-level capture registration from the generator without touching the default TRI publication/acceptance path. Preserve source owners, timestamps, patch order, and error/rollback semantics.
