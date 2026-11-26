# Map the remaining transition interfaces and affordable actions

[Draft PR 288](https://github.com/tiagosombrra/apmesh-modernization/pull/288)
at `49bd07ac2a53cf430ce28a6999bc4ad65dd08602` adds a read-only planner
for the [native certified child result](CERTIFIED_CHILD_CURVE_TRIAL_20261125.md).
It checks the bound source TRI, mixed predecessor, original tree,
grouped and ungrouped records, requests and directed curve certificate.
The archived candidate has 533 faces and 24 contour segments. Its
profile permits at most 601 faces. The planner uses the frozen shape
floors and the original contour clearance. No new candidate runs in
this comparison.

## Template actions

All 11 transition TRI below a safety floor meet an exposed template
edge. Eight triangles have immediate supporting parents with protected
requests. Three do not have four eligible original children. Among 33
possible immediate tree parents, ten individual groups and two adjacent
pairs preserve the requested sizes, existing groups and 2:1 balance.
The projected template dispatch in all 12 cases retains the short edge
of every mapped TRI. This measures direct removal of those edges; it
does not prove that other grouping patterns or a different front
history cannot improve them. The legal groups are not sent to a new
native run.

## Curve actions and batch budget

Use the directed contour lineage to identify the two incident spans at
each limiting TRI. At each recorded arc midpoint, calculate the TRI
that would use the same directed seed edge and the new curve point.
Evaluate its physical shape and angle at birth. Preserve the native
1.35 size ratio filter and exclude deeper intervals. A projected
gain requires a better angle and no loss in TRI shape. The same curve
point can have a different effect on a neighboring TRI.

| Candidate action | Projected improved birth operations | Selected angle changes | Maximum projected faces |
| --- | --- | --- | ---: |
| Upper child 8/1 | 51, 53 | 10.031° → 11.955°, 8.063° → 13.248° | 558 |
| Lower child 2/1 | 68 | 11.962° → 13.262° | 558 |
| Upper child 9/0 | 47 | 12.962° → 13.546° | 558 |
| Upper 8/1 and lower 2/1 | 51, 53, 68 | As above on the fixed bases | 559 |
| All three children | 47, 51, 53, 68 | As above on the fixed bases | 560 |

For each proposed batch, omit the affected clearance constraints
while projecting the maximum seed sites and retain the existing
seed-QUAD minimum. This reuses the conservative disk face bound
proved in the budgeted action trial. None of the projected gains
reaches the 15° TRI floor. Upper child 8/1 improves the current
limiting base but produces a projected 10.003° triangle on another
base with an existing 11.968° triangle. A native comparison must
measure all affected TRI, QUAD and geometric errors.

The exact plan already has `curve_child 8 0`. Its native parser only
supports one child request total. No batch in the table is representable
while preserving that first certified point. Replacing the recorded
request would change the matched control. The proposed next native
comparison would add 8/1 and 2/1 with an amended certificate, preserving
all 24 contour samples and IDs. Replay the current child split before
assigning the two new IDs. This scope waits for alignment. No change
to protected rules, safety floors, growth or TRI is proposed.

## Validation

- The CLI mapped the 11 TRI twice with byte-identical outputs.
  It refused a foreign ungrouped archive and the unsupported v1
  contour archive without publishing a projection for either.
- Thirteen progressive admission and six sizing controls pass locally.
  No C++ source changed, and no new native build, generation or
  sanitizer qualification was attempted in this work item.
- The [PR 287 hosted run](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/45732790527)
  passed. The [PR 288 hosted run](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/45736951313)
  was in progress. [Evidence](evidence/TRANSITION_INTERFACE_MAP_20261125.json)
  records the map and the input, profile and output hashes.
- The combined native comparison, two accepted mixed epochs, global
  mixed-curvature error, shared curves and reserved models remain open.
