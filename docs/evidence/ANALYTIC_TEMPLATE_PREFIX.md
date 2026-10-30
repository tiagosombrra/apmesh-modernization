# Checked analytic UV native template-prefix fixture

Classification: engineering-only fixture/tooling. Base: PR #128 main
`13943888bd609f5bbb987e79b0cf89af23b75c08`. Production source, selection,
templates, numerical order, tolerances and scientific policy are unchanged.
The fixture covers a bounded prefix, not a completed mesh or retirement repair.

## Analytic input and explicit cut

Four live cubic Bezier curves describe straight sides of a physical 2-by-3
rectangle. Linear control spacing supplies independent positions/lengths: twenty
physical point checks and four whole-curve length checks per context. UV vertices
remain on [0,1] squared in the serial side/traversal pattern. Native Boundary and
Edge code calculates each arc midpoint and normalized size; no manual setLen
or null-curve replacement is used in positive cases. Masks 0/15 exercise direct
and reversed incidences. Curve owners outlive the native front/boundary teardown.

The fixed matrix uses two/four subdivisions per side and empty/two-face old UV
input. The old triangles separately own their UV vertices and carry explicit
normalized h=0.25; this is a controlled prefix seed, not a claim to reproduce
Adapter's curvature-derived adaptation. Configuration records ratio 1.0,
tolerance 0.0001 (existing CLI defaults), template use and explicit depth -1.
No runtime threshold or policy is changed to obtain coverage.

The inherited AdvancingFront::execute performs its real generate/refine/template/
stage-capture/makeInitialFront sequence. A public geometric-entry override only
captures the prefix and throws a dedicated cut signal, so no selector, geometry
mesh or retirement runs. It returns no fabricated generation status. The native
front, tree, boundary and old UV owners unwind in their intended order, while
curves remain live for a subsequent length observation. Returning from teardown
does not establish a leak or no-allocation guarantee.

## Readiness checks and actual source boundary

Diagnostic copies inspect a fresh unit root, complete leaf partition and cardinal
graph before native sorting. They check positive face overlap/coverage, direction,
reciprocity, membership, count and level differences. The second cut checks the
native neighbor order. Actual first/second-hop neighbor reads are guarded at
their original expression sites, preserving slot-sharing short circuits. A missing
list/pointer refuses the fixture before that access; no neighbor is synthesized,
no production branch is skipped and iterator checks are not disabled.

The source preparer records each literal rewrite and reverses all of them exactly
to the original two native translation units. Its 98 literal neighbor expressions
include the complete source rewrite inventory, not 98 independent runtime paths.
Thirteen other native units, including the actual front and analytic curve code,
compile unchanged as C++17. A separate executable uses both original tree/cell
units. It is run only after the guarded context completes. Observed/unobserved
terminal state matches exactly outside the diagnostic counters.

At the cut, the tree still owns its template objects; transfer has not occurred.
Checks require unique live owner/ID inventories, live edge/Face endpoints and
valid front/view/adjacency observations. Independent Python geometry checks derive
neighbors from all leaf-box contacts, verify a complete nonoverlapping unit
partition and derive template area from interior leaves. They also require exact
native ID/count relationships, the analytic boundary and native stage progress.

## Measured contexts: admitted, guard-only and refused

| Context per profile | Count | Disposition |
| --- | ---: | --- |
| Four subdivisions; masks 0/15; empty/two-face old UV seeds | 4 | Nonempty prefix admitted |
| Two subdivisions; masks 0/15; empty old UV input | 2 | Prefix cut reached, no template coverage |
| Two subdivisions; masks 0/15; two-face old UV seed | 2 | Chained-neighbor preflight refusal; not qualified |
| Missing-curve boundary control | 1 | Normalized-size refusal before native prefix execution |

Each admitted prefix has nine template vertices, sixteen edges and eight positive
faces with total internal UV area 0.25. There are 107 primary and 27 chained
template-neighbor reads per admitted context. GCC and actual MSVC Debug CRT agree
on the matrix dispositions. CRT reports iterator level 2 and retains assertions;
its reports are redirected to stderr to avoid a blocking modal report window.
The fifteen native calls per profile comprise six observed/unobserved completed
pairs and three observed refusals. Only four pairs provide template creation
coverage. The two guard-only pairs and all refusals are not promoted to that
qualification. No unchecked original is executed for a refused context.

The two coarse seeded refusals are new safe observations of this fixture's
preconditions. They do not by themselves establish a supported full-application
defect or authorize a template repair. PR #127's original failed calibration and
616 excluded events remain separately sealed and are not reclassified.

## Preparation findings and exact delivery

The first build lacked an explicit front header in the fixture; its source/log
remain preserved. A reader then incorrectly assumed stdout contained only JSON;
the corrected reader recognizes the exact existing native progress prefix and
reuses the single hashed completed process without rerunning it. Unknown or
inconsistent diagnostics fail closed. Scoped analysis initially rejected a
potential null access in the recursive fixture walker; the explicit rejection
guard corrected the fixture, with the original diagnostic/source retained.
The formatter launcher's missing tool PATH and a seal-reader output-label mismatch
are also retained; neither changed native observations, checks or formatting rules.

Twenty-four checker/preparation tests challenge missing/foreign neighbors,
partition gaps/overlap, zero template claims, IDs, teardown/curve liveness,
unchecked CRT, configuration drift, output parsing, differential drift and
missing/ambiguous native preparation anchors. Local evidence under
build/analytic-template-prefix retains commands, compiler logs, raw process
outputs, executable/source identities, original preparation failures and
independent inventory/source replay. The [compact seal](stage3/analytic_template_prefix/summary.json)
identifies the immutable initial verification artifact.

Require 73 CTest entries with zero failures/skips and 380 Python tests on exact
delivery head and merged main. Each revision also requires the exact fifteen-
outcome checked-CRT inventory, raw/native replay, source reversal, canonical new
fixture formatting, whitespace, inventory/contracts, staged-byte and scoped
fixture/header analysis. Preserve the production application, prior evidence and
all 66 protected raw article inputs. No new scientific run or analyzer invalid-
access/leak control is claimed; existing scientific qualification keeps its scope.
Audit remote main, branches, PRs and checks before delivery; no hosted checks
are configured. Retain all failed/rejected preparation separately from delivery.

After delivery, the next single item is source-preserving observation of inherited
public geometry using only the four admitted prefix contexts. First measure
natural target reachability, without selector substitution, allocation-denial
sweeps or changes to template/domain policy. An unreached retirement remains
unqualified. Refused inputs require separate disposition before further use.
This fixture establishes no broader caller domain, arbitrary-alias/exception/
retry contract, process-wide/parallel lifetime, LSan/UBSan, performance or global
quality result. Stage 3 remains open with 37 numbered qualified slices; stages
0-2 remain closed for measured scope and stages 4-11 remain pending.
