# P2c — four-node physical QUAD quality diagnostic

**Date:** 2026-11-14. **Starting baseline:** P2b merge
\`21ba08e55e014d5c9fa7533c9f7361ad4c98c7dc\`.
**Mode:** default-OFF, serial curved Bézier application case only.

## Exactly what is measured

Every *actual physical*, retained four-node \`QuadrilateralAdaptive\` in the
controlled candidate is inspected before output publication. The metric
probes all four corners using the two directed adjacent **physical XYZ edges**
and the true production \`PatchBezier::Qu/Qv\` source surface normal at that
corner's original UV. Its signed scaled-Jacobian witness is

\[
J_i^{\mathrm{scaled}} =
  \frac{(p_{i+1}-p_i)\times(p_{i-1}-p_i)\;\cdot\; (Q_u\times Q_v)_i}
       {\|p_{i+1}-p_i\|\;\|p_{i-1}-p_i\|\;\|(Q_u\times Q_v)_i\|}.
\]

The smallest of four values is reported for each QUAD and the global
minimum is recorded. It must be positive, finite, and within the natural
cosine bound (with only a floating-point tolerance). The source derivatives
are evaluated at the actual four corner UV sites, **not guessed by planar Z**.

Two additional *diagnostics* are recorded:
- **Diagonal normal cosine:** the angle cosine between the 0–1–2 and
  0–2–3 physical subtriangle normals. Positive is required to exclude a
  flipped metric split; 1 means locally coplanar.
- **Physical edge ratio:** longest of the four exterior QUAD XYZ edges
  divided by the shortest. A finite ratio ≥1 is required, but no research
  optimum or article acceptance cutoff is asserted.

The four-node physical element is never replaced by two TRI. The two
triangles only supply the explicit **diagonal-normal quality witness**,
just as the earlier P2b metric uses a diagnostic triangulation.

## Test isolation and scientific boundaries

- The five original P2b topology/curvature negative controls remain.
- Four additional isolated physical-quality failure cases are tested:
  reversed QUAD winding, duplicate/collapsed corner, reversed source
  normal and nonfinite physical vertex.
- A planar square with source normal (0,0,1) must yield exactly unit
  scaled Jacobian, diagonal cosine and edge ratio.
- A fresh independent Python oracle reads the real application OBJ and
  evaluates the original source Bézier derivative controls to recompute
  the corner metrics, diagonal normals and edge ratios, including the
  retained OBJ after a failed second candidate.
- The first accepted P1 QUAD/TRI geometry, original source sampling
  and frozen TRI default are unchanged. The metrics are read-only.

**Nonclaims:** sampled signed corner scaled Jacobians are **not** a
certificate of a globally positive bilinear Jacobian over each warped
QUAD or continuous Bézier chart; a positive diagonal cosine is not a
CAD curvature bound. The metrics are currently **research observations**,
not an approved mixed-mesh acceptance functional. \`adaptive_epochs=0\`.

## Acceptance before any merge

The exact PR SHA must pass the real Linux/Windows application and native
tests, the new quality oracle, existing mixed curvature and ownership
oracles, Linux ASan/UBSan/leak, 85 CTests + 527 Python baseline and
frozen original TRI Eistute/Book comparisons. Fail closed on a mismatched
metric, and preserve the pre-export rejection boundary.

**Next P2d:** define scientifically reviewed weight/threshold semantics
for curvature, area, scaled Jacobian, distortion and error; then use
actual previous accepted mixed owners to generate **two different**
accepted QUAD/TRI adaptive epochs with retry/rollback. A duplicate
same-connectivity clone, a TRI-only commit or a detached research chart
may not count toward R3/M7.
