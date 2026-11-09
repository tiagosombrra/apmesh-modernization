# QUAD remote CI bootstrap — 2026-11-09

## Purpose and authorization

The repository owner explicitly authorized remote native compilation and narrowly scoped GitHub Actions in ChatGPT. The historical blanket prohibition in `AGENTS.md` was a repository convention, not a GitHub platform limitation. Standard GitHub-hosted runners for the current **public** repository are free; do not select paid/larger runners or silently incur costs if repo visibility or billing settings change. Reference: https://docs.github.com/en/actions/concepts/billing-and-usage .

## Implemented

- Candidate branch: `quad/integration-pr185-20261109` (separate from scientific base and main).
- Workflow: [quad-research-validation.yml](https://github.com/tiagosombrra/apmesh-modernization/blob/quad/integration-pr185-20261109/.github/workflows/quad-research-validation.yml), introduced in commit `098b8aeb12858567a9602a8d523bf844996a0461`.
- Scope: push on `quad/integration-*`, manual-dispatch declaration (the latter requires availability on the default branch to be usable via GitHub UI). Read-only `contents`, no secrets, deployment or automatic merge; bounded timeouts and seven-day failure-log artifacts.
- Exact candidate source and prior two-parent merge commit `c57749e8691907bc25575114191f20782ba16248` are preserved. Workflow adds only CI configuration, and subsequent candidate `73184eb3eb25b2f73452737753cb707c092f18f0` also changes root `AGENTS.md` and `README.md` to permit scoped public-runner CI.
- The equivalent root policy was independently published to `quad-templates` at `2709dd1135b2e751d17b402afcbb6ef4314c9891`. This does not merge the QUAD implementation.
- Linux GCC C++17 and Windows 2022 MSVC C++17 each build and execute the standalone real-quadtree QUAD native CTest entries. An independent Ubuntu job compiles the full serial TRI application, runs its CTest baseline, and discovers tooling Python tests. Native raw scientific Eistute/Book production comparisons and the complete exact-head 75/527 admission adapter are **not** automatically satisfied solely by this CI.

## Actual observed executions (not future claims)

1. [Run #42629394523](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42629394523), SHA `098b8aeb12858567a9602a8d523bf844996a0461`: Linux QUAD and Windows QUAD jobs completed **success**; TRI baseline still **in progress** at last observation. Do not label the whole run passing yet.
2. [Run #42629587785](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42629587785), final policy SHA `73184eb3eb25b2f73452737753cb707c092f18f0`: **pending** at last observation. This is the more recent candidate and requires separate exact-head confirmation.

These are connected-GitHub live job-status observations, not invented local compiles. No hosted CI evidence by itself proves new physical QUAD, full curved/XYZ, closed boundary, multipatch or adaptation, and no M1/M2/M3 gate is closed here.

## Next verifiable actions

1. Inspect final run #42629587785 job-level results, failure logs and exact SHA; if any job fails, preserve diagnosis and fix the workflow/test environment (not scientific references) or code with a reviewable commit.
2. Independently qualify the mandatory delivery gates and applicable Eistute/Book scientific oracles. Preserve original tolerances, counts, accepted/rejected traces, compiler provenance and evidence SHA.
3. Keep PR #185 and isolated integration branch unmerged until requirements pass; do not mutate modernization `main`. Once complete, publish the accepted evidence and a fresh checkpoint on `quad-templates`.
## Diagnosed CI failure and repair — session 13

[Initial run #42629394523](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42629394523) finished **failure**: QUAD Linux+MSVC native jobs each passed both CTest entries and produced the 19-leaf/42-quad/53-vertex/area 0.25 demo; TRI baseline compiled but CTest passed **67/75**, with eight failures. Seven failing entries could not read old Git commits from shallow checkout, one clang-tidy header-scope entry rejected `ExcludeHeaderFilterRegex` with the runner's older compiler tooling. Native code and reference values were not changed. Failure logs and GitHub artifact are retained.

Environment-only fix: `actions/checkout@v4` now uses `fetch-depth: 0` and Linux baseline installs `clang-tidy==22.1.8` and `clang-format==22.1.8` in a virtual environment. Candidate workflow commit `1f87f8c270df5da0bd662fa147db32cb76fb44de` and canonical workflow commit `aed5e517d897d0d8acd27208dab61cdfe13693e9`. New [run #42630886815](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42630886815) is pending final inspection; final SHA tests and scientific qualification are **not yet accepted**.
## Session 14 — full native regression success, Eistute/Book launched

[Corrected run #42630886815](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42630886815), head `1f87f8c270df5da0bd662fa147db32cb76fb44de`, completed **success**. Independent read of three job logs found Linux QUAD 2/2, Windows QUAD 2/2, full TRI CTest 75/75, Python 527/527, no failed native controls or skipped test entries in their actual suites. QUAD native demos match on counts (19 leaves /42 quads /53 UV vertices /area 0.25).

Added non-destructive [Eistute/Book science comparison job](https://github.com/tiagosombrra/apmesh-modernization/blob/quad/integration-pr185-20261109/.github/workflows/quad-research-validation.yml) on candidate SHA `602f04a26c28a163c179969763eef2813351634e`. It compiles the frozen main and candidate with matching toolchain and invokes unchanged generation/independent verification scripts, with expected five Eistute and four Book states, exact OBJ/acceptance fields and independent boundary coverage. [Run #42633924826](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42633924826) was **in progress** when this receipt was authored; no scientific-pass outcome inferred. Other physical/adaptive/memory gates remain distinct.
