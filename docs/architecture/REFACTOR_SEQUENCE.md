# Dependency-ordered follow-up from the stage 2 inventory

This is an implementation sequence within the approved stages, not a production
change in stage 2. Evidence IDs refer to [contracts.json](contracts.json).
Only one work item is active at a time; required regression gates remain exact.

## First stage 3 slice: establish and qualify lifecycle boundaries

Issue #8 implements the narrow SetNoh copy boundary: a reproduced expired
triangle observer is excluded from new owned nodes. Scalar state, caller
ownership and general NodeAdaptive value-copy behavior are preserved. Isolated
ASan and Debug CRT controls are qualified; see
[evidence](../evidence/STAGE3_NODE_LIFETIME.md). This does not close stage 3.
Issue #11 qualifies the next bounded UV boundary: registered template cleanup,
owner transfer and shared-endpoint detachment under normal, partial, post-template
failure/exception and selected transfer-allocation failures. The wider UV
lifecycle is still open: next characterize object creation before registration
and constructor/setter replacement, then curve sample/rollback ownership.

Issue #14 takes the primitive prerequisite first: Edge/Face constructors and
setVertices, endpoint-alias cache replacement and default front construction.
Pinned-original controls reproduce cache/front construction leaks, failed live
state and an endpoint-alias UAF. Both Face constructors are positive unwind
controls. Actual template arrays/object creation and Boundary registration,
other setters and helper temporary scopes follow this bounded delivery before
the sample/rollback work. See ADR-0004 and the primitive allocation evidence.

Issue #17 qualifies pending Boundary/template registration and the necessary
Face::quality temporary unwind. The prepared real fixture measures outer
vertices/edges and template types 1/4, with destruction-only cleanup after a
template exception. Boundary failures preserve state and permit retry in its
null-curve fixture. Earlier tree generation/subdivision, remaining setters/
helper paths and curve internals follow before sample/initialization/rollback.
Do not broaden these observations to every template pattern or arbitrary reuse.

The completed first slice characterized copying before repair. SetNoh now
explicitly copies scalar state and clears foreign adjacency; general implicit
node copies still carry observers. Initial-mesh callers need independent copies;
changing their boundary to adoption would alter deletion and observer semantics.

| Priority | Source fact and risk classification | Required experiment before repair | Small implementation boundary |
| --- | --- | --- | --- |
| P1 | C04/C05: SetNoh boundary repaired in #8; general node copies remain observer-bearing | Completed copy/adoption tests; separately qualify generic snapshots and adjacency removal | Keep local reconstruction order and explicit source ownership |
| P1 | C10/C11: registered payload, primitive caches, pending registration and root/midpoint construction qualified in #11/#14/#17/#20 | Other setters, mate/root sharing, failed-tree reuse and full-process cleanup remain | Extend demonstrated ownership to remaining scopes without changing template/front policies |
| P1 | C07/C12: sampled curves are non-owning but restoration explicitly deletes/recreates nodes | Shared corners across more than two sheets, retry/rejection, retained accepted mesh, final shutdown and repeated runs | Establish an exclusive sample owner or an explicit cleanup/transfer scope; preserve ID/partition restoration |
| P1 | C09/C13: raw temporary old UV faces and release of selected result | Exception injection before/after front generation, failed structural fallback, rejected selected attempt | RAII for temporary UV resources, adopted result boundary and safe failure cleanup |
| P2 | C02/C22: Model raw-owned mesh collection and pointer-taking patch copy semantics | Copy prohibition/transfer expectations; borrowed curve graph and current-submesh observers; no double destruction | Make copy/move intent explicit only after usage and compatibility review |
| P2 | C05/C17: cached triangle/control state and mutation APIs | Mutate one coordinate/control and independently recompute geometry/derivatives/curvature; isolate immutable CLI path | Explicit immutability or refresh/invalidation, no numerical formula substitution |
| P2 | Polymorphic numerical interfaces and unchecked node/curve indexing | Base/derived destruction ownership and out-of-range negative controls; current stack solver use distinguished from hypothetical heap deletion | Repair only demonstrated dangerous contracts; no opportunistic hierarchy rewrite |

