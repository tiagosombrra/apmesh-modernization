# M0 — Baseline qualification evidence

**Research branch:** `quad-templates`  
**Frozen entry commit:** `f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94`  
**Evidence record opened:** 2026-11-08  
**State:** **OPEN / PARTIAL — Linux build, full 75 CTest / 527 Python and strict articles qualified on the research delivery head/merge; MSVC captures retained. Applicable memory evidence and semantic caller inventory remain pending**. Later dated entries supersede earlier tables without erasing them.

## Read-only observations recorded in this session

| Observation | Source | Actual result | Classification |
| --- | --- | --- | --- |
| Research branch | GitHub branch search, 2026-11-08 | `quad-templates` exists; old `research/quad-templates-bento1993` is absent | VERIFIED remote metadata |
| Current static source audit | [BASELINE_AUDIT.md](BASELINE_AUDIT.md) | Quadtree template classes and downstream triangle-only assumptions documented | VERIFIED source inspection; NOT runtime proof |
| Reported regression budget | `docs/QUALITY_AUTOMATION.md` and `docs/PROJECT_STATE.md` on inherited main | 75 CTest and 526 Python reported in modernization evidence | INHERITED report only |
| Pull-request-triggered workflow query | GitHub workflow-runs endpoint for `f6050ec1...` | Empty result | NO OBSERVABLE PR WORKFLOW; not a passing gate |
| Commit status query | GitHub commit statuses for `f6050ec1...` | Empty result | NO OBSERVABLE STATUS; not a passing gate |
| Repository local build recipes | `README.md` build section | Documented `cmake --preset local-serial`, `cmake --build --preset local-serial --parallel 2`, `ctest --preset local-serial` | VERIFIED documentation only |

## Execution matrix to complete M0

| Gate | Target | Result | Evidence required |
| --- | --- | --- | --- |
| M0-G0 | Exact research-branch SHA, clean worktree, compiler/CMake/Python versions | **NOT RUN** | Full SHA, `git status --short`, versions |
| M0-G1 | GCC C++17 configure/build (serial) | **NOT RUN** | Exit code, command, generated binaries and diagnostic log |
| M0-G2 | Checked MSVC C++17 configure/build (serial) | **NOT RUN** | Exit code, flags, binary/profile ID, log |
| M0-G3 | Native full CTest suite | **NOT RUN** | Complete list, passed/failed/skipped, durations, no suppressed failures |
| M0-G4 | Python qualification/contract suite | **NOT RUN** | Actual executable script commands, pass/fail and compared output count |
| M0-G5 | Frozen Eistute and Book scientific controls | **NOT RUN** | Input hashes, accepted/rejected traces, area/quality/boundary oracle comparisons |
| M0-G6 | Applicable ASan/LSan, checked MSVC/CRT/denial controls | **NOT RUN** | Profile and actual native observations, exclusions explicitly declared |
| M0-G7 | Independent source/caller/cast and test coverage inventory | **PARTIAL** | Review [BASELINE_AUDIT.md](BASELINE_AUDIT.md), enumerate all reachable paths |

## Local starter recipe

Run in a **dedicated worktree** (do not overwrite modernization work). The commands below are from the repository README and are **proposed**, not reported as executed:

```sh
git fetch origin
git worktree add ../apmesh-quad quad-templates
cd ../apmesh-quad
git rev-parse HEAD
git status --short
cmake --version
python --version
cmake --preset local-serial
cmake --build --preset local-serial --parallel 2
ctest --preset local-serial --output-on-failure
python tools/quality.py doctor
```

Only use a compatible shell/toolchain; read `README.md`, `CMakePresets.json`, `docs/QUALITY_AUTOMATION.md`, `docs/evidence/BOOK_CMAKE_RUN_RECIPES.md` and the Eistute scientific reference **before** choosing full experiment commands. Run the MSVC variant separately according to its qualified recipe. A `doctor` preflight does **not** replace the required Python test inventory. Do not claim M0 complete until actual native and scientific gates have been measured.

## Required update after the next run

Record: UTC/local date; source SHA; model/config/input hash; OS and compiler; exact command; exit/status; number of discovered and executed tests; unexpected diffs; accepted/rejected candidates; boundary comparisons; artifacts; and open limitations. If a platform is unavailable, record **BLOCKED** and leave M0 open. Update `STATE.md` and append `SESSION_LOG.md` in the same checkpoint commit.

## Session 2026-11-08-02 — M0 execution attempt and reproducible harness

**Classification:** real environment preflight and read-only source audit; **not** a successful native build, CTest or scientific experiment.

### Attempted operations

