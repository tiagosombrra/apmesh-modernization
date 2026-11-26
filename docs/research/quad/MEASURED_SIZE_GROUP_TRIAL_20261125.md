# Measure protected physical sizes after contour-side grouping

[Draft PR 290](https://github.com/tiagosombrra/apmesh-modernization/pull/290)
at `3f2946a5a0176730c7855b05c0eca99295e1ff54` adds one opt-in plan directive for the group
authorized after the [certified child batch](CERTIFIED_CHILD_CURVE_BATCH_20261125.md).
It permits a single contour-side parent with protected size requests to
enter isolated reconstruction. The native check measures the median
physical edge length of every final face that contains each affected
request site in closed UV. A site on a common edge counts both faces.
A missing site or an oversized incident face vetoes staging. Ordinary
groups retain the existing request veto. The three certified child
splits, source fixtures, default TRI path and profile retain their
previous behavior.

## Native Ribbed Bracket result

The group `(0.625, 0.875, 0.75, 1)` affects request 490 at UV
`(0.75, 0.925)`. Its requested size is 0.661824716 model units.
Before grouping, the two incident sizes in the 533-face control are
0.191343707 and 0.500010652. The grouped front initially creates two
incident TRI of size 1.041132014. The final smoothing frame has one
incident TRI of size 1.070023658, about 61.7 percent over the request.
The experiment returns a rejected receipt and retains the prior archive
byte for byte. There is no staged candidate OBJ or front trace.

| Diagnostic | Staged control | Rejected group's isolated frame |
| --- | ---: | ---: |
| Faces | 533 | 523 |
| Minimum final transition TRI angle | 11.968° | 12.787° |
| Transition TRI below a frozen floor | 10 | 8 |
| Area-weighted geometric RMS, 48 × 48 | 0.020352477 | 0.020934666 |
| Maximum geometric deviation, 48 × 48 | 0.107484106 | 0.107484106 |

The provisional mesh replaces the original failing footprint with one
QUAD of physical minimum angle 76.489° and scaled corner Jacobian 0.9633.
The overall transition remains below 15°. The RMS increases by about
2.86 percent on identical analytic samples. The table uses retained
smoothing frames for diagnosis. The rejected group did not reach
progressive admission. Source and boundary certificates remain exact.
Zero mixed adaptive epochs were accepted.

## Separate size and shape at the front

At birth the oversized triangles share the UV edge from (0.75, 0.875)
to (0.75, 1). A read-only conforming split at the request site evaluates
the new node on the original surface and retains its four surrounding
vertices. The four TRI have sizes of about 0.4082 or 0.6351 and minimum
angles of 31.52°, 13.86°, 13.79° and 31.45°. A uniform scan of 255
interior edge positions finds 57 samples at which the sizes of all four
children meet the request; the best sampled worst angle is 13.923°.
The scan offers an observed bound for that sample set. Only a static
two-face footprint was evaluated, without rerunning generation.

Next map requests to the pre-smoothing faces and available front
vertices on both development geometries. Separate an oversized span
with acceptable shape potential from a closure whose limiting angle is
fixed by the surrounding vertices. Check feasible local front
construction with the same physical size, shape and growth criteria
before changing the native generator. Reserved surfaces, shared curves,
mixed owner reentry and global mixed-curvature error remain open.

## Validation and closure

The matching native control reproduces eight output files byte for byte.
A negative control requests 0.01 model units and rejects the
byte-identical provisional frame. The ordinary directive retains its
request veto, and a second marked group is refused. The native
original-curve contracts, 15 progressive controls, six sizing checks and
direct article rollback pass on the measured tree. The direct article
test covers three stages and rejects 11 forged inputs, five forged
smoothing cases and three forged point cases. Its rollback passes on
this tree. The earlier Windows rename failure remains in PR 289's record.

The staged quality check passed for the changed source file and
`git diff --cached --check` passed. The central validation adapter
could not resolve its required tools or baseline manifest on this
workstation. This is scoped C++17 Debug evidence. The full closure
matrix, sanitizers, independent review and hosted final result are
pending. The code remains a draft without integration.
[Hosted run](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/45739394878).
[Commands, hashes and measurements](evidence/MEASURED_SIZE_GROUP_TRIAL_20261125.json).
