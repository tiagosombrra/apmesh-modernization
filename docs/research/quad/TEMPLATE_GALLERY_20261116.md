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
