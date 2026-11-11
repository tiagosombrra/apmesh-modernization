# M4 — Geometric physical candidates on 45 real external Bezier patches

**Candidate (2026-11-11), research-only.** No production QUAD mode, ownership
transfer, global welding or full model-wide conforming mesh is implemented.

## Actual model inputs and experimental scope

The new bounded source-backed test exercises all three tracked indexed
cubic Bézier files with the **real production** `PatchReader::ReaderFilePatches`
and `PatchBezier::Parameterize / Qu / Qv`:

| Source file | Real patches | 1-owner curves | 2-owner curves | >2-owner curves | Maximum valence |
|---|---:|---:|---:|---:|---:|
| `input_models/eistute2.fixed.bp` | 4 | 12 | 0 | 1 | 4 |
| `input_models/book_v7a.bp` | 28 | 84 | 0 | 1 | 28 |
| `input_models/ribbed_bracket_nm_decor.bp` | 13 | 6 | 17 | 4 | 3 |

The **same 19-leaf native C++ Quadtree** and the **unchanged experimental
M5 local-Lawson exterior** are used as two 69-node UV candidate reference
patterns. Their 42 QUAD (actual native C++) and 36 TRI (experimental M5)
faces are lifted *independently* onto each real patch. This is a controlled
**per-patch geometry / interface diagnostic**, not mesh adaptation to each
model's curvature or the 1993 original element placement algorithm.

The read-only C++ target `quad_m4_external_bezier_sampler` first records
the production Geometry-owned curve pointer identities, patch incidence
directions and degree, then exports all 69 `XYZ, Qu, Qv, ||Qu × Qv||` samples
per patch. It never constructs a `NodeAdaptive` or publishes a global
`SubMesh`. The actual loader is required; the independent `.bp` parser
cannot stand in for this runtime test.

## Independent admission and numerical diagnostics

`tests/quad/test_m4_external_bezier_physical.py` checks the entire output
against an independent cubic Bernstein evaluator using the 16 control
records per source patch. It verifies preserved 69 ordered UV vertex
identities and 42 QUAD + 36 TRI face IDs **per patch**, plus production
shared-curve incidence against an independently sampled control-net
graph (including the Eistute 4-way, Book 28-way and Bracket triple curves).

For each production shared curve the auditor samples the **five physical
native boundary sites on each incident patch**, corrects for the
per-patch reversed local parameter direction, and computes the maximum
3D mismatch. It records any gap above a diagnostic threshold `1e-7`;
**it does not merge** the incident nodes. The report also records sampled
tangent cross norms, normal reversals relative to the patch center,
physical facet alignment and near-degenerate triangles, without assuming
all world-space normals point upward. Negative or near-zero diagnostics
are **not** silently interpreted as a valid conforming finite-element mesh.

The sample/facet verification is **not a proof of nondegenerate Jacobian
over an entire Bézier domain**, nor a guarantee of positive exact curved
element Jacobians at arbitrary integration points. This experiment does
not resolve physical normal orientation across a nonmanifold
multi-sheet surface.

Four explicit adversarial controls reject malformed `.bp`, changed
physical XYZ, mutated production curve identity, and detect a crack in a
shared curve without welding it. The full original input parser's seven
malformed control cases and all previous CTest/CLI/TRI gates remain active.

## Generated artifacts

One root serial CTest,
`quad.m4.external_bezier_physical_diagnostics`, is expected to produce:

- **Six model-centroid diagnostics:** 3 real models × 2 unapproved
  point-interior rules.
- **90 separately indexed per-patch OBJ files** (45 real patches × 2
  candidate rules) with 69 physical nodes, 42 QUAD and 36 TRI each.
- Two native-source UV CSV files, six production derivative sample CSV
  files, six production curve-incidence CSV files, and a JSON manifest
  containing SHA-256 source provenance and explicit diagnostic limitations.
- A compressed `m4_external_bezier_physical_candidates.zip` containing
  all per-patch witnesses and source/curve/differential evidence.
  The CI workflow retains this with the independent manifest for 14 days.

Expected full root CTest rises from **83 to 84**; still require
**527 tooling Python**, seven CLI negative modes, native QUAD C++ tests
on GCC/Linux and MSVC/Windows, plus independently frozen Eistute/Book TRI
equivalence. Candidate feature exact SHA and postmerge source SHA must
each pass their required gates. No CTest count is claimed *passed*
before the GitHub log proves it.

## Explicit scientific impediments

No OBJ may be described as an **approved full-model hybrid**: independent
patch files have different node IDs, even when their edge coordinates
coincide. The Eistute 4-way and Book 28-way curve, and the Bracket
3-way edges, are **not manifold two-owner edges**. Graph equality,
geometric C0 agreement and matching samples do not grant permission to
globally weld all incident sheets. The correct topological sheet identity
must be established in a separately reviewed research stage.

`ModelPneu` and `ModelNariz` are `PatchHermite` constructs and cannot
be validated by this Bézier-only adapter. `Bolha` is not a verified,
tracked model input. Full global physical owner lifecycle, rollback,
curvature-adapted tessellation, Delaunay insertion and contour contraction
from the historical 1993 source, centroid-policy approval and all-QUAD
selection remain **open**.

**Next scientific gate:** classify physical model-sheet incidences and
reconcile *which* patch-boundary nodes may be shared across actual
Eistute/Book/Bracket surfaces; separately implement/test a typed Hermite
physical adapter for Pneu. The production TRI baseline remains untouched.
