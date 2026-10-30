# Template-prefix Boundary, root-domain and neighbor preconditions

Classification: engineering-only source/caller diagnosis and documentation.
Entry: PR #127 main `f35eb16d46c8478876292ae1efb7f2cfe2946913`, with
72 CTest contracts and 356 Python tests validated on exact head/main. This audit
does not alter production, templates, selection, numerical order, tolerances or
scientific policy. No new retirement calibration is executed. PR #127's original
failed preparation, timeout/assertion and 616 excluded events remain sealed.

## Real caller and coordinate/size obligations

The serial Adapter::AdaptDomain attempt sorts canonical curve samples and appends
bottom (t,0), right (1,t), top (t,1) and left (0,t) side traces. The final two sides
traverse their parameters in reverse; a reversed patch incidence uses the existing
oriented-parameter helper and traversal convention. Each side borrows its actual
CurveAdaptiveParametric object. Those objects belong to the live patch/geometry
context and must outlive the attempt. Physical XYZ node copies and UV Vertex
coordinates are distinct domains; an arbitrary physical contour is not this input.

Complete finite side partitions with consistent points/parameters, nondegenerate
edges and a closed, consistently oriented four-side trace are caller prerequisites.
The mapped code does not prove that every invalid direct API input is rejected.
The serial and OpenMP source paths share the four-side construction pattern, but
this audit supplies no new OpenMP/MPI execution or qualification.

Boundary assigns a completed edge to the previous outgoing curve/orientation.
Edge::makeParamMid recognizes the unit-square sides and sets getLen from physical
curve arc length divided by total curve length. That normalized size differs from
Edge::length, the Euclidean UV chord. Null curves skip this evaluation. The older
UV-memory square fixture explicitly supplies synthetic normalized sizes; its
limited contract does not make arbitrary null-curve polygons faithful serial inputs.
Curve midpoint/length validity and live ownership remain required, not invented
by manually copying a chord length into a differently shaped boundary.

The serial caller also supplies old faces using actual triangle UV parameters,
assigns h through its existing physical-area/curvature calculation and resolves
the configured depth cap. A new fixture must record those inputs/settings. It
must not change their scientific meaning, silently replace curved-size evaluation
or adjust depth/template configuration merely to obtain prefix completion.

## Prefix order and the two execute paths

For a fresh tree, generate obtains the Boundary box and expands its shorter span
to make a square root. For a complete normal UV-square caller this identifies the
local square; an elongated arbitrary contour instead introduces a larger square
region. The generic API's ability to accept such coordinates is not proof of a
supported template domain. Existing roots/setters likewise do not prove a newly
attached graph's consistency with its boundary.

| Entry/path | Active sequence relevant to this audit |
| --- | --- |
| AdvancingFront::execute | generate(oldmesh), refineAccordingToNeighbors, optional native templates, stage capture, makeInitialFront, public geometry phase |
| Quadtree::execute | generate(oldmesh), refineToLevel, refineAccordingToNeighbors |
| makeTemplateBasedMesh | sort neighbors, initialize boundary-derived vertex/edge counters, outer vertices, outer edges, internal templates |

The front's refineToLevel call is commented out; the standalone tree path's call
is active. Substituting the standalone path or inserting uniform refinement would
change the preparation under audit. An older passing standalone-template test is
not proof that the exact serial front prefix is ready in another layout.

Boundary getLen inputs are consumed by initial subdivision and reset afterward.
The templates initialize IDs before makeInitialFront copies the quadtree counters.
Skipping that initialization explains the first pilot's ID problem without
authorizing manual ID repair, alternative ordering or a source change.

## What neighbor preparation establishes, and what remains required

Native subdivision creates sibling links, updates cardinal reciprocal observations
and then clears the subdivided parent's lists. refineAccordingToNeighbors addresses
cardinal counts over two and level differences over one. sortNeighbors orders
the first/last neighbors under that preparation; it is not a general graph repair
or completeness validator. Direct setNeighbors copies a list without establishing
reciprocity, positive geometric overlap, balance or readiness of other lists.

QuadtreeCell::inBoundary is true when any cardinal neighbor list is empty. It
describes the root-exterior topology and reads no geometric Boundary contour.
It therefore cannot be used as an arbitrary-polygon inside/outside classifier.
Passing that test before outer-vertex creation establishes four nonempty local
lists, but the corner-sharing code also reads neighbor-of-neighbor lists. The
source balancing loop does not explicitly validate all those chained accesses.
Slot-sharing order and short-circuit conditions determine which are consumed.

Consequently a caller-faithful diagnostic prefix needs distinct observations of:

- A fresh coherent root, complete UV-square boundary and valid normalized sizes.
- Cardinal neighbor direction, positive face overlap, reciprocal identity, bounded
  level difference, cardinal count and required ordering at the pre-template cut.
- Readiness of each chained list actually consumed by the native corner/edge
  sharing path, including the relevant slot-sharing and short-circuit context.
- Native template/owner/observer/ID state after successful prefix completion.

This is an audit-derived preparation contract, not a new production validator.
Cardinal balance alone is not proof of each later chained dereference. Conversely,
this source observation does not prove a supported application violates the
obligation or locate the prior CRT assertion at a particular expression. That
exact site remains unestablished. Do not repair templates, rebind neighbors or
disable checked iterators to turn an unmeasured or refused prefix into coverage.

## Evidence and delivery limits

The local source audit records unique source anchors, line locations and hashes
across the serial caller, domain/size conversion, root generation, both prefix
paths, template order and neighbor obligations. Its literal scope does not claim
complete alias analysis, arbitrary external-caller coverage or formal proof of
all input validation. The [compact seal](stage3/template_prefix_preconditions/summary.json)
identifies build/template-prefix-preconditions-audit/source-audit.json.
All production/application identities, the PR #127 integration/failed-calibration
seals and 66 protected raw article inputs are preserved.

The source audit is complete for this bounded item. Target retirement qualification
remains blocked: no new native calibration, prefix execution, exception sweep,
leak/ASan-control qualification, supported-domain expansion or scientific result
is supplied. Existing frozen science retains its prior scope and is not rerun.

Documentation delivery requires 72 existing CTest contracts with zero failures/
skips and 356 Python tests on exact head and merged main, unchanged source/evidence/
application/raw identities, source-anchor replay, whitespace, inventory/contracts,
staged-byte checks and fresh remote main/branch/PR/check audits. Passing these
documentation gates does not qualify a retirement path or close Stage 3.

The next single item is to prepare only a caller-faithful UV-square prefix fixture
with live analytic curves and recorded existing old-UV/configuration inputs.
Preflight the obligations above without entering an unready template path; retain
refusal and the original negative evidence. Require checked-CRT completion with
coherent owners/IDs/observers before considering retirement measurement separately.
Do not force selection, add uniform refinement, suppress assertions or alter the
scientific domain. Domain/template-policy proposals still require explicit advisor
alignment. Stage 3 stays open with 37 numbered qualified slices; stages 0-2 remain
closed for measured scope and stages 4-11 remain pending.
