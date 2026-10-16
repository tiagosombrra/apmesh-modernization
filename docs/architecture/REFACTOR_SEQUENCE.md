# Dependency-ordered follow-up from the stage 2 inventory

This is an implementation sequence within the approved stages, not a production
change in stage 2. Evidence IDs refer to [contracts.json](contracts.json).
Only one work item is active at a time; required regression gates remain exact.

## First stage 3 slice: establish and qualify lifecycle boundaries

The first slice should characterize physical node adoption/copy and adjacency
lifetime before changing its API. C04/C05 prove a discrepancy: SetNoh copies a
NodeAdaptive while its grouped comment promises adoption; the implicit node
copy also carries element observers. Existing initial-mesh callers depend on
having an independent owned copy. Changing SetNoh to adopt in place would be a
behavior change with different deletion and observer consequences.

| Priority | Source fact and risk classification | Required experiment before repair | Small implementation boundary |
| --- | --- | --- | --- |
| P1 | C04/C05: copy/adopt contradiction and copied element observers; source-proved contract ambiguity | Distinct caller/owned node identity, ID/XYZ preservation, independent submeshes, original lifetime, copied adjacency and deliberate expired observer controls | Separate explicit copy/adopt names or contracts with caller audit; rebuild/rebind adjacency as justified, preserving numerical order |
| P1 | C10/C11: Face/Edge delete shared endpoints unless detached; source-proved conditional teardown | Normal, partial, failed front, quadtree/template and exception exits with deliberate duplicate/dangling/leak controls | Explicit owners and observer-only topology under one coherent front lifecycle, in a bounded patch |
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
