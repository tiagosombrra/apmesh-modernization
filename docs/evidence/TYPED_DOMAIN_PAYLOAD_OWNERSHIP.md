# Checked serial terminal payload ownership repair

Entry: PR #169 head `aef14c4d5c7beab6d5dd01694a49dfcb4f5cc7ad`, main
`9682d53166eddada3ea52ec491205b53de0fe7e5`.
Classification: behavior-changing engineering repair of terminal error preparation
and propagation. No scientific formula, ordering or policy change is admitted.

## Trigger and ownership contract

The original [checked-CRT qualification](SERIAL_CRT_TERMINAL.md) aborts before the
first typed payload row, after eight prerequisites and before all five directed
contexts. Its original artifact, symbols and raw outputs remain immutable.
The separately qualified minimal diagnostic identifies an iterator-proxy
allocation inside MSVC 14.44.35207's noexcept std::string move. Denying that
allocation terminates before catch. Removing noexcept from the outer constructor
alone cannot repair that nested noexcept boundary.

DomainGenerationError now prepares a uniquely owned string by copying the
completed status before throwing. Preparation may allocate and propagate
bad_alloc normally; it is explicitly outside the allocation-free transfer
contract. It preserves the source string. The Adapter explicitly prepares the
error, then throws it by move. Only unique ownership crosses that transfer:
the complete bytes and const-string-reference accessor remain stable until
exception retirement. Moves and move assignment are noexcept and allocate
nothing. Explicit copies retain independent ownership and may allocate, as
before. A moved-from error is retired or assigned, not observed or copied.
There is no shared owner, borrowed source, status truncation or iterator override.

The former claim of allocation-free construction directly from a string rvalue
is withdrawn for the supported checked ABI. The preserved original nine cases
now prepare ownership before denial and require allocation-free throw transfer,
unchanged payload/context, source clearing, what() and same-object rethrow.
Additional controls deny every measured preparation allocation, require ordinary
bad_alloc and unchanged source, verify independent explicit copies/self assignment
and check storage identity through allocation-free move assignment. Actual native
SubMesh allocation during unwinding must still be denied exactly once.

Successful paths are unchanged; the only Adapter delta is its terminal throw.
The MPI/OpenMP branch retains its previous behavior. Preparation failure is a
resource exception, not a fabricated domain result or recovery guarantee.

## Finite validation and closure

Require revised checked-MSVC native preparation/reversal, all lifetime and terminal
prerequisites, then the same five SP-09/10 contexts once at their unchanged caps.
Preserve all original failed artifacts and stop at any new unexpected failure.
Require C++17 GCC/MSVC builds, complete 75 CTest / 479 Python regression,
independent nine-state Eistute/Book artifacts/traces/boundaries on the affected
production dependency, scoped read-only analysis, explicit formatting, contracts/
inventory, staged metadata and fresh remote checks on the final head. Reuse
unchanged scientific/reference artifacts only after matching identities.
Repeat required validation on merged main before closing this bounded phase.
Earlier ordinary regression and ASan/CRT artifacts retain their original scopes;
no total Stage 3, runtime/DLL, parallel or general recovery claim follows.

## Bounded implementation and measured qualification

The revised checked-MSVC target passes all nine prerequisites: actual lifetime
release/global release/shutdown release, two expected retention negatives and
allocation denial; terminal release; live/excluded/disabled AFT/allocation;
and typed payload/unwind/preparation controls. All nine payload rows have zero
transfer allocations. Eight measured preparation allocations are denied one by
one and caught normally with source intact; three length cases check independent
copies and allocation-free identity-preserving move assignment. The actual
SubMesh unwind control remains calls=1/uncaught=1/attempts=1/denied=1.

Only then do the unchanged five contexts execute: CLI Book patch 0 and Eistute
patches 0/1; external-Geometry library Book patch 0 and Eistute patch 1. Every
context has zero final normal/client deltas and an empty newer-object dump.
CLI status 1, exact typed diagnostics and failed-prefix rejection pass. Library
status 0 after catch, original attempt counts, detached owned observations and
released samples pass. No terminal prefix is counted as successful generation.

The first revised build fails before execution because the new fixture used
unqualified State, ambiguous with legacy Data::State. Its sources/logs/report
remain preserved. Explicit qualification corrects the fixture; its original
unwind counters are retained while new preparation controls run. The corrected
build passes in 6.5851881 seconds at the original two-job/600-second bound.
A later explicit format operation changes one leading indentation character in
the terminal preparation call, with equal line count and identical tokens; its
before/after source proof is retained. Final revision checks bind actual sources
and rebuilt artifacts, with runtime equivalence documented separately.

The first scientific comparison stops on missing source_config_sha256 metadata
in the older CRT reference, despite native status zero, identical OBJ and equal
decisions. Preserve that failed orchestration report. Offline analysis compares
the completed captures with the existing qualified full-metadata first-call
reference; only the unstarted MSVC Book case is launched afterward. No completed
scientific process is repeated to correct reference metadata.

The compact [repair record](stage3/typed_domain_payload_ownership/summary.json)
and local build/p3-terminal-crt-payload-repair reports retain compiler,
source/input/executable/oracle identities, original failures and finite scientific
comparisons. Final head/main verification and integration seals live separately
under build/p3-terminal-crt-payload-repair/delivery. Only a passed integration seal
closes this bounded repair/terminal phase; all ten Stage 3 rows retain their
three bounded-qualified / seven partial-open dispositions.
