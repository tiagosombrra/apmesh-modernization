# Native TRI and QUAD template gallery - 2026-11-16

User requested a historical visual reference before further balancing work.
Delivered a new Blender5.3 file with two scenes: the saved analytic/TRI/mixed
history and a gallery of six native template families T1-T6. The existing source
blend file and all original mesh coordinates/connectivity are unchanged.

## Actual native extraction

Use the unchanged d59a513 engine library, GNU C++17 Release and its real compiler
arguments. A bounded standalone diagnostic builds closed native depth3 quadtree
fixtures, refines selected neighbors of cell[0.375,0.5]^2 and captures that cell.
Canonical side masks are0,8,10,12,13,15 in bottom/right/top/left bit order.
Original TRI faces come from Quadtree::makeTemplateBasedMesh and the actual
QuadtreeCell::makeMeshType1-6 dispatch. QUAD faces come from CaptureLeafPolygons
and EmitLeafQuads with the same vertex-arithmetic-mean point rule as the live
research case. No triangle pairing or hand-drawn template topology is substituted.
The extracted coordinates are translated/scaled into the unit square for display.

| Source family | Finer-neighbor sides | Native TRI faces / nodes | QUAD faces / nodes |
| --- | --- | --- | --- |
| T1 | None | 2 /4 | 4 /9 |
| T2 | One | 3 /5 | 11 /17 |
| T3 | Two opposite | 6 /7 | 8 /15 |
| T4 | Two adjacent | 6 /7 | 12 /19 |
| T5 | Three | 5 /7 | 11 /19 |
| T6 | Four | 6 /8 | 16 /25 |

These are representative canonical examples from the implemented families, not
an inventory proving that all six occur in the last generated model. Rotations
and quality-dependent TRI diagonal/center choices can produce other instances.
Source numbering T3/T4 follows the implementation, not left-to-right Figure7
order. QUAD uses the current experimental vertex-mean rule; no literal historical
1993 point-rule equivalence is claimed. Exterior AFT triangles are dynamically
generated and are explicitly distinguished from these interior templates.

## Display and verification

Gallery: original TRI above, experimental QUAD below, yellow sides adjacent to
two finer cells, white actual emitted nodes, family/face/node labels. Blender
window QUAD_TRI_history_with_templates was opened and visually confirmed with
all12 panels visible. The other scene retains the original analytic source and
four TRI/QUAD-TRI states. Mesh snapshots before/after and the original file hash
confirm preservation; the new gallery is display-only.

Native exporter compilation and its six cases completed successfully. Independent
planar audit checks finite unique UV vertices, valid indices, positive facets,
unit area, opposite internal edge orientations, manifold incidences, expected
boundary edges, connectivity and Euler disk counts for all12 panels. A reversed
TRI face is rejected as a negative control. An initial curved-physical-patch
checker rejected flat UV coordinates because it requires a Bezier XYZ mapping;
that checker-selection failure is retained, then a planar audit is used without
changing the native output. This is not a new physical mesh or adaptation test.
No new native application build,85-test campaign, MSVC/sanitizer qualification,
scientific gate, hosted CI or algorithm/policy change is claimed.

Rebuild the Blender file using the archived JSON and recipe, with an existing
saved history as input and a new output path:

```text
blender-launcher.exe --background source-history.blend --python template_catalog_blender.py -- --catalog NATIVE_TEMPLATE_CATALOG_20261116.json --output new-history-with-templates.blend
```

Local result:build/quad-template-catalog-20261116/QUAD_TRI_history_with_templates.blend.
The bounded native extractor, command arrays and raw output remain under the
ignored local experiment directory and native result directory. The receipt
retains exporter/library/image/compiler and catalog identities. The portable
catalog is sufficient to recreate the gallery without rebuilding the engine.

[Catalog](visual/NATIVE_TEMPLATE_CATALOG_20261116.json),
[receipt](visual/NATIVE_TEMPLATE_CATALOG_RECEIPT_20261116.json) and
[Blender recipe](visual/template_catalog_blender.py).

Next: resume the existing local coupling proposal and required scientific
alignment. PR238 review, Doxygen/CRT, accepted mixed feedback and R3/M7 remain open.


## Direct comparison with the 1993 paper - 2026-11-16

User asks whether the displayed templates match the article. Re-hashed the
seven-page local primary-source PDF:49d297e24c1b8695e18c6d1307aa4ccbc39f14e265d251b840a16560aca98dc5,
5439448 bytes. Read complete printed page288 and a400-dpi Figure7 detail using
the installed Poppler renderer. PyMuPDF was unavailable in the default Python;
no installation was needed. The coauthor's public bibliography independently
confirms the1993 title/authors/pages but is not evidence for the figure geometry.
Do not redistribute the scanned page/crop in the repository.

The six split-neighbor families and intermediate polygon connectivity correspond
to the proposed Figure7 transcription. Printed column order is T1,T2,T4,T3,T5,T6;
the gallery sorts source type numbers T1,T2,T3,T4,T5,T6. The article itself does
not print these type labels. Its upper row depicts TRI patterns; the lower row
depicts intermediate polygons for later QUAD subdivision, not the final QUAD
faces shown in the gallery. Midpoints plus a supplied polygon center yield the
recorded4/11/12/8/11/16 QUAD counts in printed order.

