# APMesh QUAD — canonical state and resume point

**Branch:** `quad-templates`  
**Research entry baseline:** `f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94` (the merged modernization PR #183 at the time of branch creation)  
**Last recorded session:** 2026-11-08 (session 2026-11-08-02)  
**Current research milestone:** **M0 — baseline qualification / BLOCKED: no authorized executable checkout in this session**  
**Source of instructions:** [CONTINUATION_PROTOCOL.md](CONTINUATION_PROTOCOL.md)  
**Technical plan:** [IMPLEMENTATION_ROADMAP.md](IMPLEMENTATION_ROADMAP.md)  
**Read-only source audit:** [BASELINE_AUDIT.md](BASELINE_AUDIT.md)  
**M0 evidence:** [M0_EVIDENCE.md](M0_EVIDENCE.md)  
**Targeted static scan:** [M0_TRI_DEPENDENCY_SCAN.md](M0_TRI_DEPENDENCY_SCAN.md)  
**Local M0 runner:** [tools/quad_m0_baseline.py](../../../tools/quad_m0_baseline.py)  
**Session history:** [SESSION_LOG.md](SESSION_LOG.md)

## Current position

- A dedicated scientific branch exists. It is isolated from the ongoing engineering modernization on `main`.
- A source-level audit has mapped the six triangle-template neighborhood classes and the triangle-only downstream assumptions (UV `Face`, `Adapter`, `TriangleAdaptive`, curvature, reports and OBJ export).
- The implementation roadmap defines M0–M9 with explicit technical/scientific gates; the user requested a persistent GitHub handoff at the end of every relevant conversation.
- This checkpoint establishes that handoff protocol, discoverable from the research-branch root `AGENTS.md` and `README.md`. **No QUAD algorithm or QUAD tests have been implemented yet.**
- M0 was actively attempted. This session's execution host has GCC/CMake/Ninja/Python, but `git ls-remote` failed (exit 128: DNS could not resolve `github.com`). Thus it **cannot** check out the private repository or execute native gates on exact source. This is a blocker, not a test failure.  
- An opt-in runner was committed at `tools/quad_m0_baseline.py` and a **targeted, non-exhaustive** TRI source scan documented 37 lexical casts in selected hotspots. No production QUAD or TRI source changed.

**Most recent evidence delivery:** runner `0e51325b`, static scan `274e77dd`, M0 ledger `27f3fa20` and session log `faa0291c` (2026-11-08). This state checkpoint follows those commits. Inspect the live branch head before beginning any work.

## Current milestones

| Milestone | State | Admission / exit |
| --- | --- | --- |
| M0 — baseline qualification | **BLOCKED; executable checkout absent** | Reproducible local source SHA, C++17 builds, complete actual tests and frozen Eistute/Book comparisons |
| M1 — historical T1–T6 oracle | PENDING | Approved topology table, patterns, symmetries and negative tests tied to Figure 7 |
| M2 — independent UV QUAD topology | PENDING | Conformity, incidence, positive orientation and no hanging nodes |
| M3 — quadtree QUAD emitter | PENDING | Opt-in mode and exact default TRI preservation |
| M4 — physical quadrilateral element | PENDING | UV→XYZ area/normal, 4-node lifecycle and ownership tests |
| M5 — boundary transition | PENDING | Explicit quad-dominant vs all-quad decision and complete valid patch mesh |
| M6 — shared-curve multipatch | PENDING | 2-patch/reversed and >=3-patch matching canonical physical samples |
| M7 — repeated adaptation | PENDING | QUAD previous-state handling, accept/reject/rollback validation |
| M8 — model study | PENDING | Reproducible scientific comparisons and independent metrics |
| M9 — anisotropy | PENDING / OPTIONAL | Approved metric formulation and isolated ablation |

## Decisions that must remain explicit

- **Confirmed:** research is isolated in `quad-templates`; no QUAD feature is to be merged into `main` on the strength of this plan alone.
- **Confirmed:** match the *six neighborhood classes* in current TRI templates, not an unproven bytewise identity between current triangulation and all figures in Bento et al. (1993).
- **Pending adviser decision:** target `quad-dominant` or `all-quad`, including how to handle the AFT boundary region.
- **Pending evidence:** exact polygon topologies and symmetries of Figure 7 need independently verified golden fixtures.
- **Pending adviser decision:** prioritize multipatch conformity, non-manifold support, or anisotropy for the first paper.

## Tests / evidence status

- Prior modernization documentation reports **75 CTest / 526 Python** checks for its recent qualification. This is **inherited reported evidence**, not an execution in this QUAD branch session.
- GitHub returned zero PR workflow runs and zero commit status entries for the frozen entry ref. Neither absence is a passing test. GitHub source/API and comparison were available, but the isolated shell could not resolve github.com to clone the private repo.  
- A prepared local version of the runner passed Python syntax/help and **negative preflight** tests, but the exact GitHub runner file has **not been executed from a checkout**; the negative test is not an APMesh build.
- Local GCC/MSVC compilation: **NOT RUN** (no authorized checkout; MSVC also unavailable on this Linux host).
- Local CTest/Python suite: **NOT RUN**.
- Eistute/Book independent science comparison: **NOT RUN**.
- QUAD generation and QUAD tests: **NOT IMPLEMENTED / NOT RUN**.  
- M0-G7 targeted static review: **PARTIAL**; see [M0_TRI_DEPENDENCY_SCAN.md](M0_TRI_DEPENDENCY_SCAN.md).

## Next exact action — M0 execution on an authorized checkout

1. In VS Code or another host with authenticated Git access, fetch `quad-templates` into an **isolated and clean worktree**. Confirm `git rev-parse HEAD` and `git status --short`; do not overwrite the active modernization checkout.
2. Run `python tools/quad_m0_baseline.py --mode gcc --science` from the `quad-templates` root on a GCC-capable host; on qualified Windows/MSVC, separately run `python tools/quad_m0_baseline.py --mode msvc --science`. Both write hashed command logs and `report.json` under `build/quad-m0/`, retaining the article's 300-second per-case limit.
3. Review the actual CTest count, Python outcomes, Eistute/Book accepted/rejected/boundary oracle comparisons and MSVC/ASan/CRT evidence. **A successful runner alone is not M0 completion.**
4. Record real source/binary hashes, logs and gate dispositions in [M0_EVIDENCE.md](M0_EVIDENCE.md); continue the reachability audit for all triangle-only consumers.
5. Append [SESSION_LOG.md](SESSION_LOG.md) and update this state in GitHub. Only advance to M1 once the M0 criteria have been demonstrated, or a documented scoped exception is formally approved.

**Owner/operator note:** No background GitHub synchronization is assumed. A connected ChatGPT/Codex session must perform the actual end-of-session commit or explicitly report inability.
