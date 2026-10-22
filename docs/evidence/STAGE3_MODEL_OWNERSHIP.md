# Stage 3 slice 34: Model mesh ownership

Status: focused candidate passes; full exact-published-head/main qualification PENDING.
Entry main: cd3dd8c7e269d4384f62109ef28334184c64ce89 (PR #91).
Classification: behavior-changing lifetime defect repair; no scientific change.
Stage 3 remains open; stages 4-11 remain pending.

## Boundary and compatibility

Model borrows Geometry and exclusively owns its ordered mesh collection. Both
raw and owning append consume on entry, including a failed vector growth; existing
entries stay live and the relinquished argument is destroyed. Null still adds an
empty slot and an out-of-range getter still returns null. Destruction retains the
original reverse mesh order. Copying is prohibited. Runtime-qualified nonthrowing
moves transfer pointer identity/order and the geometry borrow, leave the source
empty/null, retire the previous destination in reverse order and preserve
self-move. An independent new argument can be appended after an observed failure
or into a moved-from Model. C02 and ADR-0035 define the contract.

This is an explicit source/layout/copy contract migration, not an external ABI
compatibility guarantee. The literal caller audit found both raw insertions inside
alternate GeneratorOmp; serial Generator keeps its mesh in mesh_. No production
Model copy expression or derived Model was found. Those negative observations do
not qualify parallel, indirect or external callers. Pre-insertion construction and
foreign Patch/current-submesh observers are separate; moving Model does not rebind
them. Geometry and borrowed nodes/patches must satisfy their existing lifetimes.
Arguments must be exclusive and deletable through MeshAdaptive. Duplicate/foreign
adoption and derived-base deletion remain invalid. No generator policy changes.

## Focused observations

[The compact focused record](stage3/model_ownership/focused.json) is a separate
prepublication record, not exact-published-head/main evidence. Model and fourteen
actual dependency units are compiled without a production-body adapter. The
original snapshot has 488 files verified against immutable entry main.

The new battery requires 57 ASan/static Debug CRT expected outcomes: normal raw
and owning handoffs, empty/seeded/null inputs, reverse release/element-before-node
order, populated/null/empty/self transfer and reuse, eight complete growth sweeps,
twelve measured zero-allocation operations, actual UAF/leak/allocation-hook
controls and rejected deliberately corrupt order/adjacency observations. All eight
calibrated growth allocations are denied exactly once; each failure preserves the
live prefix, releases its argument and permits a new independent append, ending
with zero retained blocks/bytes. Moves have runtime evidence as well as traits.

Fifteen nonempty original/candidate live pairs (five each GCC C++17, MSVC ASan and
MSVC CRT) agree on actual XYZ coordinates, node/element IDs, analytic area 0.5,
local triangle adjacency, null/order/count and geometry borrowing/reverse lifetime.
The original pairs exercise its raw API; candidate owning/move paths have separate
runtime tests. The two-file preservation guard permits only the exact owner,
copy/move, constructor-initialization and getter access delta; six independent
retirement/self-move/borrow/append/getter/handoff mutations must be rejected.
Every other production source remains identical to entry main.

[Original Model audit](STAGE3_MODEL_ROOT_AUDIT.md) and its unchanged thirteen-case
report retain four copy/rvalue UAF reproductions, two failed-append retentions
(15 normal CRT blocks/696 bytes each), independent cleanup controls and unsupported
duplicate-adoption ASan evidence. A reproduced original error is not a repair pass.

## Commands and full delivery requirements

```powershell
cmake -S tests/model_memory -B build/s34qa -G "Visual Studio 17 2022" -A x64 -DAP_MESH_MODEL_ASAN=ON
cmake --build build/s34qa --config RelWithDebInfo --parallel 2
cmake -S tests/model_memory -B build/s34qd -G "Visual Studio 17 2022" -A x64
cmake --build build/s34qd --config Debug --parallel 2
python tools/qualify_model_ownership.py --asan build/s34qa/RelWithDebInfo/model_ownership_probe.exe --crt build/s34qd/Debug/model_ownership_probe.exe --runtime '<qualified MSVC runtime directory>' --output '<new directory>'
python tools/audit_model_ownership.py --candidate-root .
python tools/compare_model_ownership.py --original '<original probe>' --candidate '<candidate probe>' --original-root build/s34-original --candidate-root . --output '<new directory>'
cmake --build --preset windows-gcc17 --parallel 2
ctest --preset windows-gcc17 --verbose
```

The fixed required inventory is 49 CTest with zero failures/skips and 74 Python
controls, all previous 29 qualified memory batteries/3005 expected outcomes plus
the new battery/57 outcomes (30 batteries/3062 outcomes), 1040 retained scalar
sequences and exact twice-repeated Eistute/Book accepted/rejected/OBJ/incidence/CSV
traces. Full exact-head and post-merge main must preserve protected input hashes,
command/case/child-log/executable identities, selected lint/explicit formatting,
architecture/contracts, checkout/environment and remote main/branches/PR/checks.
No hosted workflows are introduced. Missing or failing gates block integration.

The focused record does not establish full-process, parallel, LSan or UBSan safety,
preceding OpenMP preparation, pointer-taking patch-copy semantics, arbitrary
foreign publications, current-patch rebinding, cache/metadata/error/history/budget/
acceptance rollback, other loaders/MPI/Hermite, complete extreme meshes or broader
models. No formula, floating-point order, synchronization, tolerance, template/
front reconstruction, budget or acceptance/stopping policy changes. Allocation
counts/timing can change; no performance claim.
