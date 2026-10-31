# Source conditions for selecting a new ideal outside the root interior

Classification: engineering-only source diagnosis and documentation. Entry:
PR #130 main `5da04f14c60384d42b2444c9e8cac90245835d7b`. No production,
fixture, configuration, formula, numerical order or scientific policy changes.
No new native diagnostic context, retirement calibration or failure sweep runs.
Existing required regression retains its original cases and negative controls.

## Result and admitted caller boundary

A computed ideal outside the root is insufficient to reach retirement. The
inherited selector must finish with that fresh ideal, publish its ownership and
observers, and return a nonnull best with existed=false. Only then does makeMesh
test geometryPhase and failure of strict root interior. Source conditions are
mapped below; an admissible retirement witness is not established, and universal
unreachability is not proved. The existing four-context observation remains zero
retirements and all borrowed selections, not a new cleanup qualification.

The admitted scope retains the real serial Adapter's four UV-square side traces,
live oriented curve bindings and coherent native prefix. Physical XYZ coordinates
remain a separate domain. The caller's old-UV geometry, area/curvature-derived
sizes, depth and existing ratio/template settings are inputs with established
scientific meaning. The analytic fixture's controlled old seeds are narrower
evidence, not equivalent to all Adapter inputs. A generic API accepting arbitrary
coordinates or attached cells does not establish caller admissibility.

Finite coordinates/arithmetic, nondegenerate edges and tested triangles, live
endpoints/midpoints/cells and coherent owner/observer/neighbor state remain
preconditions. Invalid aliases, stale or manually rebound cells, NaNs and skipped
prefix initialization cannot serve as witnesses. This audit adds no production
validator or claim that every invalid direct API input is rejected.

## Native path and construction

AdvancingFront::execute keeps its native generate/refine/templates/initial-front
order. The standalone tree execute path is not substituted. A public front below
three edges returns without selection; exactly three takes the Face shortcut.
A larger front calls makeMesh(true), then makeMesh(false) only if the first pass
returns geometry-done. Both calls use the existing geometryPhase=true default.
The second pass can enter with empty queues, as in the preserved observation.

Each makeMesh pass initially rebuilds frontVertices from queued front-edge V1
pointers. That is not the complete vertex-owner inventory; successful meshing
later adds/removes live front observations. The edge view used by interception
also differs from the current front/rejected queues. Reordering the view or
deleting candidates/edges to manufacture selection would change this path.

The native selector starts h at 1.0. makeIdealVertex obtains Edge::normal(),
multiplies h by e->getCell()->height(), scales the normal and adds e->getMid().
For a finite nondegenerate directed edge this has the interpretation

`I = M + h N`, where `h = attached cell size` and `N = left unit normal`.

This expresses the existing operations; it does not replace their floating-point
evaluation order. The offset is not an equilateral height or a direct multiple
of the UV edge chord. The ratio and old sizes affect subdivision upstream, not
an additional factor in this construction. Boundary M may be the oriented curve
arc midpoint in UV; a generic edge M is its cached arithmetic chord midpoint.
Cell size is the maximum box span. Boundary/generated-edge lookup uses M with
the existing tolerance-expanded out test. Template-side cell attachment can use
the coarser adjacent cell, so chord length alone does not establish h.

For a finite point and root bounds `(lx, ly, ux, uy)`, failing strict interior
means `Ix <= lx or Ix >= ux or Iy <= ly or Iy >= uy`. Boundary points and the
tolerance halo therefore belong to the guard's target. Substituting out would
change its domain: out expands the root by TOLERANCE_AFT. Nonfinite values can
also fail the strict conjunction, but are outside the admitted finite contract.

One conditional geometric inference narrows the search without constructing a
fixture: for a coherent fresh unit-square root, an original correctly directed
boundary edge with M on its side segment and dyadic `0 < h <= 1` points inward.
Its raw ideal lies in the closed unit square. At h=1 it reaches the opposite
border and remains subject to the selector filters. This statement assumes a
valid in-segment curve midpoint; it proves neither successful new selection nor
behavior of template-front or later generated edges.

## Conditions before fresh selection can return

The following are ordered obligations from findBestVertex, not independent knobs
to tune. All relevant operations must return normally; allocation failure before
publication/return does not demonstrate arrival at the caller's domain guard.

