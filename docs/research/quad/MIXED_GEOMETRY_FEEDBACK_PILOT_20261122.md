# Mixed-state geometric feedback pilot

22 November 2026, Fortaleza. The researcher selected the bounded geometric
feedback pilot for [issue #221](https://github.com/tiagosombrra/apmesh-modernization/issues/221).
The result and the interface that precedes it are separate from the pending
smoothing comparison. The desired adaptive cycle uses the previous mixed
mesh to decide the next local sizes at both the contour and the interior.

## Graph and input identity

Draft [PR247](https://github.com/tiagosombrra/apmesh-modernization/pull/247)
(`94dc35a6c84899fb36eea86c1d352b0842ba3bcf`) contains the typed feedback
graph, compiled independently with MSVC Debug C++17. The graph is indexed by
previous mixed faces followed by the original ordered contour intervals.
Links identify opposite-oriented shared face edges, each interval's unique
owner face, and consecutive intervals. An independent directed-edge audit
matches 3,518 undirected links and all 46 original interval owners in the
fixed-1.5 Step 1-3 archives and the local two-block Step 3. Sixteen malformed
cases are rejected across the four inputs. The implementation excludes
scientific selection and remains on the draft branch.

On the first graph PR head, hosted native Linux/Windows and frozen TRI jobs passed.
The hosted TRI baseline/tooling job failed because the new CMake target
changed the architecture inventory build-input hash. Refresh only the
`tests/quad/CMakeLists.txt` inventory entry and verify 10/10 local inventory
tests. The corrected graph PR head is `d2068628218b51b0bfe485df9b1ca5cb30588676`.
Its hosted checks are pending at this checkpoint. The pipeline failure is
recorded against its original head.

## One isolated native trial

The local trial on the graph source runs within the existing real-curve
article-front application. Use the genuine final Step 2 mixed mesh as the
trial predecessor. Its status traces back to an accepted reference TRI
step; it is a baseline input for this pilot. Measure the existing analytic
surface residual per face (barycentric TRI and bilinear QUAD). Keep the
actual maximum sample location for each face. Halve the physical target on
the highest-residual face of each type. Use median physical edge size for
the initial face sizes and the native arc length for the source intervals.

Propagate monotonically using `min(current, 1.35 * neighbor)` in three
simultaneous passes on graph nodes at most three links away from either
selected face. Persist sender/receiver identities and physical sizes.
A reduced face requests at most one direct level in the deepest existing
leaf containing its residual sample, with retained leaf order resolving
ties. Coalesce duplicate leaf requests before native 2:1 balancing. A
reduced original interval receives one direct native binary split, using
its original Bézier curve and retaining every old identity and sample.
Rebuild the physical mixed mesh on the derived tree and descendant
curve partition using the same clearance rule, templates, front and
five-pass smoother. The experimental payload lives in an unpublished
archive alongside standard histories; it is never selected for the
application's accepted state.

## First native attempt

MSVC 19.44.35229.0, Windows x64 Debug C++17. The application exits zero
in 16.17 s under 180 s, while the inner feedback attempt records a
rejection. All eight reference TRI/mixed files and the original curve
trace match the independent retained archive byte for byte.

An independent replay of the sample weights on the actual Step 2 previous
mesh confirms highest-residual TRI index 254 and QUAD index 242
(zero based). The observed propagation has 39 decreases: 22 face-to-face,
eight face-to-curve and nine curve-to-curve. No curve-to-face decrease
wins the limiting comparison in this attempt. Eight distinct intervals
receive a smaller target, including five on straight sides. They are
transient boundary requests. No changed contour or candidate is published.

The local attempt stops during native leaf eligibility before any requested
tree edit or AFT successor. The first failing target is TRI index 289,
sample UV approximately (0.276021, 0.030989). The point is inside leaf
ordinal 37, box `[0.25, 0.3125] x [0, 0.0625]`, already at depth 4.
The legacy adapter resolves the input `-1` depth to the Step-N cap of 4.
The archive check identifies 17 face requests, 15 inside seven distinct
eligible leaves and two at the same capped leaf. The existing cap is
preserved. There is no new mesh, no same-site error or quality comparison
and no accepted mixed epoch. Preserve the first failed attempt and its
original trace hashes.

## Second native attempt with the cap preserved

The researcher approved a second bounded attempt disposing of saturated
requests. Keep depth 4, report the two capped requests and refine the
seven distinct eligible leaves. The native tree changes 67 to 88 leaves.
Native balancing adds no extra leaves and the explicit depth check passes.
The transient contour uses eight direct native binary divisions, giving
18 instead of 10 intervals in the experimental source passed to generation.
The original curve graph and previously observed nodes remain the source.
The eight original TRI/mixed OBJ files and curve trace are again checked
byte for byte. Preserve the first failed output and source bytes separately.

The first compilation of this change exited one with MSVC C2662:
`QuadtreeCell::getLevel()` is a legacy non-const getter. Correct the
borrowed observer type, preserving traversal and policy, before the only
native invocation of this variant. That process exits zero in 25.39 s
under 180 s. Its inner mixed candidate fails during the existing
five-pass smoothing with `Mixed smoothing inverted or collapsed a UV quad`.
The front reached smoothing after its completion and intersection checks.
The failed pass is not identified by the retained diagnostic and no
pre-smoothing shape is available. No valid successor, final error/quality
comparison or mixed epoch is produced. In this observation propagation
included face-to-curve but no curve-to-face reductions.

## Limits and next step

The next proposed comparison is to validate the pre-smoothing mixed
candidate, stop at the first geometrically invalid smoothing pass, and
retain the last fully validated positions for experimental comparison.
Obtain explicit alignment on that treatment. Keep the cap-preserving
request policy and its evidence. Once valid geometry exists, compare the
same source sites across predecessor and successor, check shape and growth,
and align scientific mixed admission before incrementing epochs.

The [numeric evidence](evidence/MIXED_GEOMETRY_FEEDBACK_PILOT_20261122.json)
binds source and archive hashes, invocation outcomes, graph evidence and
the first native attempt. This pilot uses geometric source deviation.
Qualified mixed curvature feedback, policy selection, mixed acceptance,
full exact-revision regression and at least two mixed-driven accepted
epochs remain open. The provisional result does not replace an accepted
owner or archive.
