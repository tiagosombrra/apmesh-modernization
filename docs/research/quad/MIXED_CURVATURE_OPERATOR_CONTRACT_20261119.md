# Mixed Gaussian/mean curvature operator contract - proposal

Date: 2026-11-19 Fortaleza. Baseline: canonical
`bfaded719b70a04bf821f677247819a639215cd0`, tree
`56bb682c023f3b371f54c590f3cc479f10d2c7cc`.
Status: **proposed, not adopted or implemented**. This document completes the
requested specification/references step. It does not authorize an estimator,
repair legacy formulas, qualify a prototype or change adaptation.

## 1. Functional target and preserved behavior

The next deliverable, if scientifically adopted, is a read-only per-node
Gaussian K and signed mean H estimate on the actual archived mixed graph,
including its TRI-only incident regions and boundary nodes. The current
prospective1993 mixed generator, templates, source curves, smoothing, physical
owners, acceptance/stopping, default TRI and original ErrorGlobal remain intact.
No alternative mesh generator, CGAL/Eigen dependency, new balancing law or
unrelated generation campaign is proposed.

The [approved diagonal comparison](DIAGONAL_CURVATURE_COMPARISON_20261119.md)
already establishes same-node sensitivity: Step2 node115 has analytical
K=-0.5564634621,0-2 witness+4.2705458618,1-3 witness-1.1681506589. Step3 node15
has the opposite diagonal/sign-choice problem. No fixed diagonal wins all
measures. These are required counterexamples for the next operator, not proof
that every triangulated estimator is invalid.

## 2. Current source contract and newly identified limitations

The following are source observations at the pinned revision, not new native
experiments or conclusions about the historical authors' intended equations.

| Component | Observed behavior | Consequence |
| --- | --- | --- |
| CurvatureDiscrete constructor |Sums incident physical element areas and corner angles |Area/angle conventions are scientific inputs |
| CalculateGaussCurvature |3*(factor-angle_sum)/sum_area |Existing triangle-area normalization; not a generic four-node formula |
| CalculateMeanCurvature |3*sum(signed adjacent-normal angles)/sum_area |No edge-length factor occurs in the inspected call chain |
| Adjacent traversal/concavity |Uses exactly node slots1,2,3 |Polymorphic access alone does not support a four-node fan |
| QuadrilateralAdaptive area/normal |Uses the local0-2 two-triangle geometry |Direct reuse would retain a hidden diagonal convention |
| Original ErrorGlobal |Selects Gaussian when abs(Ka)>=TOLERANCE, otherwise mean when abs(Ha)>=TOLERANCE |A Gaussian-only witness cannot fill this contract |

### 2.1 Legacy mean dimensional observation

`Adjacent::AngleElement` calls the vector angle; `ConcavityElement` supplies only
-1/0/+1. Triangle area is half the cross-product norm and GetArea returns that
area unchanged. Thus, on a fixed adjacency and fixed tolerance/concavity branch,
the inspected discrete-mean formula scales as1/s^2 under coordinate scaling by
s. The unclipped analytical mean formula scales as1/s. This is a source-level
dimensional inconsistency to investigate, **not** a newly reproduced native
failure, an established cause of the diagonal results, or permission to correct
TRI. Fixed tolerances can also change branches when coordinates are rescaled.

The legacy Kim/Jeong/Kim reference was located, but its full PDF returned403.
Its abstract does not establish the intended mean equation. No claim of a
historical transcription defect or scientifically approved repair follows.
Keep the raw legacy value and baseline reproducibility; any repair is separate.

### 2.2 Exact global aggregation and its limit

For each submesh j the code accumulates S_j=sum(discrete-analytic)^2 and
P_j=sum(analytic)^2 on the selected Gaussian/mean branches. When both sums and
N_j are positive, it forms sqrt(S_j/P_j)/N_j, then averages across submeshes.
The division by node count, zero branches, iteration order and tolerances are
part of the retained numerical contract. It is not silently replaced by RMS,
area weighting, a maximum norm or another normalization.

With geometrical K in inverse squared length and H in inverse length, adding
their squared terms in one accumulator also requires an explicit dimensional/
normalization decision. Preserving a historical numeric formula does not prove
scale invariance or scientific equivalence to a new mixed estimator. This
proposal therefore stops at nodal K/H; an approved mixed global aggregation and
its complete coverage remain distinct gates before adaptive acceptance.

## 3. Reference-backed alternatives

