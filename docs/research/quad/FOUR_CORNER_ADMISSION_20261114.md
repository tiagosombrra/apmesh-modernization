# Physical QUAD four-corner UV admission repair — 2026-11-14

## Problem and behavior

The physical research element claimed to refuse concave UV cycles but checked
only triangles012 and023. The exact dyadic concave input
`[(0,0),(1,0),(0.25,0.25),(0,1)]` passed those determinants. A new native
regression fails against the unchanged original source with exit1 and
`Concave UV quad was accepted`; the failed capture is retained.

The repair retains both original expressions and their evaluation order, then
checks the missing123 and301 turns at the same `1e-14` threshold. All four
strictly positive UV turns are required before any observer registration.
Physical metrics, point selection, boundary sampling, TRI and source ownership
are unchanged. This is a behavior-changing repair of the existing contract,
not a scientific proposal or a complete physical Jacobian guarantee.

Previously admitted near-collinear convex inputs at a missing turn<=1e-14 are
now refused deliberately. Valid inputs whose four turns exceed that threshold
remain admitted; no universal identity with previous acceptance is claimed.

## Finite validation and limitations

The same new fixture executes through the existing physical ownership probe
and an isolated seven-TU native capture. Linux GCC13.3, Windows GCC16.1 and
Windows MSVC19.44 Debug C++17 each pass60 cases:20 accepted and40 rejected.
Cases include cyclic/reflected concave, collinear, repeated-coordinate,
crossing and valid square/skew cycles, clockwise input, and exact dyadic
threshold controls on either side of1e-14. The physical square remains valid
to isolate UV admission. Two pre-existing elements and observer list-slot
addresses check pointer identity, ordering and cleanup after each attempt.

The existing fixture retains its original lifecycle/injected-failure and
native physical mixed-mesh oracles; its controller now additionally requires
the full20/40 marker and records both counts separately. These ordinary cases
do not qualify complete-process sanitizer coverage or allocation-denial scope.

Configured LLVM22 analysis of the changed element and added fixture header
passes using actual GCC metadata and an explicit header scope. Formatting of
three touched C++ files was explicit, with whitespace-removed text identity
before/after formatting. Original failed formatting/setup records remain.
Full exact-candidate regression, complete existing physical-model test,
whole-probe analysis and fresh remote checks are separate pending gates at
this implementation checkpoint. Results are bound to the delivery revision
in its local report/PR; no milestone or stage closes merely from these60 cases.

## Plan and handoff

P0 repairs this contract. P1 then closes a live controlled curved-patch R2
application run; P2 consumes the same mixed mesh for two accepted R3 epochs.
Original TRI epochs do not establish mixed history. High-valence sheet
approval, literal1993 equivalence, all-QUAD and anisotropy retain their
independent scientific scope.

[Evidence](evidence/FOUR_CORNER_ADMISSION_20261114.json) contains source/binary/
record hashes and explicit remaining gates. The former STATE is archived
byte-for-byte as [historical state](STATE_HISTORY_20261114.md), preserving
earlier failures and contradictory historical checkpoints. The new STATE has
one active item. This does not retroactively certify old evidence identities.


## Qualified research integration

PR216 merged as49c9dc3. Exact candidatea2c4277 and exact research merge each
passed85CTest/527Python without failure/error/skip; both original physical
model modes and the additional20/40 matrix passed. Configured source/header/
whole-probe analysis and all four remote jobs on each required run passed,
including fresh frozen Eistute/Book comparisons. The earlier pending gates
above describe the implementation checkpoint, not the final delivery state.
See the [delivery receipt](evidence/FOUR_CORNER_ADMISSION_DELIVERY_20261114.json).
Only bounded P0 is closed; all broader scientific/memory/application limits
remain. No main or larger draftPR214 integration occurred.
