# Geometry-phase front marker ownership

Base: qualified main `0c0a4d5a65eeb0b0989b361c38d58bc126d53065` (PR #117).
Classification: behavior-changing exception-safety/marker-ownership defect repair.
Stage 3 remains open; no scientific criterion or quality improvement is proposed.

## Defect and repair

The geometry-front makeMesh path constructs a raw default Edge as a queue marker.
Its ordinary marker branch pops and deletes it. Failed queue publication or later
allocation failure leaves the marker unowned: the front destructor clears its
observer queue without deleting that marker. The sealed original diagnosis in
`build/front-marker-audit/` retains 91 processes, 34 failed marker contracts,
60 measured denials, six unobserved/observed comparisons, seven instrument
controls and fourteen rejected lifecycle/state corruptions. GCC retains three
requested blocks/272 bytes; MSVC native observation and Debug CRT retain five
blocks/296 bytes in these ABIs. Windows ASan is not used as a leak detector.

The repair immediately adopts the original default Edge expression in a local
unique_ptr with a front-borrowing deleter. Nonallocating cleanup removes matching
marker observations from front before deleting the marker and its owned caches.
The existing raw marker remains the insertion/queue identity; reset at the
original delete point preserves ordinary consumption and destruction timing.
Construction failure leaves the owner empty. No other edge/vertex ownership,
front sorting, numerical expression, tolerance, boundary synchronization,
quadtree/template or adaptation/acceptance/stopping policy changes.

Reverse only the owner/deleter, original new-result adoption and normal reset to
require all base-source bytes. Queue state and committed Face prefixes remain
advanced on failure; this repair establishes no topology rollback or retry.

## Native scope and controls

Use actual native makeMesh(true,true) and findBestVertex, without selector
overrides or replacement generators. One/two complete existing-edge triangles
use real endpoint adjacency and a prepared native quadtree root. Downstream
two-triangle cases retain one already committed Face. Candidate, pinned original
and invalid mutations share thirteen unchanged native units plus the observed
actual advancing-front unit. Observation hooks are allocation-free and reverse
to every supplied source byte before any result is interpreted.

Require all four GCC/six MSVC marker construction/publication allocations and
all three GCC/four MSVC pending-Face allocations to be denied in both layouts.
Selection failure covers only its first allocation at the chosen first/second
invocation; later selection scratch failures remain separate. Require exactly
once propagation, actual marker/midpoint frees, zero retained marker payload,
zero remaining marker observers and no allocation during cleanup. Native owner
IDs, coordinates, adjacency, exactly-once vertex destruction, Face endpoints,
midpoint/area, queue/free-state and consumed Face ID timing must remain correct.
All normal original/candidate traces must agree, including allocation counts.

The required three-profile repair matrix contains 181 outcomes: 78 candidate,
78 original, twelve actual expired-observer detections, six actual premature
deletion detections and seven independent instrument controls. Preserve all 34
original failed contracts. Require 52 measured nonallocating candidate cleanups,
18 exact normal comparisons and 60 denial-state comparisons after excluding only
the intended marker retirement/ownership differences. Invalid controls detect
real freed-marker queue observations or destruction before consumption and exit
before unsafe access; they do not establish completed teardown or retention.

Fourteen checker/preparation tests challenge missing lifecycle observations,
cleanup allocations, owner destruction, publication/prefix timing and ambiguous
source anchors. Missing observation windows must fail, not become zero coverage.

## Exact delivery gates and limits

Retain commands, logs, sealed originals, source/executable identities and negative
controls under `build/front-marker-repair/`. Require C++17, 68 CTest contracts
with zero skips, 232 Python tests, all native matrices, source reversal,
production/positive-fixture analysis and expected analyzer detection of the
separate intentionally invalid UAF unit. Require canonical formatting,
whitespace, staged bytes and contract/source inventory gates on the exact head.
Fresh Eistute/Book must preserve nine states, 45 scientific artifacts and positive
boundary comparisons, with independent physical/UV quality and decision checks.
Preserve protected inputs and sealed diagnosis. Audit remote main, all branches,
open PRs and configured checks. Initial observations alone do not qualify
integration; delivery results belong to the exact revision/PR. Revalidate main
after merge before starting another bounded item.

The public makeGeometryBasedMesh sorting/three-edge shortcut is a source
observation, not executed wrapper-failure coverage. Arbitrary aliases/topology,
new-edge adoption, later selector allocation failures, full recovery/retry,
whole-process/parallel memory, LSan/UBSan and performance/quality claims remain
unqualified. Next after integration: diagnose the three-edge wrapper's Face
publication. The relative-area result stays negative; inverse-direction trials
stay unapproved and unexecuted.
