# Serial generation archive isolation

P4 engineering lifecycle repair, starting at main
5bcef3273c7af2f8da11052c4eb65d343707698e (PR #161).
Repeated successful serial calls reset metric vectors but previously retained
all prior saved mesh owners. The existing three-patch reader fixture reproduces
archive counts 1/2/2 for output h/h/disabled, against fresh-generator counts 1/1/0.
Graph/ID/coordinate/area bits and FindUV counts already agree with fresh instances;
the demonstrated defect is cross-execution owner retention, not numerical drift.

At serial Generator entry, clear saved error aliases before saved mesh owners.
This is the common boundary for typed/raw Execute and direct serial Generator
callers. Accepted/rejected archives within one generation retain their existing
order, owners and policy; no clearing occurs between attempts. Active mesh
replacement, communicator/ID creation, metrics, formulas and all other production
tokens are unchanged. MPI/OpenMP retain their original paths. Vector capacity may
remain reusable; no return-to-allocator or peak-memory reduction is claimed.
Borrowers must release previous result views before beginning another generation.
A reader failure occurs before this boundary and keeps its existing behavior.

The existing metrics probe uses one Generator for three successful calls, including
the raw bridge, and compares each with a fresh Generator. Both use the unchanged
initial-only Bezier fixture. Exact ordered graph signatures include patch/node/
element counts, IDs, coordinates, connectivity and areas; FindUV snapshots and
archive/error-alias counts must match. The final disabled-output call retains zero
archives. Require this control in existing CTest and in the same probe compiled
against the canonical MSVC C++17 engine. This bounded normal-call observation does
not qualify adaptive multi-step reuse, changed captured contexts, exception
recovery, concurrency, arbitrary external Geometry reuse or complete-process memory.

The first probe compilation exposed the legacy non-const ElementAdaptive::GetId
getter. Only test observer types were corrected; production signatures and the
failed preparation log are preserved. Existing physical owner/observer destructor
units retain their qualified source identities and prior ASan/CRT evidence.
They are not relabeled as a new complete-process reuse qualification; no new
instrument campaign or CTest target is added.

Require exact-head/main GCC/MSVC builds, 75 CTest entries/389 Python controls and
all previous native markers, nine frozen states/45 exact artifacts/123 positive
boundaries with accepted/rejected traces and IDs, three exact FindUV summaries,
23 MSVC invalid CLI controls and one analytic state/boundary. Source reversal,
scoped analysis, formatting, whitespace, inventory/contracts and staged/remote
gates remain mandatory. Commands, original witness, hashes and integration seal
are under build/serial-generator-reuse. Stop at the first unexpected failure.

This closes prior-archive retention across admitted normal serial calls within
S3-01/05/08. Other caller, recovery, adaptive reuse, UV/cache and instrument
obligations retain their separate limits; Stage 3 remains open.
