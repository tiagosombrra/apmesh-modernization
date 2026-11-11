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

## Verified exact-head measurements (2026-11-11 UTC)

The following are **measured scientific diagnostics**, not an expected or
hypothetical mesh. They are independently read from the source-head
[Actions #43044996136](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43044996136)
[artifact #13867960046](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43044996136/artifacts/13867960046)
on SHA `a5f46fb5da336fee2c27cf6f9e1e102832a12b30`.
The artifact was downloaded and inspected: its inner ZIP has **90 OBJ,
14 CSV and one JSON** (105 files). The PR merge-ref test
[#43045007952](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43045007952)
also passed independently.

| Model | Patches | Production curves | High-valence curves | Max sampled seam gap | Min sampled cross-derivative norm | Nonpositive local facet alignments |
|---|---:|---:|---:|---:|---:|---:|
| Eistute | 4 | 13 | 1 (degree 4) | 0 | 12.003695754670666 | 0 |
| Book | 28 | 85 | 1 (degree 28) | 0 | 1.9994063772945894 | 0 |
| Ribbed Bracket | 13 | 27 | 4 (degree 3) | 2.6645352591003757e-15 | 1.499999399999998 | 0 |

Results hold under each of the **two unapproved interior-point rules**.
45 patches × 2 rules produce 90 patch-local OBJ candidates, each with
69 distinct local physical nodes, 42 native C++ Quadtree QUAD and
36 experimental M5 Lawson TRI: **3,780 QUAD, 3,240 TRI and 6,210
patch-local sampled vertex records**. All sampled near-zero Jacobian
and near-degenerate facet counts were zero. Four negative model,
physical-sample, curve-registry and physical-seam mutations passed.

**Critical Eistute limitation:** Across its four patches there were
36 sampled differential normals pointing opposite the corresponding
patch-center reference **per rule**. These can coexist with zero
nonpositive *local facet-vs-local differential normal* alignments;
they are distinct predicates and do not prove an inverted Jacobian.
Finite samples do not certify global Jacobian positivity, lack of
self-intersection or model-wide conforming node ownership.

**CI root cause and fix:** initial [run #43033602254](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43033602254)
failed **before CTest** because optional GDB installation hit Ubuntu
GitHub-runner DNS failures (apt exit 100). The feature CI was corrected
to emit a visible `BACKTRACE NOT COLLECTED` warning when GDB is absent,
without network installation and with **no change to mandatory CTest,
Python tooling, native QUAD or frozen TRI scientific gates**. Exact
source-head run #43044996136 then passed all four jobs, **84/84 CTest**
(new external-model CTest #73), **527/527 Python**, GCC/Linux and
MSVC/Windows native QUAD, plus strict frozen Eistute/Book TRI parity.

[PR #209](https://github.com/tiagosombrra/apmesh-modernization/pull/209)
was merged to research-only `quad-templates` at SHA
`ff97e9c15d2b652433ecb494a90822fce88bea1b`.
The [exact merged-source postmerge #43046674566](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43046674566)
was **IN PROGRESS** at this documentation checkpoint and must be
checked separately before scientific stage closure.

**Scientific outcome:** source-linked per-patch physical diagnostics
are demonstrated for all three real Bezier BP models. Their 4-way,
28-way and 3-way edges remain *high-valence sheet incidences*, not
approved manifold welding. No connected model-wide mesh,
global element ownership, original 1993 Delaunay/insertion/contraction,
general regularity proof or production QUAD execution is claimed.
