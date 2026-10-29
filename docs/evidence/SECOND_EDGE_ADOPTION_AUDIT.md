# Second new Edge adoption in makeMesh

Source: qualified main `4c6f80fd5a8f23ed3e8ccfd172987392a96abfa3` (PR #121).
Classification: source-preserving diagnosis and documentation-only delivery.
No second-edge production repair or new numbered memory slice is included.

## Ownership boundary and observed failures

After handling the first lateral edge, makeMesh constructs its missing second
edge with the original `new Edge(best, e->getV2(), ++lastEdgeId)` expression.
It inserts observations first into e's second endpoint and then best, before
innerEdges.push_back establishes ownership. The separate edges list, active
front/rejected queue and cell publication follow. The owner destroys registered
edges with borrowed vertices detached. Edge's own destructor otherwise deletes
its endpoints and two distinct caches.

Complete scoped denials reproduce pending Edge/cache retention when either
endpoint insertion or owner-list publication throws. A partially published
endpoint observation may also remain. Constructor denials unwind without that
retention. Later measured observer/queue/cell failures retain a valid owner and
are distinct already-owned partial states. Consumed IDs and committed prefixes
are preserved rather than rolled back.

The same pending failure occurs both with an existing first side and after the
first new Edge has been fully adopted and published. The latter remains owned,
viewed and registered in its cell, with actual live endpoint/cache values and
two endpoint observations. Its identity/free state and eventual exactly-once
retirement survive the second-edge failure. This is measured prefix preservation,
not a whole-operation rollback or retry result.

GCC retains three requested blocks/272 bytes for the pending Edge and caches;
MSVC native allocation observations and actual Debug CRT retain five blocks/296
bytes in the measured ABIs. Those footprints agree with the unchanged native
types qualified in the preceding first-edge work. Windows ASan is used for
invalid-access controls, not as a leak detector or whole-process memory gate.

## Native coverage and negative controls

The fixture calls actual makeMesh and its native selector without substituting
branches, selection or an alternative generator. A closed quadrilateral selects
the existing first side and a missing second diagonal. A closed concave pentagon
selects the same local triangle while creating and adopting its first diagonal
before reaching the missing second one. The normal paths finish with two/three
Faces respectively. The prefix is a separate triangle committed by a real native
call before target injection.

Thirty-two contexts combine those two first-edge states, both source queues,
topology/prepared geometry, both stored sorting flags and zero/one committed
Face prefix. Sorting flags exercise the native insertion branches; they do not
establish public-wrapper sorting coverage. The fixed polygons have distinct live
endpoints and a uniquely selected highest-angle target. Independent expected
Face endpoint orientation, midpoint/area, sequential IDs and actual adjacency
are checked. Remaining Face rotations/order are retained exactly in the normal
comparison with the unobserved caller.

Seven allocation-free observation changes reverse to every original production
byte; thirteen other native translation units remain unchanged. GCC, MSVC ASan
and actual Debug CRT compile the same C++17 fixture. Each profile denies every
scoped allocation: nine with GCC and eleven with MSVC, including construction,
both adjacency insertions, owner/view lists, active queue and cell publication.
At each denial actual live owners, borrowed vertices, endpoint observations,
first-edge caches/state, committed Faces, original IDs and partial queues/cell
publication are checked.

| Observation | Matrix processes |
| --- | ---: |
| Normal observed execution | 96 |
| Construction unwind | 416 |
| Original failed pending-ownership contract | 288 |
| Later already-owned partial publication | 288 |
| Exact normal unobserved comparison | 96 |
| Explicit caller cleanup control | 288 |
| Actual wrong-deleter borrower destruction detected | 288 |
| Actual stale-adjacency ASan consumption | 64 |
| Independent allocation/leak/UAF instrument controls | 7 |
| Total | 1831 |

Exactly 144 of the 288 pending failures have a freshly adopted first Edge.
Caller cleanup removes both endpoint observations, detaches borrowed vertices
and deletes the pending Edge/caches under an allocation-forbidden hook. Actual
post-cleanup borrower/adjacency and first-edge state survive, and measured
retention is zero. These are explicit external controls, not production RAII
cleanup qualification.

Plain deletion actually destroys borrower index 7; the fixture exits before
unsafe consumption or repeated deletion. Those exits do not establish completed
teardown or storage retention. Detach-only cleanup leaves a real endpoint
observation; 64 ASan cases consume that expired Edge through its actual entry
and must produce heap-use-after-free. A separate allocation denial, deliberately
retained Vertex and independent UAF exercise the instruments. All 189 deliberate
observation corruptions and 14 missing/ambiguous source-anchor corruptions are
rejected. Zero coverage or undetected controls are not accepted as validation.

Four normal pilots and 42 denial calibrations are retained separately; the
1831 count is the completed matrix. No rejected preparation or native observation
was replaced to obtain these outcomes. None of these fixtures is an article
experiment or a mesh-quality improvement claim.

## Evidence and next repair gates

Full sources, commands, logs, binary identities and calibration are retained in
`build/second-edge-adoption-audit/`. matrix/report.json contains every native
command/exit/raw-log hash. verification.json checks the complete ordered case
inventory, original source reversal, all 2136 unchanged tracked files, 66 raw
article files and the preceding qualified main evidence. The compact
[summary](stage3/second_edge_adoption/summary.json) retains counts, source/report/
tool/binary hashes and the fixed fixture coordinates.

The prior PR #121 main campaign retains 70 CTest contracts, 286 Python tests,
1335 first-edge native outcomes, nine scientific states, 45 artifacts and 123
boundary-incidence comparisons. Those are prior qualification, not newly run
second-edge repair gates. This diagnostic delivery changes documentation only;
required local delivery checks and any subsequent main revalidation belong to
its delivery record.

Next single implementation: immediately hold the original second Edge expression
in an exclusive pending owner. Its nonallocating deleter must remove observations
from both live endpoints before detaching borrowed vertices and deleting the
unadopted Edge/caches. Release only after the original innerEdges publication
succeeds. Preserve the existing/freshly adopted first Edge, committed Face
prefixes, new-expression ID timing, endpoint/selector/normal allocation order
and all later already-owned partial states. This future change is a behavior-
changing exception-safety/ownership defect repair with unchanged successful
scientific behavior.

Before repair integration, require full native denials in all measured contexts,
actual nonallocating production cleanup and live borrower/adjacency/first-edge/
Face-prefix checks, preserved original failures, actual invalid-deleter and
detach-only controls, exact normal comparisons and adversarial checkers/source
preparation. Require exact-head local regression, scoped analysis and invalid
analyzer controls, source reversal, format/inventory/staged gates, fresh nine-
state/45-artifact article regression with independent physical/UV quality and
positive boundary comparisons, remote continuity audit and merged-main
revalidation. A missing or failing required gate blocks repair integration.

Arbitrary topology/orientation/endpoint aliases, public-wrapper sorting, earlier
vertex construction/adoption, complete retry/rollback, whole-process/parallel,
LSan/UBSan and performance/global quality remain unqualified. Stage 3 remains
open with 37 numbered qualified slices; this diagnosis adds none. Stages 0-2
stay closed for measured scope and stages 4-11 remain pending. The relative-area
experiment stays negative; inverse-direction trials remain unapproved/unexecuted.
