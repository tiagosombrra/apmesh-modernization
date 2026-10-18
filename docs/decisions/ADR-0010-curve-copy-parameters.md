# ADR-0010: preserve parameter values in initialized curve copies

Status: accepted; exact-head and implementation-main complete campaigns pass.
Documentation-only closure gates remain required; see the closure evidence.
Issue #32. Classification: behavior-changing copy-state defect repair.

## Reproduction and decision

The pointer-taking base constructor already copies sample/patch observers,
identity, length, endpoints and matrices. It omits parameters_, so populated
copies lose sample/parameter correspondence. Derived Bezier/Hermite pointer-
taking constructors inherit the loss while copying their controls/tangents.
Twelve separate populated normal cases reproduce it across both instruments;
six populated denial scopes fail their normal calibration contract, before any
allocation denial. Those six scopes are not original memory-failure evidence.

Initialize parameters_ from the non-null initialized source in the existing
base member-initializer list. Standard-container RAII handles allocation failure
and unwinds the already constructed base. No public function type, class layout,
formula, coefficient construction, evaluation order, incidence mapping, solver,
scientific policy or source ownership changes. The sequence is copied exactly;
the constructor does not validate or repair inconsistent source collections.

Parameter values and sample/patch containers have independent storage; sample
and patch objects remain borrowed. Mutating a copied collection does not mutate
the source container. Either curve object may die first only while the actual
borrowed-object owners remain alive. Copying is not adoption or a deep physical
sample clone. The source must remain initialized and non-null; no null handling
or thread-safety guarantee is added.

## Qualification and limits

The same probe compiles nine real production units against a 460-blob verified
original and the repair. Empty, forward and reversed five-sample sequences cover
three types. All initialized scalar, endpoint/control/tangent and matrix/scratch
values are checked, along with exact observer identity/order and independent
list nodes. Five cubic position/derivative samples and signed arcs use scalar
analytic expressions with existing 1e-12 bounds. All normal numerical traces
match the original; populated copied sequence state intentionally changes.
Curve evaluation scratch may change after evaluation without mutating source.

Nine independent constructor sweeps deny 123 measured allocations, preserving
source values/nodes and caller sample/patch state and requiring successful retry.
Empty copies measure seven allocations; populated forward/reverse copies measure
17 instead of 12, per type. Five extra parameter nodes are intentional, not a
portable count or performance promise. The previous populated two-parameter
copy fixture similarly grows from nine to 11 allocations and is recalibrated.
Scoped CRT retention and actual ASan UAF/CRT leak/denial controls are required;
this does not establish full-process leak freedom or LSan/UBSan coverage.

The existing CloneCurveForPatch consumer is reviewed statically only. Post-copy
publication, DisableSharedCurveSynchronization integration, implicit copy/
assignment, null/uninitialized sources, other constructors/setters, shared sample
ownership, initialization/rollback, generic observers and full-process/parallel
qualification remain open. No shared-curve policy option is enabled or changed.
Full stage 3 remains open.
