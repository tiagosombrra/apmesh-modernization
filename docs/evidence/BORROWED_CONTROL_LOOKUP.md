# Borrowed control-point lookup

Entry main: `ee677a34fd9c9303eb83b70d525c6b966c6a240f` (PR #170).
Classification: engineering-only removal of redundant internal vector copies,
P4 / S3-05 and C23/C27. No meshing formula, ordering or policy change is admitted.

## Concrete change and preserved contract

The shared control reader calls the public by-value point lookup sixteen times
per valid patch. Each call copies the entire control collection even though it
only scans IDs and returns one point by value. PointAdaptive's implicit copy has
no user callback or allocation; removing the container copies changes resource
cost rather than selection or scalar evaluation.

Introduce a private static FindControlPoint taking a const vector reference.
Keep the original ordered first-ID-match scan and default point on a miss; return
an independent PointAdaptive value. All sixteen internal control assignments use
the borrowed helper while the local parsed vector remains alive. No element
reference escapes, no index cache is introduced and duplicate IDs retain their
first-match behavior. The public GetPointVectorControlPoints signature remains
by value and delegates to the same scan, preserving its compatibility boundary,
including callers that supply an rvalue vector.

## Finite qualification

Freeze the qualified entry binaries, source and existing allocation counts before
editing. Expand the private lookup back into the original public body, permitting
only the const-reference/const-iterator change, the public compatibility delegate
and the sixteen internal call replacements. Retain the shared-reader and original
serial ownership guards; challenge reference constness, selection/default return,
public signature and complete internal call coverage with actual mutations.

Native controls require the exact public member type, duplicate/absent/empty ID
queries, scalar bits, source preservation and independent returned values. Reuse
unchanged reader/charge fixtures and 120 nonempty native trace pairs across GCC,
MSVC CRT/ASan and the actual GCC numerical estimator. Recalibrate every affected
allocation ordinal and require complete 131 serial / 189 charge memory outcomes;
the old denial counts are reference costs, not candidate coverage. Keep existing
profiles, timeouts, expected negatives, live prefixes and retention assertions.

Require canonical C++17 GCC/MSVC builds, the complete existing regression on final
head and main, scoped read-only analysis, explicit format, contracts/inventory,
fresh remote review and the same nine-state Eistute/Book reference. Reuse runtime
evidence only by verified source/build/input/oracle identities; preserve failures
and qualify changed artifacts directly. Do not claim an end-to-end speedup or
close a Stage 3 row from a bounded allocation reduction.

One active implementation item. Local evidence is under
build/borrowed-control-lookup; its separate integration seal is required for
closure. Broader loader/domain, cache/mutation, recovery, whole-process instrument,
writer-failure and parallel obligations retain their existing scope.

## Candidate measurements

The public member type is unchanged. Native duplicate/later/missing/empty queries
preserve first match, exact scalar bits, the old default point and source/result
independence on GCC and the existing MSVC CRT/ASan profiles. The new lookup guard
rejects nine mutations while the original eight shared-reader and six historical
ownership mutations continue to reject their prior changes.

All 320 expected memory outcomes pass, including deliberate real UAF/leak/hook
controls. The candidate completes sixteen serial sweeps / 2,219 actual denials
and twenty charge sweeps / 2,147 denials. Separate entry calibration uses the
same fixture paths: serial costs drop 2,731 -> 2,219 and charge costs 2,787 -> 2,147.
Every operation saves exactly sixteen vector allocations per parsed patch;
the four one/three-patch fixture families save 1,152 allocations across the fixed
calibration inventory. Entry charge first chunks establish counts only; candidate
sweeps supply complete fault coverage. No old ordinal is credited to changed code.

All 120 original/candidate native pairs pass: eight serial scenarios on each of
GCC, MSVC CRT and MSVC ASan; 24 charge scenarios on controlled GCC, actual-numerical
GCC, MSVC CRT and MSVC ASan. Controls, IDs, ordered curve incidence/direction,
evaluated bits, stable order and positive writer bytes remain identical. The
iteration passes 75 CTest / 485 Python without skips/failures; actual-unit
read-only analysis passes. Existing static-Debug-CRT iterator-zero and ASan
RelWithDebInfo scope remains; these are not whole-process instrument results.

The [compact record](stage3/borrowed_control_lookup/summary.json) and local reports
bind source, input, compiler/profile, executable, oracle and raw logs. Final
article comparisons and exact-head/main verification are recorded separately;
only the local delivery integration seal closes this bounded package. All ten
Stage 3 dispositions and wider caller/domain/mutation/recovery/instrument/parallel
obligations remain unchanged.

The canonical GCC and checked-MSVC executables each preserve the nine-state
Eistute/Book reference: 45 exact scientific artifacts and 123 positive independent
boundary comparisons per ABI, including accepted/rejected decisions and exact
mesh bytes. These measurements establish correspondence for the named cases;
they are not a new model, recovery, parallel or end-to-end timing qualification.
