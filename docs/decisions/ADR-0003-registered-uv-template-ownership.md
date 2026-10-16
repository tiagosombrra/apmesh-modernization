# ADR-0003: registered UV templates have one owner before and after front assembly

Status: engineering defect repair, stage 3 slice 2, issue #11.
Entry: main `0f2473622800907e2d15e1d5ab6216caedb36797`.

## Context

Quadtree registered generated vertices/edges/faces in raw-pointer lists. The
front copied those pointers into owner lists only at fillMesh. Failures after
templates and before fillMesh left the registered payload without cleanup.
Normal success did clean it through the front, which explains why successful
generation alone did not expose the leak.

Boundary/front teardown also used setVertices(null...) to release shared
endpoints. Those geometry setters allocate replacement caches, so low memory
could terminate a destructor. A Face midpoint aliasing an endpoint was deleted
by this setter, then deleted again by its vertex owner.

## Decision

Quadtree owns each registered template object until TransferTemplateMesh appends
its three owner lists into the front using allocation-free list splices. The
front first prepares its allocating observer views. Failure there leaves all
template owners in the quadtree. The successful commit preserves the existing
front prefix, pointer identity and vertex/edge/face append order, emptying source
owner views. Cell/front lists remain observers.

Quadtree destroys any untransferred registered payload before its root/boundary.
Boundary, quadtree and front use explicit noexcept DetachVertices before deleting
shared topology. Detachment releases a Face midpoint alias to an endpoint while
retaining ownership of distinct caches. It is a teardown operation; live cache
mutation/invalidation is a separate contract.

Keep legacy Face/Edge endpoint ownership outside these containers. Old Adapter
UV faces own distinct allocated corners; making all endpoints observer-only
without changing those creation scopes would create leaks. Do not replace this
ownership design with shared_ptr or a universal physical/parametric mesh.

## Consequences and limits

The original registered-payload leaks, midpoint-alias use-after-free and
allocation-denial termination are reproduced. The repaired cases pass ASan and
Debug CRT, including three actual observer-preparation allocation failures.
The numerical sequence, template choice, front/smoothing and scientific policies
are unchanged; article regression remains exact.

This is not arbitrary exception safety. Allocation failures inside template
creation before registration, constructor/setter replacement, mate/root sharing,
same-front execute reuse, Adapter temporaries, samples/rollback and full process
leaks remain open. Windows ASan/CRT does not qualify LSan, UBSan or parallel runs.
Evidence: [UV lifecycle audit](../evidence/STAGE3_UV_LIFETIME.md).
