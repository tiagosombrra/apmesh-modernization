> Historical report. STAGE1_ORIENTATION_REPAIR.md records subsequent repairs,
> passing gates and the current closure candidate. Failures below are retained
> as observations of their stated revision.

# Stage 1: incidence export and independent closure audit

Date: 2026-10-16 UTC (2026-10-15 Fortaleza).
Base: `32719960353d8695eb53b3d58d25d76c7ba9b0cb`; issue #2, draft PR #3.
**Stage closure and integration remain blocked.** This delivery adds observers
and independent checks; it does not repair the newly exposed geometry/report
defects or change the scientific algorithm.

## Implemented

Every serial SaveMesh now writes a separate `*_passo_N_incidences.json` before
later adaptation/rollback can change the observed state. It preserves all patch
indices, four runtime curve identities per patch, 16 original-order control
points, every owned node and every actual triangle corner with local UV and
physical XYZ at 17 significant digits. No inverse mapping or geometry evaluator
is invoked by the observer. The existing OBJ/CSV/acceptance writers are unchanged.

The Python checker independently reads the BP source, reconstructs expected
boundary groups from exact four-control-point tuples (including reversal), and
checks every patch against that source. It derives boundary chains from actual
triangle edge incidences, checks complete connected [0,1] partitions, then
compares every shared sheet's partition and coordinates. It also checks runtime
curve grouping, node/face consistency and exact connectivity/order against the
actual OBJ. It uses De Casteljau instead of the application's power-basis path.

The runner records the input model hash. Any present snapshot must cover exactly
all attempted stages and match the executed model identity. Missing/contradictory
evidence fails; rejected candidates remain rejected. Legacy data can still be
inspected without incidence certification. When both runs have snapshots, strict
regression compares their complete reports and snapshot hashes exactly. A legacy
reference is explicitly reported as lacking incidence regression coverage.

## Measured article cases

| Case | Attempted states checked | Incidences per state | Shared sheets | Independent comparisons per state |
|---|---:|---:|---:|---:|
| Eistute | 5 | 16 | 4 on one non-manifold curve | 3 |
| Book | 4 | 112 | 28 on one non-manifold curve | 27 |

All nine states pass the incidence checker, including rejected candidates.
Maximum shared-position gap is zero in these runs. Candidate repetition is exact
for OBJ, CSV, acceptance fields and all snapshots. Before/after comparison against
the previous candidate preserves every OBJ and decision/metric field exactly.
Last accepted stage remains 1: Eistute 1,168 triangles; Book 4,418.

These cases have no mixed shared-curve orientations; canonical normalization of
an exterior side is not evidence of mixed orientation support. The checker has
analytic positive controls with mixed orientations and with the reversed sheet
as its reference. Actual executable controls expose the separate defect below.

The declared comparison budgets are `4 * epsilon` for a single parameter
complement round trip and `512 * epsilon * max(1, absolute control coordinate)`
per coordinate for independent evaluator roundoff. They apply only to the new
geometric cross-check, not to strict repetition, historical report comparison,
mesh tolerances or acceptance thresholds. They are explicit conservative budgets
for the qualified fixtures/cases, not a universal numerical proof. No proximity
budget is used to create source curve identity or match control points.

## Required failure 1: actual reversed incidence

Four independently specified analytic controls are run through the executable:
aligned/reversed manifold pairs and aligned/reversed three-sheet non-manifold
junctions. Both aligned cases pass. Both reversed cases return process success
and an accepted stage 0, but contain degenerate physical triangles.

The snapshot additionally shows one changed control net, off-source boundary
positions and a shared-endpoint gap of **1 unit**. The 17-digit input control net
is compared directly; this is not an export-rounding discrepancy.

