# Reproduce the rejected ideal-point closures at the transition

The [size-driven point trial](SIZE_DRIVEN_IDEAL_POINT_20261126.md)
retains one locally successful Ribbed point. The worst remaining
TRI in both models occurs outside the physical size request sites.
This diagnosis binds the legacy CurvaBezier and Ribbed closure
snapshots and the Ribbed snapshot retaining the successful point
to the archived inputs at `4f29dd06b087f4fb0fb299924d39f825ae2ccb96`.

The standalone MSVC Debug executable uses the native article front
and QUAD residual screen. A temporary header copy exposes internal
replay state and reverses byte for byte to the original. The stored
active directed fronts and choice sequence match the archived suffix
for all three late states: 16 CurvaBezier and one face for each
Ribbed history. The Bernstein net is bound to each source and the
physical shape evaluation is independently reconstructed. The checked
local comparisons use the same floors and prior regional minima as
the legacy guard on faces that actually change.

| Model and placement | First proposed TRI | First failed face | What fails |
| --- | ---: | --- | --- |
| CurvaBezier, quarter leaf width | 40.11° | Interior TRI, operation 87 | 6.14° against 15° |
| CurvaBezier, eighth leaf width | 22.93° | Interior TRI, operation 86 | 7.96° against 15° |
| Ribbed, quarter leaf width | 51.17° | Contour-vertex TRI, next face | 0.84° against 11.91° |
| Ribbed, eighth leaf width | 45.96° | Contour-vertex TRI, next face | 3.30° against 11.91° |

The Ribbed table applies to the original shape-driven history and
the trial retaining the size-driven point. The old last face is a
single triangle in both histories. A quarter-width placement
produces three TRI and the first thin neighbor has a shape score of
0.02360 against 0.34815. In the quarter-width CurvaBezier closure,
a later contour-vertex TRI also falls to 1.03° against the
corresponding 2.53° reference minimum at birth.

## Earlier closure options and the interface

The six-edge CurvaBezier cycle is formed at operation 81 and has
one conforming fixed-site TRI/QUAD closure under the article shape
rule. The Ribbed size-driven history has a five-edge cycle formed
at operation 64. Four fixed-site closures are possible. None of the
closures for either cycle meets the physical shape floors. For
Ribbed the last QUAD of that cycle leaves the three-edge region
seen by the failing point. Fixed-site enumeration also widens
the two cycles by up to two adjacent front-generated faces.
Twelve CurvaBezier and 103 Ribbed layouts fit the tested domains.
None meets the physical size requests and shape checks together.

Replaying one alternate base at the first failed face in each
continuation gives 67 completed closures and zero local guard
passes. The 87 verified base changes at earlier snapshots retain
the same face sets. At the two commits that form the tested
cycles, the existing ideal offsets on the selected bases give
seven measurable closures and no shape pass. Another 28 positions
on the neighboring active bases give 26 measurable closures
and no shape pass. These tests isolate the current vertex and
interface constraints; they only cover the specified alternatives.

## Verification and next action

The early legacy Ribbed replay from operation 7 diverges in the
additional-pair selection at operation 55 even with the same
recorded active boundary. Exclude that replay from the validated
prefixes. The MSVC diagnostic initially needed an explicit standard
string include in its local harness. The bound late and earlier
checks reported here use the corrected build. The project source,
TRI path and numerical policies retain their measured revision.
This work did not generate a full native successor or admit a
mixed adaptive epoch. The primary local validation adapter lacked
tools and its local baseline. [Exact PR 292 checks](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/45790071630)
remained in progress at this checkpoint.

Alignment requested for a projected cavity that includes up to
one layer of neighboring template QUAD. Keep the original analytic
contour, the exterior patch boundary and all size requests. Compare
both full size and shape checks and the frozen face growth budget
before proposing any native reconstruction change. Shared curves,
owner reentry, reserved cases and the global mixed-curvature
norm remain pending.
[Replays, hashes and alternative outcomes](evidence/MIXED_CLOSURE_REFUSAL_REPLAY_20261126.json).
