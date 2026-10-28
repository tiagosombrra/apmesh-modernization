# Pending front Face ownership

Base: qualified main `f7df88a67a4db0fba0e57d685de83d91aba0cff2` (PR #116).
Classification: behavior-changing exception-safety/pending-ownership defect repair.
Stage 3 remains open; no scientific policy or mesh-quality change is proposed.

## Defect and repair

makeMesh constructs a raw Face before allocating its mesh owner-list node. If
publication throws, the completed Face/cache have no owner. The immutable original
diagnosis in `build/front-face-adoption-audit/` retains 75 matrix cases, one
separate preparation pilot, twelve failed publication contracts and fourteen
checker corruption detections. Initial ambiguous-anchor preparation failure is
preserved; the accepted observation copy reverses exactly.

The repair keeps the original direct new expression in an exclusive pending
unique_ptr. Its nonallocating deleter detaches borrowed endpoints before deleting
the Face and its owned cache. mesh.push_back receives the borrowed pointer; only
successful insertion releases the pending owner. A default Face deleter would
also delete caller-owned endpoints and is deliberately tested as an invalid
control. Preserve ++lastFaceId timing, including no increment when the first
allocation fails and consumed IDs on later failures.

Reverse only the pending owner, borrowed get and release to reproduce the entire
base source exactly. Constructor arguments, mutation/publication order, formulas,
floating order, selection, tolerance, quadtree/templates, boundary synchronization
and adaptation/acceptance/stopping policies stay unchanged. Existing committed
prefixes and advanced queue/free-state are retained; this is not topology rollback.

## Native scope and controls

The actual native selector and makeMesh run without overrides or replacement
generators, with fourteen actual production units. Candidate, Git-pinned original
and deliberately invalid deleter share thirteen unchanged native units. Three
reversible allocation-free observations surround construction and publication.

Six contexts cover front/rejected topology queues and prepared-root rejected-queue
geometry, each with zero or one adopted Face prefix. Existing native edges and
actual two-edge vertex adjacency are checked. Every scoped allocation is denied:
three with GCC and four with MSVC, including native container storage. Require
exception propagation, zero candidate pending storage, actual Face/cache frees,
live endpoint fields/adjacency and exactly-once final vertex-owner destruction.
Normal original/candidate state and numerical traces must match exactly.

The initial three-profile matrix has 193 expected outcomes: 84 candidate cases,
84 original cases, eighteen invalid-deleter detections and seven independent
instrument controls. Eighteen original publication contracts remain failed;
twelve reproduce the original topology diagnosis, six extend it to the prepared
geometry path. Candidate denials retain no pending storage. Original failures
retain 136 requested bytes with GCC or 144 bytes with MSVC/CRT in these ABIs.
Windows ASan is not a leak detector; use CRT/explicit allocation observations.

Invalid-deleter controls detect actual borrower destruction before any unsafe
read or repeated deletion, then exit with a diagnostic. They do not complete
teardown or establish retention. Twelve checker/preparation tests challenge ID
timing, prefix state, missing frees, corruption and ambiguous anchors. One initial
executor expectation wrongly required damaged endpoint index zero after a prefix;
the actual index is three. Preserve that failed preflight and its raw observations;
the corrected expectation changes no production or native fixture code.

## Required delivery and limitations

Retain complete commands, logs, originals, executables and source/report hashes
under `build/front-face-adoption-repair/`. Require C++17, 67 CTest contracts with
zero skips, 218 Python tests, all native matrices/controls, source reversal,
production/positive-fixture analysis, expected detection of the separate invalid
UAF unit, canonical format, whitespace, staged bytes and contract/inventory gates.
Run required gates on the exact delivery revision and revalidate main after merge.

Fresh Eistute/Book must preserve nine states and 45 scientific artifacts, with
independent physical/UV quality, decisions and positive boundary comparisons.
Preserve the sealed diagnosis and protected inputs. Audit remote main, all branch
heads, open PRs and configured checks. Exact delivery results belong to the PR
and revision-bound local report; initial profiles alone do not qualify integration.

New-edge adoption, front-based geometry failure/marker lifetime, arbitrary endpoint
aliases/topology, full rollback/retry, process-wide/parallel memory, LSan and UBSan
remain unqualified. No performance, quality gain, broad recovery or full-stage
claim follows. After integration/main qualification, the next single diagnosis
is the geometry-phase front marker lifetime in makeMesh. The relative-area result
stays negative; inverse directions stay unapproved and unexecuted.
