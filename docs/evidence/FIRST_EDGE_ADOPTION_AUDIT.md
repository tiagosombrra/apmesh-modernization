# First new Edge adoption in makeMesh

Source: qualified main `649f87759af7a0c749283727598113662464451e` (PR #119).
Classification: source-preserving diagnosis and documentation-only delivery.
No production repair, new numbered memory slice or scientific change is included.

## Ownership boundary and observed failures

The first missing edge in makeMesh is constructed by the original
`new Edge(e->getV1(), best, ++lastEdgeId)` expression. The caller then appends
observations to both endpoints before innerEdges.push_back establishes ownership.
Later edges/queue/cell publications observe that already-owned object. The
AdvancingFront destructor detaches borrowed endpoints before deleting innerEdges.
Edge's own destructor otherwise deletes its endpoints and its two distinct caches.

Complete denials reproduce retention after construction when either adjacency
insertion or owning-list publication throws. At these three boundaries, the
Edge and caches have no owner; a published endpoint observation may also remain.
Later measured publication failures retain a valid owner and do not reproduce
this pending-object retention. Constructor denials unwind without that retention.
Consumed IDs and committed Face prefixes are preserved, not rolled back.

In the measured ABIs, GCC retains three requested blocks/272 bytes (112 + 80 +
80). MSVC native allocation observation and actual Debug CRT each measure five
blocks/296 bytes. A separate native construction measures 120 + 48 + 40 + 48 +
40 bytes: Edge, two caches and their two empty-set nodes. Windows ASan is used
for invalid-access controls, not as a leak detector or whole-process memory gate.

## Native matrix and negative evidence

The fixture calls actual makeMesh and its native selector without overriding
selection or substituting the algorithm. Sixteen contexts combine both source
queues, topology/prepared geometry, both stored boundary-sorting flags and
zero/one committed Face prefix. A nondegenerate closed quadrilateral reaches
the first new edge and completes normal triangulation into two Faces. The
optional prefix is committed through a separate real native call. The sorting
flags do not establish execution of public-wrapper sorting.

The observation adds seven allocation-free, exactly reversible source changes.
Thirteen other native translation units remain unchanged. Each profile denies
every scoped allocation, including adjacency, owner/view lists, the active queue
and cell publication: nine GCC allocations and eleven MSVC allocations. Actual
borrower IDs/coordinates/adjacency, prefixes, Face ordering/area/midpoint, IDs,
free state, queues, cell observations and object/cache retirement are checked.

| Observation | Native processes |
| --- | ---: |
| Normal observed execution | 48 |
| Construction unwind | 208 |
| Original failed pending-ownership contract | 144 |
| Later already-owned partial publication | 144 |
| Unobserved normal execution, exactly compared | 48 |
| Explicit caller cleanup control | 144 |
| Actual wrong-deleter borrower destruction detected | 144 |
| Actual stale-adjacency ASan access detected | 16 |
| Independent allocation/leak/UAF instruments | 7 |
| Total | 903 |

Explicit caller cleanup removes both adjacency observations, detaches borrowed
endpoints and deletes the pending Edge/caches. Those controls demonstrate zero
measured retained storage; they are not production RAII cleanup qualification.
The invalid plain deleter actually destroys borrower index 4 and exits before
an unsafe read/repeated deletion; it does not establish complete teardown.
The detach-only negative leaves a real endpoint adjacency and consumes its freed
Edge, producing actual ASan heap-use-after-free. Fifty-one field corruptions are
independently rejected by the diagnosis checker.

The open-front pilot, symmetric closed-front fixture rejection and order
inspection remain preserved under build/first-edge-adoption-audit/. They are
preparation, not positive target coverage. The corrected matrix initially stopped
after 281 cases because its checker incorrectly expected 288 MSVC retained bytes.
That failed report, original checker and raw cases remain immutable. Independent
ABI measurement explained 296 bytes; the completed matrix rechecks/reuses all
281 cases and executes only the missing 622. The separate ABI probe's initial
missing-ASan-runtime launch and verifier's seven-versus-eight hook-count mistake
are retained preparation failures, not production failures or numerical results.

## Retained evidence and next repair gates

Full local sources, commands, process logs, executable hashes and prior failures:
`build/first-edge-adoption-audit-corrected/`. The completed observations are in
matrix-resumed/report.json; verification.json seals their identities, all 2125
unchanged tracked files, 51 rejected corruptions and the prior qualified main
campaign. The compact [summary](stage3/first_edge_adoption/summary.json) retains
source/report/tool/executable hashes and the completed outcome inventory.

Commands used in that directory include prepare.py/assemble.py, the three native
CMake profiles, build_profiles.py, the original interrupted run.py, resume.py
and verify.py. The original campaign remains unchanged. The prior main campaign
contains 69 CTest contracts, 252 Python tests, 397 shortcut-native outcomes, nine
scientific states, 45 artifacts and 123 boundary-incidence comparisons; those
are retained prior qualification, not newly executed repair gates.

Next single implementation: immediately own the original first Edge expression.
Its nonallocating deleter must remove endpoint observations before detaching
vertices and destroying the unadopted object/caches. Release only after the
original innerEdges.push_back succeeds. Preserve new-expression ID timing,
native selection, endpoint order, allocation/publication order, normal traces
and later already-owned partial states. This is a behavior-changing exception-
safety/ownership defect repair, without changing formulas or scientific policy.

Before repair integration, require complete actual native denial sweeps in all
contexts, live borrowers and no stale adjacency at the catch, actual object/cache
frees and zero cleanup allocations, preserved prefixes/IDs, original retention
and actual invalid-deleter/detach-only controls, exact normal comparisons and
checker/preparation negatives. Require local regression, independent physical/UV
quality and positive boundary comparison for all nine frozen states/45 artifacts,
source reversal, scoped analysis/format/inventory gates on the exact repair head,
remote continuity audit, and revalidation on merged main.

The second missing edge, arbitrary topology/orientation/endpoint aliases, public
wrapper sorting, complete retry/rollback, whole-process/parallel, LSan/UBSan and
quality/performance improvement remain unqualified. Stage 3 stays open with 37
numbered qualified slices. Stages 0-2 remain closed for measured scope; stages
4-11 remain pending. The relative-area experiment stays negative; inverse-direction
trials remain unapproved and unexecuted.