- Verified GitHub refs: `main=f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94`; initial research-head readback `quad-templates=f9e1f868e58f00d4492f7b6480db14d01274bac0` (the research branch subsequently advanced with the artifacts in this record). There were zero open PRs in the initial query.
- Inspected the task environment: Linux x86_64, Git 2.47.3, GCC 14.2.0, CMake/CTest 3.31.6, Ninja 1.12.1, Python 3.13.5; no `clang-format`, `clang-tidy` or `doxygen` on PATH in this environment.
- Attempted `env GIT_TERMINAL_PROMPT=0 git ls-remote https://github.com/tiagosombrra/apmesh-modernization.git refs/heads/quad-templates` with a 12-second external guard. Actual result: exit code 128, `Could not resolve host: github.com`. **This task environment cannot obtain the private repository checkout through Git.**
- GitHub connector read-only access is functioning, but a source-file API response is not an executable checkout. No baseline compiler could be run against the exact source.
- A locally prepared version of the M0 Python runner passed `python3 -m py_compile` and its `--help` command. Its negative smoke invocation from a non-repository folder returned **exit 2**, `blocked_preflight`, with a JSON report and no executed stages. These local checks cover the prepared script's behavior, **not the complete GitHub production source or exact GitHub-script byte identity**.
- Added [`tools/quad_m0_baseline.py`](../../../../tools/quad_m0_baseline.py) to the research branch. The exact uploaded script must be syntax/preflight checked in the real checkout before it is used for qualification.
- Added a pinned [targeted TRI dependency scan](M0_TRI_DEPENDENCY_SCAN.md) based on direct GitHub file reads; 15 selected existing files, **37 lexical TRI casts** across the four matching files (10 Adapter, 25 GeneratorAdaptive, one curvature adjacency, one OBJ writer). This does **not** establish exhaustive caller coverage.

### Current gate disposition

| Gate | Result after session | Reason |
| --- | --- | --- |
| M0-G0 — checkout/toolchain | **BLOCKED** | Toolchain partly inventoried, but private repository cannot be checked out here; exact-source worktree qualification absent |
| M0-G1 — GCC build | **NOT RUN** | No checkout |
| M0-G2 — checked MSVC build | **NOT RUN** | MSVC is unavailable in this Linux environment; requires a qualified Windows host |
| M0-G3 — full CTest | **NOT RUN** | No configured build |
| M0-G4 — Python controls | **NOT RUN** | No configured source checkout and test environment |
| M0-G5 — Eistute/Book science | **NOT RUN** | No application binary; independent oracles not compared |
| M0-G6 — memory tools | **NOT RUN** | No instrumented native binary |
| M0-G7 — TRI consumer inventory | **PARTIAL** | Pinned Git-tree census and targeted source scan; no whole-repository semantic caller analysis |

### Run next on a machine with authorized GitHub checkout

From a **clean `quad-templates` worktree**:

```sh
python tools/quad_m0_baseline.py --mode gcc --science
```

On a qualified Windows development environment with Visual Studio 2022:

```powershell
python tools/quad_m0_baseline.py --mode msvc --science
```

The runner uses the existing CMake presets, executes the GCC CTest suite, invokes the existing `tools/run_generation_case.py` for Eistute and Book at the **existing 300-second limit per model**, and collects `report.json` and logs beneath `build/quad-m0/`. It requires a clean `quad-templates` descendant of the frozen entry SHA; it stops on unexpected errors and preserves partial evidence.

**Limitations of the runner:** it does **not** prove the historically reported 526 Python outcomes, does not implement independent scientific/accepted-rejected/boundary oracle comparisons, does not run full standalone ASan/MSVC memory-probe campaigns, and does not qualify parallel/MPI behavior. Even if every runner subprocess exits zero, M0 remains **OPEN** until those independent gates are reviewed against the actual source and binary.

Never mark M0 passed merely because this script was committed or its negative preflight was observed.

## Session 2026-11-08-03 - local capture audit and continuation readiness

**Scope:** engineering-only source/environment review and offline validation of pre-existing captures. No new native build, generation, retry, scientific change or main integration.

Verified research entry `e8c55184f112d9ffb4fa004a9c9d88f5cf17ff49`, remote main `f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94`, clean isolated worktrees, no open PRs, no returned commit statuses or PR-triggered workflow runs. No production/build/config/input/test delta exists against the frozen entry. The earlier session's DNS/checkout blocker does not apply to this Windows worktree.

### Preserved execution discovered during review

Existing `build/quad-m0/20261108T141009Z-msvc/report.json` records clean source `e8c55184`, MSVC 19.44.35229, C++17 Debug (`/std:c++17 /RTC1 /MDd`), configure 6.292 s and build 106.629 s. Eistute completed in 81.719 s and Book in 44.418 s, both exit 0 within unchanged 300-second limits. Executable SHA-256: `145f800150150a2cf5be09555b8418ac59b8253e8799e961a53bcbabca0f415b`.

