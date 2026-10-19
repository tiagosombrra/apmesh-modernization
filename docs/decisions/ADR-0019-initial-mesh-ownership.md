# ADR-0019: explicit ownership during serial coarse-mesh construction

Status: accepted design; exact delivery qualification pending.

The central source node is copied by SubMesh::SetNoh, so its original allocation
needs a local owner. The pending mesh and triangles also need owners while later
allocations can fail. The existing CLI treats those exceptions as terminal.

Extract the actual serial constructor body as BuildInitialSubMesh returning an
exclusive owner. Keep each resource local until its established transfer: a
sample's first successful curve insertion, an element's owning vector insertion,
or return of the complete mesh. Preserve the raw-result wrapper and its valid,
presized serial caller handoff. Publish the patch observer only after completion.
The existing collective sample owner reclaims any published prefix on failure.

Enumerate the original exact corner values {0.0,1.0} in the same nested order
instead of using floating-point loop counters. Keep numerical evaluation/request
order, eligibility, reversal, four triangle
templates and acceptance/stopping behavior unchanged. Do not add metadata/ID
rollback or exceptional retry. General raw mesh adoption and OpenMP initialization
remain separate work items. Commands, controls and negative evidence:
[initial mesh evidence](../evidence/STAGE3_INITIAL_MESH.md).
