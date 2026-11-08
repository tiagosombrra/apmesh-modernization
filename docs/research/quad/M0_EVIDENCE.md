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
