# APMesh QUAD — canonical state and resume point

**Branch:** `quad-templates`  
**Research entry baseline:** `f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94` (the merged modernization PR #183 at the time of branch creation)  
**Last recorded session:** 2026-11-08 (session 2026-11-08-01)  
**Current research milestone:** **M0 — baseline qualification / in progress, BLOCKED on local execution evidence**  
**Source of instructions:** [CONTINUATION_PROTOCOL.md](CONTINUATION_PROTOCOL.md)  
**Technical plan:** [IMPLEMENTATION_ROADMAP.md](IMPLEMENTATION_ROADMAP.md)  
**Read-only source audit:** [BASELINE_AUDIT.md](BASELINE_AUDIT.md)  
**M0 evidence:** [M0_EVIDENCE.md](M0_EVIDENCE.md)  
**Session history:** [SESSION_LOG.md](SESSION_LOG.md)

## Current position

- A dedicated scientific branch exists. It is isolated from the ongoing engineering modernization on `main`.
- A source-level audit has mapped the six triangle-template neighborhood classes and the triangle-only downstream assumptions (UV `Face`, `Adapter`, `TriangleAdaptive`, curvature, reports and OBJ export).
- The implementation roadmap defines M0–M9 with explicit technical/scientific gates; the user requested a persistent GitHub handoff at the end of every relevant conversation.
- This checkpoint establishes that handoff protocol, discoverable from the research-branch root `AGENTS.md` and `README.md`. **No QUAD algorithm or QUAD tests have been implemented yet.**
- The current M0 audit has verified repository metadata and GitHub status visibility, **not local GCC/MSVC builds, CTest or scientific runs**.

**Most recent verified delivery:** session log checkpoint commit `18412a9740ebbd83b04c8aad502955d2e1004532` (2026-11-08); this state file update follows it. Inspect the live branch head before beginning any work.

## Current milestones

| Milestone | State | Admission / exit |
| --- | --- | --- |
| M0 — baseline qualification | **IN PROGRESS; local gates pending** | Reproducible local source SHA, C++17 builds, complete actual tests and frozen Eistute/Book comparisons |
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
- 2026-11-08 GitHub query for the baseline commit returned **zero pull-request workflow runs** via the available endpoint and **zero commit status entries**. This is **not** a passing or failing test result; it is absence of reported checks via those endpoints.
- Local GCC/MSVC compilation: **NOT RUN**.
- Local CTest/Python suite: **NOT RUN**.
- Eistute/Book independent science comparison: **NOT RUN**.
- QUAD generation and QUAD tests: **NOT IMPLEMENTED / NOT RUN**.

## Next exact action — M0 execution

1. Check out `quad-templates` in a separate worktree and run the toolchain/version preflight.
2. Use `README.md` and `docs/QUALITY_AUTOMATION.md` to run the native serial C++17 configure/build/test commands on a recorded exact source commit; collect actual stdout, exit codes, compiler versions, durations, input hashes and test inventory.
3. Run the required frozen Eistute and Book scientific profiles under their documented accepted/rejected/boundary oracle policy (without changing numerical tolerances).
4. Check memory/ownership tooling with admitted applicable fixtures (GCC ASan and checked MSVC/CRT). Record any unqualified scope.
5. Write exact results to `M0_EVIDENCE.md`, update this state and append `SESSION_LOG.md`. Only then decide whether M0 is complete and M1 may start.

**Owner/operator note:** No background GitHub synchronization is assumed. A connected ChatGPT/Codex session must perform the actual end-of-session commit or explicitly report inability.
