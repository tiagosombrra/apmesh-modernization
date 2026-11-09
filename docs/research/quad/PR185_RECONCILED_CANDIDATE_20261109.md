# PR #185 — reconciled candidate and qualification runbook (2026-11-09)

**Status:** Remote merge candidate published; full candidate qualification **NOT RUN**. This document is a checkpoint, not a green test result or permission to merge.

## Immutable identifiers at candidate creation

- Repository: `tiagosombrra/apmesh-modernization`.
- Candidate branch: `quad/integration-pr185-20261109`.
- Candidate [merge commit](https://github.com/tiagosombrra/apmesh-modernization/commit/c57749e8691907bc25575114191f20782ba16248): `c57749e8691907bc25575114191f20782ba16248`.
- Tree: `874c3dd0496dc34bc4eb5f59ccd96067bff43de8`.
- First parent (canonical research at preparation): `37a5771a396ff14dfda1647875df144773d1f9ad`.
- Second parent (original PR #185): `bb50b161cad0121402cc61475442b32aef33d2bd`.
- Original PR #185 remains open/draft; its head was not advanced. `main` and `quad-templates` source were not merged or changed.
- Candidate delta against canonical base consists of exactly 12 paths: the seven `research/quad` files, four `tests/quad` files and `docs/architecture/source_inventory.json`. Source and build-input blobs are preserved from the original feature revision. The existing base copies of `IMPLEMENTATION_ROADMAP.md` and QUAD bridge evidence were byte-identical to the original feature. The newer canonical `STATE.md`, `SESSION_LOG.md`, continuation protocol and separate delivery receipt were retained unchanged.
- Remote structural audit: candidate is a descendant of both parents, with no novel production `src/`, `include/` or `libs/` modifications. Both the research history and experimental code history remain reachable. This is structural evidence only.

## Required local qualification (clean worktree, Linux GCC)

Before executing, check local uncommitted changes and do not overwrite them. Work in a fresh worktree after fetching from GitHub.

```sh
git fetch origin
git worktree add --detach ../apmesh-quad-pr185-qualify c57749e8691907bc25575114191f20782ba16248
cd ../apmesh-quad-pr185-qualify
git status --short
git rev-parse HEAD
cmake -S tests/quad -B build/quad-pr185-linux -G Ninja -DCMAKE_BUILD_TYPE=Debug -DAP_MESH_QUAD_WITH_TREE=ON
cmake --build build/quad-pr185-linux --parallel 2
ctest --test-dir build/quad-pr185-linux --output-on-failure --no-tests=error
cmake --preset local-serial
cmake --build --preset local-serial --parallel 2
ctest --preset local-serial
python3 tools/validation_session.py plan --scope delivery --base 37a5771a396ff14dfda1647875df144773d1f9ad
python3 tools/validation_session.py run --scope delivery --base 37a5771a396ff14dfda1647875df144773d1f9ad
```

Capture the exact command/exit, compiler and environment versions, raw CTest/Python logs, source and binary hashes and failure/skip counts. The exact-head validation coordinator may require locally qualified lint/runtime tools; report missing tools as blocked. Previously reported 117 UV + 30 tree outcomes and 75 CTest / 527 Python are **historical expectations**, not new green results. Do not adjust old scientific references, timeouts or acceptance policies to pass.

## Windows/MSVC native bridge qualification

Use a separate clean checkout at the **same SHA**, Visual Studio 2022 x64 Debug. Run:

```powershell
cmake -S tests/quad -B build/quad-pr185-msvc -G "Visual Studio 17 2022" -A x64 -DAP_MESH_QUAD_WITH_TREE=ON
cmake --build build/quad-pr185-msvc --config Debug --parallel 2
ctest --test-dir build/quad-pr185-msvc -C Debug --output-on-failure --no-tests=error
```

Compare emitted adaptive-tree OBJ and the per-profile reports against approved raw captures only when the inputs, compiler profile and scientific expectations are compatible. If the standalone bridge fails, retain the failure and do not merge.

## Explicit admission gates

1. A clean resolved candidate, exact commit and no undocumented source modifications.
2. Both standalone QUAD native CTest entries execute and report the expected control outcomes; invalid-input controls remain active.
3. Complete serial application CTest and Python regression on the exact candidate head, plus applicable Eistute/Book scientific oracles. Any new dependency effects must be requalified; absent results block admission.
4. Code, tests, memory/ownership, physical topology, docs, scientific policy and known failure inventory reviewed; no falsely claimed full patch/all-quad/XYZ integration.
5. Reviewed PR integration into `quad-templates` only after the complete recorded gates; do not merge experimental QUAD into `main`. For consistency with local Codex worktrees, coordinate any fast-forward of the original PR branch instead of rewriting its history.

## Current blocker and continuation

The ChatGPT container's shell Git command cannot resolve `github.com`; the GitHub connector can read/write Git data but cannot execute a Windows/MSVC/WSL or full C++ build. The repository's own `AGENTS.md` forbids paid/automatic hosted workflows. Consequently **no native or baseline tests were run in this checkpoint**, and the candidate stays isolated.

**Next action:** obtain genuine exact-head native qualification (locally in the user's VS Code/WSL, or another environment that can fetch the repo and run its toolchains), record result hashes and failures, then review the candidate for integration. M1/M2/M3 remain partial. The numerical interior-point rule remains a separate adviser decision, not invented by this reconciliation.
