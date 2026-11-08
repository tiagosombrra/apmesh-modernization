# M0 — Baseline qualification evidence

**Research branch:** `quad-templates`  
**Frozen entry commit:** `f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94`  
**Evidence record opened:** 2026-11-08  
**State:** **OPEN — no locally executed native/quality results recorded for M0**.

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
