# Interception Face borrower lifetime

Base: qualified main `f70f755a6aa466b6fe17d9e3bae7da7a5ef34f4b` (PR #115).
Classification: behavior-changing exception-safety/borrower-ownership defect repair.
Stage 3 stays open; successful scientific behavior and policies are preserved.

## Defect and bounded repair

The native interception caller attaches three caller-owned vertices to a local
Face. Its final `setVertices(nullptr, nullptr, nullptr)` allocates a new midpoint
before committing endpoint removal. On allocation failure, the original Face
destructor deletes all three borrowed vertices. The sealed original diagnosis in
`build/front-face-audit/` retains 111 outcomes, twenty failed borrower contracts,
eight actual ASan expired reads and fourteen checker corruption detections.

A local EndpointScope is created immediately after successful default Face
construction. Its nonallocating destructor calls DetachVertices before the Face
destructor on every exit. Keep both original setters, the containment loop and
all normal cache preparation/release locations. Reversing this four-line guard
must reproduce the qualified base source exactly. No public API, layout, arithmetic,
floating order, candidate/tie policy, comparison, tolerance, front/quadtree/template,
boundary synchronization or adaptation/acceptance/stopping change is introduced.

## Targeted contracts

Permanent native probes link fourteen actual production units. Original and
candidate share thirteen unchanged units; the original backend is pinned to Git.
Four reversible, allocation-free hook insertions observe the default constructor,
attachment, containment and final reset, including midpoint release order.
Probe-only owning handles for already destroyed original objects are quarantined
to record the failed borrower contract without another invalid deletion. Candidate
cases must have zero quarantined handles; this is never production cleanup.

Four nonempty layouts cover outside, inside, boundary and equal-coordinate alias
filtering. Two additional cases cover disabled Face tests and prior edge crossing;
these are guard-only, not positive Face lifecycle coverage. Every calibrated
allocation is denied: three with GCC and six with MSVC, including native container
storage. Debug fixtures consistently use release iterator metadata. Require exact
exception propagation, all five owner identities/coordinates and the actual
two-edge adjacency of each of the three borrowed endpoints. Candidate callers
read all three vertices after normal return and every exception before cleanup.

Normal original/candidate observations must match exactly, including decisions,
midpoint, allocation count and cache release order. Preserve all twenty original
failed contracts and eight separate actual ASan expired reads. The corrected
cases must preserve every borrowed object and finish owner cleanup once. Debug
CRT and the native allocation ledger measure retention; Windows ASan makes no
leak claim. Independent allocation-denial, retained-storage and actual ASan UAF
controls must be detected. Twelve checker/preparation tests reject corrupt
lifetime, numeric, adjacency, allocation and release traces or ambiguous anchors.

## Delivery gates and limitations

Retain complete commands/logs, original failures, source/executable identities and
reports under `build/front-face-repair/`. Require the C++17 build, 66 CTest entries
with no skips, 206 Python tests, full native original/candidate matrices, actual
instrument controls, production/positive-fixture analysis and expected detection
of the separate intentionally invalid UAF unit. Require canonical format,
whitespace, staged bytes, contract/inventory checks and source reversal. Run these
gates on the exact delivery revision before integration and revalidate main.

Fresh Eistute/Book runs must preserve all nine attempted states and 45 scientific
artifacts against qualified PR #115 main, with independent physical/UV quality,
accepted/rejected decisions and positive shared-boundary comparisons. Preserve
the original diagnosis and protected inputs. Audit remote main, all branch heads,
open PRs and configured checks; no hosted workflows are introduced. Exact delivery
results belong to the PR and its revision-bound report, not this initial scope.

This is a local borrower guarantee, not full adaptive rollback/retry, arbitrary
aliased endpoints, every topology, process-wide/parallel memory, LSan or UBSan.
No mesh-quality/performance improvement or unchanged whole-process allocation
claim follows. Other pending edge/face adoption, failed-tree reuse and outer
caller recovery remain unqualified. After integration/main qualification, the
next single diagnosis is pending Face adoption in makeMesh. The relative-area
experiment remains negative; inverse directions stay unapproved and unexecuted.