The paragraph explicitly calls for the polygon centroid but provides no numerical
formula. Current live/gallery QUAD uses the vertex arithmetic mean; for general
non-triangular polygons that is not the signed-area centroid. On T2 ABOW the
former is(3/8,1/4), the latter(7/18,2/9), as already recorded in the M1 review.
Thus matching incidence/counts does not establish identical interior coordinates
or the historical software's rule. No new1987-source interpretation is imported.
Original TRI code can also select quality-dependent centers/diagonals. For
example the exported canonical T4 center is(0.5,0.524); the scan is schematic
and supplies no numerical point table, so no geometric error against that drawing
is inferred. The all-split T6 diagonal can be symmetry-equivalent to the printed
one. These are family correspondences, not pixel-for-pixel historical identity.

Conclusion: structural correspondence is supported; literal numerical reproduction
and advisor adoption are not established. Keep the gallery labeled native TRI
and experimental vertex-mean QUAD. Do not describe it as a certified1993 replica.
No source, Blender geometry, policy, test or scientific-stage status changed.


## Combined meshes and polygons in one scene - 2026-11-16

The user clarified the desired layout: retain the last TRI/QUAD examples and
place their intermediate polygons directly below, in the same Blender scene.
Delivered QUAD_TRI_templates_and_polygons.blend with three aligned T1-T6 rows:
original TRI, emitted vertex-mean QUAD and source polygons. The original analytic/
four-step generation history is also preserved in the file's other scene.

Extended the isolated native diagnostic to export actual CaptureLeafPolygons
cycles from the same canonical cells. All original12 TRI/QUAD vertex/face arrays
remain exactly equal to the previous catalog. Source polygon counts are1/3/2/3/3/4
in source type order. All18 normalized panels pass the planar topology checks;
no hand-drawn polygon table replaces the native capture. The original saved
history and mesh snapshots remain unchanged. No production build, formula or
scientific rule changed. The new Blender5.3 window was opened and all18 panels
visually confirmed together, including the purple polygon row below QUAD.

Local file:build/quad-template-catalog-20261116/with-polygons/QUAD_TRI_templates_and_polygons.blend.
Recreate it with the same command as above using
[extended catalog](visual/NATIVE_TEMPLATE_POLYGONS_20261116.json),
[three-row recipe](visual/template_polygons_blender.py) and a new output path.
[Extended receipt](visual/NATIVE_TEMPLATE_POLYGONS_RECEIPT_20261116.json) retains
native compiler/library/exporter identities and geometry preservation checks.
Earlier two-row files/catalogs remain preserved. No new CTest/CI, scientific
qualification or algorithm work was performed for this presentation change.


## Mixed final meshes and the remaining-region pairing gap - 2026-11-16

User asks whether the1993 paper mixes QUAD/TRI throughout internal quadrants.
Read the verified primary source again: complete printed pages289-291 and the
previously inspected page288/Figure7. The bibliography corroboration is separate
from this direct scanned-paper evidence. PDF hash remains49d297e24c1b8695e18c6d1307aa4ccbc39f14e265d251b840a16560aca98dc5.
No scan or rendered page is redistributed here.

The article supports a final mixed outcome but distinguishes generation roles:

- On printed page288, interior cells use the selected TRI patterns, or the QUAD
  branch constructs intermediate polygons and then subdivides them into QUADs.
  This does not describe freely selecting TRI and QUAD independently inside
  every interior template cell based on local curvature or an arbitrary factor.
- Printed pages289-290 define the remaining region between the generated interior
  mesh and the original domain contour. Boundary contraction first identifies a
  triangle; when requesting QUAD, it considers an adjacent triangle and accepts
  their combination only under its shape criterion. If no acceptable neighboring
  triangle is selected, the triangle can remain. The outcome can therefore have
  adjacent TRI and QUAD. No all-QUAD guarantee follows.
- Printed page289 explicitly identifies an apparently interior cell near the
  reentrant contour that is reclassified as boundary under the earlier rule.
  Thus this remaining region need not look like a thin uniform outer ring;
  it can extend into the drawing around geometric features. That observation
  does not prove unrestricted mixed interior templates or a complete per-element
  census of Figures12/13. A quadtree cell outline is not itself proof of a
  four-node finite element.

A concrete current implementation gap is now explicit: at exact feature d59a513,
OwnedQuadAftFront::AttemptExteriorTriangulation generates original AFT triangles;
controlled_patch_application.cpp appends all selected interior QUAD faces, then
appends each aft->Triangles() face as three vertices. It does not perform the
article's optional TRI-pair-to-QUAD step in that remaining region. Current mixed
output is seeded QUAD plus exterior AFT TRI, not a complete historical remaining-
region QUAD procedure. This explains why the displayed topology can have a more
separated QUAD core/TRI region than a pairing-enabled result. It is not evidence
that the article deliberately places TRI/QUAD arbitrarily in all interior cells.

Keep this in the M5 boundary-policy/historical-coverage inventory. No historical
shape threshold, pairing priority or acceptance policy is imported into code.
The article's geometric mixture must also remain separate from the proposed
curve/transition/interior size feedback. No new native generation/tests/CI,
Blender edit or scientific adoption occurred in this read-only clarification.
