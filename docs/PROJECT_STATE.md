# Project state

## Current checkpoint and active work

Entry main: `e8ecdd1a1ac29bd636ef4662c71d201aa62d371d` (PR #132).
The current consolidated audit/regression replaces the automatic sequence of
root-border microaudits. Its [findings and execution rules](evidence/STAGE3_CONSOLIDATION_AUDIT.md)
are the active continuity source together with the finite closure ledger below.

| Stage | Current disposition |
| --- | --- |
| 0-2 | Closed for their measured scope |
| 3: memory and lifecycle | Open; 37 historical numbered slices, with later bounded repairs recorded separately |
| 4-11 | Pending; a bounded stage 4 prerequisite may unblock required stage 3 instruments |

Current-state regression: 73/73 CTest entries, zero failures/skips, with 380
Python controls inside tooling.controls. These are nested counts, not 453
independent test entries. The baseline suite took about 33 seconds. Exact
delivery-head/main results remain separate from this entry measurement.

Since slice 37, 32 integrations include 18 touching production. The last seven
touch no production; one adds the admitted prefix fixture. Recent audits supply
scope/negative evidence, not new production repairs or stage closure.

The [closure ledger](architecture/STAGE3_CLOSURE_INVENTORY.md) has ten inherited
obligations: three have bounded qualification and seven remain partial/open.
No required observation is waived or converted into a documentation-only pass.
The [five work packages](architecture/REFACTOR_SEQUENCE.md) define outputs,
acceptance and stop rules. Completion is measured by resolved obligations or
repaired reproduced defects, not test/anchor/PR counts.

The single complete serial MSVC build observation configured successfully but
failed in curvature_discrete.cpp (M_PI), charge_estimate_process.cpp (VLAs) and
parallel/Communicator.cpp (compiled even with MPI/OpenMP disabled). The compiler
error limit was reached, so these are observed blockers, not an exhaustive list.
This is failed build evidence, not sanitizer qualification or a green stage gate.

## Next single adjustment

P1: make the complete existing serial executable buildable with the selected
memory-instrumentation toolchain. Correct only demonstrated compiler blockers,
starting with the observed compiler failures; retain C++17 comparison,
arithmetic/order, inputs and scientific policy. A working full target is the
output, not another standalone source-audit PR. Preserve the first compiler
failure and keep a specific blocker if its repair would require scientific policy.
This is a bounded stage 4 prerequisite; it does not close stage 3 or qualify
whole-process memory by itself.

The outside-root ideal retirement remains unreached/unqualified under S3-06.
Its automatic next microaudit is superseded, while all refusals, excluded events
and prior records remain intact. Reopen measurement only with an admissible
history or a named required closure experiment and a finite decision/stop rule.

Production, fixtures, baselines, MPI/OpenMP and scientific criteria are unchanged
by this consolidation. Complete prior checkpoints remain verbatim in
[PROJECT_STATE_HISTORY.md](PROJECT_STATE_HISTORY.md); their historical next-work
paragraphs are not an active queue.
