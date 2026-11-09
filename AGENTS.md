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

GitHub Actions on standard GitHub-hosted runners are allowed for this public
repository when explicitly scoped to QUAD research candidate branches. Use
read-only repository permissions, bounded run time and artifact retention, no
secrets or deployments, no paid/larger runners and no automatic merges.
Hosted CI provides executable compiler/test evidence on the exact commit; it
does not replace the full historical scientific oracles, native sanitizer
qualification, Windows-specific memory checks or independent approval.
Continue to support local checks and retain small evidence reports. Do not describe zero tests, zero compared boundaries,
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

## QUAD research branch: mandatory conversation checkpoint

When working on `quad-templates` or on QUAD scientific work, **first read**
`docs/research/quad/CONTINUATION_PROTOCOL.md`,
`docs/research/quad/STATE.md`,
`docs/research/quad/IMPLEMENTATION_ROADMAP.md`, and the latest
`docs/research/quad/SESSION_LOG.md` entry. Verify remote SHA and any concurrent
changes before edits. The QUAD research state is separate from the modernization
`docs/PROJECT_STATE.md`; do not rewrite modernization history to report QUAD work.

At the end of **each meaningful QUAD research conversation/session**, update
`STATE.md` with the exact next action and evidence status; append a dated entry to
`SESSION_LOG.md`; update the relevant evidence and roadmap only if results or
approved scope changed; and commit the checkpoint to the `quad-templates` branch.
Verify remote readback before claiming it was saved. State explicitly when GitHub
write access or native tests were unavailable. Never claim unexecuted tests,
missing CI status or missing oracle comparisons as successful checks.

This is a **required handoff procedure**, not automatic background execution.
Preserve the default TRI scientific behavior, keep QUAD implementation opt-in,
and direct scientific changes through their own research milestones and PRs.
