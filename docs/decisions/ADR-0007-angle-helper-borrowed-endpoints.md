# ADR-0007: preserve borrowed endpoints in the angle helper

Status: accepted; exact-head and implementation-main complete campaigns pass.
Documentation-only closure gates remain required; see the closure evidence.
Issue: #23. Classification: behavior-changing defect repair on allocation-failure
exits; successful numerical behavior is preserved. No scientific proposal.

## Context and reproduced defect

Edge normally owns its endpoints unless a shared container explicitly detaches
them. Edge::angle(Vertex*, Vertex*) constructs a temporary Edge and lends it
caller-owned endpoints. The original detaches through setVertices(nullptr,
nullptr) only on the successful path. Allocation failure after binding those
endpoints unwinds through the legacy owning destructor and destroys live caller
vertices. Even default construction of the three copied Vertex locals in the
other angle overload can allocate; populated adjacency copies add further sites.

The same final probe compiled against the 460 verified original production,
header and vendor blobs fails all ten new Debug CRT sweeps. Its previous 56
cases and both normal angle cases pass. This distinguishes the reproduced
failure from broad unmeasured ownership risks.

## Decision

Add an automatic EndpointScope next to the temporary Edge. Its destructor calls
the existing allocation-free, noexcept DetachVertices before the Edge destructor.
The guard owns no heap metadata. Normal construction, endpoint assignment,
Vertex value copies, angle arithmetic, final null-cache replacement and cache
destruction keep their existing order. Keep the public signatures and the
legacy destructor contract outside this query unchanged.

The overload borrows endpoints for the query, including exceptional exits. The
caller remains responsible for their lifetime. No shared_ptr, alternate mesh
generator, formula substitution, tolerance change or diagnostic suppression is
introduced. The analogous Face::quality guard remains local to its own boundary;
this repair does not introduce a universal ownership abstraction.

## Qualification and limits

Independent 3-4-5 triangle geometry checks four endpoint-match branches and the
nonadjacent -1 result with empty and populated caller adjacency. Successful
ASan and CRT traces match the original byte-for-byte. Independently calibrated
successful allocation counts also match: 24 sites in each empty-adjacency case,
27 in each populated adjacent case, and 24 in the populated nonadjacent case.
These are observed MSVC fixture counts, not portable constants.

Ten CRT sweeps deny all 252 measured ordinals. Every denial must propagate
exactly once, preserve endpoint lifetime/geometry/adjacency and receiver endpoint,
cache identity/geometry, ID and scalar state, then permit a successful query.
Caller teardown must destroy each endpoint exactly once. CRT covers allocation
denial and retained blocks; normal ASan cases plus deliberate invalid-access
controls qualify the separate instrument. No ASan allocation-denial claim is
made. Required application.uv_angle_contracts prevents zero normal coverage.

Curve-internal operations, parametric midpoint mutation, other helpers/setters,
generic copied adjacency, failed-tree observers/retry, samples/initialization/
rollback, full-process, parallel, Linux LSan/UBSan and portability remain open.
See the slice evidence for complete gates, commands and failure history.
