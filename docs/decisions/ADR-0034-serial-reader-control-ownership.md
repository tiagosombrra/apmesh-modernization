# ADR-0034: serial control-result and pending-patch ownership

Status: accepted for bounded repair; full exact-head/main qualification complete.

LoaderBezierPatchFile returns a new list of unique control-only patch owners on
each call. It retains a local unique pending patch through parsing/publication,
including the historical trailing allocation. Partial results release on failure.
The method does not publish into the raw cache used by the other legacy loaders.
The return type is an intentional source API migration at the audited serial
boundary; no binary compatibility or external raw-result contract is claimed.

ReaderFilePatches retains these owners while interning controls and reconstructing
patches. A separate unique pending patch is consumed by Geometry::InsertPatch;
it never overwrites the parsed control owner. Existing Geometry curves and patches
may remain committed on later failure. Borrowed curves outlive patch destruction,
and C25/C26 restore incomplete observer publication and retire completed observers.
Consumed IDs remain consumed; this is not a complete-reader transaction/retry rule.

Enable badbit exceptions on the second file read and both record streams so an
allocation/resource failure cannot be consumed as a partial coordinate/index row.
Keep ValidateBezierPatchInput, normal EOF/failbit behavior, all control/index and
interning order, the 1e-7 tolerance, direction decisions and every numerical token.
Other public loaders, MPI/Hermite and Model/copy remain separate boundaries.

Classification: behavior-changing resource-lifetime and failure-propagation defect
repair. No scientific proposal, parser consolidation, acceptance change or change
to adaptive budgets/stopping policies. Retain original negative reports, require
actual positive/negative instruments, complete CRT sweeps, exact nonempty live
control/incidence/numerical pairs, independent preservation mutations and the full
prior regression before integration. See [bounded evidence](../evidence/STAGE3_SERIAL_READER.md).
