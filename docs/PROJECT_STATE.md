# Project state

## Current checkpoint and active work

Entry main: `4cdeb15393487871542909bef065074bbad158b4` (PR #138).
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
at PR #135 main. All 73 native units compiled with ASan in C++17 RelWithDebInfo.
The actual release control passed and the actual expired read was detected.
Natural SP-02 ran once, returned zero and passed independent physical/UV/analytic
and boundary checks: accepted initial step 0, two patches, eight triangles and
one positive shared-boundary comparison, without an ASan diagnostic. There was
no rejected/adaptive retry state. This is bounded complete-process evidence,
not whole inventory, leak, CRT/LSan/UBSan or parallel qualification.

The next fixed campaign passed SP-01/03/04 but stopped at SP-05's 60-second cap.
One bounded CPU/stack observation localized an allocation hot path in Face::quality.
The [scratch correction](evidence/FACE_QUALITY_SCRATCH.md) changes one production
file to coordinate-only temporaries, retaining arithmetic and comparison order.
GCC, MSVC/ASan and checked Debug each preserve 4,230 scalar bits over 846 paired
rows, while quality allocations fall from 12/24/36 to zero. Actual denial controls
remain required. Public owning center APIs and all scientific policies are fixed.

Candidate SP-05 then completes once in 13.0484 seconds under the same 60-second
cap: accepted 0/1, rejected 2/3, retry 1, eight positive boundary comparisons and
no ASan diagnostic. The original three-state prefix retains 16 exact artifacts
and three exact metrics rows. Original failed processes remain failed evidence.
No other ASan production case was added in that correction. PR #137 passed its
exact-head/main 75 CTest/380 nested controls and frozen nine-state GCC regression
(45 exact artifacts, 123 boundary comparisons), plus scoped source/resource gates.

The [remaining fixed ASan production observations](evidence/SERIAL_ASAN_REMAINING.md)
now pass SP-06..08 with that same rebuilt artifact, without further compilation.
Exactly five processes complete below their unchanged 300-second caps, all with
empty stderr. Eistute and Book each repeat twice with exact OBJ/acceptance/boundary
comparisons, the prescribed accepted/rejected steps and 246 positive boundary
comparisons total. The existing no-sync configuration returns zero through normal
CLI teardown; it does not qualify synchronized boundaries. Other instrument and
caller obligations remain open.

The [terminal observer requalification](evidence/SERIAL_ASAN_TERMINAL_REQUALIFICATION.md)
now passes. An external actual SubMesh allocation and explicit counters exposed
the missing /EHsc exception semantics (C4530). The standalone test target now
requires /EHsc and treats C4530 as an error; all 74 instrumented groups are checked.
Four prerequisites pass, including nine typed payload rows and one actual
unwind allocation denied with one uncaught exception. Only then do all five
fixed SP-09/10 contexts pass their exact CLI/library oracles, without unexpected
ASan diagnostics. Original failed artifacts remain failed and intact.
Production, scientific policies and original fixture/oracle files are unchanged.
Earlier natural ASan records retain their actual flags; they do not establish
exception unwinding. No canonical application campaign is repeated.

The [closure ledger](architecture/STAGE3_CLOSURE_INVENTORY.md) still has ten
inherited obligations: three have bounded qualification and seven remain
partial/open. P1 removes the compiler prerequisite, not the S3-09 complete-process
memory obligation. No required observation is waived and no stage is closed.

## Next single adjustment after terminal observer delivery

P3: qualify the complete-process CRT observer/checkpoints with actual clean
release, deliberate retained-storage and allocation-hook controls before any
fixed-context campaign. SP-09/10 now have their five bounded MSVC/ASan terminal
observations; complete-process retained-storage/UB and remaining caller obligations
are still open. Do not repeat the unchanged terminal contexts for delivery.
SP-06..08 now pass; earlier observations retain their measured artifact identities.
Preserve/classify the first unexpected failure and stop expansion. Do not create
another source-only successor audit or repeat identical qualified observations
without a changed dependency. Other instruments, same-Generator reuse, caller
contracts and all remaining closure obligations stay unqualified until measured
or explicitly justified.
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