The runner stopped at `blocked_quality_doctor`: Ninja, clang-format and clang-tidy were absent from PATH. These tools exist at `C:\msys64\ucrt64\bin`; this is a discovery/profile issue. Failed reports/logs remain unchanged. No application run was repeated.

### Checks actually performed in this review

| Check | Actual outcome | Limit |
| --- | --- | --- |
| Exact-checkout runner AST parse and `--help` | PASS | Syntax/interface only |
| Eight captured runner logs and current binary | All SHA-256 identities match | Original capture, not a new build |
| Eistute against frozen same-ABI reference | 5 states, 25 exact artifacts, 15 positive boundaries; accepted 0/1, rejected 2/3/4 | MSVC serial |
| Book against frozen same-ABI reference | 4 states, 20 exact artifacts, 108 positive boundaries; accepted 0/1, rejected 2/3 | MSVC serial |
| Physical and parametric quality | Full-precision snapshot coverage in both cases | Existing definitions/tolerances |
| `python tools/validation_session.py environment` | FAIL: required tools unavailable in current local profile | No profile workaround applied |
| `python tools/validation_session.py plan --scope iteration` | FAIL: missing worktree-local validation baseline | No native validation started |
| WSL inventory | Ubuntu 24.04, GCC 13.3, CMake 3.28.3, Ninja present | Availability only |

Offline command: `python build/quad-m0/review-20261108-03/audit.py`, exit 0. It imports unchanged `verify_generation.verify_run` with required positive boundaries and `compare_runs`, applies the existing exact artifact checks/counts from the qualified node-copy science recipe and verifies reference/capture manifests remain unchanged. Runtime-summary timing is excluded and the compatibility `model` path field normalized exactly as in that recipe. Scientific tolerances remain unchanged.

The [compact receipt](evidence/M0_MSVC_REVIEW_20261108.json) records commands, hashes, reference locations and counts. Full local audit code/report remain under `build/quad-m0/review-20261108-03/`; original native logs stay in the capture directory.

### Current gate disposition

M0-G0 has verified source/worktree/remote and MSVC metadata, but the local validation profile/baseline is incomplete. M0-G2 build is measured in the preserved capture. M0-G5 is qualified only for these two MSVC serial cases (9 states / 45 exact artifacts / 123 positive boundaries); GCC remains pending. M0-G1/G3/G4/G6 are not newly executed; M0-G7 remains partial. Debug compiler checks do not substitute for independent lifetime/CRT/denial observations. The inherited 75 CTest / 526 Python inventory has not been executed on this research branch.

Next: prepare worktree-local validation prerequisites, execute the clean WSL GCC baseline in [STATE.md](STATE.md), and inspect actual counts and independent oracle/memory gates before M1. Preserve previous blocked attempts and stop at the first unexpected failure.

Checkpoint documentation checks: whitespace passes on all five changed files. `validation_session.py check-links` fails on the inherited `../../../../tools/quad_m0_baseline.py` link in the older evidence entry; the old append-only journal contains the same path. Preserve this failure and history. The correct current link is [the M0 runner](../../../tools/quad_m0_baseline.py). No stage/link-gate closure is claimed by this documentation checkpoint.

## Session 2026-11-08-04 - native baseline and bounded portability delivery

