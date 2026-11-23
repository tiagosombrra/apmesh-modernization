# Curvature-driven sizing and early mixed-front quality

Recorded 2026-11-23 Fortaleza. A source review and read-only replay
following the researcher's question about adapting the advancing front
to curvature. No new rule is adopted. See the
[receipt](evidence/MIXED_FRONT_CURVATURE_SIZING_20261123.json)
for mesh identities, graph observations and comparisons.

## Source interpretation

The original adapter uses analytical curve and patch curvature in
the adaptation pipeline. The existing triangular advancing front
also has an ideal-vertex construction using the local quadtree
cell height. The mixed article implementation is a contraction
on existing template and contour vertices. It sees UV leaf boxes,
selects a valid local triangle candidate by the angle opposite
the base in UV, and inspects the two quadrilateral alternatives
using the existing UV shape score and S <= 1.5. It does not
directly sample surface curvature in that selection or create a
new vertex to match a requested size during contraction.
Curvature can already reach the mixed mode indirectly through
the native curve/tree source.

Using a physical surface size field and controlling its gradation
before generation is a published approach. See
[Parametric surface meshing](https://onlinelibrary.wiley.com/doi/10.1002/1097-0207%2820000910/20%2949%3A1/2%3C233%3A%3AAID-NME931%3E3.0.CO%3B2-G)
and [Mesh gradation control](https://www.ljll.fr/frey/publications/ijnme4398.pdf).
These sources motivate a common physical sizing concept; their
generators and parameters are not adopted here.

## What the current pilot would target

Reconstruct the actual typed face/edge and ordered contour graph.
Replay the previous mixed geometric-residual samples (four per TRI,
five per QUAD), the highest residual seed per type, their initial
size reduction, and three neighboring passes with the existing 1.35
factor. Validate all 39 recorded updates of the original capped
pilot, including their origins and receiver order. Replay this
same policy as a read-only observation on the two guarded archives.
The Ribbed replay uses archived normalized arcs and independently
integrated analytical total length for each side.

| Case | Worst TRI angle | Its residual rank among TRI (largest first) | Graph distance from nearest residual seed | Initial to requested physical size of that TRI |
| --- | ---: | ---: | ---: | ---: |
| Ribbed Bracket ordinary Step 2, guarded | 3.79 deg | 30 / 60 | 4 | 1.35972 to 1.35972 |
| Built-in Bezier capped successor, guarded | 5.09 deg | 15 / 64 | 7 | 0.24070 to 0.24070 |

The Ribbed triangle touches a straight contour side. The four
analytical Bezier controls of that side are collinear. The two
incident original arcs are approximately 2.0 each. The graph
nevertheless proposes 0.8460 and 1.1421 there from nearer seeds
while leaving the TRI itself unchanged. In the built-in case,
both contour intervals at the worst TRI and its direct face
neighbors receive no reductions. These are requests only; no
reconstruction or improvement is inferred. A residual indicator
and a boundary curvature indicator alone do not capture every
observed bad shape.

## Placement in the research plan

Use curvature to indicate where smaller faces are geometrically
justified, and local size gradation and physical element shape
to identify where the curve-to-template meeting needs attention,
including on a straight segment. First align a local sizing
proposal feeding the original binary curve and native quadtree
before running the existing mixed front. Preserve the original
TRI workflow and mixed UV selection, and measure TRI/QUAD shape
before smoothing as well as on the final mesh, with geometric
deviation and total counts. If a bad pocket survives with
compatible sizes, inspect the available front vertices and
selection before proposing an in-front change. No native tests,
new element generation, scientific adoption, global mixed
curvature or accepted mixed epoch follows from this replay.