[Cazals and Pouget, SGP2003](https://graphics.stanford.edu/courses/cs164-10-spring/Handouts/papers_p177-cazals.pdf)
estimate local differential quantities from polynomial jets of surface samples.
The paper discusses least squares, rank deficiency, conditioning and scaling.
Its convergence analysis assumes sampling conditions; it does not guarantee
accuracy for our finite irregular archive or choose our neighborhood policy.
The journal version is recorded by [DOI10.1016/j.cagd.2004.09.004](https://doi.org/10.1016/j.cagd.2004.09.004),
but the full primary text inspected here is the2003 conference paper.

The [CGAL jet-fitting manual](https://doc.cgal.org/latest/Jet_fitting_3/index.html)
documents a PCA fitting frame, polynomial fitting, principal curvature output,
minimum sample requirements and degeneracy/conditioning caveats. It is an
implementation reference, not a proposed dependency or evidence of identity
with a future standard-library implementation. The inspected manual identifies
version6.2.1; retrieval date is2026-11-19.

| Route | Benefit for this task | Unresolved cost/limitation | Disposition |
| --- | --- | --- | --- |
| Literal TRI operator through Quad virtual methods |Small apparent code delta |Three-slot adjacency, triangle normalization, diagonal-dependent area/normal and legacy mean observation remain |Do not treat as an engineering refactor |
| Polygon Laplacian family |Published handling of general polygon faces |Requires matching mass/normal/Gaussian/boundary definitions and does not automatically reproduce the legacy mean rule |Alternative for explicit future alignment |
| Local quadratic jet |Both K and H from the same local physical geometry, without selecting a QUAD diagonal |Sampling, rank, frame and boundary accuracy require validation; not legacy numerical equivalence |Recommended bounded candidate, not adopted |

[Alexa and Wardetzky2011](https://ddg.math.uni-goettingen.de/pub/Polygonal_Laplace.pdf)
describe polygonal Laplacians. [Bunge et al.2020](https://onlinelibrary.wiley.com/doi/10.1111/cgf.13931)
describe a virtual-point polygon refinement/coarsening construction. These
support the alternative's existence, not a complete K/H selection for this
project. Full PDF retrievals exceeded this tool's size limit; their primary
abstracts were inspected, not a full coefficient-by-coefficient implementation
audit. A search abstract must not settle their detailed numerical choices.

## 4. Recommended candidate - project choices requiring adoption

The following is a proposed executable specification. It is a project
instantiation of a published method family, not a claim that every choice below
comes from the paper or was used by the1993 mesher.

### 4.1 Scope and samples

- First scope: the existing smooth, oriented, single Bezier patch and its
  retained initial/accepted/rejected/retry snapshots. No shared-junction fitting,
  cross-patch normal averaging or global node welding.
- Keep all physical positions fixed. Include the query node and each other
  vertex of incident TRI/QUAD faces once, including the opposite QUAD corner.
  Preserve observer containers; use a separate ordered sample-index list.
- Start with this coface one-ring. If there are fewer than six points, the frame
  is numerically ambiguous or the design is rank deficient, expand once to the
  complete coface two-ring in the same chart. Recompute on that complete set.
  No partial ring, k-nearest Euclidean replacement, analytic-error-based stencil
  selection or larger hidden fallback.
- Sample order is the immutable archived local node index. Duplicate coordinates
  with different identities are not silently merged; report invalid sampling.
  Boundary nodes use the same bounded one-sided sampling rule.

The two-ring cap, opposite-corner inclusion and unweighted samples are explicit
project choices. More samples can smooth features; neither six points nor a
full-rank matrix guarantees a good curvature estimate.

### 4.2 Frame, scale and fit

1. Compute covariance of centered sample positions and its symmetric eigensystem.
   Use the smallest-eigenvalue direction for the rough normal. Require a
   numerically distinct smallest eigenspace; record all eigenvalues and the gap.
2. Orient the rough normal consistently with the existing source chart's Qu cross Qv.
   This reference fixes sign only: do not feed analytical K/H or derivative
   magnitudes into the fit. Undefined or numerically orthogonal orientation is
   unavailable, not an analytic-curvature fallback. Recheck orientation of the
   fitted normal after estimating derivatives, as specified below.
3. Use a deterministic right-handed tangent frame: project the world axis least
   aligned with the rough normal, with X/Y/Z tie order; take its cross-product
   complement. Only the normal is taken from PCA, avoiding an arbitrary tangent
   eigenvector choice at repeated tangent eigenvalues.
4. Translate by the query node and divide all local coordinates by the maximum
   sample distance h>0. Fit the full six-coefficient graph
   w=c0+c1*x+c2*y+c3*x^2+c4*x*y+c5*y^2 with uniform least squares.
   The constant is free; an overdetermined fit need not interpolate the query.
5. Solve the rectangular system with SVD, without normal equations or an external
   production dependency. Propose numerical rank threshold
   tau=max(N,6)*machine_epsilon*sigma_max; require rank6. For covariance use the
   analogous max(N,3)*epsilon*norm2(C) eigengap/zero guard. These are proposed
   numerical guards, not proven error bounds or mesh acceptance thresholds.
6. Record sigma_min/max, numerical rank, kappa2, residual and fitted-origin
   offset. Do not expand a full-rank stencil solely because analytical error is
   high, tune against the answer, or claim that a large condition number is safe.
   No accuracy-based condition cutoff is adopted by this proposal.

Standard-library-only small-matrix numerical code would need its own independent
analytic/differential checks. Using SVD conceptually does not license copying
CGAL code or importing a new production dependency.

### 4.3 Curvature outputs and units

At local x=y=0, the physical graph derivatives are
p=c1, q=c2, r=2*c3/h, s=c4/h and t=2*c5/h. Let D=1+p^2+q^2. Return

    K = (r*t-s*s)/(D*D)
    H = ((1+q*q)*r-2*p*q*s+(1+p*p)*t)/(2*D^(3/2))

K has units1/L^2 and H has units1/L. The graph formula above uses the fitted
normal n_fit=(n-p*t1-q*t2)/sqrt(D). Check its dot product with the chart reference
normal; if negative, reverse n_fit and H, leaving K unchanged. If its absolute
alignment is within max(N,3)*epsilon of zero, report undefined orientation.
Export the fitted normal/alignment, not just the rough PCA normal. A rough normal
sign check alone does not establish the final fitted orientation.
The fitted evaluation point can be displaced from the original query by
h*c0 along the rough normal; export that offset and still identify the original
source query. Do not project a mesh node, evaluate analytical curvature at the
fitted point to conceal error, or claim literal CGAL numeric equivalence.

For opt-in mixed diagnostics use this one operator at all nodes of the mixed
chart, including nodes incident only to TRI, so an interface does not arbitrarily
switch definitions. The default pure-TRI generator and stored Gd/Hd remain
untouched. Optional jet measurements on retained pure-TRI snapshots are a
separate diagnostic comparison, not replacement of that path.

This is diagonal-free for a fixed QUAD representation and sample set. Splitting
actual QUAD faces into TRI can change coface neighborhoods; general invariance
to remeshing/connectivity changes is not claimed.

### 4.4 Unavailable estimates and publication boundary

Return a typed unavailable reason for insufficient samples, ambiguous frame,
rank deficiency, degenerate scale, duplicate/invalid samples or nonfinite data.
Keep the observed support/ring/rank diagnostics. No zero-curvature, diagonal,
legacy-TRI or analytical-value fallback is allowed for an unavailable mixed node.
The initial five-node mesh can legitimately be insufficient; it is not a passed
mixed-global-error case. Boundary fits do not use pi-minus-angle as Gaussian K.

Store results in separately owned value records, tied to snapshot/hash and local
node identity. Do not write NodeAdaptive curvature fields, change patch observers,
replace owners, mutate accepted/rejected lineage or feed adaptation yet. If
boundary or other nodes are unavailable, report coverage honestly; never drop
them and call a whole-mesh global error qualified.

## 5. Finite validation and acceptance boundary

If adopted, implement one cohesive nodal K/H candidate and execute:

| Required evidence | What it must establish |
| --- | --- |
| Small-matrix core |Independent known solutions, singular/repeated-spectrum/rank cases, residuals and orthogonality; no manufactured normal-equation oracle |
| Known-frame polynomial fixtures |Plane, paraboloid and saddle derivatives/K/H; cylinder K=0 with nonzero H to exercise the missing mean channel |
| Full-pipeline curved fixtures |Sphere/cylinder and irregular/one-sided sampling with independent analytical references; do not claim finite PCA fits exactly recover every quadric |
| Invariances |Translation/rigid rotation within declared error budget, K scaling1/h^2 and H1/h, normal reversal changes H sign only, fixed-sample QUAD cycle rotation leaves estimates unchanged |
| Actual functional objective |Per-node K/H/support/condition/residual on the existing22 archived observations, including source rejections and retry; raw coverage and analytical differences |
| Required counterexamples |Step2 node115/Step3 node15 plus coarse insufficient, duplicate, collinear, rank-deficient and near-degenerate stencils; no silent fallback |
| Preservation |Archived input bytes, default TRI values/histories, scientific policies and ownership unchanged |
| Delivery |Configured native/compiler/sanitizer checks, required exact-head baseline, reviewable research PR and exact research-merge validation before integration claims |

Set numerical fixture budgets from analytical/conditioning arguments before
seeing fitted real-mesh errors. Do not choose real-mesh quality thresholds after
the measurements. Unit tests on a known fitting frame and full PCA/neighborhood
tests establish different facts and must be reported separately.

The nodal candidate must first expose actual coverage/error. It does not promise
that all current nodes are supported, that curvature improves monotonically, or
that a resulting global error is suitable for acceptance. The legacy mean
dimensional observation and mixed-channel aggregation remain visible scientific
questions; neither is resolved by calling the new output a global error.

## 6. Decision requested and current evidence status

Recommended decision: adopt Section4 as one read-only quadratic-jet candidate
for the existing mixed charts, preserve legacy TRI and all generation/adaptation
policies, and require Section5 before any estimator adoption. Approval would
authorize this bounded implementation and measurement, not a legacy repair,
global normalization, new acceptance threshold or accepted mixed epoch.

No prototype, native test, numerical matrix qualification or new generation was
executed in this specification session. Existing PR242 exact85/17/three-profile
and hosted4/4 evidence remains pinned to its own revision/scope; it is not
relabeled as validation of the unimplemented operator. This documentation-only
proposal is checked for source/reference consistency and staged quality. Full
historical/native/CRT and R3/M7 limitations remain; mixed global error is
unavailable and accepted mixed epochs remain0.

[Evidence and source hashes](evidence/MIXED_CURVATURE_OPERATOR_CONTRACT_20261119.json).
