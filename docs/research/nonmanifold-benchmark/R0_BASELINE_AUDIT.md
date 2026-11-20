# R0 — Repository baseline and concurrency inventory

**Observation:** 2026-11-14; repository read-only inspection, not fresh local execution.
**Scope:** research branch `research/benchmark-corpus-reverse-patches`; planning PR #225.
**Planning base and observed main:** `f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94`.
**Observed research head before this delivery:** `21971d5ae2e7dc7ef69375a8253c333babda17cb`.
These identities must be rechecked on the next delivery; a newer main does not invalidate the recorded snapshot.

## Concurrency review

At this read, the open PR list was:
- #227 `research(quad): P2d1b0 trial two real error-driven native Quadtree edits`, **draft**, head `4dba0421807047975a2163c917bd8bcd802bca8c`.
- #225 `docs(research): benchmark admission and reverse-patch feasibility plan`, **draft**, head `21971d5ae2e7dc7ef69375a8253c333babda17cb`.
- #214 `research(quad): R2c2 detached Eistute/Book owner stage and rollback (no weld)`, **draft**, head `7cd5014936a417565415d736bad40dc70deb35df`.

The state may change during parallel work. No QUAD or modernization branch was modified, rebased or merged by this research activity.

## Historical model identity (observed Git blob identity, NOT SHA-256)

| Path | Git blob SHA-1 | Size |
|---|---|---:|
| `input_models/book_v7a.bp` | `7e3338a4ebc43f0b3119b1cb6eda47e2ac205d14` | 11577 bytes |
| `input_models/eistute2.fixed.bp` | `6fa2f40e4270cccb6da140111953bbbcb69b0086` | 2213 bytes |
| `input_models/ribbed_bracket_nm_decor.bp` | `b4bd029815a6b83f2f523e177632f28d7d6d5179` | 5619 bytes |

The project provenance names these Book, Eistute and Decor Shelf. The original input data remain immutable; `ribbed_bracket_nm_decor.bp` vs. Decor Shelf should be documented explicitly in future figures/tables to prevent ambiguous attribution. Git blob SHA-1 is not a raw-file SHA-256; no fresh SHA-256 was calculated in this R0.

## Existing scientific and validation gates (requirements, NOT run results)

- `docs/GENERATION_VALIDATION_CONTRACT.md`: strict BP grammar (indexed 16-point bicubic patches), accepted/rejected saved stage semantics and fresh isolated outputs.
- `tools/check_boundary_incidence.py`: independent BP / runtime curve-group / actual OBJ comparison, positive shared-incidence coverage including non-manifold incidents; requires actual generation snapshots.
- `docs/REPRODUCIBILITY.md`: Eistute stage-4 archived numerical target is a retained candidate and must not be mislabeled accepted. Book/Decor archived numerical oracles have a narrower scope.
- `docs/QUALITY_AUTOMATION.md`, `docs/PROJECT_STATE.md` and `AGENTS.md`: architecture/cycle-life, memory and exact-image local qualification requirements; current Stage 3 continues separately.
- The repository state references a 75 CTest / 526 Python historical exact-head/main qualification for a production delivery. This is documented prior evidence, **not** a fresh R0 pass.
- GitHub status API on recorded main returned no combined statuses; GitHub check-run API returned zero check runs for recorded main and planning PR head. **No hosted CI result is inferred.**
- This research planning delivery has not run CMake/CTest, Python suites, memory probes, article reproduction or any scientific generation.

## R0 conclusion

**R0 repository / concurrency inventory: DOCUMENTED.** **R0 execution/qualification: NOT RUN**, since no production code is proposed here. Before any implementation or baseline-affecting work, qualify the exact new head and current main in an authorized toolchain, with positive/negative independent oracles and complete source/build/config hashes. A missing CI workflow is neither a pass nor a reason to relax mandatory local gates.
