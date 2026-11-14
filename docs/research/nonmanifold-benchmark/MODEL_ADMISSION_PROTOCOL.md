# Model admission and independent audit protocol

Status: PROPOSED / NOT YET EXECUTED. Do not label any external model APPROVED until all required evidence exists.

## Topology taxonomy

- INTENDED_EDGE_NONMANIFOLD: a topological edge/curve intentionally incident to at least three distinct sheet/patch sides; documented physical junction and orientation.
- MANIFOLD_SURFACE_CONTROL: shared edges with two incidents, or free edges with one incident; valid for geometry/quality controls but NOT a non-manifold positive.
- VERTEX_ONLY_NONMANIFOLD: singularity detected from vertex link; no evidence of shared non-manifold curve.
- SELF_INTERSECTION_OR_OVERLAP: geometric intersection not encoded as a valid desired topological junction.
- DUPLICATE_OR_DEGENERATE: coincident duplicated faces/edges, zero-area facets, repeated vertices or invalid connectivity.
- UNKNOWN_OR_AMBIGUOUS: insufficient metadata to distinguish a designed interface from mesh defects.

Tests must distinguish topological incidence from tolerance-based geometric coincidence. For edge classification, examine the number of incident oriented faces/sheets; for non-manifold vertices, inspect the link graph. Preserve multi-edge cases and duplicated-but-distinct coordinates without automatic merging. Track disconnected components, face orientation, closed/open boundaries and nonorientable patches.

## Hard gates (no weighted score can override)

| Gate | Evidence required | Rejection / block |
|---|---|---|
| G1 provenance and rights | exact file identifier, stable source, citation, per-asset license and raw hash | license unclear -> BLOCKED; redistribution denied -> external download/reference only |
| G2 topology | independent source graph/edge incidence/vertex-link classification; intended junction explanation | only malformed or vertex-only cases -> NEGATIVE_UNSUPPORTED for the edge-junction hypothesis |
| G3 representation | explicit four-sided patch decomposition and shared boundary graph; bicubic Bezier representability or bounded approximation | no valid bounded decomposition -> UNSUPPORTED |
| G4 geometric fidelity | units, feature-preserving normalization, independent bounded or convergent error metrics | unmeasured/excessive distortion -> BLOCKED/FAIL |
| G5 experimental value | unique hypothesis and nonredundant geometry/topology bucket | redundant -> lower priority, not failed geometry |
| G6 reproducibility | source+output hashes, tools/parameters, commands and independent validation | manual/opaque transformations -> BLOCKED |
| G7 research regression | exact scientific baseline on same frozen qualified environment; real output incidence comparisons | failures, missing outputs or zero coverage -> no integration |

For G2, positive non-manifold coverage requires an intentional shared EDGE/CURVE with >=3 distinct incident sheets/patch sides. A dataset-level 'non-manifold' flag is only a lead. For a manifold-control case, G2 may PASS for its expressly designated control role but must not count as non-manifold generalization.

Proposed qualitative prioritization after gates: topology relevance 25, converter feasibility 20, ground-truth strength 20, scientific comparability 15, diversity 10, integration cost 10. These weights are heuristic and must be frozen before ranking candidates; priority scoring is not a substitute for evidence.

## Proposed status machine

DISCOVERED -> METADATA_VERIFIED -> TOPOLOGY_CLASSIFIED -> REPRESENTATION_ASSESSED -> CONVERTED_AND_AUDITED -> APMESH_TRI_ADMITTED -> PUBLICATION_FROZEN.

Any state may transition to BLOCKED, REJECTED or NEGATIVE_UNSUPPORTED with a named reason and source evidence. CONVERTED_AND_AUDITED does not imply TRI_ADMITTED. Historical models are HISTORICAL_FROZEN and do not follow the external gate sequence.

## Explicit numerical contracts to freeze

- Input units, physical scale, normalization map, smallest retained feature, conditioning and reasonable coordinate domain.
- Maximum allowed surface and feature-curve error, relative to domain size AND local feature scale. No universal threshold assumed here.
- Geometric error: sampled bidirectional Hausdorff and RMS with sampling density/convergence and independent implementation; state clearly if no certified continuous bound exists.
- Topology: exact incidence correspondence of declared edge/curve identities; no epsilon pass for lost/shared edges.
- Shared curves: common canonical boundary controls and parameter direction, with exact/reversed BP control-net comparison. Verify reversed incidence explicitly and avoid near-equality welding.
- Numerical roundoff versus approximation tolerance versus generator adaptation tolerance kept distinct.
- Pilot tolerances determined on synthetic analytic controls and reviewed BEFORE externally held-out final experiments.

## Required adversarial test families

1. 3, 4 and >=5 sheets meeting along one exact source edge with reversed and mixed orientations.
2. Distinct nearly coincident curves (must NOT weld) and mathematically shared curves (must remain one entity).
3. Vertex-only bow-tie singularity versus intentional edge junction.
4. Duplicated faces, open boundaries, holes, intersections, zero-area triangles, inverted faces and disconnected components.
5. Trimmed / periodic / non-bicubic surfaces requiring segmentation, or explicit unsupported classification.
6. Sliver feature smaller than candidate tolerance; large dynamic-range coordinates and high curvature.
7. Malformed or truncated CAD/mesh inputs, NaN/Inf, invalid indices, enormous declared counts, parser rejection and resource denial.
8. Generation retries, rejected saved stages, missing incidence snapshots, partial outputs and zero-compared-boundary controls.
9. Identical visual shape but different source incidence graph: topology change must be detected.
10. Conversion re-run and source-independent audit on a fresh output directory.

Do not count a negative-case rejection as a successful supported model, and do not count a saved rejected mesh as an accepted result.

## Audit evidence and reviewer signoff

One artifact bundle per model: source identity, metadata, inventory, independent topology report, mapping sidecar, BP validation, geometry report, generator attempt/decision logs, boundary checker, regression report and signed reviewer decisions. Record status, current commit/tool versions, all failures, open blockers, approval date and reviewer role. Do not assert external reviewer or advisor signoff until recorded.

Existing independent controls: tools/check_boundary_incidence.py, docs/GENERATION_VALIDATION_CONTRACT.md and current quality/regression controls. Reuse actual checker semantics; extension of its domain or new controls must be separately justified.
