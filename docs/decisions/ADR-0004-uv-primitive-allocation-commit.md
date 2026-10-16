# ADR-0004: prepare UV primitive resources before committing ownership and caches

Status: engineering defect repair, stage 3 slice 3, issue #14.
Entry main: `0146fbd4925721a53a9b52717b82c5af8c4e0115`.

## Demonstrated problem

The pinned entry implementation leaks the first Edge cache if the second cache
cannot be constructed. Default AdvancingFront construction leaks its Boundary
if Quadtree construction fails, including failure in member-container setup.
Edge/Face setVertices change endpoints and delete old caches before allocating
replacements. A failed replacement therefore leaves partially changed state.
Face replacement also deletes an old midpoint that aliases an endpoint and then
reads that freed endpoint when computing its centroid. ASan confirms the access.
Both Face constructors pass their independent allocation-unwind controls; no
direct constructor change is justified by those controls.

## Decision

Edge/Face setVertices prepare the same caches from the requested endpoints in
local unique_ptr owners. They commit only after all allocations complete. Old
endpoints, bounds, caches and scalar state survive allocation failure. Existing
public Edge makeMid/makeVector continue to return caller-owned raw pointers;
private overloads reuse the same arithmetic for proposed endpoints.

Face deletes only a distinct owned old cache; an old endpoint-alias midpoint
remains borrowed during replacement. It then commits the prepared cache and
endpoints. Successful setters continue to leave discarded endpoints to the
caller/container; this is not a new endpoint-adoption API. New endpoints must
not alias a distinct cache owned by that same object.

Default front construction holds Boundary in a local unique_ptr until Quadtree
construction completes, then releases it to the existing Quadtree owner. No
shared_ptr, new numerical policy or universal mesh abstraction is introduced.

## Qualification and limits

The same calibrated runner is applied to the pinned original and candidate.
Each observed allocation ordinal is denied separately in Edge construction,
both Face constructors, default front construction and Edge/Face setVertices.
Caller endpoint ownership and unchanged failed-replacement state are required.
ASan/Debug CRT positive cases and deliberately invalid controls remain mandatory.
Normal geometry, identity/scalar state, null caches and endpoint-alias behavior
are also checked through required CTest. Detailed counts are fixture/toolchain
observations, not portable allocation-count invariants.

Template arrays/creation, Boundary registration, other setters, parametric
midpoints, helper temporaries and allocation failures elsewhere in the full
front algorithm remain open. Generic raw-copy/adoption and same-front reuse are
not qualified. Windows ASan/CRT does not establish Linux LSan/UBSan or complete
process memory safety. Scientific article regression is required independently.
