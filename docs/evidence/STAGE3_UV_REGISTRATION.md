# Stage 3 slice 4: pending UV registration and evaluation unwind

Issue #17. Entry main `c341ba7cb7b514b4073330e59ccef14d000e45de`, tree
`e8fa1c66bfbec903dfb57879f3b610a25d420e67` (746 blobs). Classification:
demonstrated engineering lifetime/context repairs. Full stage 3 remains open.

## Entry authority and reproduction

Remote main, twelve branches, open PRs/issues, checks and Actions were audited.
No concurrent work existed. All 744 available local text blobs match entry;
two immutable remote-only publication binaries remain preserved. No hosted
checks/Actions are configured or created. Entry CTest 12/12, 74 Python controls,
UV 35/35, node 7/7, selected five-unit lint and exact Eistute/Book repetition/
previous-slice comparison pass. Entry results remain distinct from this repair.

The target still compiles 14 real UV/curve/numerical units without production
stubs. Its separate 416-file original source/header/vendor snapshot is matched
against entry Git blobs. The same final 49-case probe/runner is used for original
and repaired sources. Original remains **failed in 12 cases**, while its prior
35 cases and new successful registration traces pass.

| Allocation/context control | Pinned original observation across the sweep | Repaired observation |
| --- | --- | --- |
| Boundary first vertex, 4 sites | Three blocks / 112 bytes retained; IDs change | No retention; unchanged state and successful retry |
| Boundary append, 14 sites | 56 blocks / 2,344 bytes; owners/IDs/adjacency change | No retention; unchanged owners/IDs/adjacency and retry |
| Boundary close, 10 sites | 21 blocks / 1,032 bytes; contour/adjacency/IDs change | No retention; contour start survives for retry |
| Face::quality temporaries, 36 sites | Invalid heap deletion during exception unwind | No retention; caller endpoint geometry preserved |
| Outer vertices, 164 sites | 123 blocks / 4,592 bytes retained | No retention; failed tree safely destroyed |
| Outer edges, 664 sites | 1,512 blocks / 74,304 bytes retained | No retention; failed tree safely destroyed |
| One actual type-1 template, 134 sites | Invalid-access process failure during sweep | Every measured failure unwinds; no retention |
| One actual type-4 template, 335 sites | Invalid-access process failure during sweep | Every measured failure unwinds; no retention |
| Unowned-cell Edge and Face subdivision queries | Separate ASan zero-page access violations; CRT failures | Both overloads report std::logic_error |

Eight new sweeps inject **1,361 allocation failures**, in addition to 53 primitive
and three transfer failures from previous slices. Counts are fixture/toolchain
observations. Boundary uses null curves; the prepared tree follows the real
front generate/refine sequence. Template types 1/4 are measured, not all six.
Valid CRT cases retain zero blocks/bytes. Deliberate UAF, duplicate deletion,
allocation-hook denial and a three-block/112-byte leak remain detected.

## Repair and explicit scope audit

Boundary guards pending vertices/edges, removes provisional adjacency on failure,
undoes an inserted edge node if vertex insertion fails, and commits IDs/start/
outgoing state only when registration succeeds. Successful creation and curve
evaluation order remain unchanged. Retry is measured for the null-curve fixture.

TemplateStorage preserves the original separate heap buffers, allocation and
registration sequence. It owns unregistered suffixes, tracks adopted prefixes
and cleans pending faces, edges and vertices in dependency order. Registered
prefixes remain at Quadtree. Outer creation and adjacency insertion use guards.
A template exception yields a destructible partial tree; partially published
observer views are not qualified for consumption or same-tree retry.

Face::quality guards its centers and detaches its stack edge's borrowed endpoints
on unwind. Its arithmetic and successful allocation/deallocation order remain.
Two null-owner subdivision overloads, discovered by the first full selected
lint run and reproduced independently with ASan, now reject missing context.
Valid owned-cell subdivision thresholds and decisions are unchanged.

Production scope: three implementations, two existing contract headers and one
new private helper header. The new helper is formatted in full and existing
production changes by range (34 replacements). Eight inherited pointer-only
NULL uses were reviewed manually; index zeros/comments are preserved. No
clang-tidy automatic fixes, suppressions, check changes or vendor edits.
The initial ten-error cell lint report remains evidence. An audit also restored
a locally misdecoded UTF-8 comment exactly from entry and repaired documentation
encoding; final source was rebuilt and requalified. See ADR-0005.

Scoring formulas/order, template selection, curve partitions, front/smoothing,
adaptation/acceptance/stopping, inputs, vendor and independent numerical
verifiers are preserved. The complete address-free successful UV trace (all
inner vertices, edges, faces, IDs, coordinates and order) matches original
byte-for-byte in both instruments. Measured successful allocation counts also
match the original, including template calibration before its failing sweep.

## Validation and failure history

GCC 16.1 serial C++17 Release, MPI/OpenMP/LTO off; CMake/CTest 4.4.3; LLVM
format/tidy 22.1.8; MSVC 19.44.35229 ASan and separate Debug CRT. Required normal
CTest now has **14 tests**, including registration and missing-context controls;
74 Python controls remain. Instrument qualification requires **49/49 UV** and
**7/7 previous node** cases. Selected lint expands to six real production units.
Inventory: 123 production files (57 units, 66 headers), five CMake inputs,
22 contracts and 92 anchors; the original six-header cycle remains open.

Article repetitions and strict entry/previous-slice regression retain all nine
attempted states, positive shared-incidence coverage, zero measured position
gap, exact OBJ/acceptance/CSV/incidence results and 189 matching named CSV fields.
Both accept steps 0/1; Eistute/Book retain **1,168/4,256** triangles. No oracle or
tolerance change. Candidate application SHA-256:
`f843a1e64a38bd70a03bcce8aed145dd8306ce6cfbb62786eabe078281f398e1`.
Exact published-head and post-merge closure gates remain required.

Original, entry and candidate reports, failed diagnostic excerpts, raw log hashes,
source identities and format ranges are under `stage3/uv_registration/`. Large
CRT object dumps stay local with hashes; excerpts are explicitly identified.
Two early template fixtures used Quadtree.execute, which adds uniform refinement
and reached no type-4 leaf. Their failure is retained as setup failure, not a
product defect. The final fixture follows AdvancingFront's actual generate/
refineAccordingToNeighbors sequence and keeps the positive type assertion.

Initial MSBuild compiler checks failed with a DirectoryNotFoundException in a
long TryCompile tracking path. Short build directories reg0a/reg0d work with the
same compiler/flags. Configuration log hashes and the failed lint report remain.
Process budgets are 180 seconds for exhaustive template/outer sweeps and 30 for
other instrument cases; these do not modify application stopping thresholds.

Build/runner/scientific commands follow STAGE3_UV_ALLOCATION.md. The original
standalone builds use AP_MESH_UV_SOURCE_ROOT pointing at the pinned snapshot.
Required normal commands include CTest, inventory freshness and selected tidy
for advancing_front, boundary, edge, face, quadtree and quadtree_cell.

## Remaining boundary

Next qualify earlier quadtree generation/subdivision failures and remaining
mutation/helper temporaries, then curve internals, sample/initialization and
rollback ownership. All template patterns, same-tree/front reuse, arbitrary
exceptions, full-process leaks, parallel modes, Linux LSan/UBSan, Decor Shelf
and every internal retry remain unqualified. Stages 0-2 are closed for measured
scope; stage 3 is in progress; stages 4-11 remain pending.
