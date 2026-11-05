# Modernization plan and cumulative candidate regression

Audit date: 2026-11-05, Fortaleza. Classification: documentation-only engineering
audit and existing regression/qualification observations. No production, test,
configuration, scientific input, formula, ordering, acceptance, stopping, compiler
check or timeout is changed by this audit.

## Decision and measured revision

The existing engineering direction is supported within the measured scope. The
immediate dependency changes: current GCC and checked-MSVC Eistute/Book reuse
passes, so another speculative performance implementation is not the next item.
Complete delivery review and applicable exact-head/main gates. This audit is a
working-tree documentation update, not an integration or stage-closure seal.

| Identity | Value |
| --- | --- |
| Measured source head | `1604599cb36b9064907b5e93a3c45e56143a391f` |
| Measured tree | `e3ce60d9d956b06eb813e8a155b94d751d8aab00` |
| Reviewed remote main | `d1619137af4ad53e3bb98cf5fc4336f75350629f` |
| Branch / review at audit entry | `fix/adaptive-generator-reuse`, PR #163, draft; no configured hosted checks/statuses |
| Checked-MSVC reuse executable SHA-256 | `080ce9bf2c47faa219587b678b8be18482ee93a7e3467e5be4de553cece739b8` |
| Checked-MSVC reuse PDB SHA-256 | `42878e7705d53772b35430ea0368213c24f25c6ba9c3a88619c7222b62d6919c` |
| GCC CLI executable SHA-256 | `73fccf8e6b87f10a67786bfd2ea1f2628026fffe997fc7aa747f43ab4e439aa0` |
| MSVC CLI executable SHA-256 | `da2f2e56454dcb6709435ecded8f1b8dd1881ab8ae1673cf82f4b471c9a42c7b` |

Remote main, all branch heads, the open PR, check-runs and commit statuses were
queried before regression. The candidate has 16 commits beyond reviewed main,
touching seven production translation units and four production headers. The
audit examines that cumulative delta, including the four diagonal-list guards,
diagnostic state/timing repairs, AFT membership/incidence/count structures,
curvature point access/transfers and local FindUV array scratch. The retained
operand-copy rejection is not silently reinstated.

## New observations

| Gate | Observed result | Scope |
| --- | --- | --- |
| Canonical GCC C++17 and checked-MSVC Debug builds | Pass; incremental builds preserve the sealed executables/PDBs byte for byte | Existing compiler profiles, not new clean-build, Clang or C++23 qualification |
| Full CTest inventory | 75/75 pass, zero failures/errors/skips; inventory names equal JUnit names; 391 nested Python controls | Includes actual boundary/retry/rejection, accepted-root/snapshot, malformed-input, lifecycle and checker corruption controls |
| Current MSVC native controls | Metrics and diagnostics pass; six cumulative numeric/resource markers also pass on GCC | 60 point-access cases, 120 sorter comparisons, 912 transfer checks, 65 edge-count cases, 75 FindUV cases and balanced timing/payload controls per ABI |
| Current checked-MSVC CLI | All 23 invalid inputs rejected; one existing aligned analytic state passes with one independent boundary comparison | Actual CLI, distinct from the typed reuse probe |
| Current checked-MSVC UV/CRT | All existing contracts, 12 membership cases, 12 repeated empty transfers, real allocation-hook control and all 515 measured allocation denials pass; zero retained fixture blocks/bytes | Fixture-local allocation/publication/owner guarantees, not whole-process leak accounting |
| Ordinary frozen GCC Eistute/Book | Nine states, 45 exact scientific artifacts, 123 independent boundary comparisons | Eistute accepted 0/1, rejected 2/3/4; Book accepted 0/1, rejected 2/3 |
| GCC same-generator reuse | Both calls of each model match frozen references: 90 artifact comparisons and 246 independent boundary comparisons over 18 observed states | Same captured configuration, fresh Timer/reapplied process state, serialized execution |
| MSVC Eistute same-generator reuse | One pair completes in 200.651931 s; five states and 15 independent boundaries per call; 25 scientific artifacts identical between calls and to the retained prior first call | Unchanged total 300 s cap; previous live output restored byte for byte |
| MSVC Book same-generator reuse | One pair completes in 115.115937 s; four states and 108 independent boundaries per call; 20 scientific artifacts identical between calls | Unchanged total 300 s cap; independently checked fresh same-ABI first call |
| Archive/FindUV counters | Eistute: 5 archives, 14,660 calls, 1,542 I_MAX exits per call. Book: 4 archives, 33,456 calls, zero I_MAX exits per call | Equal first/second values; three ordinary CLI summaries also equal their preserved references |
| Cumulative static analysis | Pass on all ten changed production/test translation units, including six changed headers, using actual compile commands and cumulative changed-line ranges | Scoped analysis, not a claim that all legacy diagnostics are absent; no fixes or new suppressions |
| Format, whitespace, architecture/contracts | Pass on the cumulative branch delta | Explicit read-only checks; no blanket source formatting |
| Full Doxygen | Fails, exit 1, with 2,718 error-formatted diagnostic lines | Documentation remains unqualified; diagnostics are retained, not disabled |

The CTest inventory includes 69 entries labelled application, 35 labelled lifecycle
and 21 labelled memory; labels overlap. Those ordinary contract tests are not
instrumented ASan/LSan/UBSan campaigns. No zero-coverage or expected rejection is
reported as successful mesh generation.

