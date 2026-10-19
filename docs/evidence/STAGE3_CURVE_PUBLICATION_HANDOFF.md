# Stage 3 slice 15: Generator curve sample publication

Issue #50. Entry main 4a69a037eef3f258675771c0cc03d9cb0373f745. Entry's 530
qualified inputs match slice-14 implementation-main; the existing full report
is reused with hashes, without claiming a fresh entry campaign.

Per-curve publication now parks original point/parameter list nodes after all
entry preparation, snapshots cache values and owns both returned lists before
allocating point-observer copies. The curve pass, surface pass and optional
target rebuild retain their order and numerical inputs. Rollback erases only new
cache keys, restores existing values in place, deduplicates/deletes new samples
without allocation and restores original point/parameter nodes. Entry samples
and preexisting cache values stay borrowed, including shared endpoints. Rebuild
may already have deleted discarded surface interiors; rollback never consumes
those stale curve observers. Commit deletes superseded first-pass samples and
transfers final samples to the existing collective graph lifetime. The unused
result-vector storage and late allocating keep-set are removed explicitly.

Publication 139/139: 54 normal ASan/CRT outcomes, 27 positive calibrated sweeps
denying 2403 allocations, 54 controlled upstream abort/restore/retry outcomes,
and four list-move/UAF/leak/hook controls. Every denied ordinal propagates once;
attempts equal ordinal+1, requiring allocation-free rollback. Final denied
publication follows all expected ID requests, including growth/shrink/equal/no
rebuild, cached/closed/reversed/two-endpoint and alias-overwrite fixtures across
three actual curve types. Independent interior polynomial geometry and borrowed
scalar/adjacency state, point/parameter/cache entry identity and successful retry
are required. Consumed IDs stay consumed; cached two-endpoint first passes
correctly request zero. All 54 normal complete original/repaired traces match.

Original: 27 allocation sweeps and 54 controlled upstream aborts stop at the
first partial-publication assertion; later unsafe observer consumption, later
ordinals and CRT retention in aborted cases are unmeasured. Other 58 outcomes
are expected. Sixteen pinned production units plus a verified publication-block
adapter are compared against seventeen actual candidate units plus the actual
publication template. Callbacks use actual sample/rebuild units, controlled
parameters and a controlled upstream point-list reversal; full historical
Generator/Adapter TUs and upstream numerical selection are not instrumented.
Original unused storage is rebound to a one-curve vector initialized within the
fixture operation; allocation timing/counts/bytes/peak storage change explicitly,
without a performance claim. Only the new target consistently disables optional
NRVO and Debug iterator metadata, retaining actual CRT heap and negative controls.

Required prior batteries: samples 88/88, rebuild 117/117, snapshots 89/89,
sync 73/73, adoption 53/53, copy 30/30, curve 19/19, UV 81/81, node 7/7.
CTest 25/25, zero skips, 74 Python controls; new-unit read-only lint, explicit
formatting and inventory pass (133 production files, 62 units, 71 headers;
22 contracts/113 anchors; existing six-header cycle retained). Two repetitions
per Eistute/Book preserve all nine attempted OBJ/acceptance/rejection/incidence
states, 189 CSV fields and 1,168/4,256 last-accepted triangles exactly.

Classification: behavior-changing ownership/exception-consistency defect repair
on failure paths, with success-preserving engineering consolidation. No scientific
formula, float order, numerical selection, synchronization, quadtree/templates,
front reconstruction, tolerance, budget, verifier or adaptation/acceptance/stopping
change. Source/history/licenses are preserved. C07 and ADR-0016 delimit this
boundary; evaluator scratch, previous successful curves, initial graph cleanup
and full Adapter/AdaptCurve/patch/mesh/history/budget rollback remain unqualified.

Candidate, exact published-head and implementation-main qualification pass through PR #51; see STAGE3_CURVE_PUBLICATION_HANDOFF_CLOSURE.md.
Commands, executable/source/complete Git-tree identities, all original normal
traces/partial-publication diagnostics and raw-log hashes are in
stage3/curve_publication/. All 534 qualified input bytes are recorded once.
Failed initial CMake ordering/cache configurations, the six-outcome fixture
zero-request assertion defect, valid preliminary 139-case coverage and a stale
inventory gate after explicit range formatting are preserved with raw-log hashes.
No failed record is relabeled as successful qualification. The final probe also
requires no allocation during rollback after each denial. Whole stage 3 stays open.
