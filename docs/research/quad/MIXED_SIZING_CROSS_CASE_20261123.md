# Cross-case mixed sizing and transition conditions

Recorded 2026-11-23 Fortaleza. Scope is one native cross-case replay
using the already retained isolated MSVC Debug C++17 pilot binary,
read-only comparison of archived shared curves, and an unexecuted
sizing proposal. See the [receipt](evidence/MIXED_SIZING_CROSS_CASE_20261123.json)
for exact artifacts, commands and numeric observations.

## Second surface and native comparison

Screen actual indexed Bezier source patches with an 8x8 grid. The
screen uses the largest angle between analytic normals on the four
edges of each grid cell. This describes variation in normal direction,
with no role in the generator. Patch 12 (zero-based) of
Ribbed Bracket varies from 2.12 to 15.67 degrees in this measurement.
Its single-patch input preserves all 16 original control points and
their order. Only the input and output paths differ from the retained
fixed-1.5 pilot configuration.

The executable exits with Windows code 4294967295 (native signed -1)
in 1.93 s under 180 s. The retained prefix contains ordinary TRI and
mixed Step 1, plus TRI Step 2. During ordinary mixed Step 2, UV QUAD
483 inverts or collapses in smoothing. The protected comparison of the
earlier pilot was called only *after* a valid ordinary mixed Step 2;
this attempt never reached it. There is no published mixed Step 2 or
Ribbed feedback candidate. Retain the prefix and avoid retrying under
different parameters.

| Case, Step 1 | Worst TRI angle, TRI to mixed | Worst QUAD angle | Maximum adjacent face size ratio, TRI to mixed | Area-weighted XYZ RMS, TRI to mixed |
| --- | ---: | ---: | ---: | ---: |
| Built-in curved Bezier | 29.76 to 37.62 deg | 31.55 deg | 1.65 to 2.70 | 0.02649 to 0.02217 |
| Ribbed Bracket patch 12 | 21.61 to 20.22 deg | 27.75 deg | 1.57 to 2.83 | 0.11573 to 0.09941 |

Each comparison uses 576 common sites on its own analytic surface.
RMS values use that model's physical units. Both Step 1 comparisons
are 17 nodes and 24 TRI versus 33 nodes and 24 QUAD plus 8 TRI, with
eight original contour segments. Lower geometric deviation can
coexist with poorer shape or larger size jumps.

## Shared boundary measurements

Verify the four archived M4 two-patch controls, including two reversed
charts. Each has one seam with four matching edges, five physical
sites and opposite winding. A one-sided coordinate mutation is
rejected in each. Their physically symmetric faces produce an
across-curve size ratio of 1 within floating-point tolerance.

The actual Ribbed Bracket M4 archive adds an asymmetric measurement.
The production curve incidence agrees with the independently parsed
control nets. On 17 curves with exactly two incident patches, all
68 archived seam intervals agree in physical location and have opposite
winding. The largest adjacent face size ratio is 5.84, even though
those owners already share the same curve partition. Its face sizes
are 2.02427 and 0.34664 on the seam between patch 2 side 2 and patch 8
side 0. Both are physical median edge lengths. Accordingly, curve
synchronization and the grading from incident faces on both sides
must be evaluated. The M4 templates and Lawson exterior form a
different archive; it supplies a seam control and no native mixed
adaptation claim. The two shared curves incident on patch 12 each
have three owners and remain outside this paired control. The live
experimental entry currently requires exactly one Bezier patch.

## Sizing proposal and work order

Keep requested physical size, discrete native actions and realized
face sizes distinguishable. The ideal equal-arc calculation on the
previous ten baseline intervals estimates depths 0 through 3 and
32 contour segments for meeting every recorded request. The capped
pilot produced 18. This is an illustrative cost comparison, with no
binary policy, higher cap or new node budget adopted. Refine only
regions where the combined error and shape evidence justifies it.
Validate TRI and QUAD angles and shape separately, physical size
ratios on both sides of the contour, a common-site geometric error
and growth. Report missed sizes and each active resource limit.
Keep the original binary curve splitter, native quadtree balance,
templates, advancing front and default TRI workflow.

First obtain alignment for one Ribbed ordinary Step 2 comparison
starting at the validated pre-smoothing mesh. Use the original
last-valid pass as control and the already tested five-pass protected
motion as experimental arm. Retain the original failure. If the
protected arm produces a valid Step 2, its topology, errors and
sizes are a new named source for feedback; measure them before
trying a numerical choice for the size conversion. A later
controlled multi-patch candidate must represent one shared curve
partition and both patch sides; the current M4 archive supplies
a counterexample to relying on conformance alone. No new sizing
policy, native shared-curve adaptive output, mixed-global curvature
error or accepted mixed epoch is established here.