**Classification:** engineering-only validation infrastructure. [PR #184](https://github.com/tiagosombrra/apmesh-modernization/pull/184) targets `quad-templates`, head `d11b83c33c6fc68892ea72d42c0cd5a1ba5aa205`, merge `a29711bea1e38f6a1ea49dde443f0ae58ebadfa7`. The two trees are identical. Main stays at `f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94`. No QUAD generator, production source, input, compiler preset, formula or scientific policy changed.

The [compact qualification receipt](evidence/M0_GNU_QUALIFICATION_20261108.json) records hashes, actual scopes and the preserved failures. Local raw records and 168 byte-verified copied artifacts are under `build/quad-m0/session-20261108-04/`; the native clone is `/home/apmesh/quad-m0-20261108-04` in Ubuntu 24.04 WSL.

### Preparation and observed blockers

The Windows-created worktree's drive-letter gitdir pointer is unusable by native Linux Git. A new native clone used locally available objects at the verified published entry `d400f37`; remote heads were independently checked through authenticated Windows Git. Original worktrees were preserved. The worktree-local validation baseline protects 75 CTest / 391 historical Python IDs; the current set separately preserves all 526 entry IDs and adds exactly one regression.

| Preserved observation | Actual result | Explicit correction |
| --- | --- | --- |
| Original Linux full build | Fails linking Windows `_Znwy` / `_ZdlPvy` symbols | Compiler type checks choose actual size_t mangling for new/sized delete |
| First candidate CTest | 42 pass; tooling suite fails generated fingerprint | Regenerate only the changed CMake input hash |
| Next candidate CTest | 42 pass; inventory differs by host Path ordering | Explicit case-folded POSIX order with a deterministic spelling tie-break; one new regression |
| Next candidate CTest | 52 pass; snapshot copy-denial context fails | Independent control proves shared libstdc++ allocation bypass; link C++ runtime locally only for the GNU Linux test probe |
| Next candidate CTest | 57 pass; clang-tidy 18 rejects ExcludeHeaderFilterRegex | Install official LLVM 22.1.8 tools and update local discovery profile; retain configuration and diagnostics |
| Successful head CTest plus local summary | All 75 pass; local controller cannot find Python summary in truncated JUnit output | Offline verification reads the full preserved LastTest.log: 527 executed, no failure/skip; original failed controller report retained |

Each failed invocation stopped expansion and retained a separate directory. Subsequent invocations followed an identified source, generated-metadata or tool dependency correction. No case, oracle, tolerance, budget or timeout was weakened. The complete successful head observation was not repeated merely for the summary parser. The required post-merge regression is a separate exact-revision observation.

### Actual qualified outcomes

- GCC 13.3 / C++17 / serial / Release: complete build, **75 CTest and 527 Python controls** on delivery head and exact research merge, with zero failures or skips. LLVM format/tidy 22.1.8 matches the existing configuration; GNU remains the production compiler. Native default `__cplusplus` is 201703L.
- Windows GCC 16.1: six affected native entries pass at `851049c`; 527 Python controls pass at `3078ab0`. The later test-runtime condition is Linux-only and the standalone control adds no production target. Relevant Windows code/effective flags are preserved; full Windows CTest is not claimed as a new observation.
- New ordering control detects the original implementation under Linux with exactly one expected assertion failure and no errors. The repaired control passes on Windows/Linux. Original 526 test identities remain a subset of the final 527.
- Independent [allocation calibration source](../../../tests/allocation_wrap_control.cpp): dynamic-runtime copy of 257 characters exits 1 with `caught=0 denied=0`; static C++ runtime exits 0 with `caught=1 denied=1`. Actual commands, binaries and source hashes are retained. This is instrument calibration, not an application memory-safety claim.
- Fresh Eistute and Book execute once each at the unchanged 300-second cap. Unchanged verification and strict comparison against qualified Linux Clang references pass **9 states, 45 exact scientific artifacts and 123 positive boundary comparisons**, including full-precision physical/UV quality and original accepted/rejected decisions. Timing and the existing relocated compatibility model-path field retain their documented treatment; no numerical tolerance or raw line ending is normalized.
- The exact executable and source tree survive research integration; post-merge regression passes and scientific capture reuse is bound to that identity. Windows and Linux checkout receipts preserve all 2,368 tracked file times. The preserved MSVC captures are not regenerated.

Commands: existing `cmake --preset local-serial`, build with `--parallel 2`, `ctest --preset local-serial --output-on-failure --stop-on-failure --no-tests=error --output-junit ...`, and unchanged `tools/run_generation_case.py --timeout 300`. CTest's stop switch is explicit because the original M0 runner does not include it. Local orchestration scripts and per-command caps/hashes remain with the raw reports. GitHub reports zero statuses/check-runs; no green CI inference is made.

### Bounded delivery audit and remaining M0 scope

| Audit area | Disposition |
| --- | --- |
| Code | Six reviewable development/test files; unchanged production, input, preset and scientific trees |
| Tests | Exact head/merge 75/527; bounded Windows controls; actual ordering and allocation-hook negative evidence |
| Contracts | Original native ownership/denial/release and scientific ordering/selection/stopping oracles retained; no skipped entry |
| Documentation | Generated build hash updated; source-backed compact receipt and research checkpoint; prior failure entries retained |
| Scientific scope | Existing TRI behavior preserved by strict independent outputs; no QUAD algorithm, all-quad decision or novelty claim |
| Known inventory | LLVM 18 incompatibility, dynamic-hook gap, failed prefixes, summary-controller failure and broader memory/caller gaps remain explicit |

M0-G0/G1/G3/G4 now have measured Linux outcomes; G2 retains the verified MSVC source/profile capture. G5 has bounded MSVC and Linux article outcomes. **G6 remains pending** for a source/build/input/ABI/instrument-bound disposition of applicable baseline memory evidence; ordinary release/hook controls do not close whole-process ASan/LSan/CRT. **G7 remains partial** despite expanded lexical coverage. Inherited broken historical runner links remain a documentation finding. M0, M1 admission and broader Stage 3 remain open.

Next: resolve G6/G7 using these exact artifacts and finite relevant evidence; do not repeat completed builds/articles or create an unrelated instrument campaign. Then assess M1 admission and independent historical topology fixtures.
