# Stage 3 slice 11: curve clone publication and recovery

Issue #38. Entry main 45af645c230d9179bd0b8b03a7d28621d0b31cf0,
tree 493f321dfcb6f7ddb0480036c13fc66be527cbc3 (1102 blobs).
Remote entry: 26 branches, no open PRs/issues/check contexts/Actions. The status
API says pending with zero contexts; that is absence of hosted checks.
One active work item; historical source and vendor remain untouched.

Fresh entry instruments: adoption 53/53, copy 30/30, curve 19/19, UV 81/81,
node 7/7. Serial baseline reuses qualified slice-10 implementation-main
4e23bd00e457e68056ff956869732b1872f04822; its 514 qualified compiled/tool/test/
build/input identities are unchanged on entry documentation-main. No fresh
entry serial campaign is claimed. All 460 original source/header/vendor blobs
are extracted from Git and byte-verified. See original_source_blobs.json.

The original comparison uses twelve pinned actual units and a mechanically
extracted function adapter, not the entire old generator translation unit.
Original function bodies are unchanged except the member qualifier needed for
independent linkage; a unique-return wrapper only adopts after successful helper
completion, so it cannot repair an internal exception. Original blob, function
hashes, transformation and adapter bytes are retained. Candidate runs the actual
new production unit linked by the serial application and the narrow test.

## Original findings and repaired boundary

Twelve graph sweeps fail after denied ordinal 1 because the source has already
lost its original incidence set before a clone exists. Ordinal 0 passes; further
original graph ordinals are unmeasured after the failed contract. There is no
retention in those final graph-failure cases. Four direct-helper sweeps complete
their denial loops but retain a leaked pending clone at target-incidence failure
(five CRT blocks for the base type, nine for each parametric/Bezier/Hermite type).
The remaining 57 of 73 original control outcomes are as expected.

Unique pending owners and ordered Geometry batch publication defer mutation until
all clones for one original curve are ready. Source capacity already holds more
than one incidence; clearing/reinserting one pointer and replacing patch edge
slots do not allocate. Failure preserves that original curve and cleans pending
owners; earlier committed curves remain. Retry completes the unchanged suffix.
This is not whole-operation atomicity or adaptive snapshot/rollback.

The 73-case runner uses four dynamic curve types, two original curves per graph,
ordinary/non-manifold/null-filtered/mixed/all-non-Coons incident sequences,
repeated edge references, forward/reversed sample lists, real PatchBezier
orientation flags/control nets and both helper target/null-target variants.
It requires independent line position/derivative and planar patch evaluation,
exact observer ordering/types, external sample ownership, coherent committed
prefixes, retry and idempotent success. All normal reported traces match original.
Twenty independently calibrated sweeps deny 484 final observed allocations,
each once, including failures after a committed prefix. Preparation intentionally
changes allocation timing/counts/bytes; counts are toolchain observations.

## Setup and quality failures preserved

The first fixture appended observers after the patch constructor's four generated
curves, producing invalid edge expectations and fixture leaks. It now explicitly
owns those constructor-created objects and replaces the four existing slots.
Those preliminary failures are invalid setup, not production repair evidence.
MSVC initially rejected standard alternative operator tokens without /permissive-;
the new target now uses the root application's standard conformance flag.
With Debug iterator level 2, vector's noexcept default constructor allocates an
iterator proxy and terminates at denied ordinal 0. The new target consistently
uses Debug iterator level 0 across all its units, matching serial/ASan layouts,
while retaining CRT heap accounting and every denial/retention assertion.
Earlier targets retain their original flags and controls. No claim of recovery
from MSVC debug-iterator metadata allocation is made. Installed STL source paths
and hashes, failed reports and raw log hashes are retained in setup history.
Unchanged lint then required an explicit Hermite destructor override; that failed
report is retained and the full campaign is rerun with the final compiled bytes.

## Commands, candidate gates and closure inventory

```powershell
. ./build/local-env.ps1
cmake --build --preset windows-gcc17 --parallel 2
ctest --preset windows-gcc17 --verbose --output-junit <phase>/ctest.xml
cmake -S tests/curve_memory -B build/s11a -G "Visual Studio 17 2022" -A x64 -DAP_MESH_CURVE_ASAN=ON
cmake --build build/s11a --config RelWithDebInfo --target curve_synchronization_probe --parallel 2
cmake -S tests/curve_memory -B build/s11d -G "Visual Studio 17 2022" -A x64
cmake --build build/s11d --config Debug --target curve_synchronization_probe --parallel 2
python tools/qualify_curve_synchronization.py --asan build/s11a/RelWithDebInfo/curve_synchronization_probe.exe --crt build/s11d/Debug/curve_synchronization_probe.exe --runtime <MSVC-runtime-directory> --output <phase>/sync
python tools/quality.py tidy src/data/geometry.cpp src/generator/curve_synchronization.cpp --build build/windows-gcc17
python tools/inventory_architecture.py --output docs/architecture/source_inventory.json --contracts docs/architecture/contracts.json --check
```

To compare original, use `AP_MESH_CURVE_SOURCE_ROOT=<verified-original-root>` and
`AP_MESH_SYNC_IMPLEMENTATION=<original_adapter.cpp>` with the same probe/flags.
Exact commands, source/input/executable identities, compiler versions and report
hashes are in stage3/curve_synchronization/. Raw leak/UAF dumps remain unchanged
locally with hashes; they are not normalized to satisfy whitespace tooling.

Candidate CTest 21/21, zero skips, 74 Python controls; synchronization 73/73,
adoption 53/53, copy 30/30, curve 19/19, UV 81/81, node 7/7; selected two-unit
lint, explicit new-file/changed-range formatting and inventory pass. Inventory:
125 production files, 58 units, 67 headers, 22 contracts/103 anchors and the
existing six-header cycle. C03/C07, ADR-0012, current state/plan/worklog/quality
and architecture sequence document ownership, source extraction and limits.

Eistute and Book each repeat twice and compare strictly to slice-10 main:
nine attempted states, all OBJ/acceptance/rejection/incidences and 189 named CSV
fields are exact; measured shared coverage is positive with zero gaps, accepted
steps 0/1, rejected Eistute 2/3/4 and Book 2/3; final accepted triangles remain
1,168/4,256. This default-policy regression does not run the full CLI option with
synchronization disabled. Exact published-head/main gates subsequently passed through PR #39; see STAGE3_CURVE_PUBLICATION_CLOSURE.md.

Scientific audit: formulas, floating-point order, incidence policy, quadtree/
templates/front, budgets, verifiers, tolerances and adaptation/acceptance/stopping
remain unchanged. This is a failure-path ownership/consistency repair plus a
bounded extraction and override annotation, not a scientific proposal.
Open: full CLI disabled-policy integration, whole-operation atomicity, adaptive
snapshot/rollback, other construction/mutation, shared sample initialization,
generic observers/custom subclasses, full-process/parallel/LSan/UBSan and stage-8
undocumented APIs. Full stage 3 stays open; only this measured boundary may close.
