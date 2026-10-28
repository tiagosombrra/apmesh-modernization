# Angular selection temporary ownership

Classification: behavior-changing exception-safety defect repair, preserving
successful numerical behavior. Base: main
`f37ea32f00e223c725b81a7c0eba6852aee0701b` (PR #114 integrated and revalidated).
Stage 3 stays open; this is one bounded obligation, not a new full-stage closure.

`AdvancingFront::findBestVertex` allocated two temporary native `Vertex` objects
without pending owners. Failure while constructing the second retained the first
after fixture teardown. The immutable original diagnosis is retained under
`build/front-angle-audit/`: three failed clean-unwind contracts, three normal
selections, three balanced first denials, two actual instrument controls and ten
checker corruption detections. Its original source SHA-256 is
`1b6d11c5bfdcadd279c19039c20cfb749d2ce6dc37ae4745465e9d2d18985ae9`.

The repair gives each temporary a local `unique_ptr`. Both original construction
expressions remain in order. Borrowed arguments use `get()`. Explicit resets at
the original cleanup location preserve successful deletion order: first `v1`,
then `v2`. Exceptions reclaim every fully constructed temporary. No public API,
object layout, arithmetic, comparisons, tolerances, candidate traversal, tie
policy, front/quadtree/template, boundary synchronization or adaptation/acceptance/
stopping policy changes. Explicit canonical formatting is a separate mechanical
operation in the same delivery. Reversing the six ownership edits must reproduce
the formatted pinned original exactly, including all other code and comments.

## Targeted qualification

The actual protected method is called through a derived fixture with all fourteen
native production units, without geometry/math replacements. Reversible hooks
observe only the temporary construction/selection/release window. Five nonempty
layouts cover one candidate, symmetric ties in both orders, a later strict angle
improvement and an attached-root geometry-phase selection. The latter is a bounded
prepared-root caller, not general quadtree/template generation qualification.

For each compiler profile, calibrate the actual normal allocation count and deny
every ordinal. GCC has two allocations; MSVC has four, including native container
storage. Require propagated `bad_alloc`, complete release and zero retained
storage after fixture teardown. Compare original/candidate successful traces
exactly: candidate identity, final vector components, selected maximum angle,
allocation count and outer-object deletion order. Independently recompute vector/
angle expectations. Original second-object denials must remain failed clean-unwind
contracts; reproducing those failures does not validate original cleanup.

Use native GCC allocation observation, MSVC ASan and Debug CRT checkpoints. Actual
ASan use-after-free, deliberate retained native storage and independent allocation
denial controls must be detected. Windows ASan is not a leak detector; retention
claims use CRT or the explicit allocation ledger. Twelve checker/preparation tests
challenge corrupt traces and missing/ambiguous observation anchors.

Retain commands, complete build/test logs, executables and source/report hashes
under `build/front-angle-repair/`. Initial compilation exposed an ambiguous test
symbol (`count`, colliding with inherited `std` imports); the fixture now uses
`record_count`. Canonical formatting also exposed an overly narrow preparation
anchor; it now accepts declaration whitespace. Both preparation failures precede
qualification and do not constitute native candidate failures. Initial static
analysis detected the deliberately invalid ASan control in the combined fixture.
That control now lives in `uaf_control.cpp`, where the exact analyzer diagnostic
and nonzero result are required. Production and positive fixture analysis must
pass without disabling or suppressing any diagnostic.

## Delivery gates and limits

Before integration, require exact-head CTest (65 contracts, no skips), all 194
Python tests, native original/candidate sweeps and instrument controls, full
changed-unit/positive-fixture lint plus the detected invalid control, canonical
format, whitespace, staged bytes and updated
architecture inventory. Seal original diagnosis files and protected scientific
inputs. Run fresh Eistute/Book serial experiments: all nine attempted mesh states,
45 scientific artifacts, physical/UV quality, boundaries and accepted/rejected
decisions must match the qualified PR #114 main outputs. Recheck remote main,
all branch heads, open PRs/statuses/checks and revalidate main after merge.

Initial profile comparison passes 137 expected outcomes: 65 repaired normal/denial
cases, 65 original cases (25 failed clean-unwind contracts retained) and seven
actual instrument controls. Fifteen successful native traces match exactly across
the three profiles. Exact delivery results belong to the PR and its
revision-bound local report. A green initial profile alone does not qualify
integration. No mesh-quality improvement, performance, whole-process allocation,
parallel, LSan/UBSan, general rollback/retry or every angular tie branch claim is
made. Earlier temporary `Face` construction with borrowed endpoints, pending
edge/face adoption and failed-tree observer reuse remain unqualified. The next
single diagnosis after integration is the borrowed-endpoint `Face` lifetime in
`interceptionTest`, before proposing another repair. The relative-area experiment
remains negative; inverse-direction trials remain unapproved and unexecuted.
