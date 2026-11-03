# Generator-owned serial attempt metadata

Engineering-only delivery supporting S3-08; Stage 3 and full Stage 6 remain open.
The serial AdaptDomain caller now supplies step_ and the existing
current_budget_retry_count_ to Adapter rather than reading ADAPTIVE_CURRENT_STEP
and ADAPTIVE_CURRENT_RETRY. No new state, context group, allocation or layout change
is introduced. The nonnegative int retry is assigned to the unsigned instance
counter in its original loop slot before adaptation and converts back exactly.

The two global definitions and original mirror assignments remain for compatibility.
Their assignment order, OpenMP path and the MPI/OpenMP-compiled AdaptDomain
arguments are unchanged; explicit compile-time guards restrict the new inputs
to the serial profile. They are no longer
inputs to serial domain adaptation, including direct default-generator callers.
Such callers supply generator-owned state; mutating a process mirror does not
configure that generator. This is a bounded metadata contract, not a reentrancy,
parallel, repeated-generation or whole-process memory qualification.

Only two production argument bindings change. Complete source token reversal
checks every other expression, selection, local repair retry literal (1/2/3), ID
allocation, publication, report, formula, stopping/acceptance criterion and order.
Parser, ApplyRuntimeConfig, input models/configurations, scientific oracles and all other production
files remain unchanged. All 203 runtime definitions remain; the 185 context bindings
and 18 uncaptured-definition count are unchanged. The attempt entries now denote
compatibility mirrors with retained parallel consumers, not serial inputs.

## Finite validation and closure

Use the existing GCC/MSVC C++17 builds, 75 CTest entries and 385 nested Python
controls on exact delivery head and merged main. Existing 32 candidate contracts
and deliberate retained-storage control now run with foreign globals (-91/17).
The existing 40 snapshot contracts cover initial attempt labels 0 and 5 with the
same foreign globals, preserving independent selection, local retry, null-cache,
copy-failure and cleanup oracles. No new target, model or instrument campaign.
The existing metrics/export negative controls and nine frozen Eistute/Book states
retain accepted/rejected/retry traces, exact IDs/OBJ/45 scientific artifacts and
123 positive boundary comparisons. Retain 23 MSVC invalid CLI controls and the
existing analytic state with one positive boundary comparison. Changed code
requires rebuilt artifacts; historical instrument evidence keeps its own hashes.
Require scoped analysis on actual compilation commands, token-checked explicit
formatting, whitespace, inventory/contracts, neutral staged metadata and remote
checks. Any unexpected failure stops expansion and must retain its original record.

The first focused snapshot run failed at scenario 9: scenario-specific setup
replaced the expected initial retry 5 with zero. The fixture now sets its first
expected label after those lists; subsequent retry labels and selection oracles
are unchanged. The original failed process/report and executable hash remain in
build/attempt-state/snapshot-check. Only this affected gate was repeated after the
specific correction. No production change or weakened assertion resolved it.
The local entry/proof drivers also retain their UTF-8/counting setup refusals.

Exact-head/main commands, source/binary identities, outputs and remote/PR state
are retained in build/attempt-state, with integration-verification.json as the
final delivery seal. The integration seal is required before claiming delivery.
Existing CRT/leak/UB, repeated execution, other callers, precision and parallel
obligations remain open. The next independent production debt is the three legacy
positional CMake run recipes, already recorded in the milestone inventory.
