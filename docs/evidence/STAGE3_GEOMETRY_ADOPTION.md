# Stage 3 slice 10: Geometry ownership adoption

Issue #35. Entry main bf93d85456ab5ddfd21e2472fec9b18cca12cb04, tree
703f9b160b0b1e78e6d221473f284c42802ebea8 (1017 blobs). Remote entry audit:
24 branches, no open PRs/issues or configured check/status contexts or Actions.
The status API's pending state with zero contexts is absence of checks, not a
green hosted run. Keep one active item. This is a behavior-changing ownership
failure-path defect repair; no scientific proposal is implemented.

## Entry and reproduced failures

The original's 460 production/header/vendor blobs are extracted with git archive
and verified against Git blob identities. Fresh entry instrument outcomes pass:
copy 30/30, curve 19/19, UV 81/81, node 7/7. Serial comparison reuses the previously
qualified slice-9 implementation-main d5abb5495b28e8ec5a2b6f779c3adf173929ed04
outputs. Entry documentation-main has all 512 qualified compiled/tool/test/build/
input/contract identities unchanged; no fresh entry serial campaign is claimed.

Raw Geometry insertion can allocate vector storage before forming unique_ptr.
Eight original raw adoption cases fail the exactly-once argument destruction
contract with positive CRT retention: parametric/Bezier/Hermite copies each retain
13 blocks, patches one block, for both empty and one-entry destinations. All
45 other original outcomes are as expected, including eight unique-owner denial
controls. Failed original diagnostics and raw log hashes are retained; raw dumps
with tool-produced whitespace remain unchanged locally, not normalized.

## Repair, measured behavior and commands

Each raw overload delegates through a pending unique_ptr. C03 and ADR-0011 record
exclusive/deletable argument preconditions, ownership consumed even on failure,
unchanged destination prefix and fresh-argument retry. Successful normal traces,
identity/order/null slots and successful allocation counts match the original.
Initialized clones use actual pointer-taking constructors before the adoption
measurement. Physical samples and the incident patch stay externally owned.
Line position and derivative use independent analytic checks with 1e-12 bounds.
All 16 positive-calibration scopes deny 16 observed allocations, each once.
Counts are toolchain observations, never a portable count or performance claim.

```powershell
. ./build/local-env.ps1
cmake --build --preset windows-gcc17 --parallel 2
ctest --preset windows-gcc17 --verbose --output-junit <phase>/ctest.xml
cmake -S tests/curve_memory -B build/g10a -G "Visual Studio 17 2022" -A x64 -DAP_MESH_CURVE_ASAN=ON
cmake --build build/g10a --config RelWithDebInfo --target geometry_adoption_probe --parallel 2
cmake -S tests/curve_memory -B build/g10d -G "Visual Studio 17 2022" -A x64
cmake --build build/g10d --config Debug --target geometry_adoption_probe --parallel 2
python tools/qualify_geometry_adoption.py --asan build/g10a/RelWithDebInfo/geometry_adoption_probe.exe --crt build/g10d/Debug/geometry_adoption_probe.exe --runtime <MSVC-runtime-directory> --output <phase>/adoption
python tools/quality.py tidy src/data/geometry.cpp --build build/windows-gcc17
clang-format --dry-run --Werror tests/curve_memory/adoption_probe.cpp
python tools/inventory_architecture.py --output docs/architecture/source_inventory.json --contracts docs/architecture/contracts.json --check
```

Original configuration uses the same probe with
`-DAP_MESH_CURVE_SOURCE_ROOT=<verified-original-root>`. Exact argv, byte hashes,
compiler identities, old/current instrument reports and model comparisons are
in stage3/geometry_adoption/. All previously required instrument runners are
invoked too. Explicit production/header range formatting is checked separately;
no repository-wide formatting or analyzer fix is applied.

Candidate CTest 20/20, zero skips, 74 Python controls; adoption 53/53, copy 30/30,
curve 19/19, UV 81/81, node 7/7; selected lint, formatting and fresh inventory pass.
Inventory remains 123 production files, 57 units, 66 headers, 22 contracts with
100 source anchors and the existing six-header cycle. Eistute/Book each repeat
twice and compare strictly against slice-9 implementation-main: all nine attempted
states and OBJ/acceptance/rejection/incidence results match; positive measured
shared incidence coverage with zero gaps, 189 named CSV fields, accepted steps
0/1, rejected Eistute 2/3/4 and Book 2/3, final accepted triangles 1,168/4,256.
Exact published-head and implementation-main gates subsequently passed through PR #36; see STAGE3_GEOMETRY_ADOPTION_CLOSURE.md.

## Explicit closure inventory

- Code: two raw-adoption delegation changes and English failure contracts; no math,
  interface type, layout, growth policy, vendor, generator or historical source change.
- Tests: positive nonempty comparisons, failed original, eight unique-owner controls,
  null slots, independent line geometry, destruction counts, retry and instrument
  negative controls; ordinary CTest does not itself inject Debug CRT failures.
- Contracts/docs: C03, deterministic inventory, ADR-0011 and current plan/state/quality
  updated. Full application documentation remains stage 8 and its warnings still fail.
- Scientific scope: all formulas, operation order, synchronization, adaptation,
  acceptance, stopping, budgets, verifiers and tolerances preserved.
- Open findings: generator CloneCurveForPatch/DisableSharedCurveSynchronization is
  statically reviewed only, despite direct Geometry adoption being exercised here.
  No graph transaction/rollback, earlier clone allocations, implicit copying,
  alias adoption, remaining constructors/mutations, shared sample initialization,
  generic observers, whole-process, parallel, LSan or UBSan qualification is claimed.

This measured ownership boundary is qualified on exact head and implementation-main. Full stage 3 remains open.

Initial formatting checks failed because the changed short patch-adoption function
requires one-line formatting. A first range-only correction did not resolve it.
The failed reports and raw XML are retained in format_failure_inventory.json.
Explicit formatting changed only the touched function; inventory was refreshed
and the full campaign restarted on the final compiled bytes. No rule was suppressed.
