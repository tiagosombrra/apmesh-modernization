# ADR-0009: commit prepared curve collections by swap

Status: accepted; exact-head and implementation-main complete campaigns pass.
Documentation-only closure gates remain required; see the closure evidence.
Issue #29. Classification: behavior-changing defect repair on exceptional exits.

## Reproduced boundary

SetPoints and UpdateParameters receive a fully prepared by-value standard list,
then copy-assign it into live state. In both growing populated MSVC fixtures,
the first seven denied ordinals preserve state, but ordinal 7 overwrites an old
prefix before extension fails. Both failures are retained. Empty destination,
shrinking, equal-size, clearing, self-alias and two copy-constructor controls
are positive controls; deliberately invalid instrument cases remain separate.

## Decision

Swap each prepared input into its live list. Remove top-level const from the
UpdateParameters parameter to permit swap; its C++ function type and call
interface are unchanged. Use existing standard-allocator containers and RAII;
there is no new shared owner or alternate numerical implementation.

Preparation failure preserves that live list's values, nodes and element
observers. Lvalue caller inputs remain unchanged. Rvalue input consumption stays
permitted. Success replaces all old element nodes, invalidating old element
iterators/references; references to the list container itself remain valid.
Borrowed point and patch objects are never destroyed by these setters. Old
container nodes are destroyed from the swapped-out argument at function exit.
The two setters are independent operations, not a joint point/parameter update.

Successful allocation counts and node reuse deliberately change: the second
copy disappears. MSVC growing counts fall 10 to 7 and empty-destination counts
12 to 7 per setter. Other measured lvalue counts remain 4/5/2/5; constructor
controls remain 7/9. These are measurements, not portable constants, and no
performance or peak-memory claim follows. Ordered values, duplicate/null point
observers, caller ownership, coefficients and numerical policies are preserved.

## Qualification and limits

The same final probe runs against all 460 Git-verified original source/header/
vendor blobs and the repaired tree. Fourteen normal setter variants have exact
address-free original/repaired traces in ASan and Debug CRT. Fourteen separate
calibrated denial sweeps cover 60 setter and 16 pointer-copy-constructor
allocations, with exactly one propagated denial, unchanged live values/nodes,
caller inputs/objects and successful retry. Actual UAF, retained-block and
allocation-hook controls prove instrument response. Valid CRT cases retain zero
normal blocks/bytes; this is scoped retention, not full-process leak freedom.

Constructor controls cover base borrowed collections and initialized id/length/
coefficient state. The existing pointer-taking parametric constructor does not
copy parameters_; this static semantic finding is retained and not silently
repaired or claimed as full value-copy qualification. Implicit copy/assignment,
derived Bezier/Hermite constructors, other setters, joint updates, shared samples,
initialization/rollback, general observers and full-process/parallel/LSan/UBSan
remain open. Scientific expressions and adaptation/acceptance/stopping policies
are unchanged; full stage 3 remains open.
