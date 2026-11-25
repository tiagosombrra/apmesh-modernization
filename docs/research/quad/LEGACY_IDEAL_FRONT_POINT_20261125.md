# Mixed advancing front with the legacy ideal point

The [draft implementation](https://github.com/tiagosombrra/apmesh-modernization/pull/282)
is `ffdf0b267cd9bbb6b59e3e4bd1397bf7efd79ee9`, with exact source tree `e8c38fbe8e5733e824d97fa4ff749a9a753256d2`.
The paired [contour handoff control](CONTOUR_TEMPLATE_HANDOFF_20261125.md)
is `acb12e6ba97f3cfeecbc0bde7e57102b56932818`. This is a scientific proposal scoped to the native research
successor. Its result blocks adoption.

## Placement and comparison

The native single-patch feedback plan optionally accepts
`ideal_front_points <point_limit> <minimum_angle_degrees> <minimum_shape>`
with a certified predecessor boundary. For a selected TRI with exactly one
original contour vertex and physical quality below the existing profile, the
trial tries a new point if the active front cannot supply a valid TRI that
meets the same floor. The proposal uses the midpoint and inward unit normal
of the directed base, offset by the UV width of the unique leaf on its
unmeshed side. This reuses the geometry-phase formula from the original TRI.
The proposal must be strictly inside the chart, distinct from existing
vertices, off active edges, UV-valid and above the physical floor. The
Bézier surface supplies its XYZ position. Eligible QUADs keep precedence.
The birth trace records the introduced vertex and retains the old search
choice. The contour certification, tree, requests, templates, smoothing
and admission profile are identical between arms.

The physical floors for the insertion test were 15 degrees and TRI shape
0.125. The explicit insertion limits, 50 and 31, were half the respective
control headroom of 101 and 63 faces, rounded down. An insertion may change
the TRI/QUAD mixture, so the original independent face-budget test still
applies. Both native runs staged candidates. The mixed reference used for
admission is the same exact pre-handoff predecessor in both arms.

| Model | Inserted points | Faces, control → trial | Transition TRI below floor | Worst final transition TRI angle | Area-weighted geometric RMS (48 × 48) |
| --- | ---: | ---: | ---: | ---: | ---: |
| CurvaBezier | 2 | 704 → 707 | 37 → 27 | 3.15° → 1.85° | 0.007765 → 0.007882 |
| Ribbed Bracket | 0 | 538 → 538 | 14 → 14 | 8.06° → 8.06° | 0.017874 → 0.017874 |

The four meshes retain 17 and 23 contour segments, respectively. Both
trials satisfy the experimental growth budget and improve geometric error
relative to their own bound mixed predecessors. CurvaBezier increases RMS
by 1.51 percent relative to the handoff control. The frozen profile blocks
both trials on shape. Accepted mixed adaptive epochs remain zero.

Two CurvaBezier births improve from 13.76° to 33.80° and from 8.04° to
35.19°. A later closure involving the second inserted vertex creates a
0.998° TRI at operation 97. Smoothing raises it to 1.846°. An interior TRI
involving the first inserted vertex is 3.242° at birth and 3.417° after
smoothing, versus a 12.074° final interior minimum in the control.
The regression therefore also occurs at birth. Ribbed reproduces the mesh
bytes and every front operation. Its control operation 82 places the
full-offset ideal point on the analytical contour, where this rule refuses
an interior insertion.

A read-only replay on the original histories found a valid point and
individual TRI passing the physical floor at 29 CurvaBezier and 14 Ribbed
operations when offsets of one, one half, one quarter and one eighth leaf
width were considered. The full offset alone covered four and zero.
The Ribbed witness includes operation 81, one operation before the limiting
TRI. This measures geometric feasibility on unchanged front states.
It cannot evaluate downstream closure quality or predict a native result.

## Validation and handoff

- MSVC 19.44 x64 Debug C++17. `cmake --build ... --target ap_mesh
  quad_real_boundary_source_contracts --config Debug --parallel 4` passed.
  Executable and artifact fingerprints are in [the native receipts](evidence/LEGACY_IDEAL_FRONT_POINT_20261125.json).
- Both bound native arms were generated once. The control without the
  option reproduced nine artifacts byte for byte. Independent Python replay
  checked birth point placement, previous available apices, shape, ordered
  contour certificate, native tree and regional quality on both models.
- The original-curve native contracts reported six captures, 54 source
  refusals, six certified splits, six unchanged cases and 24 certificate
  refusals. Ten progressive admission controls passed. Direct article
  application audit passed three stages, rollback and 19 deliberate
  forged witnesses. CTest invocation from the build directory failed to
  find its relative fixture config. The audit passed from the source
  directory. The validation session adapter reported unavailable tools
  and a missing baseline manifest. Full stage validation, native sanitizer
  qualification and independent review remain open.
- The prior [PR 281 checks](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/45688349735)
  passed four jobs. The [PR 282 checks](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/45703420735)
  were in progress at the recorded checkpoint.

Next, align a general trial that compares local front closure with and
without the new point, applying the same rule in both development models.
Use the shorter-offset replay to bound that test. Preserve the successful
births and the downstream regressions as separate evidence. The shared
curve, reserved models, two accepted mixed epochs and global mixed
curvature error remain open.
