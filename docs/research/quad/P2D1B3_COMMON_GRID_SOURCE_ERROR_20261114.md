# P2d-1b3 — independent common-site Bernstein source-error gate

Date: 2026-11-14. Base: qualified P2d-1b2 [PR229](https://github.com/tiagosombrra/apmesh-modernization/pull/229),
single original curved `ModelCurvaBezier` physical P1 and complete
connected-band candidate. Scientific R3/M7 remains open: [issue #221](https://github.com/tiagosombrra/apmesh-modernization/issues/221).

## Why this is necessary

P2d-1b2's genuine physical original-AFT reconstruction changes
42 QUAD/36 TRI into 62 QUAD/44 TRI, and the original
four-/five-point-per-face source error probe consequently changes
from 354 to 486 sampling sites. Although the sampled max and RMS
both decrease, **those two different finite sampling populations
are not a valid same-site comparison of continuous error**.

This gate uses an exact *common set of 4096 interior parametric
sites* `((i+0.5)/64, (j+0.5)/64)`, with `i,j=0..63`, on both
actual source-OBJ surfaces. It implements independent element
lookup and physical interpolation **in Python only**:

- TRI uses the exact source-UV barycentric linear interpolant.
- QUAD keeps four real physical vertices and uses Newton inversion
  of the genuine UV bilinear map; it is never silently split into TRI.
- Original target XYZ and derivatives are calculated from the
  separate versioned original sixteen-point Bezier Bernstein
  control-net oracle, not from the C++ adaptive geometry routines.
- `L2_UV_samples` is the RMS error over the same 4096 UV
  points. `L2_source_area_samples` weights each squared XYZ
  error by `||Q_u × Q_v||` at the same sites, divided by the
  sum of those physical-area weights. `Linf_samples` is the
  maximum over the same sites. These are numerical discrete
  quadrature measurements, **not** analytical integrals or
  strict supremum error bounds.

The independent reference prototype (Shapely locator) and the
pure-Python implementation agree at all three baseline numerical
metrics and both face populations:

| Same-domain metric | Original P1 physical | Band physical candidate | Relative decrease |
| --- | ---: | ---: | ---: |
| 64×64 maximum XYZ error | 0.06564122093 | 0.05160741346 | 21.38% |
| 64×64 uniform UV RMS | 0.01729520385 | 0.01251800084 | 27.62% |
| 64×64 source Jacobian-weighted RMS | 0.01598126566 | 0.01181032464 | 26.10% |
| QUAD sample locations | 1024 | 1344 | +320 sites |
| TRI/AFT sample locations | 3072 | 2752 | -320 sites |

The exact research-first model must retain these values within
explicit narrow numerical tolerances on Linux and Windows.
This criterion is **a benchmark regression**, not a universal
parameter tuning rule or an approved scientific adaptive acceptance
threshold. Physical QUAD split-normal cosine can become worse even
when source error falls; compare multiple quality objectives.

## Scope/risks

The report is attached to original `report.json` from the
opt-in controlled real CLI; all new fixed-grid evaluations must
use separate source OBJ files and must not mutate accepted
objects or publish a new epoch. No source `AdaptCurve`,
original 1993 Delaunay+contraction, real coupled multi-patch
nonmanifold welding, anisotropy, all-QUAD, or general
mesh-convergence claim is supported. **`adaptive_epochs=0`**.

Required CI: exact-source GCC/Windows MSVC real app and
native contracts, independent original Bezier source, Linux
ASan/UBSan/leak, 85 baseline CTests/527 tooling Python,
frozen Eistute/Book TRI equivalence. R3/M7 remain OPEN.
