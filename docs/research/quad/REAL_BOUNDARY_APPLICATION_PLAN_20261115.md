# Real-boundary QUAD application integration plan

Date: 2026-11-15. Base reviewed: `2b5eadfdbedd1b4169d4866c1680ecbe1f666b98`.
This updates execution order after the boundary/AFT discussion. It preserves
all prior evidence, R0-R4/M0-M9 criteria and the accepted-epoch gate. One work
item is active: integrate original curve discretization into the live opt-in
single curved manifold patch QUAD/AFT application.

## Functional delivery to implement next

1. **Obtain the real original curve partition.** Reuse the original serial
   `GeneratorAdaptive::AdaptCurve` workflow and its `AdaptCurveByCurve` /
   `AdaptCurveBySurface` calls with the same initial source state and runtime
   configuration as the original reference. Preserve source control nets,
   curve order, parameters, IDs, shared endpoints, curvature inputs, budget,
   adaptation factors, acceptance and retry/stopping rules. Calling the two
   Adapter functions with a newly chosen constant factor is not full workflow
   equivalence. Do not reimplement the discretizer or add synthetic knots.
2. **Construct the compatible native boundary and quadtree.** Map each actual
   source parameter onto its oriented patch side; retain original XYZ/source
   identity and handle reversed curve traversal. Reuse the original parametric
   edge midpoint, normalized size and native tree construction/refinement
   conventions. Replace the live case's fixed quarter-parameter sampling and
   manually prescribed level-2/level-3 tree, not merely the printed counters.
3. **Connect the existing QUAD interior and original exterior AFT.** Feed that
   boundary/tree to the typed interior dispatcher and owned QUAD/AFT seam.
   Preserve original geometric and conditional topological AFT closure and
   reject unresolved fronts, overlap, holes, invalid orientation and dangling
   observers. Audit the role of the original `fillMesh`/`improveMesh` phases
   before making full-pipeline claims; current typed publication does not call
   them. Do not insert a triangle-only phase into a mixed owner without a
   demonstrated compatible contract.
4. **Publish and inspect one real-boundary application mesh.** The actual
   `ap_mesh --config` run must produce a typed physical QUAD/TRI `SubMesh` and
   OBJ from that source partition, with independent boundary/source witnesses
   and nonempty-owner failure preservation. Replace hardcoded acceptance of
   16 boundary intervals and 69/42/36 topology in this new path with derived
   source contracts. Counts are measured outputs. Preserve the fixed16 case,
   its hashes, negative evidence and existing tests as a named regression.

Start with the existing controlled curved manifold source, not full Eistute/
Book welding. Reuse only reviewed PR214 source-boundary helpers and tests
that fit this contract; do not merge its entire draft. Shared endpoints and
curve provenance still require checks in this slice. Multi-patch scientific
sheet continuation and global physical-owner welding remain later gates.

## Finite acceptance gate

- Exact source/configuration identity and independent comparison of every
  original curve parameter, source ID and XYZ against the original curve
  workflow. Exercise an actual nonuniform partition and valid reversed side
  traversal. A coincidental count of 16 is neither a failure nor proof of reuse.
- Boundary nodes/intervals retained exactly in the typed physical export;
  one compatible QUAD/AFT seam, drained exterior front, positive oriented
  elements, complete UV coverage and independent physical Bezier evaluation.
- Negative controls for missing/duplicate source sites, inconsistent traversal,
  foreign identity/XYZ and broken seam; failed generation/publication retains
  the prior nonempty owner, ordered observers and published output.
- Preserve the fixed16 regression and default TRI behavior. Run applicable
  native GCC/MSVC, sanitizer/memory, configured analysis and frozen Eistute/Book
  TRI gates plus the current root/tooling suite on the exact delivery revision.
  Require bounded exact-head remote CI before research integration and repeat
  required validation on the research merge. Unmeasured required gates block
  closure. Retain failed attempts; do not change policy or silently rerun a
  failed campaign to hide a failure. Preserve the algorithm's original retries.
- Export the qualified physical result for Blender inspection with source/run
  identity. Visualization is an inspection aid, not a scientific oracle.

No implementation or new native campaign is claimed by this plan. The opt-in
output will change from the fixed fixture; reuse existing scientific policies
and classify the implementation explicitly. Any new numerical selection,
tolerance, budget or stopping policy needs separate scientific alignment.

## Queue after the real-boundary gate

Resume P2d-1c4b on the qualified real-boundary path: durable typed accepted
history, immutable source provenance and memory/file publication fault/recovery
qualification. Register the approved mixed error/quality/complexity selection
policy before accepting two distinct transitions driven by their actual
previous accepted mixed states. A replacement that is merely pointer-swapped
then reverted remains a rehearsal, not an accepted epoch.

Then resume R4 whole-model experiments and approved shared-sheet ownership.
Historical 1993 identity, all-QUAD output, broader geometry/lifetime coverage
and anisotropy retain their separate gates. `adaptive_epochs=0`; R3/M7 #221
remains open. No new fixed16 candidate campaign is the next functional delivery.
