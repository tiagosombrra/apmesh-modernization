# Outside-root ideal Vertex retirement: source audit and rejected calibration

Classification: engineering-only source diagnosis/documentation. Production,
selection, formulas, tolerances, templates and scientific policy are unchanged.
Base: PR #126 exact-main-qualified `0124b0f1880a550c1faf01835123ee22aa11e934`.
Its 72 CTest contracts/356 Python tests, preceding public-front diagnosis and
PR #125 repair/frozen-science evidence remain preserved within their measured
scope. This record introduces no production repair or new qualified slice.

## Ownership and domain boundary found in source

In geometry-phase findBestVertex, the original ideal enters a dedicated pending
owner. Successful adoption inserts frontVertices, then innerVertices, releases
the pending owner and inserts the vertices view. A nonnull newly selected best
returned to makeMesh therefore already has an innerVertices owner. The caller's
geometryPhase && !existed && !quadtree->in(best) branch is outside the pending-
ownership repair. It must not be modeled as another unowned temporary.

Quadtree::in delegates to the root's strict comparisons on both coordinates.
Root-boundary points are not in. QuadtreeCell::out instead has a tolerance-expanded
boundary, and on means neither in nor out. Thus this branch includes boundary
and tolerance-halo points as well as genuinely exterior points. Replacing !in
with out would change the domain policy and is outside this diagnosis.

The branch first publishes the current Edge to rejected in the first pass or
front in the second pass. Only after insertion returns does it remove the ideal
from vertices, innerVertices and frontVertices, delete it and continue. New Edge/
Face construction follows this branch, not the other way around. If that queue
insertion throws, source ordering still retains the ideal's existing owner;
it does not establish queue rollback, retry readiness or complete-caller atomicity.
These are source observations; exception-path and arbitrary-alias qualification
are not supplied by this delivery.

## Calibration attempts and why they are rejected

A standalone C++17 fixture used inherited native selection and the public
makeGeometryBasedMesh wrapper, with eight closed contour layouts, two sorting
settings and two cyclic starts. Native supporting units and copied front source
were unchanged apart from reversible observations. No selector or domain predicate
was overridden and no numerical threshold was adjusted.

The first 64-process GCC pilot called native boundary construction, tree generation
and neighbor refinement, but skipped makeTemplateBasedMesh before makeInitialFront.
That omitted native initialization of template vertex/edge ID counters and allowed
ID collisions. It is rejected preparation, including its zero target entries and
reported terminal statuses; it is not evidence of global unreachability.

The second preparation included the native template prefix and checked distinct
live IDs and owner/observer membership. The inherited code then reported 308
retirement entries per completed GCC and MSVC/ASan profile. The hooks counted
returned queue insertion, three-list detachment and return after delete in both
passes, with exact observed/unobserved terminal-field comparisons. However,
matching hooks and a clean ASan run do not establish a valid caller prefix.

| Preserved preparation | Completed process records | Target events in those records | Disposition |
| --- | ---: | ---: | --- |
| Initial GCC pilot without template prefix | 64 | 0 | Rejected: missing initialization |
| Template-prefix GCC | 64 | 308 | Rejected preparation |
| Template-prefix MSVC/ASan | 64 | 308 | Rejected preparation |
| Template-prefix checked CRT before interruption | 8 | 0 | Partial preparation only |

The checked CRT build retained iterator assertions. After four observed/unobserved
square-context pairs, its next native prefix stopped at the executor's 20-second
limit. That timeout was not classified as numerical failure or fixed by disabling
iterator checks. A separate diagnostic build redirected CRT reports to stderr
and marked preparation/public-entry stages; it preserved the same native library,
container checks and source operations. It reported an empty-list back assertion
before preparation returned, with process status 0xc0000409. Geometric entry was
not reached. The captured diagnostic explains the apparent wait; the original
timeout/report and completed records remain intact. No completed native campaign
was repeated, and no timeout increase was used to claim a passing target case.

The template-prefix campaigns include native double-rejection statuses and
partial meshes, sometimes with outstanding front entries. Only the square and
diamond contexts returned geometry-done in the completed GCC/ASan profiles.
The other contours' partial areas/template faces are retained observations, not
successful triangulations, scientific quality results or supported-domain evidence.
The 616 apparent retirement events are explicitly excluded from qualification.
This diagnosis does not identify an exact production call site for the assertion,
prove a supported-application defect or authorize a template/domain repair.

## Preservation and evidence identity

Production advancing_front.cpp SHA-256 remains
`8549f65b04795f78a8c7b3deee4f244bea3e9af0528e9f4ddbc3d7759798252e`.
There are 24 reversible front observation edits. Exact reversal recovers current
production bytes; missing/duplicate public anchors fail closed. Raw-log hashes,
observations, executable identities, complete/partial case inventories and paired
terminal fields are replayed only to preserve the failed preparation faithfully.
Replay is not retirement qualification. The compact seal records 340 rejected
observation corruptions and 12 rejected public-anchor corruptions.

Artifacts live under build/outside-ideal-vertex-audit. preparation.json identifies
the entry revision/source and prior integration seal; templates/calibration-*/
retain original process reports and logs; crt-diagnostic retains the captured
assertion and prefix-stage evidence. failed-calibration-seal.json labels all
records as rejected preparation and target qualification as blocked.
The [tracked compact seal](stage3/outside_ideal_vertex/summary.json) identifies it.
The initial fixture build also failed on an ambiguous counter name; its source,
compiler log and report remain separate from the explicitly corrected namespace
build. Scoped fixture analysis completed without a configured diagnostic failure;
that static observation does not override the checked runtime prefix failure.

All production/application identities and 66 protected raw article inputs are
preserved. Prior scientific evidence is retained; there is no new scientific run,
allocation-denial sweep, leak/nonallocation guarantee, invalid-access control,
outside-root cleanup repair or lifetime qualification in this delivery.

## Delivery boundary and single next item

Documentation-only delivery requires 72 existing CTest contracts with zero failures/
skips and 356 Python tests on exact head and merged main, sealed negative evidence,
unchanged production/application/raw inputs, whitespace, inventory/contracts and
staged-byte checks. Audit remote main, branches, open PRs and checks before delivery
and repeat regression after merge. Passing those documentation gates must not
turn the rejected target calibration green. No hosted checks are configured.

The next single item is source/caller analysis of the real Boundary, root-domain
and template-neighbor preconditions needed before reopening retirement measurement.
Distinguish a missing fixture obligation from a supported-caller defect. Do not
force a selector result, suppress checked-container assertions or change templates,
domain predicates, numerical order or scientific criteria. A proposed supported-
domain or template-policy change requires explicit advisor alignment. A reproduced
ownership defect would require its own bounded repair and exact-head/main gates.

Target retirement qualification remains blocked. Source ordering alone does not
cover exceptional queue publication, arbitrary aliases, retries, complete adaptive
callers, whole-process/parallel lifetime, LSan/UBSan, performance or global quality.
Stage 3 remains open with 37 numbered qualified slices; stages 0-2 remain closed
for measured scope and stages 4-11 remain pending. Earlier negative relative-area
evidence and unapproved inverse-direction trials retain their dispositions.
