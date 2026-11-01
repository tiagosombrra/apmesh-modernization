# Project state

## Current checkpoint and active work

Entry main: `98f99ff84858932eb7b86ea3f4ce028acf04bf1b` (PR #134).
The [consolidated audit](evidence/STAGE3_CONSOLIDATION_AUDIT.md) replaced the
automatic sequence of root-border microaudits with five finite work packages.

| Stage | Current disposition |
| --- | --- |
| 0-2 | Closed for their measured scope |
| 3: memory and lifecycle | Open; 37 historical numbered slices, with later bounded repairs recorded separately |
| 4-11 | Pending; P1 supplies a bounded stage 4 compiler prerequisite for stage 3 instruments |

P1 delivered the demonstrated complete serial MSVC build repair. The actual
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

P1 exact head/main passed 74 CTest entries without failures/skips, with 380
Python controls nested in tooling.controls, focused native and real MSVC CLI
controls, nine Eistute/Book states, 45 exact scientific artifacts and 123 boundary
comparisons. PR #134 and its local integration seal identify revisions/artifacts.
P2 preserves that evidence by identity; it does not repeat or relabel it.

P2 fixes the [serial execution ledger](architecture/SERIAL_EXECUTION_LEDGER.md):
ten groups using existing inputs/controls, explicit owner/observer roots,
terminal-versus-logical-retry decisions, and three instrument applicability
profiles. It names 32 nominal production launches and five directed caller cases;
these are a future finite inventory, not new memory observations. Output-mode
variants, no-sync lifetime, same-process reuse and external Geometry remain
distinct. Debug compilation is not leak accounting. The ledger retains every
open closure assignment and stops expansion at the first instrument/caller failure.

P2 exact delivery head/main requires the existing 74 CTest entries and 380 nested
Python controls, source/input/application/prior-evidence identity, recipe replay,
architecture/contracts, whitespace and staged/remote checks. No production,
fixture, test, scientific input or numerical criterion changes in P2.

The [closure ledger](architecture/STAGE3_CLOSURE_INVENTORY.md) still has ten
inherited obligations: three have bounded qualification and seven remain
partial/open. P1 removes the compiler prerequisite, not the S3-09 complete-process
memory obligation. No required observation is waived and no stage is closed.

## Next single adjustment after P2 delivery

P3: qualify the complete MSVC/ASan C++17 target and actual positive/negative
instrument controls, then observe SP-02 once with native selection and no fault
injection. Preserve and classify the first failure before expanding the fixed
inventory. Repair a reproduced supported defect in a bounded item; do not create
another source-only successor audit. Other instruments/observer portability and
all remaining cases stay unqualified until measured or explicitly justified.
Follow the [five work packages](architecture/REFACTOR_SEQUENCE.md). Completion is
measured by resolved obligations or repaired defects, not test or PR counts.

The outside-root ideal retirement remains unreached/unqualified under S3-06.
Its automatic successor microaudit is superseded; all refusals, excluded events
and prior records remain intact. Reopen measurement only with an admissible
history or a named required closure experiment and a finite decision/stop rule.

Fixtures, baselines, MPI/OpenMP routing and scientific criteria are unchanged.
Complete prior checkpoints remain verbatim in
[PROJECT_STATE_HISTORY.md](PROJECT_STATE_HISTORY.md); their historical next-work
paragraphs are not an active queue.
