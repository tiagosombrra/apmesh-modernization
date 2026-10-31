# Stage 3 consolidated audit and execution correction

Classification: engineering-only process/documentation adjustment. Entry main:
`e8ecdd1a1ac29bd636ef4662c71d201aa62d371d` (PR #132). Production, test
targets/assertions, fixtures, compiler configuration sources, scientific inputs,
numerical order, acceptance criteria and MPI/OpenMP behavior are unchanged.
The audit changes the active work queue and records a current build blocker.

## Findings and current regression

The delivered history since numbered slice 37 contains 32 integrations, 18
touching production. Examples include actual pending Face/Edge/ideal ownership,
terminal error cleanup, accepted-root/stopping and reporting repairs. Production
path changes are an inventory, not proof that every changed path is a separate
qualified repair. The 37 numbered slices exclude these later separately recorded
repairs and are not a percentage or effort estimate.

The last seven integrations (#126-#132) change no src/include production file;
only #129 adds test/tool/build inputs. The production tree remains identical to
PR #125. The last three integrations add source/observation documentation without
production corrections. Those records preserve useful negative/scope evidence,
but continued source-audit successors were no longer a sufficient progress goal.

One fresh current-state regression on entry main passes 73/73 CTest entries,
with no failures/errors/skips. tooling.controls contains the 380 Python tests:
these are nested counts, not 453 independent CTest entries. The suite takes
32.85 seconds (32.90 seconds including invocation overhead). Test execution
therefore explains little of the recent wall-clock effort; investigation,
repeated checkpoint preparation and fragmented delivery dominated it.

The [compact audit](stage3/consolidation/summary.json) and local
build/stage3-consolidation-audit/current-state.json retain the commit/path
classification. Current regression commands, XML, complete output and hashes
remain in its current-regression subdirectory. No old custom native allocation
or scientific campaign is repeated to obtain this observation.

## One actual complete serial compiler observation

A single Visual Studio 2022 x64 Debug build of the real ap_mesh target uses the
current source with BUILD_TESTING, MPI, OpenMP and LTO disabled. Configure succeeds;
build exits 1. This is an uninstrumented compiler diagnosis, not an ASan/CRT or
whole-process lifetime result. No source adapter or extracted-method substitute
is used, and there is no retry.

| Observed translation unit | Compiler evidence | Disposition |
| --- | --- | --- |
| src/curvature/curvature_discrete.cpp | C2065, undeclared M_PI | Current full-target portability blocker |
| src/estimate/charge_estimate_process.cpp | C2131 and cascading C3863 on runtime-sized arrays | Current full-target portability blocker; preserve numerical expressions/domain when repairing storage |
| src/parallel/Communicator.cpp | C2131, C3863, C2668, C2296 and C1003 | Included by the full target even in this serial profile; preserve MPI/OpenMP behavior when correcting serial build selection or source portability |

Sixty reported compiler diagnostics are not sixty independent defects. The
compiler reaches its error limit, so later blockers may remain. The first failed
report/log is retained with configuration, source revision, command, toolchain
and hashes. No required gate is described as passed because it failed as expected.
S3-09 remains open; the audit delivers the diagnosis, not a working MSVC target.

This is a concrete prerequisite for the required full-process memory obligation.
The existing plan already permits one bounded stage 4 portability prerequisite
to unblock stage 3. The next output is the complete serial executable compiling
with the selected toolchain, followed by appropriate scientific/reference gates
for the actual code/build change. This audit does not invent a numerical repair
or authorize supported-domain changes merely to make compilation/coverage pass.

## Finite closure ledger and dependency route

All ten original closure obligations are retained with stable S3-01 through S3-10
identifiers. Three have bounded component qualification; seven remain partial/
open. Historical qualifications and their limits are not widened or invalidated
by the green regression. No open observation is reclassified as optional or
closed. [The current ledger](../architecture/STAGE3_CLOSURE_INVENTORY.md) gives
each row its contracts, remaining gap, required observation and delivery package.

| Package | Concrete output |
| --- | --- |
| P1, next implementation | Complete serial instrumentable-toolchain build; correct demonstrated compiler blockers while preserving scientific semantics |
| P2 | Supported serial executable/input/caller and terminal-versus-retry ledger, mapping existing evidence to missing required observations |
| P3 | Fixed minimal actual complete-process inventory with qualified positive/negative instruments, teardown/repeated execution and bounded repairs of reproduced defects |
| P4 | Related supported-caller lifecycle/observer/UV repairs with admitted triggers and exact invariant/gate exits |
| P5 | Explicit closure audit over all ten obligations and required exact-revision/main evidence; any missing gate keeps Stage 3 open |

These five packages are a dependency route, not a time estimate or a claim that
unknown defects take exactly five PRs. Detailed acceptance and stop decisions
are in [the delivery sequence](../architecture/REFACTOR_SEQUENCE.md). One work
item remains active at a time. A long campaign must have a fixed case inventory,
dependency justification and decisive output before execution.

The automatic root-border proximity microaudit is superseded. Outside-root ideal
retirement remains an open S3-06 obligation, with zero reach in the four admitted
contexts. Preserve every refusal and the 616 previously excluded events. Reopen
only with an admitted native history or named required closure experiment and
a finite question/output/stop decision. This changes scheduling, not the claim
that retirement is unqualified or the rule that missing required gates block
stage closure.

## Operational changes made by this delivery

- Current PROJECT_STATE.md is a short dashboard with one next implementation.
- MODERNIZATION_PLAN.md contains the current route plus unchanged original stage
  definitions, mandatory closure, test program and scientific/architecture rules.
- Closure inventory and refactor sequence have one current finite queue.
- Full original bytes of these four documents remain in same-directory history
  files, preserving their relative evidence links and historical records. Old
  next-work paragraphs no longer select the next task.
- Each task names a closure row, concrete output, supporting defect/gap, minimal
  affected checks and stop decision. Progress means an obligation resolved, a
  reproduced defect repaired or a required caller newly qualified.
- Focused checks run during implementation; required full regression runs on
  exact delivery head and merged main. Successful identical-revision evidence is
  reused. Large campaign repetition needs a changed dependency, named missing
  required gate or justified response to a preserved failure.

No assertion, test inventory or scientific threshold is reduced. A failed/
refused experiment is classified before a retry; no forced selector, fabricated
graph, unchecked iterator or altered domain obtains coverage. Unsupported
interface and instrument applicability/equivalence decisions must be explicit;
broader models or parallel gates are not silently moved out of stage 3.

## Delivery and remaining limitations

This audit may be integrated as documentation of the measured current regression,
failed compiler observation and changed queue. It does not integrate a failed
compiler repair, qualify the MSVC build or close a required stage gate. Require
73 CTest entries/380 nested Python controls on exact delivery head and merged
main, unchanged production/test/tool/build/contract/application identities, all
66 protected raw inputs, byte-identical historical snapshots, unchanged prior
sealed evidence, local whitespace/inventory checks and staged/remote audits.
Exact-head/main checks are separate from the entry regression above.

The audit/process adjustment is complete after those delivery checks. Stage 3
remains open with 37 historical numbered slices and its separately evidenced
later repairs. Stages 0-2 retain measured closure; 4-11 remain pending apart from
the bounded P1 prerequisite. No current full-process, parallel, LSan/UBSan,
universal retirement, global quality or performance qualification is added.

Next single implementation: P1, correct the demonstrated full serial MSVC build
blockers and deliver the actual executable build, preserving C++17 comparison,
formulas, numerical order, scientific inputs/criteria and MPI/OpenMP semantics.