The unchanged previous executable reproduces the same invalid reversed OBJ
bytes on identical input bytes. The observer did not introduce the defect.
Source inspection points to `Geometry::VerifyCurveGeometry`, which accepts
reversed controls, followed by `PatchReader::ReaderFilePatches` and the
curve-based PatchBezier constructor, which consumes the reused curve's stored
direction. The adapter also assumes stored curve direction when mapping points
to local UV. These findings define the next repair scope; do not claim that
changing the constructor alone qualifies adaptive/retry/rollback behavior.

`application.boundary_orientation` is a required CTest that currently fails.
It is neither skipped nor marked WILL_FAIL. The analytic checker-positive
fixtures do not substitute for passing real generation. Minimal failing BP,
OBJ and snapshot artifacts are retained under `stage1/incidences/`.

## Required failure 2: CSV header/value alignment

Independent audit of 21 control fields against their named per-stage analysis
log exposes shifted CSV labels. For example, Eistute stage 0 reports
`actual_elements_step=1` in CSV versus `16` in its named analysis log, and
`top_patch_candidate_count=initial` versus `0`. Equal row/header lengths do not
detect this failure. Source inspection shows adaptation_relaxation positioned
earlier in the header than its emitted value; intermediate control columns are
therefore assigned the wrong labels.

The defect also occurs in the previous executable's retained Eistute output.
Strict before/after equality preserves this pre-existing defect; it does not
establish correct report semantics. `tools/audit_metric_schema.py` checks named
values without a numerical tolerance. Its positive, shifted-header and missing
field controls pass. Required CTest `application.metric_schema` fails on a real
aligned two-patch run, with nine mismatched fields even though geometry passes.
The CSV writer and oracle have not been changed to conceal the discrepancy.

## Audit and regression results

- Native Windows UCRT64 GCC 16.1.0, C++17 serial Release, MPI/OpenMP/LTO OFF.
- Build PASS. New exporter/header clang-format PASS.
- 65 Python controls PASS: the former 38, 24 incidence controls and three schema
  audit controls. The 23 executable invalid-input controls still pass.
- Full CTest: **5 passed, 2 failed, 0 skipped**. The failures are the required
  reversed-generation and CSV-schema checks above. This is not a passing suite.
- Exact article repetition and previous-candidate comparisons PASS, with the
  semantic/geometry limitations above explicitly retained.
- Full selected exporter clang-tidy FAIL: 18 diagnostics in existing included
  legacy/Eigen headers; none attributed to new exporter lines. Configuration and
  checks were not weakened, vendor code was not edited and suppressions were not
  added. The failure log is retained; no full lint-clean claim is made.
- No ownership, sanitizer, parallel-mode, C++23, Eigen-removal or performance
  qualification is implied. Decor Shelf remains outside this campaign.

Exact source, input and executable identities, comparison results, failing
controls and logs are in `stage1/incidences/validation_manifest.json` and adjacent
reports. Large article snapshots/raw campaign outputs stay local; their hashes
are retained. All failures are kept as evidence.

## Reproduction and continuation

```sh
cmake --build --preset local-serial
ctest --preset local-serial --output-on-failure
python tools/repeat_generation.py --exe build/local-serial/bin/ap_mesh --model eistute --output build/incidence-eistute-new --report eistute-repeat.json
python tools/verify_generation.py build/incidence-eistute-new/repetition-1 --require-boundary-coverage --report eistute-boundaries.json
python tools/audit_metric_schema.py build/incidence-eistute-new/repetition-1 --report metric-audit.json
```

Use `.exe` on Windows and fresh output directories. The repeatability check is
not a replacement for the required semantic-schema audit. Run Book in the same
way. CTest retains complete control outputs in its build workspaces.

Next: repair direction handling throughout control-net construction and
boundary-to-UV mapping, with real aligned/reversed and non-manifold adaptive
controls; repair CSV serialization and qualify its header/row contract. Preserve
the historical failing results and classify behavior/output changes explicitly.
Then repeat the closure audit and all required regressions on the same head.
Keep issue #2 open, PR #3 draft and main unchanged; stages 2-11 have not begun.
