# Stage 3 slice 32: completed Bezier observer retirement

Status: bounded prepublication qualification complete. Required published-head
confirmation is recorded in the review PR; integration/post-merge gates pending.
Entry main: `061223689ad6d2caa15243dbcfa6a4e45ba7ce96` (PR #85).
Classification: behavior-changing lifecycle/observer defect repair, with no
scientific proposal. Stage 3 remains open; stages 4-11 remain pending.

## Root causes and bounded repair

Completed PatchBezier destruction left its expired address in borrowed curve
observer vectors. Zero retained heap bytes does not establish observer validity.
Remove all equal current-incidence entries without allocation, retaining every
other pointer in order. Curves must remain alive through patch destruction;
arbitrary replacement and foreign/copied publications are not repaired here.

Default Geometry move assignment released its destination curves before its
destination patches. This violates their dependent lifetime and can dereference
expired curves in a derived patch destructor. Move through a temporary Geometry
and swap each owner collection, then let reverse member destruction retire the
old patches before curves, vectors and points. Self move preserves the graph.

## Qualification obligations

The normal contracts include 576 retirement observations across three incidence
layouts, two surfaces, three retirement positions, empty/populated prefixes and
all direction masks, plus five Geometry destruction/move scenarios. Repeated
slots and degenerate tracking fixtures are lifetime guards, not geometric proof.

The isolated ASan/Debug CRT runner requires 126 expected outcomes, 19 measured
zero-allocation operations, actual UAF/leak/allocation-hook controls and an
independent prefix corruption control. ASan leaks are disabled; static Debug CRT
measures terminal retention. Both the preceding and updated original harness
retain 103 failing outcomes and 23 other expected outcomes. Actual ASan UAFs are
reproduced when consuming expired patch observers and during dependent Geometry
move destruction. Failed raw reports and the earlier probe version remain
separate and are not overwritten.

Six paired original/repaired live traces per compiler/instrument compare 576
patch records, 2,304 incidence records and 15,552 scalar observations. All actual
Parameterize/Qu/Qv bits, patch IDs and directions must match. This trace mode
clears registrations while patches remain alive to allow comparison with the
original; dynamic retirement is measured by the separate lifetime campaign.

The preservation audit checks six production files against immutable entry main.
Only the exact new removal API/body, completed destructor and Geometry assignment
are normalized. Every other API/layout, constructor and numerical token must
match; six independent lifetime/numerical mutations must be rejected. The earlier
constructor audit retains all constructor obligations and its four independent
mutations, normalizing only this exact separately checked destructor.

Required delivery gates include 45 CTest entries (the prior 43 plus observer
contracts and preservation), 74 Python controls, all prior 27 memory batteries,
the new battery, retained scalar/analytic comparisons, read-only selected lint,
explicit changed-range formatting, current inventory and twice-repeated exact
Eistute/Book accepted/rejected/incidence/CSV regression. Results and identities
must be recorded on the exact delivery revision before integration.

```powershell
. ./build/local-env.ps1
cmake --build --preset windows-gcc17 --parallel 2
ctest --preset windows-gcc17 --verbose
python tools/audit_bezier_observers.py --candidate-root .
python tools/qualify_bezier_observers.py --asan build/s32qa/RelWithDebInfo/bezier_observer_probe.exe --crt build/s32qd/Debug/bezier_observer_probe.exe --runtime '<qualified MSVC runtime>' --output '<new directory>'
python tools/compare_bezier_observers.py --original '<original probe>' --candidate '<candidate probe>' --original-root build/s32-original --candidate-root . --output '<new directory>'
```

## Observed prepublication results

The full campaign passes all 106 commands on the frozen 598-input manifest:
45/45 CTest, zero failures/skips, 74 Python controls and 28 memory batteries with
2874 expected outcomes. The new battery passes 126/126 with 19 zero-allocation
operations. Six actual GCC C++17 live trace pairs and twelve MSVC ASan/CRT live
trace pairs match. The new six preservation mutations and the earlier four
constructor mutations are rejected; all prior batteries, numerical/analytic
comparisons and 1040 retained scalar sequences pass.

Two repetitions each of Eistute and Book preserve every attempted OBJ, boundary/
incidence, acceptance and independently audited CSV observation against the
integrated reference. Eistute accepts steps 0/1 and rejects 2/3/4; Book accepts
0/1 and rejects 2/3. No acceptance criterion or comparison budget is changed.

Selected read-only lint, explicit new-probe/changed-range formatting, whitespace,
inventory and environment identities pass. The actual compilation database
covers all 73 production units; the inventory has 151 files, 585 potential
includes, 26 contracts and 164 anchors. The existing six-header cycle remains.

An independent pass verifies all command, case, child-log, artifact and source
identities. The original source-only snapshot matches all 488 immutable
production/vendor input hashes. Runtime evidence checks fourteen actual GNU
C++17 compilation commands per observer target (thirteen production units plus
the probe), compiler identity, executable hashes and static Debug CRT imports.

Compact reports are in [bezier_observers](stage3/bezier_observers/), including
[the complete prepublication gate inventory](stage3/bezier_observers/prepublication_qualification.json).
The report explicitly identifies a modified prepublication working tree and its
source manifest, rather than claiming the entry commit contains the repair.
Raw reports/logs remain local and hash-linked. Published-head confirmation must
pass before integration and is recorded in the review PR; post-merge validation
and full stage 3 closure remain separate.

## Closure audit and remaining scope

The audit adds the missing required CTest registrations and exercises Geometry
ordering in the ordinary contracts, refreshes the reviewed source/contract
inventory, restores the contiguous work-log table and corrects contradictory
current-status/architecture counts. Existing full-file
formatting debt in curve_adaptive.h is distinguished from changed-range formatting;
no repository-wide reformat or analyzer suppression is used.

Code, tests, C26 and ADR-0033 describe the same bounded current-incidence lifetime.
No formula, floating-point order, numerical selection, synchronization algorithm,
quadtree/template/front, tolerance, budget or adaptation/acceptance/stopping policy
is changed. Successful caller adoption, Hermite retirement, arbitrary ReplaceCurve
publications, copied observers, SubMesh observers, cache/metadata/acceptance
rollback and full-process/parallel/LSan/UBSan remain unqualified. See the finite
stage 3 closure inventory rather than historical next-work paragraphs.
