# Reuse archive diagnostics

Date: 2026-11-06, Fortaleza. Classification: engineering-only test-fixture
observability repair. Production, scientific inputs, formulas, ordering,
acceptance, retry, stopping and timeout policies are unchanged.

## Problem and bounded repair

The [PR #163 main attempt](PR163_MAIN_VALIDATION.md) completed ordinary frozen
science but aborted when its reuse fixture renamed live to first. Buffered
native return/counter output was lost, and the exception did not identify a
blocking file or process. The second call never started. Preserve that failure;
it is not a demonstrated meshing defect or a successfully qualified reuse pair.

The existing attempt_metrics_probe now flushes its actual call result before
archiving. A shared test-only helper attempts the same directory rename once,
reports the error and returns failure instead of terminating with an uncaught
filesystem exception. It does not retry, delay, copy, delete, skip the archive
or change the output/configuration contract.

On Windows, failure diagnostics report the filesystem category/code, immediately
observed last-error value, source and target. Read-only DELETE-access probes
identify restricted direct entries. Restart Manager records query status, PID,
process start time and whether an owner is the fixture itself. Its session is
scoped; only start/register/list/end APIs are used. There is no shutdown, restart,
foreign-handle closure or permission change. Query errors and empty observations
are reported, not converted to proof that no blocker exists. Direct-entry
inspection does not promise recursive or directory-handle ownership coverage.
The last-error value is diagnostic context, not a replacement for the returned
filesystem error code. Portable builds retain the one-attempt error report;
Windows ownership observations do not qualify another platform.

Rstrtmgr is linked only to the Windows test target. The serial production engine
and CLI retain their dependency and source identities. Existing recorded runtime
evidence is reused only after source/input/control/compiler/binary checks; changed
probe binaries require their own native and scientific caller observations.

## Controls and pre-delivery observations

The existing application.attempt_metrics runner adds native archival controls,
without a new CTest target or scientific model:

| Control | Required observation |
| --- | --- |
| Closed output stream | One successful rename; payload preserved and live absent. |
| Occupied nonempty destination | Error return; both source and existing destination preserved. |
| Fixture-owned open stream, Windows | Error return and sharing violation 32 for the file; Restart Manager identifies the known child PID. |
| Externally owned open stream, Windows | Error return and sharing violation 32; Restart Manager identifies the known parent PID. |

All four controls pass with the actual GCC and checked-MSVC probes before
delivery. The original metric/negative/scientific oracles remain unchanged.
The two portable controls do not establish unmeasured non-Windows qualification.

Before the tracked repair, a separate diagnostic copy used the same GCC engine,
actual compiler command and GNU wrapping options. Three reversible text edits
added the helper, flushed the summary and propagated archival failure. Both
Eistute calls then completed in 13.121102 seconds total, with 25 exact scientific
artifacts and 15 independent boundaries each, and equal archive/FindUV counters.
Both renames passed. This failure was not reproduced, so no owner was attributed
to the original abort. That calibrated diagnostic observation is not substituted
for the revised delivery's required exact-head/main gates.

Local identities, commands, controls, native stderr and that diagnostic pair are
retained under `build/reuse-archive-diagnosis/`. The prior timeout, reviewed build
continuation, failed archive and successful ordinary science retain their
separate reports under `build/pr163-delivery/`.

## Delivery gates and remaining limits

Require exact-head/main GCC and checked-MSVC probe compilation, the existing
75 CTest entries/391 nested controls with no skips, the four archive controls
on both Windows ABIs, scoped changed-line analysis, formatting, whitespace,
inventory/contracts, links and fresh remote concurrency/check review. Require
one fixed Eistute and Book reuse pair per ABI on each delivery revision, with
the unchanged 300-second total cap, strict frozen GCC/fresh same-ABI MSVC
comparisons, positive independent boundaries and equal archive/FindUV counters.
Stop at the first unexpected failure; retain unchanged qualified observations.

Full production sources and CLI/engine identities are unchanged by this repair;
bind the prior ordinary frozen science, unaffected native/negative/CRT evidence
and scoped analysis by identity. Do not rerun unrelated instruments or models.
The PR and local delivery/integration records identify final revisions and results.

This repairs failure observability, not the unproven cause of the original
permission/sharing event. No stable timing improvement, mesher defect repair,
Stage 3 closure or full-process memory qualification is claimed. All ten ledger
dispositions and the Doxygen failure remain. The next production package stays
blocked until the revised exact-head/main delivery requirements pass.
