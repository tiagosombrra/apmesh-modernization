# Project state

## Current checkpoint and active work

Entry main: `c44f1860916ac10f914a3a179354535b4dc55ce6` (PR #135).
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

P2 exact head/main passed 74 CTest entries and 380 nested Python controls, source/
input/application/prior-evidence identity, recipe replay, architecture/contracts,
whitespace and staged/remote checks. PR #135 retains its exact identities.

P3's [first complete MSVC/ASan observation](evidence/SERIAL_ASAN_SP02.md) passed
at this entry main. All 73 native units compiled with ASan in C++17 RelWithDebInfo.
The actual release control passed and the actual expired read was detected.
Natural SP-02 ran once, returned zero and passed independent physical/UV/analytic
and boundary checks: accepted initial step 0, two patches, eight triangles and
one positive shared-boundary comparison, without an ASan diagnostic. There was
no rejected/adaptive retry state. This is bounded complete-process evidence,
not whole inventory, leak, CRT/LSan/UBSan or parallel qualification.

Documentation delivery reuses this single ASan observation by source/tool/artifact
identity, with the existing 74 CTest/380 nested Python controls on head/main.
Production, fixtures, tests, scientific inputs and numerical criteria remain fixed.

The [closure ledger](architecture/STAGE3_CLOSURE_INVENTORY.md) still has ten
inherited obligations: three have bounded qualification and seven remain
partial/open. P1 removes the compiler prerequisite, not the S3-09 complete-process
memory obligation. No required observation is waived and no stage is closed.

## Next single adjustment after the first P3 witness

P3: continue the fixed remaining production cases SP-01 and SP-03..08 with the
qualified unchanged MSVC/ASan artifact. Preserve/classify the first unexpected
failure and stop expansion. Repair a reproduced supported defect in a bounded
item; do not create another source-only successor audit. SP-02 is not repeated
without an invalidated dependency. Other instruments, SP-09/10 observer
portability and all remaining cases stay unqualified until measured or justified.
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
