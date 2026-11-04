# Balanced serial timing intervals

Classification: diagnostic behavior-changing defect repair. Scientific expressions
and generation policies are unchanged. Starting head: 5bb7090ba5512b6dc0210e97a7e48d77b5c6928f.

Retained reports showed a full-generation duration near 1.79 billion seconds and
error-evaluation totals much longer than process wall time. Code inspection finds
no full-interval start in serial typed Execute. ErrorGlobal's serial post-curvature
branch closes slot 7 and restarts slot 6 instead of closing 6 and resuming 7.
Two serial callers also bracket slot 7 although ErrorGlobal already owns it.

Start slot 10 at serial typed Execute entry, before input loading; raw Execute
delegates to that entry. Correct the post-curvature 6/7 pair and remove four
duplicate serial caller operations. Every remaining generator token matches the
starting source after reversing only these timing edits. Timer's implementation,
clock provider, MPI/OpenMP operations and external 300-second watchdog are intact.
Production reads of these aggregates are reporting/printing; slot-5 input timing
and scientific decisions are unchanged.

## Reproduction and bounded validation

Commands, exact hashes and reports: build/serial-timing/.

The existing metrics probe adds an interval-protocol control using its established
Bezier input. It computes reference error/node curvatures, then repeats with only
timer timestamps seeded to simulate 100 seconds per node and a stale paused slot.
No scientific value or OS clock is injected. An early rejected-input call checks
the full start, explicitly closing that failed attempt in the control. The old
MSVC binary reports balanced=0, started=0, same_payload=1, curvature=0, error=1200
and full approximately 1.79e9 seconds. Its binary/PDB/source and log are retained.

The first built-in-generation control exceeded its 60-second fixture cap and was
rejected. Its source/binary/output remain retained; the bounded early-failure
protocol replaces that fixture, not a scientific timeout or failed numerical gate.
It requires no new scientific model or test target.

Corrected GCC/MSVC controls report balanced=1, started=1, same_payload=1 and
300 simulated curvature seconds, with no stale error interval. Global error and
all twelve node-curvature scalars match the reference bit for bit. Existing
direct Generator test callers now explicitly own their full-interval start.

Canonical C++17 GCC/checked-MSVC builds, scoped analysis, existing 75 CTest/389
Python controls, native controls, formatting and inventory/contracts pass. Frozen
GCC Eistute retains five states, 25 exact artifacts and 15 independent boundary
comparisons with accepted 0/1 and rejected 2/3/4. Only the intentionally variable
runtime summary changes: full_without_io=6.19113 s, curvature_aux=0.512554 s and
error_evaluation=0.006957 s, against 7.05320 s process wall time. The checked
curvature/error sum fits within the measured full interval. These are one-run
diagnostic observations, not a speedup or cross-ABI benchmark.

## Limits and remaining gates

No new long MSVC Eistute pair, Book run or retry was performed. Prior 300-second
failures remain required negative evidence; fixing reports does not resolve that
wall-clock gate or qualify integration/Stage 3. Direct legacy Generator callers
still own the outer start. Failed Execute does not publish a completed summary.
Clock resolution/monotonicity, parallel timing and complete recovery retain their
existing obligations. The repaired per-stage data can guide the next production
package without relying on the invalid accumulated totals.
