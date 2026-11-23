# Literature-supported safeguards for the mixed adaptive cycle

23 November 2026, Fortaleza. Focused review of primary studies on improving
surface TRI/QUAD shape, controlling size gradation and using geometric error
in adaptation. Scope is the live APMesh mixed reconstruction and the
[cap-preserved feedback pilot](MIXED_GEOMETRY_FEEDBACK_PILOT_20261122.md).
The pilot used actual previous mixed error, changed 67 to 88 leaves and
provisionally split eight intervals. It reached the existing UV smoothing,
where a QUAD lost positive convexity. The first invalid pass number and
its preceding mesh were not exported. The case has no accepted mixed
successor.

## Literature and fit

| Primary work | Transferable idea and APMesh fit |
| --- | --- |
| [Canann, Tristano and Staten, constrained Laplacian and optimization-based smoothing (1998)](https://citeseerx.ist.psu.edu/document?doi=83b460eaa8a47fc9d79fe0b2b8af755eda6affea&repid=rep1&type=pdf) | Sections 4.1–4.2 test changes to incident TRI/QUAD distortion and halve a proposed move when it is unacceptable. Add this kind of move guard around the current UV mean, with the original contour fixed. The existing [APMesh design](MIXED_SMOOTHING_SHAPE_DESIGN_20261122.md) supplies explicit local scores and a bounded sequence. Its rules and trial counts are an APMesh proposal. |
| [Garimella, Shashkov and Knupp, local parametrization for triangular and quadrilateral surface mesh quality (2004)](https://cnls.lanl.gov/~shashkov/papers/cmame.pdf) | Reposition vertices in a surface parametrization and evaluate incident neighborhoods in physical geometry. On the APMesh Bézier patch, UV is already available and the source evaluation already maps nodes to XYZ. Sections 3.4 and 4.1 support local iteration and Jacobian-based shape measurement. |
| [Knupp, algebraic mesh quality metrics (2001)](https://doi.org/10.1137/S1064827500371499) and [Gargallo-Peiró, Roca and Sarrate, CAD surface smoothing and untangling](https://dspace.mit.edu/entities/publication/d155ff33-d962-4dde-a233-57cf40cbad94) | Treat validity, shape and size as complementary observations. Positive orientation is a hard requirement. Minimum angle, corner scaled Jacobian and edge proportion reveal different defects. The CAD method combines size and shape distortion in a constrained optimizer. It is a later option if a poor element cannot be improved by the bounded motion, or if the initial candidate is invalid. |
| [Borouchaki, Hecht and Frey, mesh gradation control (1998)](https://www.ljll.fr/~frey/publications/ijnme4398.pdf) | Filter a spatial size field before generation. The typed feedback graph in [PR247](https://github.com/tiagosombrra/apmesh-modernization/pull/247) already connects intervals and faces. Keep physical requests distinct from the discrete curve/leaf lengths the generator can realize. Check nearby generated sizes in both directions and record unmet requests. The pilot's 1.35 factor and three graph passes are project parameters; the literature gives no universal emitted-mesh limit. |
| [Loseille and Alauzet, continuous mesh framework (2011)](https://doi.org/10.1137/090754078) | Separate local error from the size field and control complexity. Keep the existing mixed physical interpolation residual as the pilot's local signal and use a fixed set of UV sites for before/after geometric comparison. The continuous metric/interpolation theory does not supply a convergence guarantee for this mixed pilot. |
| [Cazals and Pouget, osculating jets (2005)](https://doi.org/10.1016/j.cagd.2004.09.004) | Local polynomial fitting provides a basis for the existing typed curvature candidate. Previous coverage and boundary errors remain relevant. Keep this on the curvature qualification track, and keep sampled geometric deviation and curvature error distinct. |

## Checks against existing APMesh evidence

### Size requests are not equivalent to realized splits

The eight contour target fractions of previous physical arc length range
from 0.195 to 0.724. All eight received one binary division. Under the
idealized half-arc calculation, five intervals request less than half
and cannot reach the requested target in one division; the other three
become finer than their target. The largest half-to-target ratio is 2.57.
The 17 face targets range from 0.308 to 0.990 of their starting size.
A one-level tree edit halves UV leaf width but does not imply that
generated physical faces halve their size. These checks point to a
gradation and quantization problem alongside smoothing. They do not
identify the cause of the particular flipped QUAD.

### Damping reduces the change but can still degrade a witness

Re-evaluate fractions of the recorded first whole-pass UV displacement
on two retained, already valid mixed meshes, using the analytic surface
and the original fixed boundary and oriented connectivity. This is a
read-only geometry diagnostic, without a new native pass.

| Archived witness | Before first pass | One eighth of the pass | Full archived first pass |
| --- | ---: | ---: | ---: |
| Step 2 contour QUAD minimum angle | 25.85° | 24.55° | 16.24° |
| Same QUAD, scaled corner Jacobian | 0.42261 | 0.40144 | 0.15809 |
| Two-block Step 3 corner TRI minimum angle | 6.95° | 6.46° | 2.59° |
| Two-block Step 3 sampled source-area-weighted XYZ RMS | 0.011827 | 0.011602 | 0.010147 |

The Step 3 RMS improves while the critical TRI deteriorates. Local shape
checks are warranted alongside any displacement damping. The initial
archive check compared the raw face order and failed. The corrected audit
matches cyclic oriented faces because the two exports order them
differently. The corrected check preserves orientation, exact fixed
boundary and counted topology.

## Recommended sequence for APMesh

1. **Isolate smoothing on the current pilot.** Keep the approved
   predecessor, graph targets, cap, curve splitting, tree edits, templates
   and 1993 advancing-front choices. Export the completed front before
   smoothing and validate it with the complete mixed checks. The control
   stops at the first invalid pass and keeps the last fully validated
   state. If the starting candidate fails, record whether rejection came
   from UV, physical orientation or overlap before considering repair.
2. **Compare a bounded local move guard.** Use the existing mean and source
   evaluation, a fixed contour and full/half/quarter/eighth moves, following
   the earlier design. Require valid incident TRI and QUAD and protect
   physical shape using the per-type angle and distortion measures. Recheck
   each whole pass atomically. Report skipped moves, minimums and tails,
   sampled error on identical sites, and shape/size degradation in unaffected
   regions. Scientific alignment is required for the control and candidate
   selection policies. This experiment has one reconstruction and compares
   two smoothing strategies from the same geometry.
3. **Then improve the adaptive size conversion.** Keep a requested and a
   realized size field with separate face and interval evidence. Assess
   saturation, excessive reduction and local size transitions before
   changing the split policy. Once valid candidates exist, define an aligned
   mixed admission rule including geometric error, shape and complexity,
   preserve rollback and demonstrate two distinct mixed-driven epochs
   under [issue #221](https://github.com/tiagosombrra/apmesh-modernization/issues/221).

## Evidence and scope

The [receipt](evidence/MIXED_ADAPTATION_LITERATURE_20261123.json) binds
the local pilot traces and archived surface calculations. The command was
`python build/quad-literature-20261123/audit.py`. No C++ change,
new native mesh generation, changed scientific policy or new accepted
epoch was produced. Draft PR247 head `d2068628218b51b0bfe485df9b1ca5cb30588676`
now has [four successful hosted checks](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/45080831115)
for the typed adjacency and reference scope. It remains a draft,
separate from the experimental feedback and smoothing proposals.
