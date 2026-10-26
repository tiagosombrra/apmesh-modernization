# Independent physical-quality report verification

Classification: engineering-only verifier repair. Reference main:
`4772fe9588750c7a5602196618e3b6fef37632ad`. No producer, mesh algorithm, threshold,
floating-point evaluation order or scientific acceptance/stopping policy changes.

## Defect and resulting behavior

The verifier already checks OBJ-derived minimum/mean quality against acceptance
logs, and strict run comparison detects drift against a sound reference. It
does not independently check the CSV's physical-quality values. An actual copy
of retained Book output still passes verification after step 2 is changed to
minimum/mean quality 1, poor percentage 0 and good/excellent percentages 100.
This is a false-metric negative control, not a newly observed generator defect.

After full incidence/source/OBJ validation, the verifier uses the snapshot's
full-precision XYZ face coordinates to recompute 2r/R with scaled stable Heron
arithmetic. It checks `quality_min`, `quality_mean`, `poor_ratio_lt_0_30`,
`q_ge_0_60` and `excellent_ratio_ge_0_80`, for every attempted state, including
rejections. Reports distinguish integer triangle counts from CSV percentages
and expose per-patch poor counts. UV coordinates do not supply physical quality.
Duplicate CSV headers are rejected before values can be silently overwritten.

Six-significant-digit serialization is checked with a separate 1e-10 arithmetic
comparison budget before rounding. This is an observational checker budget,
not a meshing tolerance. If a reconstructed quality lies within that budget
of a classification threshold, verification reports unresolved counts and fails;
it does not reject or modify a generated mesh. Legacy output without incidence
snapshots retains the earlier OBJ/log checks but explicitly reports unavailable
full-precision physical-quality coverage. The strict boundary gate requires
snapshots and includes the stronger physical-quality checks.

## Functional observations

The corrected verifier rejects the original adulterated Book copy. It checks
45 quality fields over all nine retained Eistute/Book states, preserves the
accepted/rejected interpretation, and independently confirms 70 poor physical
triangles at Book patch 0, step 2. The closest reconstructed reference quality
to a threshold is about 9.138e-6 away, so no reference count is ambiguous under
the declared checker budget. Article cases are reused without regenerating
their meshes. Detailed results and input/report identities are retained under
`build/quality-oracle-audit/`.

Ten new analytic/corruption tests cover independent isosceles/right/equilateral
geometry, scale/rotation, XYZ versus UV, counts versus percentages, all five
false fields, serialization, empty/degenerate data, nonfinite/out-of-range data,
missing columns, duplicate JSON and threshold ambiguity. Two further controls
exercise real verifier integration and duplicate CSV headers. Tooling totals
93 tests. The existing analytic nonmanifold/reversed boundary fixture now uses
closed-form physical-quality values in its CSV.

One preparation failure is retained: a negative test initially used the correct
rounded mean 0.509214 as its allegedly incorrect value. Only the corrupted test
value was corrected to the adjacent 0.509215; the checker budget was not widened.

The previous Book direction diagnosis remains a local frozen-state observation
on the same reference: 22,641 native replay evaluations and two unchanged live
traces. A reverse-direction policy experiment remains unapproved and unexecuted.
Neither the diagnostic nor this verifier repair improves the mesh or closes
Stage 3. The subsequent UV extension is recorded below; other statistics remain
separate work.

## Physical repair delivery checks

On the exact review head and merged main: retain 57/57 CTest with zero failures/
skips, 93 Python controls, whitespace/diff and architecture-inventory checks;
repeat the nine-state/45-field retained audit and original-corruption rejection.
Verify all C++/build/scientific inputs and the production executable are unchanged,
and audit remote refs, PRs and configured checks. Full generator rebuild, memory
matrix and article regeneration are unnecessary for this verifier-only change.
Exact revision/report hashes and post-merge observations belong to the PR record.
Unavailable hosted checks are not a hosted validation result.

## UV-quality extension

Classification: engineering-only verifier extension from main
`9a2c928d657e0d2cbfe7adf832f7dc34bdc627e4` (PR #104). An actual copy of retained
Book output passes the old verifier after its ten step-2 UV fields falsely
describe perfect quality. Its physical values, geometry and decisions remain
correct. The new UV checks reject that copy. No incorrect original producer
values are observed in the nine retained Eistute/Book states.

The independent radius-ratio computation uses only each corner's full-precision
UV parameters, following source/OBJ/incidence validation. It checks
`quality_uv_min`, `quality_uv_p05`, `quality_uv_p50`, `quality_uv_p95`,
`quality_uv_max`, `quality_uv_mean`, `quality_uv_std`,
`quality_uv_poor_ratio_lt_0_30`, `quality_uv_q_ge_0_60` and
`quality_uv_excellent_ratio_ge_0_80`. Percentiles interpolate at p*(n-1).
Deviation uses n-1 and is zero for one sample. Count, percentage and coordinate
semantics remain distinct from physical quality. Only CSV comparison/rounding
is shared with the physical checker after checking both sets of field meanings.

The native UV helper returns a zero sentinel at binary64-epsilon perimeter,
area or circumradius guards. These cases lie outside this independent
nondegenerate metric qualification; they fail with an explicit domain diagnostic
rather than reporting successful quality agreement or changing the native
sentinel. Near-threshold classification uses the existing 1e-10 arithmetic
budget and stays unqualified when unresolved. This does not change the AFT
area floor or any generation/acceptance/stopping criterion.

All 90 UV fields across nine retained states agree with the original CSVs.
The 45 physical checks reproduce the PR #104 reports exactly. At Book patch 0,
step 2, 28 triangles have UV q<0.30 while 70 have physical q<0.30. The closest
UV threshold distance is about 1.019e-6, above the checker budget. Detailed
reports, original corrupted output and identities remain under
`build/uv-quality-oracle-audit/`; no article regeneration is needed.

Twelve new UV controls cover analytic mixed distributions, all ten false fields,
sample versus population deviation, interpolated versus nearest-rank percentiles,
single-sample deviation, percentages, nonfinite/range errors, missing columns,
native zero-guard domain, classification ambiguity, rounding and zero coverage.
One actual verifier integration control brings the total Python inventory to
106. Exact head/main require 57/57 CTest with zero failures/skips, these controls,
the 90 UV/45 physical retained checks, original false-report rejection,
whitespace/inventory/diff and protected-input/executable/remote checks. Delivery
revision and report hashes belong to the PR record. No C++/build/configuration
changes, reversed smoothing trials, mesh improvement or stage closure are included.
