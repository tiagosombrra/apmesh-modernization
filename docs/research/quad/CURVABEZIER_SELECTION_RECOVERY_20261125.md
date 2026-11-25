# CurvaBezier selection record and process recovery

Updated 2026-11-25 Fortaleza. [Commands and receipt](evidence/CURVABEZIER_SELECTION_RECOVERY_20261125.json).

[Draft PR 267](https://github.com/tiagosombrra/apmesh-modernization/pull/267)
at `0fd8ae1e` adds a selection record and explicit recovery to the existing
research runner. The incremental changes after PR 266 touch the runner,
tests and documentation. The native source and grouping/admission criteria
match the earlier trial.

The runner records the original mixed OBJ and native front before staging.
It atomically replaces `result.json` as the authoritative decision and
materializes `selected.obj` from the recorded source. The receipt binds the
previous and selected mesh and front by SHA-256 and checks the native curve
witness. The candidate also requires an eligible frozen comparison. A failure
before replacing the decision record leaves the baseline authoritative.
If a process stops after the record is replaced, the selected copy can lag
until recovery. File contents are flushed before replacement.

```text
python tools/quad_grouping_trial.py --recover <trial-directory>
```

Run recovery after the original process stops. It validates the retained
files and rewrites the selected OBJ. Recovery after an interrupted process
depends on the recorded native files being present. Power loss and a
live in-memory adaptive owner commit require separate evidence.

Four subprocess and validation controls cover exit just before and after
the decision commit, tampered native artifacts and the unsupported old
record format. The exact runner reuses the same MSVC C++17 executable as
PR 266 because native source and configuration match. The directed suite
discards the selected copy and runs recovery for the eligible candidate,
the native forced rejection, and the protected-size veto. All three
selected OBJ hashes and the native candidate hash reproduce PR 266.
The 26 reporting tests pass. Native source negative controls and the full
matrix were not rerun locally.

PRs 265 and 266 each have four successful hosted checks and await independent
review. PR 267 had 0 successful, 4 pending and 0 failed hosted jobs at checkpoint.

This checkpoint qualifies a durable experimental selection record and recovery
for one trial. No selected OBJ is counted as an adaptive epoch. Use typed source
state and a qualified mixed estimator to derive a new native edit from the
previous accepted mesh before applying issue 221 admission.
