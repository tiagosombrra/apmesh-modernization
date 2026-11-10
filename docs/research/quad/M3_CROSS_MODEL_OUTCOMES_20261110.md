# M3-6d — cross-model real GeneratorAdaptive global event qualification

**Integrated in research `quad-templates` via PR #194; pre-merge exact-head CI passed. Post-merge CI separately tracked.**

The M3-6c Eistute real GeneratorAdaptive hook fixture is extended to run unchanged on the independently pinned **Book** article configuration. The new root CTest `quad.generator.real_global_outcomes.book` reuses the existing research-only executable and relocation wrapper. Neither original article thresholds nor the production TRI CLI are modified.

The probe additionally checks that at least one locally selected Adapter attempt has an outer (session, epoch, retry) key present in an actual global GeneratorAdaptive outcome. It continues to require that all locally selected events match provisional observations and that the bounded log did not truncate. These are **runtime event correlations**, not a numerical QUAD proof or physical mesh output.

The existing C++ probe currently requires accepted and restored TRI global steps, based on the observed Eistute runtime. The Book test is an independent experiment: if Book does not naturally emit a restored state, the failure must be audited against the unchanged model; do not modify model settings just to force a green test. Negative CLI/zero-hook behavior remains covered by separate historical regression.

Admission: root 78 CTest (including Book probe), Python 527, two platform QUAD native 4 CTest each, seven CLI rejects, frozen Eistute/Book scientific 5/4-state exact OBJ/acceptance/boundary equivalence, pre- and post-merge exact-head CI. Main remains unchanged. M1/M2/M3 partial; no physical QUAD, approved centroid, complete boundary, 3D mapping, multipatch, OpenMP runtime or sanitizer claim.

## Evidence closure

[CI #42826247691](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42826247691): SUCCESS four jobs; 78/78 TRI CTest, including actual Eistute and Book probes, 527/527 Python, 7/7 CLI rejects, QUAD GCC/MSVC 4/4 each and strict frozen 5/4 state parity. PR #194 merged as `abab2155896671c70cf370fd032edab865b942c8` without production changes. [Post-merge CI #42827666971](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42827666971) was in_progress at checkpoint. This does not select a centroid or publish QUAD.
