# Actual accepted steps in final serial reports

Base: main `103a81c7491674035a9487e48a16295a9214b271` (PR #113).
Classification: engineering-only report identity repair.

The preserved reporting audit checks 224 scalar associations across four qualified
normal cases and two new controlled callers. Scalars match the accepted states,
but both gap cases print accepted 0/1/4 as 0/1/2. Actual step 2 was rejected.
Normal article states 0/1 have no gap, so their original identity contracts pass.
Ten corrupted-observation controls are detected. The audit's CRLF parser failure
remains preserved, without altering raw data or repeating its generation cases.

A serial function-local vector now records initial/accepted IDs and supplies the
final label through checked access. Rejected trials do not append; a new Generator
call gets fresh storage. The public class layout and APIs are unchanged. Scalar
histories, numerical order, criteria, last-attempt reasons, runtime counts/formulas
and nonserial report inputs are preserved. This is not broad history rollback,
resume or unchanged-allocation qualification. Local value storage uses RAII.

Initial real-caller evidence preserves the gap's archived artifacts and every
serialized scalar while printing 0/1/4. The uninjected analytic plane computes zero
error and prints initial step 0. Ten report-checker tests pass. One initial test
mutation was a no-op and is preserved; it was corrected to corrupt a real field.
The first caller executor wrongly expected stable ADAPTIVE_MAX_STEPS=0 to mean
zero iterations; existing input clamping produced accepted 0/1. Its failed report
is retained. Consecutive cases use an explicit limit of 2, and the plane supplies
the initial-only witness. Production clamping and policies were not altered.

Required actual caller gates: two frozen production articles, archived/unarchived
acceptance gaps 0/1/4 with rejected 2/3/5, archived/unarchived consecutive acceptance,
an uninjected initial-only plane, and missing/duplicate-ledger controls. Separate
copies force only test acceptance or corrupt only report IDs. The missing ledger
must terminate with nonzero status, while the duplicate ledger must fail the
independent identity checker. These controls do not measure physical acceptance,
complete resource-failure recovery or mesh-quality improvement.

Require original failures on both archived/unarchived retained gap traces and
nonempty original successes. All sixteen serialized scalar fields remain exact;
only labels change for gaps. Preserve nine frozen mesh states, 45 artifacts,
strict decisions, independent physical/UV quality and shared boundaries. Preserve
the controlled archived gap's artifacts too. A reversible source-token check must
exclude every unrelated Generator change. Compiled diagnostic copies are reviewed
and reversed before interpretation; their controls are absent from production.

Exact-head delivery requires C++17 build, 64/64 CTest (zero failures/skips), 182
Python tests, all caller/original/mutation/scientific gates, full changed-caller
analysis, formatting/whitespace, contracts/inventory and staged/remote audits.
Results, command/source/input/executable/report hashes and preparation failures
remain in the delivery PR and local `build/accepted-step-repair/` evidence.
An open PR is not an integration result; revalidate main after merge.

Runtime measured_steps still counts accepted advances, and its normalization/
clock validity remains separate. Stage 3 stays open without a new qualified memory
slice, whole-process/parallel/ASan/CRT/LSan/UBSan or complete rollback/resume claim.
The relative-area result remains negative; reverse directions remain unapproved.
