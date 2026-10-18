# ADR-0012: prepare owned curve clones before publishing incidences

Status: candidate qualified; exact published-head and implementation-main gates required.
Issue #38. Classification: ownership/exception-consistency defect repairs and
engineering extraction, preserving successful policy.

The original helper returns a raw pending clone and can lose it if inserting
its target incidence throws. Four direct-helper sweeps reproduce scoped CRT
retention. The consumer truncates original incidences before cloning: 12 graph
sweeps fail coherence at denied ordinal 1. Ordinal 0 passes and later original
graph ordinals are not reached. Four all-non-Coons graph sweeps are passing
original controls, alongside normal and instrument controls (57 expected outcomes).

Return a unique pending owner. For each original shared curve, collect the same
nonnull incidences in the same order, prepare clones for exactly the same eligible
positions/types, then pass the owned batch into Geometry::InsertCurves. That
method guards size overflow and reserves before appending noexcept unique owners.
The failing batch is destroyed without changing existing object identities.
Only then clear/reinsert the source incidence and assign the same existing patch
edge observers. The source already has capacity for multiple incidences, so
reinserting one pointer cannot allocate; ReplaceCurve only assigns existing slots.

Earlier curves may already have committed when a later curve fails. This is an
ordered prefix guarantee, not a whole-geometry transaction. Retry traverses the
same operation: completed curves/clones have one incidence and are skipped, while
the unchanged failing suffix can complete. Success preserves the original
incidence/null/non-Coons filtering, clone/edge order, dynamic types, sampled values,
parameter direction and orientation. Extra preparation buffers, full pre-commit
incidence-vector copies and batched storage change allocation timing/counts/bytes;
this is explicit resource overhead, not a performance improvement.

The actual operation moves to a narrow production unit; GeneratorAdaptive's
existing private method delegates directly. No option default or numerical code
changes. The test compiles 13 actual production units and uses real PatchBezier
control nets/flags. Original evidence uses 12 verified units plus exact extracted
function bodies with an adapter whose provenance/hash is retained; the full old
generator translation unit is not claimed instrumented. One Hermite destructor
override is required by unchanged lint rules, without a runtime/ABI change.

Qualification: 73 ASan/Debug CRT outcomes, 20 positive-calibration sweeps with
484 denials, both committed-prefix states and successful whole-operation
retry, idempotent success, observer ownership, line/patch analytic checks and
required invalid access/leak/hook controls. Previous instruments and strict model
regression stay required. No tolerance, verifier, budget or scientific policy changes.

Only the new CRT target disables MSVC debug iterator proxies consistently across
all units. The installed STL allocates those proxies inside noexcept vector
construction, so level-2 denial terminates before recovery can be tested. Failed
level-2 results, initial /permissive- compile failure and invalid first fixture
results remain explicit setup history. CRT heap instrumentation remains enabled;
ASan/serial Release layout matches this mode, and prior targets are unchanged.

Full CLI synchronization-disabled execution, whole-process memory, adaptive
rollback, arbitrary custom subclasses/inconsistent sources, duplicate adoption,
other constructors/mutations, shared sample initialization, generic observers,
parallel, LSan and UBSan remain unqualified. The size-overflow guard is reviewed
but not dynamically exercised. Full stage 3 remains open.
