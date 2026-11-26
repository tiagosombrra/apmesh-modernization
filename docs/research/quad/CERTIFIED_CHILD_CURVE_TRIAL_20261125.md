# Certify one native subdivision of a previously split contour segment

[Draft PR 287](https://github.com/tiagosombrra/apmesh-modernization/pull/287)
at `ab7b2e60aef01f48323bd38892fdbedc7071dcb3` adds a bounded experimental
request to the single-patch feedback plan. `curve_child <interval> <child>`
requires exactly one matching original split and boundary certification.
Child 0 denotes the half from the original start to the first inserted
point in directed contour order. Child 1 denotes the other half.
Only one child request may be added to the plan.

The original binary subdivision and certificate produce the intermediate
contour. The same subdivision and certificate then produce the final
contour, preserving all intermediate sites, including their XYZ,
parameters, order and owner IDs. The new ID exceeds every previous
mesh and contour ID. The native certificate v2 records both steps.
The Python checker reconstructs both ordered contours independently,
checks the recorded original and child requests, and verifies the
original-curve samples against the complete output. Plans using only
original intervals keep the v1 format and exact archived results.

## Bound Ribbed Bracket result

Use the 534-face output of the
[budgeted transition action trial](BUDGETED_TRANSITION_ACTION_20261125.md)
as the matched control. Both arms keep the same original TRI, mixed
predecessor, native requests and grouped quadtree. Add only
`curve_child 8 0`. The native top-edge point is UV (0.875, 1). It divides
the previously certified child into arcs of 0.49999992 and 0.49999999
model units. All 23 control contour points remain in the same order
and with the same IDs and geometry. The original nine first-pass
certificate witnesses also match the control. The child ID is 560,
between the previous directed sites 29 and 558.

| Measurement | Control | Certified child split |
| --- | ---: | ---: |
| Contour segments | 23 | 24 |
| Final faces | 534 | 533 |
| Worst TRI in the original limiting footprint | 8.056° | 13.194° |
| Worst TRI in the complete transition | 8.056° | 8.063° |
| Transition TRI below the frozen floors | 12 | 11 |
| Area-weighted geometric RMS on 48 × 48 sites | 0.020301269 | 0.020301368 |
| Maximum geometric deviation on 48 × 48 sites | 0.107484106 | 0.107484106 |

The original limiting triangle is absent at birth. A different TRI
that already existed in the control becomes the limiting one. Both
stages are measured on the same grids. Native faces fit the projected
upper bound of 557 and the profile maximum of 601. Shape still blocks
admission. This is one native development-model experiment. The
physical 15° threshold and the profile remain unchanged. Zero mixed
adaptive epochs were accepted.

Eleven remaining sub-floor transition TRI meet an exposed seed
template edge. Ten have exactly the same UV vertices at birth as a
sub-floor TRI in the control. The new limiting triangle is born at
operation 53 at UV (0.625, 0.9375), (0.65625, 0.9375) and (0.75, 1).
Next map the remaining template edges to eligible certified boundary
and protected template requests, and project a common face budget
before proposing a combined native plan. Native owner reentry, shared
curves, reserved cases and global mixed-curvature error remain open.

## Validation and closure

- MSVC 19.44 x64 C++17 Debug built `ap_mesh` and
  `quad_real_boundary_source_contracts` in the existing native profile.
  Original-curve contracts retained six captures, 54 source refusals,
  six certified splits, six unchanged witnesses and 24 certificate refusals.
- The exact executable generated the child candidate and a v1 control
  that reproduced eight artifacts byte for byte. Four invalid native
  requests were refused before candidate publication: invalid child,
  repeated child request, missing parent split and missing certification.
- Thirteen progressive tests and six sizing tests pass. The direct
  article application audit passes three stages and verifies rollback
  with 19 deliberately forged witnesses rejected. This exact revision's
  control passes the check that previously encountered a Windows
  rename error. The prior failed invocation remains recorded.
- The validation-session adapter still lacks the configured tools and
  baseline manifest. The full local stage, sanitizer qualification and
  independent reviews remain pending. The [PR 286 hosted run](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/45709796800)
  passed. The [PR 287 hosted run](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/45732790527)
  was in progress. [Evidence](evidence/CERTIFIED_CHILD_CURVE_TRIAL_20261125.json)
  includes both certificate stages, trial hashes and quality receipts.
