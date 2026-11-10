# M3-5 — real Adapter patch fixture, not a mock

The regression candidate introduces a serial-only root CTest `quad.adapter.real_patch_capture` using the production `ap_mesh_engine` and the **actual** `Models3d::ModelBaseQuadrada` patch with a real `BuildInitialSubMesh` TRI seed. The test links `quadtree_quad.cpp` and `uv_mesh.cpp` **only** into its test executable, not into `ap_mesh`.

Two bounded scenarios call `Adapter::AdaptDomain` on the patch with quadtree depth capped at 3: (1) a successful TRI patch attempt with real `CaptureLeafPolygons` and a `SelectedForAdapterReturn` decision; (2) a provider/sink observation interrupted by a deliberate exception before any TRI local selection, ensuring the former coarse patch binding is retained. Each snapshot must contain nonempty value-owned UV polygons, remain provisional, and retain its step/patch/retry/attempt identity. The default production execution does not install hooks.

**Completed M3-5 scope:** The final positive fixture demonstrates **three actual local Adapter attempts**, three corresponding UV snapshots, **one selected** and **two superseded/failed**, returning 30 TRI elements. A separate real abort scenario records one UV snapshot and zero selected decisions or generated meshes. This is **patch-local**, not global GeneratorAdaptive acceptance. The original single-attempt-only scope was superseded by evidence from the actual retry path. Scientific centroid, physical QUAD elements, boundary closure and global generator acceptance remain blocked.

**Quality gates:** exact-feature-head CI on root CMake's **76 CTest** (historical 75 plus this new real-Adapter test), 527 Python, seven CLI negatives, and Eistute/Book exact scientific parity; standalone QUAD Linux and Windows MSVC retain four native tests. OpenMP syntax checks do not prove parallel execution. Never merge with a failing test or simply loosen the timeout.

## First segmentation fault diagnosed using the actual CI stack

The initial live Adapter test **failed** in `CurveAdaptiveParametric::SortPointsByParameters()` at PR-head CI [#42793750717](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42793750717). The test incorrectly bypassed the prerequisites normally installed by `GeneratorAdaptive`: `ptr_aux.resize(size_thread, nullptr)` and the per-curve `parameters_` produced by adaptation. The GDB stack shows the illegal indexing of the empty sort-scratch vector before any UV provider invocation. The revised fixture uses a scoped restore of `ptr_aux` with one serial slot and supplies the two authentic coarse-curve parameter endpoints `{0,1}` to each of the four real patch curves. This is **test setup only**; no production algorithm, acceptance or scientific point rule is changed. The repair must pass the exact-head 76 CTest gate before integration.

## Qualification and integration — 2026-11-10

The test fixture changed without weakening the historical QUAD/triangular scientific oracles. Test-local `AftConfig::ratio=0.15` generates adequate real quadtree interior cells; production defaults and `CaptureLeafPolygons` remain unchanged. A previous forward-declaration build failure was corrected by including `application/generation_context.h`. A later failed fixture assumption `local_attempt==0` was replaced with **real multi-attempt provenance** and exactly one local selection constraint.

[Final feature-head Actions #42808140065](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42808140065) completed SUCCESS (4 jobs): QUAD Linux GCC 4/4, Windows MSVC 4/4, full root TRI 76/76 CTest, 527 Python controls, seven CLI negative tests and frozen Eistute/Book five/four-state scientific equivalence, exact OBJ bytes and verified boundary incidence.

Reviewed PR [#190](https://github.com/tiagosombrra/apmesh-modernization/pull/190) merged as `536c94009ea8b6a3a613886dfdf93314f94c91f6` (identical source tree as tested feature). [Post-merge Actions #42809300817](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42809300817) was in_progress at this checkpoint. [Machine-readable evidence](evidence/M3_REAL_ADAPTER_FIXTURE_20261110.json).

**Important:** No positive QUAD application mode, no approved numerical centroid and no physical/full-boundary quadrilateral mesh. No global accepted/rejected GeneratorAdaptive status or OpenMP runtime/sanitizer proof has been inferred.
