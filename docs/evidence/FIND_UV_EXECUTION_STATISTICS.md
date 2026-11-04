# Execution-owned FindUV statistics

Engineering diagnostic isolation, starting at main
29c5484b4ca9fd5b25b902f019d31e0397300d62 (PR #157).
GeneratorAdaptive owns a calls/imax_exits value. Each serial typed Execute clears
that value and binds a same-thread scope before constructing its local geometry.
The raw argument bridge delegates to the same entry. GetFindUvStatistics returns
a value snapshot of the latest serial call, including partial counts on failure.
The CLI serial summary reads this result, so earlier work in the process no longer
contaminates that execution's final counts. Direct Generator(Model,...) and
standalone patch calls are not newly scoped implicitly.

The Bezier and Hermite solvers record at exactly their original call/I_MAX exit
positions. Each helper always performs the original relaxed atomic increment;
when an execution observer is active it additionally increments that owner's
plain unsigned count. The I_MAX helper returns the original process-wide ordinal,
retaining the first-five/every-2000 diagnostic cadence, messages and arithmetic.
The two cumulative atomic globals remain linkable compatibility aggregates and
are never cleared by production code. MPI/OpenMP Execute and CLI paths retain
their original aggregate behavior; worker-thread binding is not introduced.

The scoped observer is a trivial function-local thread-local pointer in an inline
header, shared across translation units. It borrows a live generator-owned value;
copy/move of scopes is disabled. Nested scopes charge their current owner only,
and destruction restores the previous observer on normal or exceptional exit.
Scopes and owners must remain on the same thread. The owner is already stationary.
No application dependency is introduced into the geometry layer and no new heap
owner is needed. The extra member changes layout; consumers require rebuilding.
This does not qualify concurrent/reentrant generation, complete repeated Generator
reuse/recovery, general observer safety or whole-process memory/parallel behavior.

## Finite validation and closure

The existing metrics probe now checks actual Bezier/Hermite calls, normal and
I_MAX exits, ten bit-identical coordinate results across scoped/unscoped calls,
independent nested counts, unwind/restoration and the original global message
cadence against foreign aggregate values. Two fresh generators run the existing
Bezier input fixture through typed/raw entries; each result equals the actual
aggregate delta despite foreign increments between calls. A later missing-input
call clears only that generator's diagnostic result, and restores an outer scope.
These controls qualify bookkeeping, not complete repeated-generation safety.

The first focused run used the built-in Hermite model with output h and stopped
at the existing Bezier-only incidence snapshot precondition. The failed process,
exit and original executable hash are preserved locally. Only the control was
corrected to the existing unchanged tests/curve_memory/data/charge_input.bp;
production policy and the original metric/scientific oracles were unchanged.
The corrected focused control passed before the complete regression resumed.
That regression then stopped at four historical complete-file source guards,
which correctly rejected the new diagnostic binding. Their immutable bases,
comparisons and original mutation inventories remain unchanged. A shared narrow
normalizer restores only the original call/I_MAX increment slots and declarations;
the entire reviewed helper header is pinned before normalization. Four additional
Python controls reject relocation, changed numerical tokens and helper tampering
through all four historical audit entry points. The original 385 controls remain,
for 389 total. The failed head and logs remain preserved locally.

Require GCC/MSVC C++17 builds, the existing 75 CTest entries/389 Python controls
and every prior native marker plus the new statistics marker on exact head/main.
The frozen nine Eistute/Book states retain 45 exact artifacts/123 positive boundary
comparisons, accepted/rejected/retry states and IDs. Their final FindUV summaries
must exactly match PR #157's same-profile reports. Existing 23 MSVC invalid CLI
controls and one analytic state/positive boundary remain required. No new test
target, input model or instrument campaign. Historical instrument observations
retain their original identities and open obligations.

Complete source reversal preserves solver/Execute/CLI tokens except the named
recording, serial scope and summary-source changes. All other production, existing tests,
build flags, configurations, models and numerical oracles remain exact. Historical
source-guard normalization is updated narrowly as described above. Require
scoped analysis using unchanged actual compiler commands, token-checked explicit
formatting, whitespace, inventory/contracts and staged/remote gates. The matrix
retains 201 runtime definitions (185 captured, 16 uncaptured; two retired symbols)
and separately lists the scoped observer. Stage 3 and full Stage 6 remain open.
Commands, hashes, failures and the final integration seal are retained under
build/find-uv-execution. Stop expansion at the first unexpected gate failure.
