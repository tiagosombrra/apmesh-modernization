# Mesh Studio — R2.7.18 research decision: nonwelded multi-sheet node identity

**Date:** 2026-11-17. **Status:** scientific design decision; does not enable
new frontend rendering or scientific LOD. **PR:** #239 draft/unmerged.

## Observed source facts

R2.7.14 source-incidence audit found one source curve shared by
**4 Eistute patches** and one by **28 Book patches**.
R2.7.15 measured identical paired source sample t/XYZ within its
stated tolerance in **6/6 and 378/378** original patch-owner
comparisons, but no completely matching logical node-ID pair.
R2.7.16 retained one source-scoped sample group per **11 / 13**
observed boundary samples, preserving every original patch-local
ID instead of creating a new global mesh ID.
R2.7.17 observed that the accepted UV(0,0) corner ID came
from edge 0 in **4/4 / 28/28** patches; its edge-3 source ID
agreed only in the first patch in each source model.

R2.7.18 preliminary direct C++ observation found that
each native accepted UV(0,0) node was actually owned by its
respective SubMesh and registered as an observer of an
accepted triangle: **4/4 and 28/28**. No matching owner
C++ object pointer was observed between those patch corners.
The original local Adapter Boundary::close() executed in
**104 Eistute / 84 Book provisional local attempts**,
which are deliberately distinct from global commits.

## Identity model to expose in a future Inspector

| Domain | Identity key | Valid scope | What it does not establish |
| --- | --- | --- | --- |
| Accepted original native snapshot | Validated model/config/source SHA + actual accepted step | Real C++ source-verified step only | Cross-epoch face descent |
| Original source curve | Source geometry's canonical `source_curve_slot` and original native curve ID | One original source geometry instance | Physical node welding |
| Source sample association | Accepted snapshot + canonical source curve slot + sample ordinal | Read-only group qualified by real per-patch UV and XYZ comparisons | Newly allocated native node/global welded ID |
| Original physical node | Accepted native snapshot + source patch slot + original native node ID and local SubMesh node slot when observed | That physical patch-local accepted mesh | Uniqueness across different patches/epochs |
| Original face corner | Patch slot + accepted face's original native element ID and UV corner index | One accepted native snapshot | OBJ face ordinal |
| C++ object identity | In-process pointer-equality observation **only**, serialized as explicit true/false with scope | Lifetime of observed original accepted C++ objects | Stable numeric pointer address or future persisted identity |

The source association must remain a relationship (**many original
patch-local nodes can belong to one canonical sampled source
curve**) rather than rewriting connectivity.

## Required future user experience

1. Clicking a shared original source curve selects the **source
   curve**, not a synthetic new welded mesh edge. Show every
   incident source patch, original curve slot, original orientation
   and complete original sample count.
2. Selecting a sampled source location displays its current
   `(accepted step, source curve slot, sample ordinal, canonical t)`
   and lists the **original native logical node ID of each patch**,
   alongside raw original XYZ and UV side data.
3. Selecting one local physical corner distinguishes its actual
   `(patch slot, native ID)` from other nodes at the same XYZ.
   Show whether the original native triangle observed the live
   node from that patch's SubMesh and whether actual C++ pointer
   equality was observed. **Never show memory addresses**.
4. A filter can distinguish **matched sampled geometry** from
   **matched original native logical ID**, and both from
   **welded physical C++ ownership**; these are three independent
   scientific assertions.
5. When observing local `Adapter::Boundary::close` attempts,
   visually label them as **provisional attempts**, not
   globally committed generations; do not silently select one
   as the true parent attempt when the origin cannot be proved.
6. Non-manifold fan support must retain all N source patch
   incidences (Book N=28). Never collapse them into a pairwise
   manifold-only edge or discard their original sheet orientation.
7. A rejected candidate is never a new LOD epoch. A future LOD
   selector must require at least two actual original accepted
   adaptive steps and independently verified descendant
   correspondence with continuous geometric-error bounds.

## No mutation or deployment in this stage

No new physical node, face, edge or C++ pointer is created
for STUDIO. No source original ID, UV/XYZ, adjacency or
triangle connectivity is changed. No release, merge,
default visualization mode or browser feature is activated
by this decision. The experimental VTK default remains unchanged.
Both existing BVH selectors stay bounded and opt-in; scientific
R2.8 LOD remains **BLOCKED**.

The next UI work should be independently reviewed as a
*read-only source identity inspector*, implemented behind a
feature flag and verified with original source-bound accepted
TRI evidence before it may be treated as a scientific result.
