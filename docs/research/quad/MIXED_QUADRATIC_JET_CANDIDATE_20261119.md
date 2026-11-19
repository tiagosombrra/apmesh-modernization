# Mixed quadratic-jet candidate: implementation and accuracy limits

Updated 2026-11-19 Fortaleza. Research PR [#243](https://github.com/tiagosombrra/apmesh-modernization/pull/243), source `f2dbd4716d68b1b8cb9cf4d78143021b81e3ccda`, tree `7ef3e90a7a5897555aaa53955cae960fbc07524d`. This is a diagnostic candidate, not an adopted global-error estimator or an integrated adaptive mesher.

## Authorized scope and delivered behavior

The researcher explicitly adopted Section 4 of the [operator contract](MIXED_CURVATURE_OPERATOR_CONTRACT_20261119.md) for implementation and validation. The original specification records its pre-adoption status historically; this report records the subsequent adoption and experiment. The method family follows the primary Cazals/Pouget reference already inspected in that contract; it is a separate, approved surface-curvature experiment, not a claim about the 1993 generator's historical curvature formula.

`research/quad/quadratic_jet_curvature.h` consumes immutable physical positions and polygon cycles. Each node receives a separately owned value record containing Gaussian curvature K, signed mean curvature H, availability reason, exact support/ring, normalized scale, covariance spectrum, SVD rank/condition/residual, fitted-origin offset and fitted normal. The reference chart normal fixes sign only. Analytical curvature is used exclusively by the independent reporting comparison, never supplied to the fit.

The implementation preserves the adopted complete coface one-ring, including opposite QUAD corners, with one complete two-ring expansion only for insufficient samples, ambiguous PCA or deficient rank. It uses uniform full six-term quadratic least squares, a deterministic PCA-based frame and a standard-library rectangular one-sided Jacobi SVD without normal equations. A distinct Python oracle uses characteristic eigenvalues and column-pivoted Householder QR. Fixed QUAD cycle rotations produce identical results; invariance to splitting or remeshing is not claimed.

The probe and report tool are research-only. No application source, NodeAdaptive field, ownership transfer, original TRI curvature, curve discretization, template/front selection, smoothing, acceptance/stopping or adaptation policy changes. No nodes are moved. K has units 1/L^2 and H has units 1/L. Their absolute differences below are neither percentages nor a combined global error.

## Actual archived observations

The executable evaluates all 22 retained observations: current article history (8), original rejected-source history (8), and stable retry history (6). It retains source acceptance/rejection/retry identities and hashes. Initial five-node snapshots are explicitly unavailable at all nodes in both schemes. All subsequent nodes in these three particular archives yield finite converged full-rank values. Availability does not establish accuracy.

The following TRI column uses this new diagnostic on retained TRI geometry; it does not replace or restate legacy ErrorGlobal. Medians concern different node sets at successive steps and do not establish a convergence rate or superiority of one mesh type.

| Step | Snapshot | Nodes | Median absolute K difference | Maximum K difference | Median absolute H difference | Maximum H difference |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | TRI | 17 | 0.00783183 | 6.24246 | 0.0289105 | 6.18729 |
| 1 | QUAD/TRI | 33 | 0.00430805 | 9.53779 | 0.0255958 | 6.33587 |
| 2 | TRI | 78 | 0.00383374 | 16.9533 | 0.0177210 | 6.30527 |
| 2 | QUAD/TRI | 281 | 0.00136256 | 6.43032 | 0.00477536 | 6.60000 |
| 3 | TRI | 223 | 0.00116372 | 6.12165 | 0.00614871 | 5.53832 |
| 3 | QUAD/TRI | 689 | 0.000463183 | 6.24141 | 0.00160540 | 6.20927 |

Boundary tails remain large. In the final mixed snapshot the 14 boundary nodes have median absolute differences K=1.3092602 and H=1.6863838, with maxima K=6.2414053 and H=6.2092708. No boundary node is discarded to improve these numbers. The first mixed step's maximum K error is interior, so the problem is not confined to the boundary.

The previously identified diagonal witnesses are also retained. At Step 2 OBJ node 115, analytical K=-0.5564634621 versus jet K=-0.8156368253; analytical H=-1.6716444896 versus jet H=-1.5805790318. At Step 3 OBJ node 15, analytical K=-1.2456069096 versus jet K=-0.8978586732; analytical H=-1.7936910723 versus jet H=-1.5651633513. Both use eight-point one-rings; condition numbers are approximately 87.18 and 60.46. These values remove the diagonal choice but do not establish exact or improved curvature everywhere. Machine-readable supports use zero-based local indices; OBJ labels are one-based.

## Retained failed expectation and scientific counterexample

The first MSVC contract run failed `Symmetric paraboloid full pipeline` (exit 1). Its original command/stdout/stderr/result are retained and hashed in the evidence. The campaign stopped before further validation. Investigation showed that an exact full-pipeline expectation for every one-sided PCA stencil was unjustified by the adopted specification.

For z=(x^2+y^2)/2 sampled at x in {-0.1,0,0.1} and y in {-0.1,0}, exactly the same six points also lie on z=x^2/2-0.05*y. At the boundary query, the selected stencil has numerical rank 6 and condition approximately 2393.06, yet the fit recovers the alternative parabolic cylinder: K approximately 0, H approximately 0.49937617. The paraboloid's analytical K at the original query is approximately 0.98029605. Thus a unique numerical fit does not establish that sparse samples distinguish the intended surface.

The correction changes the test expectation, not the algorithm: exact paraboloid recovery is checked on a declared symmetric support; a separate mandatory negative control proves the shared samples and preserves the inaccurate one-sided result. It is not relabeled as scientific accuracy success. No new accuracy cutoff, condition threshold, extra expansion or analytic/diagonal fallback was inserted.

The initial exact-head regression at d1970a1 also stopped (exit 1) at architecture freshness before running baseline CTest. Adding the CMake targets required refreshing its retained build hash. Source f2dbd47 changes exactly that one inventory hash, with unchanged production file inventory, contracts and numerical source. The original failed report remains separate from the corrected execution.

## Validation, audit and reproducibility

The [bounded evidence](evidence/MIXED_QUADRATIC_JET_CANDIDATE_20261119.json) records exact commands, source/input/binary/output hashes, numerical differences, negative controls and final gate outcomes. The implementation-level gates exercise matrix rank/repeated spectra/residual/orthogonality, known-frame polynomials, sphere/cylinder, scaling/rigid motion/normal sign, complete neighborhoods, malformed/degenerate/coarse inputs and the retained one-sided counterexample. Fixture budgets were set before measuring real archive errors.

Each of MSVC Debug, GCC 13.3 and Clang 18.1 ASan/UBSan with leak detection executes 182 native checks, six Python reference/control tests, the 22 actual archive observations and 30 altered-record refusals. Native values are independently checked using QR and covariance eigen residuals; coefficients/K/H use the predeclared 1e-7 absolute/relative numerical agreement budget. Separate frame/eigen/residual checks use 1e-10. Cross-profile maxima are approximately 5.69e-14 for K and 4.41e-11 for H. Those are instrument comparisons, not accuracy tolerances for the physical estimator.

LLVM 22.1.8 scoped static analysis passes for both new translation units and their new headers using actual GNU compilation metadata, unchanged checks and no suppressions. MSVC standalone CTest has 22 entries, including the two new tests. Exact source f2dbd47 passes the full local 85/85 root regression, including 527 tooling controls. [Hosted run 44551769795](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/44551769795) completes 4/4 successful jobs: Linux/Windows native 22/22, actual jet histories on both and sanitized Linux, root 85/527, and strict frozen Eistute five-mesh/Book four-mesh OBJ, acceptance and boundary parity. Superseded run 44551318672 at d1970a1 was cancelled when the inventory correction was published; it is not a passed gate. The configured process environment supplies the LLVM tools; a direct staged checker outside that environment reported missing clang-format and did not pass. The configured staged check and normal commit hook pass.

Closure audit: numerical/header code is isolated and value-owned; native and independent controls exercise the actual probe; typed unavailable values remain explicit; contracts and source hashes bind preserved generation/TRI behavior; documentation separates measured numerical agreement from unresolved physical accuracy. Public source, branch/commit/PR metadata and staged bytes are screened. This does not substitute for independent scientific review or qualify whole-process CRT/allocation/transaction behavior.

To reproduce on an existing source archive after building the native probe:

```text
python tools/quad_quadratic_curvature.py --archive <existing.steps> --probe <quad_quadratic_jet_probe> --output <new-output-directory>
```

The output contains `jet.json` and `nodes.csv`, including unavailable rows, analytical references and all actual per-node differences. The three-history checker is `tests/quad/test_quadratic_jet_archive.py`; CI runs it on actual newly generated article/rejection/retry archives on Linux, Windows and the sanitizer path.

## Remaining decision and next action

Keep PR243 a draft diagnostic candidate. Accuracy is unqualified for global-error/adaptive adoption; the original five-node coverage limit also remains. The proposed next experiment compares the unchanged candidate with uniform complete two-ring support on the same histories, preserving degree/weights/nodes and reporting possible oversmoothing. It awaits an explicit scientific response; this report does not authorize or execute it.

Mixed global normalization/aggregation and any activation of adaptation require later scientific decisions. Mixed global error remains unavailable; accepted mixed adaptive epochs remain 0. The source-only legacy mean scaling concern is not repaired. No new meshes or Blender scene were requested or generated here. Full historical 1993 numeric identity, M1/M5/R3/M7, broader geometry/curved-metric, native CRT/allocation/transaction/exact-tie and retained enum/DrvFS/Doxygen failures remain open. Main and concurrent PRs are unchanged. No research integration or post-merge validation is claimed for this draft.
