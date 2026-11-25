# Compare adjacent bases before mixed front closure

[Draft PR 284](https://github.com/tiagosombrra/apmesh-modernization/pull/284)
at `df57d744e664e9531f8f8834bc71102730eedd81` isolates front order in
the fixed-vertex native research path. It compares the same control and
order-only plans on CurvaBezier and Ribbed Bracket. Both arms start with
the same certified ordered contour, grouped native tree, template faces
and physical vertices. The previous guarded-point candidates are retained
as a separate reference that uses new vertices.

The `guarded_front_order` mode triggers when the original front base would
commit a TRI under the frozen TRI angle or shape floor with one contour
vertex. It previews the active predecessor and successor bases, in that
order, taking the first of each in the existing ordered front. Both use
the same TRI/QUAD selection and prospective shape and geometry controls.
The trial changes only the first committed face. All remaining edges keep
their relative order. The control and alternate previews complete with
further experiments disabled. Cancel identical oriented faces, verify
the same directed patch boundary and require no decline in the minimum
angle or shape by face family and region. A new family or region must
meet its frozen safety floor. At least one comparable minimum must improve
beyond the existing numerical tolerance. The unchanged native validity,
smoothing, face budget and admission checks still apply.

| Model | Alternate bases examined | Completed previews failing the comparison | Incomplete alternatives | Changes selected | Control and trial faces | Worst final transition TRI |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| CurvaBezier | 76 | 70 | 6 | 0 | 704 | 3.15° |
| Ribbed Bracket | 32 | 32 | 0 | 0 | 538 | 8.06° |

The final mesh and pre-smoothing front commits are identical to the
fixed-vertex control in both cases once trial diagnostics are removed
from the history. The area-weighted RMS stays 0.007765 and 0.017874 on
the 48 × 48 grid. TRI of the transition below the floor remain 37 and 14.
Both satisfy the face budget and both remain blocked on quality. This
test covers two adjacent first bases under the declared trigger and
quality gate. It does not enumerate alternative orders.

## Size evidence and next step

In both fixed-vertex controls, the limiting transition TRI uses a short
template edge as its active base and has two much longer connections
toward the contour. The baseline ratios below are longest to shortest
physical edge on the same face.

| Model | Birth operation | Template base length | Longest edge length | Ratio |
| --- | ---: | ---: | ---: | ---: |
| CurvaBezier | 77 | 0.06508 | 0.52846 | 8.12 |
| Ribbed Bracket | 82 | 0.12500 | 0.73075 | 5.85 |

CurvaBezier has no nearby recorded geometry request at this TRI. The
closest logged request is 0.89000 units away in UV. Ribbed has an
actionable 0.49024 physical-size request 0.01334 units away in UV.
These different request histories lead to the same type of edge
disparity. Next, align whether transition size mismatch can originate
a request in the existing graded size field before template dispatch
and closure. Retain the geometric error trigger, common profile and
verified real contour. No mixed adaptive epoch has been accepted.
Shared curves, owner reentry, reserved validation and global mixed
curvature remain open.

## Validation and limitations

- C++17 Debug MSVC 19.44 x64 built the application and native source
  contracts. Both bound order arms ran. The default native plan and
  previous guarded-point plan each reproduced nine artifacts byte for
  byte. Independent audit validated the original bases, ordered
  alternatives, unchanged births and unchanged final meshes.
- Native source and certified-boundary contracts and ten progressive
  controls passed. The direct article application test reached the
  rollback check but failed. Windows denied the rename of the pending
  baseline directory before the intentional rejection ran; the expected
  rollback marker was missing. The first failure was kept and this gate
  remains open on the exact source tree. The scoped test result does not
  establish the cause of the filesystem denial.
- The validation adapter still reports unavailable tools and a missing
  baseline manifest. Full exact-head local validation, native sanitizer
  qualification, and independent approval remain pending. The
  [PR 284 hosted checks](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/45706360614)
  were in progress. The [evidence receipt](evidence/MIXED_FRONT_ORDER_TRIAL_20261125.json)
  includes machine-readable results and hashes.