These are priorities for qualification. Static hazards are not all reproduced
runtime failures, and no new whole-application leak-free claim is made here.

Stage 3 needs a usable sanitizer/diagnostic route. Prior MSVC whole-application
instrumented builds hit portability blockers; Windows ASan alone does not imply
LSan coverage. Start with the smallest actual physical/UV ownership boundary,
prove positive and deliberately broken instrument controls, and document what
the tool measures. If an actual portability blocker prevents that slice, use a
single stage 4 work item to unblock it and then return to stage 3. Do not declare
missing instrumentation green or convert a failing test to an expected pass.

## Remaining stage dependencies

| Stage | Concrete dependency exposed by the inventory | Completion constraint |
| --- | --- | --- |
| 4: portable C++/build | USE_MPI/USE_OPENMP vs AP_MESH_HAS flag gap; VLAs/extensions; platform includes and initialized state | Verify effective preprocessor values and actual entry path, qualify compilers and sanitizer route, compare C++23 against the C++17 reference |
| 5: standard-library math | Central Eigen aliases, Bezier matrices and inverse/root operations | Preserve actual operation order and aliasing semantics; analytic and differential point/derivative/curvature/mesh/decision controls before deletion |
| 6: component integration | Generator owns policy/history/IO while Adapter bridges domains; six-header UV include cycle; globals and test adapter | Extract a library and thin CLI with explicit context, narrow domain interfaces and owner/observer lifetimes, then consolidate proven duplicates |
| 7: English interfaces | Separate local UV vs XYZ, curve vs incidence and copy vs adopt vocabulary | Translate in reviewable batches with configuration/report/CLI compatibility; do not rename two distinct concepts into one |
| 8: Doxygen | Mutation, failure, units, ownership and ordering contracts now indexed | Document actual APIs with generated pages reviewed and diagnostics resolved |
| 9: performance | Timer/Data::time clock differences, copies and candidate retention | Qualify clocks, profile equivalent accepted outcomes repeatedly, preserve partition/quality/acceptance coverage |
| 10: integrated campaign | Current measurements are bounded serial Eistute/Book and analytic controls | Qualified memory, portability, docs, negative inputs and supported parallel modes on the same revision; MPI separate |
| 11: freeze | Defect repairs and historical failures already have separate ledgers | Reproducible release identities, input/commands/toolchain/results and explicit remaining limitations |

## Consolidation rules

Keep physical and UV meshes distinct, even if both contain vertices and faces.
Keep analytical and discrete curvature distinct. Preserve the scientific
quadtree/template/front/smoothing sequence and shared-curve partitioning.
The one-dimensional curve tree is not the two-dimensional patch quadtree.

Potential shared primitives include ID-free geometry helpers, aggregations after
domain/threshold review, integration wrappers with explicit interval direction,
and report serialization after precision/identity contracts. Every proposed
deduplication must identify input domain/units, ownership, tolerance, accumulation
order, failure policy, cache invalidation and accepted/rejected regression.

Do not import an alternative apmesh-core generator as an architectural cleanup.
Do not change scientific error metrics, interpolation, adaptation budgets or
acceptance thresholds under the label of removing duplication. Such proposals
remain separate advisor-aligned scientific work.

## Quadtree construction boundary (#20)

Root extents and midpoint construction use local ownership until adoption.
Five calibrated scopes cover generation, uniform subdivision, old-face and
actual neighbor refinement; failed trees permit destruction only. Successful
allocation, cell/neighbor/leaf order and scientific expressions are preserved.
Mate/root sharing, retry and full-process/parallel qualification remain open.
See ADR-0006 and `../evidence/STAGE3_UV_TREE.md`.

## Angle-query temporary boundary (#23)

