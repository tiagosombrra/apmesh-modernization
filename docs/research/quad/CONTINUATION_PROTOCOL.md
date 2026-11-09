# QUAD research: durable conversation and agent handoff

This protocol is **mandatory for every substantial QUAD-related development, research, review, or implementation session** on `quad-templates`, including ChatGPT, Codex in VS Code, and local contributors. It does not schedule work or grant unattended GitHub access: a connected agent must perform the Git update during that session.

## Single source of truth

1. **Start here:** [STATE.md](STATE.md), containing the one current active milestone, result, precise next action, open blockers, baseline and evidence.
2. **Plan:** [IMPLEMENTATION_ROADMAP.md](IMPLEMENTATION_ROADMAP.md), authoritative scope, dependencies, gates M0–M9 and scientific assumptions.
3. **Static audit:** [BASELINE_AUDIT.md](BASELINE_AUDIT.md); facts derived from reading code, not proof of executed tests.
4. **Session history:** [SESSION_LOG.md](SESSION_LOG.md); append-only chronological record of work and decisions.
5. **Current M0 evidence:** [M0_EVIDENCE.md](M0_EVIDENCE.md); measured versus pending checks must remain separate.
6. **Modernization status is separate:** `docs/PROJECT_STATE.md`, `docs/MODERNIZATION_PLAN.md` and the repository root `AGENTS.md`.

Do not rely on a prior chat or a ChatGPT memory as the authoritative project status. A conversation can be truncated; only verified repository content persists for all collaborators.

## At the beginning of every new conversation/session

1. Read this protocol, `STATE.md`, `IMPLEMENTATION_ROADMAP.md`, the latest `SESSION_LOG.md` entry and the relevant evidence.
2. Verify the repository, current branch head, remote `main` head, open PRs and CI/quality status if available. Identify whether work has advanced since the previous checkpoint.
3. Check any local uncommitted changes before writing. Do **not** overwrite concurrent changes or reset a branch without explicit approval.
4. State the active milestone, the first pending gate and the intended scope. Preserve the historical TRI path, ownership contracts and the independent modernization plan.
5. If a listed fact cannot be verified, label it **unverified** or **pending** instead of treating the previous statement as current.

## During work

- Only one active milestone/work item at a time unless a documented parallel experiment is explicitly approved.
- Use small reviewable commits or PRs targeting `quad-templates`; do not merge scientific code into `main` by default.
- Record commit/PR identities, changed files, precise commands, toolchains, data hashes, scientific results, negative controls and failures.
- Keep claims distinct: `implemented` != `compiled` != `tested` != `scientifically validated` != `merged`.
- Do not silently change historical oracles, scientific tolerances, input corpus, timeout, element definitions or scope to satisfy a gate.
- Distinguish adapter/UV infrastructure, new research algorithms and speculative scientific claims.
- Avoid editing modernization documents just to report QUAD progress.

## Mandatory checkpoint at the end of every session

Before giving the final user-facing status, or after each milestone when the session spans multiple commits:

1. **Update STATE.md**: UTC timestamp/date if known; active milestone and status; work completed; exact changed paths/commits/PRs; tests run with results; tests **not run**; new blockers; next command/task.
2. **Append SESSION_LOG.md**: one dated entry stating intent, actual changes, results, warnings, decisions and handoff. Never rewrite past entries to hide a failure; add an explicit correction.
3. **Update IMPLEMENTATION_ROADMAP.md only when** a milestone's actual status, approved scope, sequencing or acceptance criteria changes. Keep historical rationale.
4. **Update the relevant evidence file** when a gate is attempted. Store output or bounded reference; record an `unavailable` gate as blocked, not passed.
5. Commit/push the checkpoint to GitHub in the research branch, inspect readback or compare before declaring success. If push is unavailable, leave a clearly identified local commit/diff and state that remote persistence **did not** happen.
6. If multiple agents worked concurrently, resolve state conflicts using verified commit ancestry and explicit latest evidence; never silently discard the other agent's entry.
7. End the response with the repository document links and a concise current/next/blocker summary.

