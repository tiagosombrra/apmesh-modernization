# Integrated mixed fill: implementation alignment - 2026-11-17

Classification: engineering preparation of the historical mixed-fill path.
Scientific pairing/selection is not activated. One priority: complete coherent
TRI/QUAD filling before adding new adaptive size-balancing policies. Default TRI,
real-curve partitions, quadtree/templates, original AFT and accepted/rejected
history remain unchanged. Preserve previous evidence and known failures.

## Implemented engineering slice

The real-boundary application archives two additional diagnostic CSV files per
completed history: boundary_pair_stages.csv and boundary_pair_candidates.csv.
Only actual exterior TRI faces after a seeded QUAD region are inventoried.
Initial TRI-only source stages are explicitly not applicable; their source
triangles are not falsely labeled observed mixed-region AFT triangles.

boundary_pair_candidates.h enumerates adjacent oriented TRI pairs using value
indices only. It preserves source triangle order, canonicalizes the four-node
boundary start without reversing winding, and rejects foreign/repeated indices,
inconsistent shared-edge directions, duplicate triangles and nonmanifold edges.
Candidates may conflict, be concave, degenerate or fail physical quality. No
geometry acceptance, quality score, winner, element replacement or new ownership
publication is implemented. No candidate is written as an accepted OBJ face.

The archive records step/epoch/retry/domain-generation identity and actual TRI
reference acceptance. Face and node indices are one-based references to that
stage's unchanged mixed OBJ. Selection status is not_evaluated, selected count0,
scope topology_only_policy_pending. Native contracts and an independent Python
reader check the actual arrays/adjacency/cycle boundaries and forged records.

This is a completed-output read-only inventory. It is not an implementation of
the historical in-front pairing algorithm, nor permission to adopt a greedy
postprocessing matcher. The measurements make actual candidates reviewable for
the next integrated implementation rather than adding a detached generator.

## Next scientific and ownership slice

Use the original frontier operation to identify one triangle and its admissible
neighbor alternatives, evaluate the explicitly aligned shape rule and select a
pair deterministically. Preserve a valid TRI when no acceptable pair exists.
The1993 Figure11 defines a planar shape score and threshold; its UV versus XYZ
interpretation on a curved patch and the order/tie choice among multiple valid
pairs must be explicit. AGENTS.md requires advisor alignment before activating
that numerical selection. Do not invent new weights, global factors or thresholds.

Commit a selected pair through one reversible physical owner operation. Preserve
source nodes/shared curves, oriented seam, coverage, manifold incidence and
accepted owner/observers; retain failed and rejected candidates. Paired exterior
QUADs must have AFT-pair provenance, not fabricated native-leaf/template origins.
Current Candidate.quads/quad_origins describe seeded native QUADs; do not silently
reuse those invariants to label new exterior QUADs. Both kinds contribute to total
QUAD count only after their distinct origin/transaction contracts are qualified.

Required change-relevant validation: actual curved source histories, positive and
rejected pair choices, multiple alternatives/ties, wrong generation/source IDs,
nonconvex/degenerate candidates, nonempty rollback and independent UV/XYZ/seam
coverage. Require native compiler/sanitizer profiles, frozen TRI and exact-head
regression/review. Fewer elements or zero observed pairs is not scientific success.

## Subsequent work and retained scope

After mixed-fill selection/publication is qualified, return to mixed error and
curve-transition-interior local feedback. The existing local-balance proposal is
retained but sequenced after integrated filling. No global-factor sweep, uniform
flat-region refinement or boundary point clipping replaces this objective.
Current source adaptation remains TRI-driven; mixed_adaptive_epochs=0, R3/M7 OPEN.
Centroid identity, full1993 equivalence, Doxygen/CRT and independent review are
separate unresolved obligations. No automatic integration or stage closure.

Exact source/compiler/test evidence is recorded in canonical STATE.md on
quad-templates; this contract alone is not a qualification receipt.
