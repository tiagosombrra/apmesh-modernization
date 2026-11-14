# P2b — read-only typed QUAD/TRI vertex-link and angle-defect gate

**Date:** 2026-11-14. **Base:** qualified P2a merge PR #218
(\`d40114ed2dc9def294b382557a571e5b62285b83\`).
**Delivery scope:** one controlled, curved, serial application candidate.
**Scientific status:** diagnostic/engineering-only. No mixed adaptive epoch.

## Independent polygon-aware topology

The header \`research/quad/typed_mixed_curvature.h\` contains a
C++17 header-only, read-only diagnostic on face cycles with **three or four
distinct source indices**, with no \`TriangleAdaptive\` reinterpret cast.
It checks real directed physical mesh edges, opposite winding for two-owner
edges, one- or two-sided incidence, and for **every node** a connected
vertex-link graph whose degrees are:

- Interior: every neighbor-link vertex has degree 2, one cycle.
- Boundary: exactly two degree-1 link endpoints, all others degree 2,
  one path.

Disconnected bow-tie fans, repeated face vertices, nonmanifold incidence,
same-direction shared edges, collapsed physical facets, nonfinite positions
and unattached nodes are rejected.

## Curvature witness, not a production estimator

For the read-only diagnostic alone, each physical QUAD retains **one
four-node element**, while the metric is explicitly interpreted as two
physical subtriangles on its local diagonal **0–2**. The per-node barycentric
dual area is the sum of triangle areas divided by three; all incident
subtriangle corner angles contribute to the node angle sum.

For interior nodes, defect = \`2π − Σθ\`; for boundary nodes, turning
defect = \`π − Σθ\`. The density is defect/positive barycentric area.
The total angle-defect sum for the connected disk must agree with
\`2π\` within \`1e−7\`. This is a **triangulated metric witness**,
not an approved intrinsic four-node QUAD Gaussian/mean curvature operator,
not a globally regular Bézier parametrization proof, and not scientifically
equivalent to the legacy TRI estimator.

The positive application audit reuses the validated real 69-node,
42-QUAD/36-TRI, 16-edge source-boundary P1 patch. Five independent
malformations must be refused. The Python regression independently
recomputes the OBJ metric via **side-length cosine law and Heron area**,
not the C++ dot/cross arithmetic. The computation runs before OBJ
publication; a failure cannot leave newly published output.

## Explicit exclusions and next acceptance steps

- Do not modify legacy \`Adjacent\`/\`CurvatureDiscrete\` on this PR;
  it still contains TRI-only three-slot logic. This patch establishes
  the independently testable mixed topology/diagnostic substrate first.
- Do not label the clone or metric probe an adaptive epoch:
  \`adaptive_epochs=0\` remains required.
- No source curve adaptation, alternate point rule, nonmanifold welding,
  production QUAD CLI default, all-QUAD, anisotropy or literal 1993
  reconstruction is claimed.
- P2c must explicitly integrate typed reconstruction, physical quality
  and a scientifically chosen mixed estimator; P2d must demonstrate **two
  distinct accepted mixed adaptive epochs** with rejection/rollback,
  plus unchanged frozen TRI evidence.
- Merge only after exact-head and postmerge GitHub Linux/Windows native,
  sanitizer, TRI scientific baseline, root CTest and Python controls,
  with all independent negative witnesses retained.
