# APMesh QUAD - canonical state and resume point

**Branch:** `quad-templates`

**Entry baseline:** `f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94` (modernization PR #183)

**Last session:** 2026-11-08-03

**Active milestone:** **M0 - PARTIAL / OPEN; full baseline qualification pending**

**Protocol:** [CONTINUATION_PROTOCOL.md](CONTINUATION_PROTOCOL.md)

**Plan:** [IMPLEMENTATION_ROADMAP.md](IMPLEMENTATION_ROADMAP.md)

**Evidence:** [M0_EVIDENCE.md](M0_EVIDENCE.md), [MSVC receipt](evidence/M0_MSVC_REVIEW_20261108.json)

**History:** [SESSION_LOG.md](SESSION_LOG.md)

## Verified current position

- An isolated Windows worktree exists at `C:\Users\tiago\Documents\dev\research\apmesh-quad`. Authenticated Git works; the previous session's DNS/missing-checkout blocker is resolved on this host.
- Session entry verified remote research head `e8c55184f112d9ffb4fa004a9c9d88f5cf17ff49`, main `f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94`, clean worktrees and no open PRs. No commit statuses or PR-triggered workflow runs were returned; this is not passing CI.
- A pre-existing capture at `build/quad-m0/20261108T141009Z-msvc/` records MSVC 19.44 C++17 Debug configure/build and completed Eistute/Book, then `blocked_quality_doctor`. This review did not rerun those native operations.
- Offline verification passes: nine states, 45 exact scientific artifacts, 123 positive boundary comparisons, preserved accepted/rejected decisions and full-precision physical/UV quality snapshots. All eight runner-log hashes and the current executable match the capture.
- No QUAD algorithm or QUAD tests exist. Production/build/input/test files are unchanged from the entry baseline. GCC/Linux and complete research-branch regression/memory qualification remain pending.

## Milestones

| Milestone | State | Remaining admission / exit |
| --- | --- | --- |
| M0 - baseline | PARTIAL / OPEN | GCC/Linux, full 75 CTest / 526 Python inventory to verify, remaining science/memory gates and complete caller inventory |
| M1 - historical T1-T6 oracle | PENDING | Verified Figure 7 topology, symmetries and negative controls |
| M2 - UV QUAD topology | PENDING | Coverage, incidence, orientation and no hanging nodes |
| M3 - quadtree emitter | PENDING | Opt-in QUAD and exact default TRI preservation |
| M4 - physical QUAD | PENDING | Defined UV-to-XYZ geometry and four-node lifetime/ownership |
| M5 - boundary transition | PENDING | Adviser decision: quad-dominant or all-quad; complete valid patch mesh |
| M6 - shared-curve multipatch | PENDING | Reversed two-patch and at least three-patch conformity |
| M7 - repeated adaptation | PENDING | QUAD history and accept/reject/retry/rollback |
| M8 - model study | PENDING | Reproducible independent metrics |
| M9 - anisotropy | OPTIONAL / PENDING | Approved formulation and isolated ablation |

## Blockers and limits

- Windows doctor failed because Ninja, clang-format and clang-tidy were absent from its process PATH. They exist under `C:\msys64\ucrt64\bin`. Do not repeat completed MSVC generation to repair tool discovery.
- This worktree's `validation_session.py environment` also fails on unavailable discovery tools. Iteration planning fails on missing `build/validation-session/local/validation-baseline.json`. Preserve both command failures; they are local prerequisites, not numerical failures.
- WSL Ubuntu 24.04 has GCC 13.3, CMake 3.28.3 and Ninja. Availability only was checked; no Linux configure/build/test was run.
- The M0 runner executes CTest only in GCC mode; MSVC uses `BUILD_TESTING=false`. It omits full Python, independent science comparison and ASan/LSan/CRT qualification. Verify actual compiler metadata and complete separate gates; runner success cannot close M0.
- TRI consumer coverage remains partial: [M0_TRI_DEPENDENCY_SCAN.md](M0_TRI_DEPENDENCY_SCAN.md). Face, Adapter, curvature/adjacency and metrics/output need deliberate typed QUAD paths.
- Documentation link validation stops on an inherited four-parent runner link in M0 evidence; the older journal also contains that path. These historical entries are retained. The correct current runner link is [tools/quad_m0_baseline.py](../../../tools/quad_m0_baseline.py). This checkpoint does not close the link gate.

## Scientific decisions retained

Keep QUAD opt-in and isolated from modernization main. Match six neighborhood classes without inferring historical polygon topology from TRI diagonals. Figure 7 fixtures remain unverified. Quad-dominant versus all-quad, boundary strategy and first-paper multipatch/non-manifold/anisotropy priorities require adviser alignment. No scientific merge is authorized by this checkpoint.

## Next exact action

Continue M0 without repeating the completed MSVC cases. Prepare worktree-local validation environment/baseline using verified tool paths and the existing qualified inventory; retain the failed profile observations. Then run the clean GCC/Linux baseline from WSL Ubuntu 24.04:

```sh
cd /mnt/c/Users/tiago/Documents/dev/research/apmesh-quad
python3 tools/quad_m0_baseline.py --mode gcc --science
```

Inspect the actual profile, keep existing time caps and stop at the first unexpected failure. Record full CTest/Python counts, offline GCC comparisons, applicable memory evidence and M0-G7 coverage before admitting M1. Unchanged source alone does not transfer previous qualification. Update this state and append the journal, then verify the remote checkpoint at session end.
