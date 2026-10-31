# Project state

## Current checkpoint and active work

Entry main: `57d4cac866cf6a8677d33370e2367fc60045ee01` (PR #133).
The [consolidated audit](evidence/STAGE3_CONSOLIDATION_AUDIT.md) replaced the
automatic sequence of root-border microaudits with five finite work packages.

| Stage | Current disposition |
| --- | --- |
| 0-2 | Closed for their measured scope |
| 3: memory and lifecycle | Open; 37 historical numbered slices, with later bounded repairs recorded separately |
| 4-11 | Pending; P1 supplies a bounded stage 4 compiler prerequisite for stage 3 instruments |

P1 now implements the demonstrated complete serial MSVC build repair. The actual
full ap_mesh target builds with C++17 and Debug iterator checks, without excluded
source units. The existing pi definition and automatically owned replacements
for runtime-sized scratch arrays resolve the observed blockers in three source
files. Formulas, expression order, inputs and scientific policies are preserved.
Stack scratch becomes dynamically allocated storage; no unchanged-allocation or
MPI exception guarantee is claimed. The original compiler failure remains intact.

Build the executable with `cmake --preset windows-msvc-serial` followed by
`cmake --build --preset windows-msvc-serial`. The output is
`build/windows-msvc-serial/bin/Debug/ap_mesh.exe`. This is a development artifact;
whole-process sanitizer, Release distribution, MPI/OpenMP and C++23 qualification
remain outside this delivery. [Build scope and evidence](evidence/MSVC_SERIAL_CPP17_BUILD.md)
record the commands and limitations.

Exact delivery head/main gates require 74 CTest entries without failures/skips,
with the existing 380 Python controls nested in tooling.controls. The focused
portability check and real MSVC CLI controls accompany the GCC reference
comparison: nine Eistute/Book states, 45 exact scientific artifacts and 123
boundary comparisons. The PR and local integration seal identify their exact
revisions and outcomes; implementation alone is not integration qualification.

The [closure ledger](architecture/STAGE3_CLOSURE_INVENTORY.md) still has ten
inherited obligations: three have bounded qualification and seven remain
partial/open. P1 removes the compiler prerequisite, not the S3-09 complete-process
memory obligation. No required observation is waived and no stage is closed.

## Next single adjustment after P1 delivery

P2: establish the supported serial executable/input/caller and terminal-versus-
retry ledger from existing controls, then freeze the finite P3 complete-process
instrument inventory. Follow the outputs, acceptance and stop decisions in the
[five work packages](architecture/REFACTOR_SEQUENCE.md). Completion is measured
by resolved obligations or repaired reproduced defects, not test or PR counts.

The outside-root ideal retirement remains unreached/unqualified under S3-06.
Its automatic successor microaudit is superseded; all refusals, excluded events
and prior records remain intact. Reopen measurement only with an admissible
history or a named required closure experiment and a finite decision/stop rule.

Fixtures, baselines, MPI/OpenMP routing and scientific criteria are unchanged.
Complete prior checkpoints remain verbatim in
[PROJECT_STATE_HISTORY.md](PROJECT_STATE_HISTORY.md); their historical next-work
paragraphs are not an active queue.
