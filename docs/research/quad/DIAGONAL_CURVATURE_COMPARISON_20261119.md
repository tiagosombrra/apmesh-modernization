# Both-diagonal Gaussian witness experiment - 2026-11-19

The explicitly adopted experiment compares both physical QUAD diagonals on the
already retained real meshes, without changing generation or adaptation. PR242
source `d2eb15e05733d1d384402c92aeb0a7293bd7a3df` is integrated as
`7ccd8d769536b291a2264b140fa4acfc76f3960a`; parents are canonical
`3052a7c0cbcb52ac0e5a1afb944668a575fc9411` and that candidate. Identical tree
`db837237445646074412eac3b2bdd8ac3bd5aa78` is verified. This completes the bounded
diagnostic comparison, not selection of a mixed estimator or full R3/M7 closure.

## Method and scientific scope

The generated read-only native probe calls the unchanged P2b
`AuditMixedCurvature` header. Its existing0-2 subtriangle angle/area arithmetic
is unchanged. Rotating each copied QUAD cycle by one vertex selects1-3 through
the same routine; TRI cycles are untouched. Source nodes/elements/files are not
changed and no diagonal is inserted into the actual mesh. The probe owns only
value vectors; it neither adopts nor publishes a physical SubMesh.

An independent cosine-law/Heron calculation verifies each native node's angle
sum, barycentric area, defect and density. Comparison requires both primitives
and density to agree with absolute/relative tolerance1e-7. This is an instrument
agreement bound, not an acceptance criterion. Actual cross-compiler differences
are much smaller, reported below. Both variants retain the existing disk
vertex-link/edge/winding and2pi Gauss-Bonnet witness checks.

Analytical Gaussian K is evaluated from the existing independent bicubic
Bernstein control net and exact first/second derivatives at the archived UV
coordinates. It uses no numerical differencing, FindUV or production small-K
clipping. Plane/paraboloid/saddle polynomial control nets and a spherical
derivative fixture verify the analytical calculation. Rotation, inverse-area
scaling, malformed geometry and pure-TRI invariance are also controlled.

Only interior nodes enter analytical Gaussian comparisons. Boundary pi-minus-
angle density is retained as boundary turning density; it is not treated as
Gaussian error. Both diagonals use exactly the same original node sites within
each mesh. Differences are absolute, in inverse squared model units. No relative
normalization near K=0, selected diagonal, accepted mixed state or global mixed
error is introduced. Different meshes have different site sets; these summaries
are not a common-site TRI-versus-mixed convergence or superiority experiment.

## Current article path results

All values below use interior sites of the actual mixed reconstruction. Absolute
differences compare each witness with smooth analytical K at those same sites.

| Step | Interior sites | Median abs difference0-2 | Median abs difference1-3 | Maximum abs difference0-2 | Maximum abs difference1-3 | Maximum diagonal gap |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
|1|25|0.0100630|0.0121587|0.241745|0.352265|0.345818|
|2|271|0.0100440|0.00984049|4.827009|3.839127|5.438697|
|3|675|0.0102498|0.00996614|2.342681|3.446951|1.819897|

Neither fixed diagonal wins every stage/distribution measure. Diagonals have
opposite estimated signs at8/25,82/271 and139/675 interior sites. This counts
opposite witness signs, not necessarily two analytical sign errors.

At Step2 node115, UV(0.5754748725,0.1006557135), analytical K=-0.5564634621,
0-2 density=+4.2705458618 and1-3 density=-1.1681506589. Its diagonal dual areas
are0.0052097723 and0.0177276155. At Step3 node15, analytical K=-1.2456069096,
0-2 density=-1.7763299861 and1-3 density=+0.0435665516. These are concrete
same-node counterexamples to assuming a harmless diagonal choice. They do not
prove all diagonal-based estimators invalid or establish a replacement operator.

The22 retained observations include current article8, original-curvature
accepted/rejected control8 and stable-retry control6. They contain4227 node
observations per profile, not4227 distinct physical states. Pure TRI diagonals
are exactly identical. Accepted/rejected source identities are preserved; no
missing retry is fabricated. Input hashes/bytes are unchanged. All three native
profiles agree; maximum cross-profile absolute density difference is
2.0321522242738865e-12. Full per-node CSV/JSON and a visually checked common-scale
UV scatter figure are local artifacts under `build/quad-diagonal-curvature-20261119/`.
Portable summaries, worst nodes, hashes and provenance are in the evidence JSON.

## Exact qualification and closure inventory

| Gate | Exact candidate | Exact research merge |
| --- | --- | --- |
| Local required baseline |85/85|85/85|
| Reporting/analytical controls |17/17|17/17|
| Actual both-diagonal native comparison |MSVC19.44.35229 Debug, GNU13.3, Clang18.1 ASan/UBSan/leak;22 observations each|Same current-source checks actually re-executed with identical qualified probe images |
| Native malformed controls |Three refused inputs per profile: empty/repeated-vertex/collapsed|Same three actual refusals per profile |
| Hosted exact checks |44521151484,4/4 SUCCESS|44522539529,4/4 SUCCESS |

Hosted jobs run17 Python reporting/analytical controls on both native platforms,
existing20 native contracts,85 root tests/527 tooling Python and exact frozen
Eistute5/Book4 OBJ/acceptance/positive-boundary comparisons. Existing actual
GNU/ASan/MSVC article histories agree. The generated both-diagonal probe/archive
experiment is executed locally in three profiles; no hosted execution of that
specific experiment is claimed. No source-generation or new-model campaign runs.

The execution announcement was09:09 Fortaleza; the first recorded qualification
command actually starts09:10:17 and finishes09:12:49. Post-merge execution runs
09:18:27-09:20:14. First qualification failures stop
the controller and preserve output; none occurs. An earlier shell-quoting error
in CMake-project text preparation starts no compiler/test and is corrected with
file-based preparation. It is not hidden as a successful invocation or a test
retry. Direct identical-tree research checkout preserves2679 tracked files'
bytes/size/write-times. Existing C++/config/source/header identities remain
unchanged; the generated probe is new detached diagnostic code. No existing
generator, curve sampling, smoothing, ordering, acceptance/stopping or TRI
estimator changes. Main ef40c0f and concurrent work remain separate.

The bounded closure audit covers code/value ownership, numerical/analytical/
negative controls, source/file/history contracts, explanatory output and
scientific exclusions. Preserve old enum-analysis exit1/DrvFS failures and
historical/native-CRT/allocation/transaction/exact-tie/general-geometry/Doxygen
limits from PR240. No full-stage, historical-equivalence, memory-exhaustion,
production estimator, accuracy-superiority or adaptive-epoch closure follows.

## Next bounded action

Prepare a reference-backed mixed Gaussian/mean operator contract for scientific
alignment, using the same-node sign-flip examples as required validation cases.
The original ErrorGlobal path also uses mean curvature when analytical Gaussian
curvature is below its existing tolerance (generator_adaptive.cpp:7259). This
Gaussian-only witness cannot substitute for that complete contract. Define
adjacency, area/angle conventions, mean curvature and boundary treatment before
adopting a mixed global error; preserve the original TRI and acceptance/stopping
policies. No automatic diagonal selection or further flag/generation sweep is
the successor. Actual mixed global error remains unavailable; accepted mixed
adaptive epochs remain0.

[Portable evidence](evidence/DIAGONAL_CURVATURE_COMPARISON_20261119.json).
