# Domain factor-bound repair delivery - 2026-11-16

Exact feature d59a513a04ea8c9573e006789641f4adbeecedee, draft
[PR238](https://github.com/tiagosombrra/apmesh-modernization/pull/238).
User-authorized behavior-changing configured-factor defect repair, opt-in under
curved_bezier_bounded_domain_vertex_mean_v1. No scientific adoption or merge.
The existing TRI, original-curves and fixed16 paths retain the historical rule.

## Delivered behavior

The ranked-domain step2 override is projected into the configured factor interval
only when explicitly enabled by the bounded research case. Configured bounds1.5
now reach actual domain generation as1.5 at all three steps; the old case retains
1.5/1.0/1.5 as a negative control. Curved boundary points remain3/5/9, straight
sides3 each. There is no point-count trim or replacement curve generator.
Mean domain h at step2 changes0.0901984 ->0.135298; source leaves136 ->67.
New example: configs/quad/curved_patch_bounded_domain.conf.

| Mixed source step | Old coarse nodes / QUAD / TRI | Corrected nodes / QUAD / TRI | Old / corrected RMS % |
| --- | --- | --- | --- |
| 1 | 33 /16 /24 | 33 /16 /24 | 0.830346 /0.830346 |
| 2 | 615 /548 /122 | 281 /242 /66 | 0.290323 /0.420207 |
| 3 | 843 /772 /126 | 797 /724 /130 | 0.267236 /0.275132 |

Step2 has54.31% fewer nodes, but geometric RMS is44.74% higher. Its minimum
physical TRI mean-ratio improves0.0398114 ->0.135358 while the minimum QUAD
scaled corner Jacobian decreases0.520605 ->0.429872. All measured corner
Jacobians remain positive; this is not a continuous map-validity proof. Step3
still grows281 ->797 nodes and retains TRI minimum0.0398114. This is a contract
repair, not an optimal growth controller or a uniformly better mesh.

For the corrected run, TRI versus mixed same-site RMS is0.939743% /0.830346%
at step1,0.522476% /0.420207% at step2, and0.340648% /0.275132% at step3.
Mixed uses33/281/797 nodes versus TRI17/78/223: no equal-cost efficiency claim.
Metrics use identical64/128 UV midpoint grids and independent original Bernstein
XYZ with source-area weights, normalized by corner diagonal sqrt8. New mixed
measurements exactly match the existing common-grid kernel. Old metrics are
reused only on identical OBJ hashes. Both old default and old coarse cases
reproduce all eight previous OBJ files byte-for-byte. This is geometric
interpolation error, not solution error, a continuous bound or an approved mixed
curvature estimator. Histories remain TRI-driven with mixed_adaptive_epochs=0.

## Exact-revision validation and retained failures

- GNU C++17 Release, MSVC Debug and Clang Debug with ASan/UBSan/leak detection:
  five-case old/new application test passes; old in-range control is identical;
  all case reports and OBJ hashes agree across profiles. Each profile also passes
  fixed16, original/stable accepted/rejected/rollback histories and original source
  contracts with six captures, three reversed captures and54 native negatives.
  Each bounded normal/rollback run rejects nine corrupted source/topology inputs.
- Local full baseline:85/85 CTest via validation_session delivery plan based on
  e90d5a3, report1794828785596882800-532fdd13; doctor, whitespace, links, inventory,
  build and required tooling outcomes pass in their recorded scopes. This does
  not close broader CRT/allocation-denial or scientific milestones.
- Configured LLVM22 analysis with actual compiler metadata: generator, controlled
  application, runtime config, application dispatch and two source/header consumer
  probes; six translation units, no visible first-party diagnostics.
- New GNU image versus retained frozen f6050ec reference outputs: Eistute5 and
  Book4 states exactly equal for OBJ and acceptance; boundary coverage verified.
- Exact candidate hosted run43859454045 completes4/4 SUCCESS, including the
  root TRI/tooling job and frozen scientific comparison. Prior e90d5a3 checks
  are not substituted for the new head.

Commands are retained per stage in the local ignored results: cmake --build
<profile-build> --target ap_mesh quad_real_boundary_source_contracts --parallel2
(with --config Debug on MSVC); test_domain_factor_bounds_application.py,
test_controlled_application.py and test_real_boundary_application.py with
--exe <profile-image> --directory <fresh-results>; native source contracts with
an original-curves config; validation_session.py run --plan <exact-delivery-plan>;
configured clang-tidy -p <actual-build> <translation-unit>; run_generation_case.py
--model eistute/book --timeout300 followed by verify_generation.py --baseline
<frozen-output> --require-boundary-coverage. No fast-math or scientific tolerance
change. Compiler flags and command arrays remain attached to local raw results;
portable receipts retain image, artifact and source identities.

Retained failures: pre-commit header formatting rejection before the source
commit; stale generated inventory before the mechanical hash/byte refresh;
two copied harnesses rejected a misdecoded UTF-8 BOM before any native command.
These were explicitly corrected, with original files/logs retained. Direct
protected WindowsApps binary execution returned access denied; the installed
Blender application launcher created/opened the scene. No permissions changed.
Earlier Doxygen API-reference failures, broader CRT coverage and independent
approval remain unresolved; no new Doxygen or full stage closure is claimed.

## Blender and next action

Blender5.3 scene contains the analytic display reference on the left and actual
TRI/QUAD-TRI rows for all four source states0-3. Only object translations are
applied; mesh coordinates use native Blender storage precision without smoothing,
subdivision or height scaling. White analytical boundary and yellow generated
chords remain distinct from mesh nodes. The scene was opened, visually confirmed,
enlarged and its viewport saved. The dense analytic display is not a generated
mesh. Local file:build/quad-domain-bounds-d59a513/QUAD_TRI_domain_bounds_steps_analytic.blend.

Next: complete exact-head review/checks for the opt-in repair. Further growth
control must coordinate boundary fidelity with interior h changes and declare
geometry/quality/cost targets under the required scientific alignment. Do not
promote fixed1.5 or invent a cap from these states. Mixed accepted feedback and
R3/M7 remain OPEN; no integration or main/post-merge qualification was performed.

[Comparison receipt](evidence/DOMAIN_FACTOR_BOUNDS_COMPARISON_20261116.json) and
[validation receipt](evidence/DOMAIN_FACTOR_BOUNDS_VALIDATION_20261116.json).