## 2026-11-09: remote-first continuity between ChatGPT conversations and local Codex

This section applies in addition to the mandatory checkpoint and scientific gates above. It is an **operational handoff contract**, not permission to weaken an oracle or claim scientific qualification.

1. **Start from live GitHub, never chat history.** Confirm the default `main`, canonical research `quad-templates`, open PR base/head and the actual working branch SHAs. Then read `STATE.md`, the latest append-only session log, this protocol and the relevant evidence/implementation. In a new ChatGPT conversation, request GitHub access if the connector is not available. Missing GitHub access means no remote update, not an implicit successful checkpoint.
2. **Separate three kinds of state.** Canonical status and scientific decisions live under `docs/research/quad/` on `quad-templates`; experimental C++ source and tests live on a feature branch/PR targeting `quad-templates`; the modernization `main` remains separate. An uncommitted VS Code worktree is not visible through the GitHub connector and must be inspected locally before the user/agent changes or synchronizes it.
3. **No concurrent blind writes.** Before any write, re-fetch the exact target file/blob SHA and feature/base branch heads. If upstream moved or the local working tree has changes, reconcile explicitly; never reset, discard, force-push, or overwrite another agent's work by default. Prefer one active feature branch/PR per work item, small reviewable changes, and a reviewed integration.
4. **Checkpoint every substantive completed session.** Publish source changes to their feature branch with a PR, update `STATE.md` and append `SESSION_LOG.md` on the canonical research branch, and include exact SHA/PR, changed paths, completed tests with platform and result, failures and tests **not run**, pending gates and one concrete next action. Verify the remote readback before claiming persistence. Documentation-only checkpoints do **not** certify the new SHA scientifically; run all applicable exact-head gates before claiming milestone qualification or merging code.
5. **Respect execution boundaries.** GitHub read/write does not provide access to the user's Windows working tree, local unpushed commits, MSVC, WSL, or native logs. Do not claim local builds or tests unless actually executed in a suitably configured environment. The connected actor must perform all GitHub writes during the session; none occur autonomously after the conversation.
6. **Public-repository hygiene.** Keep credentials, private correspondence, personally identifying information, copyrighted scans without distribution rights, and private filesystem artifacts out of commits. Preserve only approved source-derived evidence and safe paths/hashes.

**Resume instruction for any new conversation or Codex workspace:** "Resume the QUAD work in `tiagosombrra/apmesh-modernization`. First read `docs/research/quad/STATE.md`, `CONTINUATION_PROTOCOL.md`, `SESSION_LOG.md` and `IMPLEMENTATION_ROADMAP.md` from the live `quad-templates` branch; then inspect PR #185 and the actual feature-branch SHAs. Identify the next unqualified gate and continue without touching `main`. At the end, update the canonical state and append a session checkpoint with verified GitHub readback. Do not claim unexecuted tests."

## Resume prompt (copy into a fresh conversation)

> Continue the APMesh QUAD research on GitHub `tiagosombrra/apmesh-modernization`, branch `quad-templates`. Read `AGENTS.md`, `docs/research/quad/CONTINUATION_PROTOCOL.md`, `STATE.md`, `IMPLEMENTATION_ROADMAP.md`, and the latest `SESSION_LOG.md`. Verify the current remote heads and gates, resume exactly the next pending item, and commit an updated `STATE.md` plus a session log entry before ending. Do not conflate this work with the modernization of `main`. Do not claim tests passed without evidence.

## Limitations

A repository protocol **cannot automatically update itself after an unrelated chat**. The agent working in that chat must have GitHub access and actually write and verify the checkpoint. When the tool is unavailable, the response must say so and supply a patch/manual instructions rather than claiming persistence.
