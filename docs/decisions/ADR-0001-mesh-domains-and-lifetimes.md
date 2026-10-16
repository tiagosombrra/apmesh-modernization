# ADR-0001: Preserve mesh domains and make lifecycle boundaries explicit

Status: accepted engineering constraints for staged modernization.
Date: 2026-10-16. Base: d4561c9421226503cb4a478faad71ed5ad012381.

## Context

The stage 2 inventory shows a physical mesh with XYZ/curvature/adjacency and a
temporary parametric CRABMesh representation carrying UV/front/quadtree state.
Adapter performs the conversion, and Generator owns adaptive policy, snapshots,
acceptance and saved candidates. Some ownership is explicit through unique_ptr;
other routes rely on raw-pointer adoption, copying and detach-before-delete.
Related names and formulas do not establish interchangeable domains or owners.

## Decision

1. Keep distinct physical and parametric domain concepts. Introduce explicit
   conversion contracts before considering shared abstractions.
2. Keep canonical shared curve identity and per-patch incidence direction
   separate, preserving every incident sheet and its boundary partition.
3. Define owners/observers and copy/adopt/transfer behavior at lifecycle
   boundaries before reducing copies, merging containers or extracting a library.
4. Treat cache invalidation, retry/rollback rebinding and failure teardown as
   API contracts. Use source-backed characterizations and qualified negative
   diagnostic controls before repairing them.
5. Consolidate only computations proven equivalent in domain, units, precision,
   ordering, tolerance and policy. Analytical vs discrete curvature and UV vs
   physical quality are not presumed duplicates.
6. Preserve scientific sequence and exact accepted/rejected regression. Keep
   historical failures and behavior-changing repairs explicit. Scientific
   proposals still require advisor alignment.

## Consequences

Stage 2 delivers source coverage, reviewed contracts and a dependency-ordered
repair backlog. It leaves production/build/model identities unchanged. Stage 3
starts with measured lifecycle qualification; stage 4 may unblock its tools.
Eigen removal and library/context extraction remain stages 5 and 6.

This decision does not declare every static hazard a reproduced runtime defect,
all memory paths safe, parallel modes qualified or whole-repository lint clean.
The lexical include inventory supplies traceability and coverage, not semantic
or runtime proof. Existing required gates and the user's end-stage audit and
regression rule continue to apply.

Evidence: [architecture inventory](../architecture/MESH_ARCHITECTURE.md),
[contracts](../architecture/contracts.json),
[follow-up sequence](../architecture/REFACTOR_SEQUENCE.md).