| Step | Native requirement |
| --- | --- |
| Candidate identity | Skip base-edge endpoint pointers and exact coordinate matches using Vertex::matches. |
| Spatial window | For other candidates, skip coordinates outside the ideal-centered h box, then skip Euclidean distance greater than h. Boundary equality passes these filters. |
| Base distance | A surviving near candidate with dist<0 or dist<=0.1h aborts the entire selector with null best; it does not merely skip that candidate. Earlier accepted candidates do not prevent this later abort. |
| Existing candidate acceptance | interceptionTest(e,candidate,true,false) must return false: both proposed sides against all observed edges, plus the live-front point/Face check. Accepted candidates enter bestVertices. |
| Empty survivor list | The scan must complete normally with bestVertices empty. A nonempty list instead deletes the pending temporary and follows existing-vertex angle/tie selection, returning existed=true. |
| Fresh ideal interception | The empty-list branch must pass interceptionTest(e,best), whose defaults retain the same all-edge and point/Face checks. |
| Fresh ideal proximity | No edge in edges may satisfy edge->intercept(best), the native point-to-edge distance threshold. |
| Adoption and return | Assign the original next ID; publish frontVertices and innerVertices, release pending_ideal, then publish vertices. The successful geometry branch returns existed=false with nonnull best. |
| Caller domain | Only after the null-best path is excluded, require geometryPhase && !existed && !quadtree->in(best). |

The literal dist<0 branch must be preserved, but it is not a signed half-plane
test under finite nondegenerate arithmetic: Edge::straightDistance is twice
Vertex::surface divided by edge length, and surface takes fabs of oriented area.
The explicit accordingToNormal candidate filter belongs to the topology else
branch, not the geometry branch. Adding it to geometry would be a behavior/policy
change outside this audit. This finding is not evidence of a supported defect.

Interception also cannot be summarized as a general closed-contour clipping
proof. Segment intersection uses strictly negative cross-product products for
both sides: collinear and endpoint contact alone are not proper crossings in
that predicate. The tentative Face check separately rejects a nonmatching live
front vertex for which !Face::out holds, including its barycentric tolerance.
The final point-to-edge test uses distance<TOLERANCE_AFT, not <=. These filters
may veto an apparent exterior ideal before adoption. Passing one geometric
intuition or one predicate is not proof that all predicates pass on an admitted
native state. Degenerate/nonfinite arithmetic is not an acceptable bypass.

## Ownership and witness obligations

At the guard, a selected new ideal is already owned by innerVertices; the
temporary pending_ideal was released inside the selector. The caller first
publishes the base edge into rejected in the front pass, or into front in the
rejected pass. It then removes best from vertices, innerVertices and
frontVertices, deletes it and continues. This is distinct from pending-ideal
cleanup before selection. Queue publication can allocate; this source audit
provides no exception-retirement, rollback, retry or nonallocating guarantee.

A future witness would have to establish all of the following in one admitted
native history: original prefix readiness; actual cell/midpoint provenance and
finite exterior-or-border ideal; normal empty-survivor scan; both ideal vetoes
passing; completed adoption/return; and actual caller guard/retirement entry.
A raw exterior formula, a direct protected-method call, a borrowed best, an
empty second-pass entry or a manually chosen new best supplies only part of
that obligation. No such witness is supplied here. PR #127's 616 excluded events
and refused prefixes retain their earlier dispositions.

## Evidence, regression and disposition

The [source facts](stage3/selected_ideal_domain_conditions/source_facts.json)
record 71 unique scoped anchors, source locations and hashes across ten files.
Their replay checks identity and ordering; they are source evidence, not formal
alias analysis, symbolic floating-point verification or runtime path coverage.
The [compact summary](stage3/selected_ideal_domain_conditions/summary.json)
identifies the initial audit seal. Local build/selected-ideal-domain-audit retains
commands, source replay, prior-seal preservation and exact delivery reports.

PR #130's immutable initial/head/main raw observations and executable/source
identities are verified without rerunning its custom normal-geometry observation.
No fixture or analyzer control is added. Existing required exact-head/main
regression remains 73 CTest entries, with no failures/skips, and 380 Python tests,
including its existing accepted/rejected and negative-control inventories.
Require source-anchor/order replay, unchanged non-documentation tracked files,
application identity, all 66 protected raw article inputs and prior sealed
evidence, plus whitespace, inventory/contracts, staged-byte/metadata and remote
main/branch/PR/check audits. No new scientific run or sanitizer qualification is
claimed. A documentation gate passing does not supply the missing witness.

The bounded source-condition audit is complete. Retirement remains unreached
and unqualified. Stage 3 stays open with 37 numbered qualified slices; stages
0-2 retain measured closure and 4-11 remain pending. No supported-application
defect, universal impossibility theorem, repair or scientific-domain expansion
is established.

Next single item: source-only audit of template-front and generated-edge
cell/midpoint provenance and their exterior-crossing obligations, to determine
whether an admissible witness can be justified before any new measurement.
Keep fixtures, selection, tolerances, templates and scientific policy unchanged.
