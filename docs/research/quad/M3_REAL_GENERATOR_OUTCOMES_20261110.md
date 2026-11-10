# M3-6c — actual hooked GeneratorAdaptive runtime outcome contract

**Merged in research `quad-templates` via PR #193; exact feature-head CI passed. Post-merge CI is tracked separately.** This fixture executes the real serial `GeneratorAdaptive::Execute` with hooks installed by the research test process, using the pinned Eistute article configuration relocated into a temporary directory. It does not alter the production CLI, and the historical TRI regression/scientific comparisons remain independent mandatory gates.

The provider observes real refined Quadtree roots and copies their **leaf count only** to a value-owned placeholder. It does **not** reconstruct a complete QUAD mesh, choose centroid/interior points, or certify geometry. The sink tracks provisional UV observations, and a second sink tracks local Adapter selections using the session/epoch key.

The test reads the real `GlobalOutcomeLog` **after** `Execute` returns, requiring: a completed TRI run, non-truncated trace, monotonic outer epochs, at least one post-commit `AcceptedStepCommitted` and one post-restore `RejectedStepRestored`, active Quadtree observations and correlations from local selections back to observed outer epochs. It counts budget/growth evaluation events but does not require either if the original article policy does not trigger them. The test intentionally avoids changing frozen numerical thresholds to force an event.

Build target: `quad_generator_outcome_probe`, linked only to existing `ap_mesh_engine`, registered with a Python relocation wrapper as a serial-only CTest. It must not be compiled or invoked from the shipping `ap_mesh` executable. Eistute/Book scientific proofs of OBJ identity are still run separately by the existing GitHub Actions baseline. Unqualified: full concurrent OpenMP runtime, MPI, sanitizer/allocator fault campaigns, historical numerical point rule, positive physical QUAD, complete boundary and multipatch/adaptation.

## Audit receipt — 2026-11-10

Exact reviewed head `ab91727c555c222f4a3e95143522615fa16522ca`, [CI #42823072772](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42823072772): all four jobs passed; root TRI 77/77 CTest, Python 527/527, Linux/Windows native QUAD 4/4 each, and frozen Eistute/Book 5/4 equivalence. Merged as `131623d1fb39350d90779d61a0255b35fecb3dea`; [post-merge #42825582252](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42825582252) queued at checkpoint. No approved physical QUAD or centroid.

## Exact M3-6c post-merge closure — 2026-11-10

[GitHub Actions #42825582252](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42825582252) completed **SUCCESS** all four jobs on merged SHA `131623d1fb39350d90779d61a0255b35fecb3dea`. The former queued status is retained in [evidence](evidence/M3_REAL_GENERATOR_OUTCOMES_20261110.json) as prior state. Subsequent cross-model work is tracked in [M3-6d](M3_CROSS_MODEL_OUTCOMES_20261110.md).