The angle helper's borrowed endpoint lifetime is qualified in slice 6:
original allocation failures delete caller vertices, while a local detach guard
preserves them without changing successful computation/allocation order. Ten
measured sweeps include copied adjacency and final cache reset. Continue other
helper/mutation and curve-internal scopes, then parametric midpoint replacement
and samples/initialization/rollback. Do not generalize successful helper reuse
to failed-tree observer consumption or retry. See ADR-0007 and the slice evidence.

## Parametric midpoint cache boundary (#26)

Prepare the replacement midpoint/normalized length before changing live Edge
state, then destroy the old owned cache and commit. Old-cache observer lifetime
ends on successful commit; allocation failure preserves its identity/geometry.
Curve evaluation scratch remains mutable. C11 and ADR-0008 record the measured
four-side/two-direction, fallback and null-curve boundary. Zero allocations in
the direct polynomial examples do not qualify failures inside all curve APIs.
Continue other curve mutation/constructor/setter paths before sample ownership,
initialization and rollback; full-process and parallel qualification stay open.

## Curve collection transaction boundary (#29)

SetPoints and UpdateParameters each swap their prepared by-value input into the
live list. C07 defines failed value/node stability, borrowed object ownership,
successful element-observer invalidation and the intentional removal of the
second copy. The two setter calls do not form a joint transaction. Reviewed
serial adapter/generator callers use copied local lists or consume iterators
outside replacement calls; generic external observer compatibility is not
claimed. The omitted parameter sequence identified here is addressed by the
initialized pointer-copy boundary (#32) below. Implicit copy/assignment and
publication of copied curves remain separate findings.
Continue remaining curve constructor/mutation contracts before shared sample
ownership, initialization and rollback. See ADR-0009 and the slice evidence.

## Initialized curve copy boundary (#32)

The omission identified in slice 8 is reproduced for base parametric, Bezier and
Hermite pointer-taking copies. Their base constructor now copies parameters_
under standard-list RAII. C07/ADR-0010 define independent container nodes,
borrowed physical objects, initialized value/control state and non-null source
preconditions. The fix preserves canonical polynomial evaluation and sequence
direction; it does not choose a shared-curve policy or repair inconsistent input.
Next characterize ownership/publication around curve clones and remaining
constructor/mutation paths, then shared samples, initialization and rollback.
Implicit copy/assignment, source-object lifetime versus borrowed-object lifetime,
general observers and full-process/parallel qualification remain distinct.

## Geometry ownership adoption boundary (#35)

Raw curve/patch adoption now guards the relinquished argument before vector
allocation. C03 defines failed argument destruction, unchanged existing entries,
fresh-argument retry and unchanged success/null behavior. Actual initialized
parametric/Bezier/Hermite copies are exercised through Geometry; this does not
execute CloneCurveForPatch or qualify the generator's policy or graph rollback.
Continue that consumer/transaction boundary and remaining constructor/mutation
paths before shared samples, initialization and rollback. No scientific policy
is changed. See ADR-0011 and the measured slice evidence.

## Clone publication boundary (#38)

The actual clone helper and synchronization-disabled operation are isolated in
generator/curve_synchronization.cpp. C03/C07 and ADR-0012 define pending owners,
ordered batch publication and per-original-curve commit. A failing curve stays
unchanged; committed prefixes can remain and whole-operation retry completes.
Successful incidence/filter/replacement/type/orientation policy is preserved,
including mixed/non-Coons behavior. Allocation timing/counts/bytes intentionally
change; no performance claim. Whole-operation atomicity, complete CLI execution
with synchronization disabled and adaptive snapshot/rollback are distinct open
boundaries. Continue remaining construction/mutation and shared-sample
initialization/rollback; full-process/parallel qualification remains open.

## Qualified curve snapshot restoration boundary (#41)

Capture and point-graph restoration are extracted without changing Generator
retry/rejection call order. Prepare pending unique nodes and every list before
committing direct swaps, releasing owners and deleting unique old samples.
C07/C12 define collective source ownership, observer invalidation and unchanged
first-ID success policy. Parameter and full mesh rollback are separate. Continue
with remaining sample construction/mutation and full retry/rollback contracts;
do not infer complete adaptive rollback from this narrow point-graph transaction.
