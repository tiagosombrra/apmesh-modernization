# Retired dormant runtime registries

Engineering-only cleanup of the internal engine state, starting at main
cd248e082a7f9a00067d596aeeb2314d511fe15b (PR #156).
LIST_ALL_POINTS_MODEL and LIST_ALL_SUB_MESH_MODEL had no first-party consumers:
each appeared only in its definition and extern declaration. Neither registry
represented an active owner or observer publication contract. Both definitions
and declarations are removed, together with the unused set include and geometry
forward declarations in runtime_state.h. No replacement container or context is
introduced. This retires the complete dormant registry pair from process state.

The application state header no longer depends on these geometry types or set.
All 201 remaining initializers retain exact tokens and order. Other production,
tests, fixtures, CMake/compiler flags, models, configurations, formulas, IDs,
boundary synchronization and scientific policies are unchanged. The reviewed
matrix records 201 active definitions (185 captured, 16 uncaptured), two retired
symbols and the historical 203-definition baseline. Its capture/group counts
remain 185 bindings, 181 group fields and four identity/output fields.

This internal source cleanup removes two linkable legacy symbols. No installed
SDK or stable external ABI was promised by the internal engine milestone; an
out-of-tree user of those dormant symbols needs source adaptation. There is no
new runtime ownership, memory, reentrancy, recovery or parallel qualification.
Stage 3 and full Stage 6 remain open with the same closure/failure inventory.

Validation reuses the existing C++17 GCC/MSVC builds, 75 CTest entries and 385
nested Python controls, including their negative controls, on exact delivery
head and merged main. The frozen nine-state Eistute/Book reference requires 45
exact scientific artifacts and 123 positive boundary comparisons, retaining
accepted/rejected/retry states and IDs. Existing MSVC invalid CLI controls and
one analytic state/positive boundary comparison remain required. No new test,
fixture, scientific model, instrument campaign or generated configuration is
introduced. Prior instrument records retain their original artifact/profile scope.
Scoped analysis uses the actual runtime-state and runtime-config production
commands, covering the changed header. Explicit formatting is token-checked.

Complete token comparisons permit only the named removals. All other production,
test, build, input and configuration hashes remain exact. Inventory/contracts,
whitespace, staged metadata and remote checks are required. The original use
inventory, source snapshots, commands, hashes, outcomes and final integration
seal are retained in build/dormant-runtime-state. Stop at the first unexpected
failure and preserve it. The bounded output is retirement of dormant state and
header dependencies; passing regression does not close the remaining stages.
