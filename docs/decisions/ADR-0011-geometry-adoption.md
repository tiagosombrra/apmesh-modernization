# ADR-0011: guard Geometry arguments before container allocation

Status: accepted; exact published-head and implementation-main gates passed through PR #36.
Issue #35. Classification: behavior-changing ownership failure-path defect repair.

## Reproduction and decision

Raw InsertCurve/InsertPatch declare adoption but pass the raw pointer directly
to vector::emplace_back. Storage growth can throw before unique_ptr construction.
Eight original failure cases reproduce a missing destruction and positive Debug
CRT retention, across initialized parametric/Bezier/Hermite copies and patches,
with empty/nonempty destinations. The eight unique-overload sweeps are passing
controls. The same ten actual production units are compiled against a verified
460-blob original and the repair; the historical repository is untouched.

Wrap each raw argument in a unique_ptr before delegating to its existing
unique-owner overload. No storage pre-reservation, growth policy, interface type,
class layout or numerical code changes. Both overloads consume exclusive ownership
on entry. Failure destroys the argument exactly once and preserves existing
entries. The caller must not reuse the failed pointer. Retry passes a freshly
created argument. Successful adoption preserves object identity, order and
null-slot semantics. Duplicate/aliased adoption remains invalid; adoption is not
a copy and observers must respect the owner's lifetime.

## Qualification and limits

Candidate: 53/53 ASan/Debug CRT outcomes, including 32 normal variants, two null
controls, 16 independently calibrated sweeps (16 injected ordinals), and
deliberate invalid access/leak/allocation-hook controls. Full normal traces and
successful adoption allocation counts match the original. Tests check source
values, sample/patch identities, prefix identities/order, analytic line position
and derivative, exactly-once destruction and fresh-argument retry. Each operation
is measured after argument construction; clone construction failures are not part
of these adoption sweeps. Counts are observations, not portable promises.

The generator uses the raw adoption API after cloning, but its anonymous helper
and synchronization-disabled policy are reviewed statically only here. Earlier
clone allocations, whole helper/policy integration, graph rollback/publication,
generic observers, other constructors/mutations, shared sample ownership and
full-process/parallel/LSan/UBSan remain unqualified. No synchronization option,
formula, accumulation order, tolerance, adaptation/acceptance/stopping policy,
vendor or independent numerical verifier changes. Full stage 3 remains open.
