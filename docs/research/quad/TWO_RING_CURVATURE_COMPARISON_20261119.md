# Complete two-ring curvature comparison on fixed real meshes

Updated 2026-11-19 Fortaleza (execution also dated 2026-11-20 UTC). Research source `c93a383e2775d33eb8a7e5f28cbc410e3d98593d`, tree `55da4bafc86edc06a5e5999c234574df63d1a460`, draft [PR243](https://github.com/tiagosombrra/apmesh-modernization/pull/243). The researcher explicitly adopted this comparison after reviewing the [original candidate and its accuracy limits](MIXED_QUADRATIC_JET_CANDIDATE_20261119.md).

## Result and scientific disposition

Uniform complete two-ring support is not a general improvement on these retained meshes. It fixes the earlier synthetic six-point boundary ambiguity and improves some real sites, but it increases error at most nodes in the current final mixed snapshot. Recommendation: retain this as comparative evidence; do not replace the original bounded policy or activate a global error/adaptation rule on the strength of this experiment. This is a measured negative result for uniform replacement, not rejection of a generated mesh by a new acceptance criterion.

Both candidates remain scientifically unqualified for global/adaptive adoption. The original bounded candidate is preserved, including its inaccurate boundary counterexample. No new support selection, degree, weighting, condition cutoff, normalization, curve refinement or mesh acceptance rule is chosen here. The earlier code is still a draft candidate; this session does not integrate PR243.

## What was compared

The original policy tries the complete coface one-ring, including opposite QUAD corners, and expands once only for insufficient samples, ambiguous PCA or deficient rank. The explicitly selected variant always uses the complete two-ring, even when the one-ring is already full rank. Both retain the same six-term degree-two fit, uniform weights, query location, PCA/frame/SVD/rank/orientation rules and unavailable outcomes. The reference chart normal supplies sign only; analytical K/H never enter the fit.

The same three article/rejected-source/stable-retry archives provide 22 paired TRI/mixed observations, or 44 evaluations per compiler profile. Every paired query has identical snapshot lineage, source hash, analytical reference and node identity. Actual mesh nodes, topology and OBJ bytes are unchanged. No original TRI curvature field, generation/adaptation/acceptance/stopping policy, owner or observer is modified. An extra option exists only on the research probe/report tool, not on the application generator.

All initial five-node snapshots remain unavailable in both policies: five positions cannot determine six quadratic coefficients. All later nodes of these particular archives are available in both. The report nevertheless retains all four coverage transitions and tests that a hypothetical loss cannot be silently dropped. Availability is not accuracy.

## Current article results

Values below are median absolute differences from analytical curvature at the same nodes. K has units 1/L^2 and H has units 1/L; these are not percentages or a combined/global error. TRI rows apply this diagnostic to TRI geometry and do not replace legacy ErrorGlobal. Comparisons within each row are paired; changing node sets across steps does not establish convergence.

| Step | Snapshot | Nodes | K original | K complete two-ring | H original | H complete two-ring |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | TRI | 17 | 0.00783183 | 0.00767852 | 0.0289105 | 0.0697957 |
| 1 | QUAD/TRI | 33 | 0.00430805 | 0.00669348 | 0.0255958 | 0.0471755 |
| 2 | TRI | 78 | 0.00383374 | 0.00844596 | 0.0177210 | 0.0411175 |
| 2 | QUAD/TRI | 281 | 0.00136256 | 0.00388633 | 0.00477536 | 0.0182124 |
| 3 | TRI | 223 | 0.00116372 | 0.00276983 | 0.00614871 | 0.0131274 |
| 3 | QUAD/TRI | 689 | 0.000463183 | 0.00155674 | 0.00160540 | 0.00529776 |

Final mixed snapshot, with 14 boundary and 675 interior sites:

| Region/channel | Original median | Two-ring median | Improved / worsened / numerical tie |
| --- | --- | --- | --- |
| Boundary K | 1.3092602 | 1.4975638 | 4 / 10 / 0 |
| Boundary H | 1.6863838 | 0.9966856 | 5 / 9 / 0 |
| Interior K | 0.000432107 | 0.00145775 | 63 / 610 / 2 |
| Interior H | 0.00142232 | 0.00491119 | 75 / 598 / 2 |

Across all 689 sites, K improves at 67, worsens at 620 and ties at 2; H improves at 80, worsens at 607 and ties at 2. Boundary H's lower median therefore does not mean most boundary queries improve: the ordering/distribution changes. Boundary maxima also worsen, K from 6.2414053 to 7.1103883 and H from 6.2092708 to 6.4875759. Improvements elsewhere are retained: for example Step1 mixed interior maximum K falls from 9.5377886 to 0.2542516, despite its worse median and worse H maximum.

For numerical ties only, the report uses the existing independent 1e-7 absolute/relative agreement budget declared before measurement. This is a reporting convention, never a scientific accuracy or acceptance threshold. Full per-node errors, coverage, support and source identities remain in the exports.

## Why additional samples need not improve the result

In the final mixed snapshot the median support grows from 9 to 25 sites, and its median physical radius from 0.0946607 to 0.1900254. At the boundary, median support grows from 9 to 30, radius from 0.6367420 to 1.1368304. Boundary condition improves (median 273.88 to 129.67; maximum 6798.34 to 362.43) while Gaussian accuracy worsens. Better numerical conditioning alone does not establish a better local surface approximation.

The complete pipeline now retains two independent analytic controls. The six one-sided paraboloid samples also lie on a cylinder; the additional symmetric nine-site support distinguishes them and recovers the paraboloid in that fixture. Conversely, for z=x^4 at the center of a regular five-by-five chart, true K=H=0: the original nine-site fit gives H=0.01, whereas the 25-site fit gives H=31/700, approximately 0.0442857. More distant samples increase the local quadratic approximation bias in that control. No node is smoothed or moved by either diagnostic.

The real radius growth and deterioration are consistent with this locality tradeoff; the experiment does not isolate every contribution of the changed PCA frame and polynomial fit, or prove a unique cause for every boundary error. It does show that simply increasing the ring count is insufficient. No automatic mixed per-node choice based on analytical error is introduced.

## Reference repair, validation and preservation

The first Python run stopped with an independent covariance-eigenvalue disagreement in the new quartic control. At nodes 7/12/17 the matrix is exactly diagonal with repeated tangent values 0.33333316666674995 and normal value 1.1111105555558335e-7. The previous acos cubic reference artificially splits the repeated pair by about 9.5591e-10, exceeding the unchanged 1e-10 eigenvalue budget; native Jacobi returns the exact diagonal spectrum.

The engineering repair replaces that reference with a scaled single-Givens tridiagonal reduction and indexed Sturm bisection, independent of native Jacobi. Repeated/zero/dense-known spectra and the observed diagonal case now have analytic controls. Householder QR, all numerical budgets and the native estimator are unchanged. The failed command/stdout/stderr/result and diagnosis are preserved and hashed, rather than counted as a pass.

Exact source c93a383 passes local 85/85 root CTests including 527 tooling tests, MSVC 22/22 standalone CTests, and per MSVC/GCC13.3/Clang18.1 ASan/UBSan/leak profile: 203 native checks, 9 Python tests, 22 paired stages/44 evaluations and 60 altered-record refusals. LLVM22.1.8 analysis covers both changed consumers and their research header using actual existing compiler metadata, with no suppressions or --fix. CMake and its retained architecture identity are unchanged and the freshness check passes. [Hosted run44658134604](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/44658134604) completes4/4 SUCCESS on exact c93a383: native22 each Linux/Windows, actual both-policy archive evaluations on both plus sanitized Linux,85/527 and frozen Eistute5/Book4 exact OBJ/acceptance/boundary parity. The [evidence](evidence/TWO_RING_CURVATURE_COMPARISON_20261119.json) retains exact identities, commands, failures and final readback.

All 22 original-policy per-node records per profile and all nine original CSV exports remain byte-identical to the previous qualified candidate. Across both policies and all profiles, maximum K/H differences are approximately 5.69e-14/4.41e-11, within the existing numerical agreement budget. Archived input files remain byte-identical. No new mesh or Blender scene was generated.

Closure audit covers isolated value-owned code, fixed-support/typed-unavailable contracts, analytic/native/reference/coverage/forgery controls, exact baseline, documentation and retained failures. It qualifies the bounded diagnostic comparison, not physical estimator accuracy or whole-process memory/CRT/transaction behavior. PR243 remains draft and no research merge/post-merge validation is claimed. Main and concurrent PR work are separate.

Reproduction after building the probe, using an existing archive and a new output directory:

```text
python tools/quad_two_ring_comparison.py --archive <existing.steps> --probe <quad_quadratic_jet_probe> --output <new-output-directory>
```

Outputs include original `jet.json`/`nodes.csv`, `complete-two-ring/jet.json`/`nodes.csv`, and paired `comparison.json`/`comparison.csv`. The existing three-history checker now exercises both policies; CI uses actual generated article/rejected/retry archives on Linux, Windows and sanitized Linux.

## Next action and remaining limits

Present this negative/mixed comparison for scientific disposition. Recommendation: preserve the bounded diagnostic and keep complete-two-ring opt-in for comparison; do not promote uniform replacement. Before selecting another estimator experiment or defining global aggregation, explicitly settle boundary locality and initial five-node coverage in a concrete scientific contract. No next formula, weight, cutoff or new sweep is authorized by this result.

Mixed global curvature error remains unavailable and accepted mixed adaptive epochs remain 0. The legacy mean scaling question is not repaired. Full historical 1993 numeric identity, M1/M5/R3/M7, curved-metric/general-geometry/native-CRT/allocation/transaction/exact-front-tie qualifications and prior enum/DrvFS/Doxygen failures remain open. Previous failed expectation and inventory reports keep their original source-bound scope. The canonical documentation checkpoint does not qualify its own SHA natively.