The one MSVC pair per model observes the required liveness/reuse gate. It is not a
repeated, paired timing experiment establishing a stable speedup or attributing a
whole-process improvement to one package. Preserve the older 289.468 s unchanged-
binary completion, all 300 s failures, the rejected hash/debug-proxy abort and the
qualified first-call profile with its overhead/prefix limits.

## Findings and plan corrections

1. The active timeout paragraph was stale after the new measured pairs. Replace
   it with the current result and delivery dependency; retain its entire prior
   chronology verbatim in the plan/state history files. Their existing bytes
   remain an unchanged prefix, verified by hashes.
2. The execution ledger and closure inventory still called SP-06..08 unrun or
   SP-09/10 unqualified after later artifact-specific reports. Link the measured
   reports and mark the P2 machine ledger as the preserved entry specification.
   Its recipes/parameters and historical measurement fields remain unchanged.
3. A delivered-milestone paragraph still described 203 current definitions and
   18 uncaptured symbols. The current matrix has 201 active definitions, 185
   bindings, 16 uncaptured and two named retirements. All five matrix source
   hashes match current files; preserve 203 as the original historical count.
4. General 'later stages pending' wording obscured bounded compiler, storage,
   engine/context and timing deliveries. State which capabilities exist while
   keeping every full stage unclosed. The internal engine milestone is not full
   Stage 6; local FindUV arrays do not remove public Eigen types/evaluation.
5. Passing functional/fixture checks do not requalify the changed complete process
   under old ASan binaries. Preserve old instrument scopes and retain the required
   full-process CRT/UB/leak, parallel, caller, mutation, recovery and domain work.
   The ten closure dispositions stay three bounded-qualified and seven partial/open.
6. Full documentation validation still fails. Retain the measured Doxygen debt
   in Stage 8 and final integrated qualification; do not change warning settings
   or imply the entire modernization is qualified because current CTest passes.

These changes update [the plan](../MODERNIZATION_PLAN.md),
[current state](../PROJECT_STATE.md), [delivery route](../architecture/REFACTOR_SEQUENCE.md),
[execution ledger](../architecture/SERIAL_EXECUTION_LEDGER.md) and
[closure inventory](../architecture/STAGE3_CLOSURE_INVENTORY.md). The six controlling
documents had no missing local link targets before the edits; links and document
identities are checked again after the consolidated update.

## Execution record and remaining delivery

Complete commands, inventories, stdout/stderr, source/input/configuration/compiler/
binary identities, comparisons and failures remain in `build/plan-audit-20261105/`.
The local drivers use exclusive new output/log paths and never overwrite previous
campaign reports. The main entries are `entry.json`, `regression.json`,
`analysis.json`, `gcc-eistute.json`, `gcc-book.json`, `gcc-reuse/report.json`,
`msvc-eistute/{process,verification}.json`, `msvc-book/{process,verification}.json`,
`additional-gates.json`, `documentation-audit.json`, `history-preservation.json`
and `final-verification.json`.

Commands include canonical incremental builds, CTest inventory/JUnit comparison,
the existing MSVC metrics/diagnostics/invalid-input/UV controls, both ordinary
frozen GCC cases, the existing GCC reuse driver and one fixed MSVC pair per model.
Static-analysis arguments and real compilation commands are retained in the local
analysis report/database. Read-only quality entry points include:

```text
cmake --build build/windows-gcc17 --parallel 2
cmake --build --preset windows-msvc-serial
ctest --test-dir build/windows-gcc17 --show-only=json-v1
ctest --test-dir build/windows-gcc17 --output-on-failure --no-tests=error --output-junit build/plan-audit-20261105/ctest.xml
python tools/quality.py format --base origin/main
python tools/quality.py whitespace --base origin/main
python tools/inventory_architecture.py --output docs/architecture/source_inventory.json --contracts docs/architecture/contracts.json --check
python tools/quality.py docs
```

Continue with one consolidated delivery review: bind unchanged runtime evidence
to the exact delivered source/binaries and explicitly record the documentation
delta, recheck remote concurrency/checks and every applicable local requirement.
After integration, validate the actual main revision before the next production
package. This audit neither merges PR #163 nor substitutes the candidate's local
results for those main gates. No new performance package, additional scientific
model, instrument Cartesian product or automatic source-audit successor is queued.

## PR #163 delivery continuation

The subsequent bounded delivery consolidates these documentation changes without
altering runtime/test/input/compiler bytes. Review and stage the exact delta,
then run the required local inventory, builds, regression, negative/native/CRT,
ordinary frozen science and fixed GCC/MSVC reuse gates once on the committed
head. Each MSVC pair retains its total 300-second cap; the first unexpected
required failure stops integration. Previously qualified scoped static analysis
is reused only after source/control/compiler-command identity checks.

Audit fresh remote base/head, PR/checks and publication metadata before merging
the tested head. Verify that the merge tree matches the qualified head, then
repeat the required validation on actual main before starting another package.
Commands, exact hashes, reports and the integration disposition remain under
`build/pr163-delivery/`; the PR records the final head and main revisions. The
original audit entry above remains a historical pre-delivery observation.

This is integration of the bounded P4 repair/engineering package, not Stage 3
closure. All seven partial/open rows, artifact-specific ASan limits, complete-
process CRT/UB/leak, parallel/caller/mutation/recovery obligations and the failing
Stage 8 Doxygen gate remain explicit. No scientific threshold, support promise,
baseline, instrument assertion or configured check is relaxed for delivery.
