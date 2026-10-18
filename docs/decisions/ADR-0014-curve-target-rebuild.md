# ADR-0014: prepare paired curve target rebuild state before commit

Status: candidate qualified; exact published-head and implementation-main gates required.
Issue #44. Classification: ownership/exception-consistency defect repairs and
engineering extraction, preserving successful numerical and ID policy.

The original target-count lambda can lose raw new nodes if list insertion or
later preparation throws. It deletes old interiors before copying parameters,
and its shrink loop deletes while still constructing the two lists. Twenty-four
original sweeps stop safely at the first deleted-live-sample failure (per-case
ordinals 11-28); later ordinals and CRT retention in those aborted sweeps are
unmeasured. Three two-endpoint growth sweeps complete and retain 48 CRT blocks
each across all their denied allocations. Other 90 outcomes are expected.

Keep the original point/parameter vector copies, guards, uniform growth formulas,
ID request sequence and rounded/sorted/deduplicated shrink indices. Prepare
new nodes under unique ownership, every point list node and every parameter list
node before commit. Swap directly with the supplied point list and public curve
parameter list, release pending nodes and delete removed old interiors afterward.
The standard default allocators match and swaps do not allocate. The built-in
initialized sample destructors are nonthrowing. The existing successful raw
sample ownership convention remains; curve lists themselves remain observers.

Removable interior sample objects must be distinct and exclusively deletable;
endpoints may be borrowed/shared, including a closed endpoint alias. Failure
preserves both live lists, their element nodes and samples. Success invalidates
old list-element and removed-sample observers. The independent curve point list
is not published by this helper. Its later Generator SetPoints call can still
fail; full AdaptCurve and whole-graph/mesh rollback remain separate unqualified
transactions. Snapshot restoration still does not capture/restore parameters.

IDs requested before an exception remain consumed, as before. Positive controls
exercise both consumed/unconsumed growth failures; retry starts at the current
manager sequence. Normal traces retain exact request order/count and zero/null
manager behavior. Existing narrowing from manager ULInt to unsigned long is
preserved; overflow/wrap behavior and manager constructors are outside this repair.
Reversed growth keeps the original uniform parameters and reused endpoints even
when they do not describe consistent geometry; this preserves policy without
endorsing inconsistent input. Bounded positive fixtures do not qualify extreme
sizes, arbitrary subclasses, allocators or competing owners.

The actual production helper is called through the original lambda position.
Original comparison uses 12 Git-pinned units and a hash-verified lambda adapter
with exactly two member-context substitutions for the same nullable manager.
Candidate instruments 13 actual units. New Debug CRT uses non-debug iterator
metadata consistently; actual heap checks, allocation propagation and deliberate
negative controls remain required. It is not full old Generator instrumentation,
iterator-level-2 recovery or cross-compiler ABI qualification. Earlier targets
retain their settings. Valid 108-outcome preliminary coverage and 117-outcome
zero-start runs remain explicit history; final fixtures set the intended nonzero
ID start after RangedIdManager constructor adjustment, with separate zero/null
controls. No manager source change is proposed.

Candidate: 117/117 outcomes, 36 sweeps/597 denied ordinals, 78 complete
normal original/repaired traces exact; previous seven batteries, CTest 23/23,
zero skips/74 controls, actual new-unit read-only lint, explicit formatting,
inventory and strict repeated default-model regression pass. Extra preparation
changes allocations/timing/bytes/peak storage without a performance claim.
No numerical formulas/order, synchronization, quadtree/templates/front, tolerance,
budget, verifier or adaptation/acceptance/stopping policy changes. Full stage 3,
full-process/parallel/LSan/UBSan and stage-8 undocumented API debt stay open.
