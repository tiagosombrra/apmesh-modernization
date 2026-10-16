# Repository working agreement

Read `docs/PROJECT_STATE.md` and `docs/MODERNIZATION_PLAN.md` before work.
Use the remote repository as the continuity source. Keep one active work item.
Audit remote main, branches, open PRs and checks before each delivery. Never
overwrite concurrent changes. Preserve the historical source repository.

All new first-party code, symbols, comments, diagnostics and documentation use
English. Preserve attribution and licenses. Legacy identifiers are migrated in
reviewable batches, not hidden behind a blanket translation claim.

Preserve formulas, ordering, boundary synchronization, quadtree/templates,
advancing-front reconstruction and adaptation/acceptance/stopping policies.
Classify changes as engineering-only, behavior-changing defect repairs, or
scientific proposals. Scientific changes require explicit advisor alignment.
Do not import alternative generators from apmesh-core as a refactor.

Use RAII and explicit owners/observers. Avoid shared_ptr as a substitute for an
ownership design. Consolidate duplicate concepts only after checking semantics,
units and conventions; parametric and physical meshes have distinct roles.
Target C++23 after compiler qualification; preserve C++17 reference comparison.
Production serial code will use only the standard library. Eigen removal needs
independent analytic and differential tests before deleting the dependency.

Run local quality tooling documented in `docs/QUALITY_AUTOMATION.md`. Formatting
and whitespace fixes are explicit operations. Never run clang-tidy --fix over
the repository. Do not suppress diagnostics merely to make a gate green.
Never use -ffast-math or change floating-point order without numerical evidence.

No paid Actions or automatic hosted workflows. Use local checks and retain
small evidence reports. Do not describe zero tests, zero compared boundaries,
rejected candidates or unavailable tools as successful validation.
Open reviewable PRs; merge only after required local gates pass on the exact
head revision and remote checks, if configured, are green. Recheck after merge.
Update plan/state and evidence with results, failures and remaining limitations.

At the end of every stage, perform an explicit closure audit of the code, tests,
contracts, documentation, scientific scope and known failure/coverage inventory.
Run the required regression on the exact delivery revision, including negative
controls and accepted/rejected traces. Record commands, hashes, results and
unresolved findings. A failing or unmeasured required gate blocks stage closure
and integration. After merge, repeat validation on main before the next stage.
