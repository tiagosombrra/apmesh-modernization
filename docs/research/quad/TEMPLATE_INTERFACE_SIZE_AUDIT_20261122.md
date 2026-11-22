# Template interface size audit with the original curve fixed

22 November 2026, Fortaleza. The researcher chooses to retain the native
curve partition and investigate template sizes. The
[one-split curve proposal](LOCAL_CONTOUR_SPACING_TRIAL_DESIGN_20261120.md)
is closed without an implementation or a native run. This audit uses the
same MSVC fixed-`1.5` `curva_bezier` archive as the
[negative front-order result](MIXED_TRANSITION_SHAPE_20261120.md).

## Where the short edges come from

The three small exposed sides of the Step 3 pocket are original T1 template
edges, from the archived leaf ordinals 111 and 114 (zero based in `front.json`).
The first leaf spans `[0.125, 0.1875] x [0.125, 0.1875]` in UV. The relevant
intermediate polygon keeps the whole left side, from `v=0.125` to
`v=0.1875`. The existing corner/midpoint/centroid QUAD subdivision halves
that side. The specific edge `[13, 349]` is the resulting 0.03125 UV edge,
0.04731 in physical space. No fine-neighbor split on that T1 side is
needed to explain it. The quadtree has already selected a width of 0.0625
before the QUAD template is emitted.

The neighboring leaf 89 starts at `u=0.0625`. It is excluded by the
approved contour clearance: its distance 0.0625 is smaller than one
fifth of the unchanged 0.5-unit UV contour segment. The selected template
edge remains at `u=0.125`. The mixed front then connects `[13, 349]` to
the original straight-side midpoint `(0, 0.5)`. The two physical links
have lengths 0.714 and 0.670, yielding the 1.42-degree TRI. The tree scale,
standard template subdivision, clearance and final front connection
each have an observable role.

| Retained stage | Native leaves | Exposed seed edges | Median exposed length, UV | Median exposed length, XYZ |
| --- | ---: | ---: | ---: | ---: |
| Step 1 | 16 | 16 | 0.125 | 0.26381 |
| Step 2 | 67 | 56 | 0.0625 | 0.12579 |
| Step 3 | 223 | 100 | 0.03125 | 0.06545 |

The archive replay attributes every exposed edge to exactly one
intermediate polygon half-side, matches seed centers with the independent
area-centroid oracle and checks the existing clearance counts. The original
contour UV/XYZ is exact through smoothing in all three archives. The
reported length distributions describe the template interface before the
front and smoothing. The archive shows the final native leaf bounds;
it does not isolate which earlier native boundary, face-size or balancing
event generated each child.

## Local layout consequence

In a geometric calculation on the archived boxes, the four included T1
children fill one parent box `[0.125, 0.25] x [0.125, 0.25]`.
Every side of that box meets two finer native neighbors. Replacing only
the children by their parent therefore selects T6, which partitions the
parent into the same four intermediate squares. All 16 resulting QUADs
have exactly the same oriented cycles in UV, and the four exposed edges
still have length 0.03125.

The four west neighbors grouped as `[0, 0.125] x [0.125, 0.25]` have no
seed QUAD: two touch the outer contour, and the two others are in the
clearance band. Grouping this block as well leaves its parent outside the
template seed because it touches `u=0`. The seeded parent now has
neighbor counts `2, 2, 2, 1` in bottom/right/top/left order and uses the
existing T5 template. The measured 2:1 level difference still holds
across both parent boxes. In the reconstructed local seed, the four edges
of 0.03125 become two edges of 0.0625 on the contour-facing side. Their
physical lengths are 0.09725 and 0.10719. The block would emit 11 instead
of 16 QUADs and the full seed 619 instead of 624. The other exposed seed
edges and total seed area agree with the archive. These are layout
predictions; final front, smoothing and mixed quality remain unmeasured.

## Next experiment decision

Propose one isolated Step 3 comparison using a separate, derived copy
of the original native tree. Use the two exact sibling blocks above.
Keep the original contour samples, native TRI history, approved
clearance formula, existing shape templates and mixed-front/smoothing
implementations. Keep the original captured tree and its replay available
as the baseline. Check the 2:1 rule and seed/interface invariants before
running the front. Then compare final node/element counts, angle and
shape tails by type and region, neighboring size ratios and sampled
XYZ error, with the status of the original TRI source recorded.
The new derived leaf arrangement requires scientific alignment before
implementation. A different template interface can move a poor element
to another part of the front.

**Evidence.** The [receipt](evidence/TEMPLATE_INTERFACE_SIZE_AUDIT_20261122.json)
binds the archive hashes, native leaf boxes, polygon sides, seed edges,
and both local layout calculations. The read-only archive calculations
were run with `python build/quad-template-size-20261122/audit.py` and
`python build/quad-template-size-20261122/local_layout.py`. The canonical
checkpoint changes documentation and evidence. No C++ build, application
generation, CTest or hosted checks were run for this audit. The separate
mixed global error and adaptation remain open.
