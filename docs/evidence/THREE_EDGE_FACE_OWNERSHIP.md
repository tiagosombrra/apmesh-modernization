# Three-edge public geometry Face ownership

Base: qualified main `2162dc87064b08f2bae3224ae1c96749eaa8fbbd` (PR #118).
Classification: behavior-changing exception-safety/pending-ownership defect repair.
Stage 3 stays open; no scientific criterion or quality improvement is proposed.

## Original defect and bounded repair

makeGeometryBasedMesh returns ADVF_EMPTY with fewer than three front entries.
With exactly three, it constructs a raw Face from the first/second/last edge's
first vertex and appends it to mesh. The branch returns before sorting or the
general makeMesh path. If mesh-list allocation throws, the completed Face/cache
are unowned. The sealed original diagnosis in `build/three-edge-face-audit/`
retains 292 processes, 36 failed ownership contracts, 132 original denials,
36 native unobserved comparisons, explicit caller cleanup, actual wrong-cleanup
damage, guard-only cases, seven instruments and twenty rejected corruptions.
GCC retains two requested blocks/136 bytes; MSVC native observation and actual
Debug CRT retain three blocks/144 bytes in these ABIs. Windows ASan is not used
as a leak detector.

The repair holds the original Face expression in a local unique_ptr immediately.
Its nonallocating deleter detaches borrowed vertices before deleting the pending
Face and distinct cache. The original mesh.push_back receives its borrowed
pointer; only successful publication releases ownership. Constructor arguments,
original new-expression ID timing, successful allocation/publication order,
sorting bypass, guard/return status and endpoint order stay unchanged. Reverse
only the owner/deleter/get/release to every original production byte.

This does not modify the separate qualified makeMesh Face/marker owners. No
formula, tolerance, synchronization, quadtree/template, front reconstruction or
adaptation/acceptance/stopping policy changes. Existing prefixes remain committed
and later allocation failures consume their original IDs; no rollback is added.

## Native contracts and controls

Call the actual public makeGeometryBasedMesh without overrides, substituted
branches, selectors or alternative generators. Twelve contexts combine three
cyclic native front orders, both sorting flags and zero/one committed Face
prefix. The prefix is itself published through the same public caller on a
separate owned triangle before target injection. Actual endpoint fields and
two-edge adjacency remain live until each real vertex owner destroys it once.
Face IDs, endpoint order, midpoint/area and front/free-edge state are checked.

Candidate, Git-pinned original and deliberately invalid production deleter share
thirteen unchanged native units plus the observed actual front unit. All source
observations are allocation-free and exactly reversible. Deny every scoped
allocation: three with GCC and four with MSVC, including native container storage.
Require zero candidate pending retention, one propagated exception, actual
Face/cache frees, correct prefixes/IDs and no allocation during cleanup.

The three-profile matrix requires 397 outcomes: 168 candidate Face cases and nine
candidate guard cases; the same 177 original cases; 36 actual wrong-deleter
detections and seven independent instrument controls. Preserve all 36 original
failed publication contracts and all 177 earlier observed original/guard traces.
Require 36 nonallocating production cleanups, 36 exact normal comparisons, 132
denial-state comparisons and nine guard comparisons. A guard returning ADVF_EMPTY
without entering construction is not positive Face-publication coverage.

The invalid production deleter omits endpoint detachment and actually destroys
caller-owned vertices after failed publication. A destructor observation stops
before an unsafe read/repeated deletion. These control exits do not establish
completed teardown or retention. Twenty checker/preparation tests challenge
borrower destruction, missing windows, geometry/order, counter timing, cleanup
allocation, guard-only classification and missing/ambiguous source anchors.

## Exact delivery gates and limitations

Retain complete commands/logs, original failures, source/executable identities and
prior diagnosis under `build/three-edge-face-repair/`. Require C++17, 69 CTest
contracts with zero skips, 252 Python tests, the full native matrix, source
reversal, production/positive-fixture analysis and expected detection of the
separate intentionally invalid UAF unit. Require canonical format, whitespace,
staged-byte and source/contract inventory gates on the exact delivery revision.
Fresh Eistute/Book must preserve nine states and 45 artifacts with independent
physical/UV quality, accepted/rejected decisions and positive boundary comparisons.
Preserve protected inputs and the original diagnosis. Audit remote main, all
branches, open PRs and configured checks; initial results alone do not qualify
integration. Revalidate merged main before beginning another bounded item.

General wrapper sorting/more-than-three execution, arbitrary topology/orientation,
endpoint aliases, new-edge adoption, complete retry/rollback, whole-process/
parallel memory, LSan/UBSan and performance/global quality remain unqualified.
After delivery, diagnose first new-edge adoption in makeMesh. The relative-area
result stays negative; inverse-direction trials stay unapproved and unexecuted.
