# Native two-block template interface experiment

22 November 2026, Fortaleza. The researcher explicitly approved one local
replay of the two adjacent sibling blocks specified in the
[template interface audit](TEMPLATE_INTERFACE_SIZE_AUDIT_20261122.md).
The research source is based on
`c93a383e2775d33eb8a7e5f28cbc410e3d98593d`. The experimental source and
outputs are retained under `build/quad-two-block-20261122`.

## Experimental boundary

Use the existing fixed-`1.5` `curva_bezier` MSVC Debug C++17 configuration.
Only the Step 3, retry-zero, area-centroid mixed reconstruction receives a
derived copy of the tree. In that copy, restore the parents
`[0.125, 0.25] x [0.125, 0.25]` and
`[0, 0.125] x [0.125, 0.25]` in place of their eight leaf children.
Replay the other native subdivision events by captured cell identity.
The original source remains available for normal replay and its
curve witness is used by mixed boundary and physical publication checks.
The current clearance formula, 2:1 requirements, template catalog,
front selection and all five smoothing passes are used. The TRI native
generation and its original decision occur before the derived replay.

The local trial checks the 217-leaf and 619-seed-QUAD prediction before
advancing. It retains the completed front before smoothing and logs the
start of each attempted pass. Validation of a valid output uses the original
contour identity audit, both layout inventory and exact front replay, the
existing UV smoothing checker, and shape/XYZ-error measurements before and
after. If a candidate fails, retain its exact output prefix and first failure.

## Measured results

MSVC `19.44.35229.0`, Windows x64 Debug C++17. Configuration, build,
application and independent comparison all exited zero. The application
completed once in 16.48 s under 180 s. The reference curve-stage CSV, all
four native TRI OBJ files and the first three mixed OBJ files (Steps 0-2)
are byte-identical. Source Step 3 still has 430 TRI and global curvature
error 0.0303172, with its original accepted status. The mixed contour
preserves the 14 original intervals by identity, UV/XYZ and orientation.
Nine corrupt reference-boundary controls were rejected by the independent
auditor. The candidate front replays all 106 commits and all five recorded
smoothing passes, with six approved prospective QUAD contractions.

The native derived tree removes the eight intended children and adds
only the two parents, yielding 217 leaves. Seed count decreases from
624 to 619. The isolated substitution of four 0.03125 UV segments by
two 0.0625 UV segments is exact. All other exposed seed edges and UV
seed area 0.609375 match. The three original narrow pocket triangles
are absent. Both new contact triangles stay in the actual front trace.

| Step 3 observation | Reference | Two-block trial |
| --- | ---: | ---: |
| Nodes / QUAD / TRI | 689 / 630 / 102 | 683 / 625 / 100 |
| Minimum angle among contact TRI, before smoothing | 1.42° | 3.06° |
| Minimum angle among contact TRI, after smoothing | 3.10° | 5.45° |
| Minimum angle on the full mesh, before smoothing | 1.42° | 2.27° |
| Minimum angle on the full mesh, after smoothing | 1.87° | 1.87° |
| Minimum angle on contour-edge QUAD, after smoothing | 18.92° | 18.92° |
| Minimum scaled corner Jacobian on contour-edge QUAD, after smoothing | 0.32013 | 0.32013 |
| Worst neighboring size ratio on vertex-only transition, after smoothing | 5.43 | 4.94 |
| Area-weighted sampled XYZ RMS, after smoothing | 0.009542 | 0.009486 |

The neighboring-face ratio compares the two median physical edge lengths
across a shared edge, reporting the larger divided by the smaller. Its
median on the vertex-only transition remains about 1.44. The candidate's
minimum interior QUAD angle before smoothing falls from 64.41° to
42.21°; the respective final minima agree at 12.17°. Other measured
statistics also trade off; see the complete region and phase receipts.
Sampled XYZ RMS before smoothing rises slightly (0.011821 to 0.011827).
The native TRI curvature error and the mixed sampled geometric diagnostic
are different quantities.

The limiting TRI near the fixed UV corner `(1, 1)` has precisely the same
UV/XYZ and angle trajectory in all six frames. Its starting angle 6.95°
falls to 2.59° on the first pass, reaches 1.86° at pass three, and finishes
at 1.87°. The grouped blocks give a real local front improvement with
seven fewer mixed elements. This separate corner limits the final minimum
on the patch.

## Scope and current handoff

Retain this bounded positive transition result locally. The two exact
boxes define a case-specific experiment. A general tree policy and
integration remain open. The next work item is the quality of the five
mixed smoothing passes at the observed limiting corner. Prepare one
local shape-preservation comparison over the already generated control
and specify its acceptance of individual node moves for scientific
alignment. Check the contour-area QUAD losses and transition TRI tails
in the same assessment. Keep the original curve and TRI reference.
No additional template sweep or mixed global curvature adoption follows
from this experiment.

The [numeric receipt](evidence/TWO_BLOCK_TEMPLATE_TRIAL_20261122.json) binds
the candidate source/configuration, compiler inputs, command outcomes, and
output hashes. No new exact-revision CI, complete CTest or additional corpus
qualification is claimed for this isolated comparison.
Mixed global curvature error and mixed adaptive acceptance remain separate.
