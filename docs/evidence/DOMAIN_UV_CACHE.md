# Serial temporary UV cache ownership

Reference main: `82dda844fc3ecf7a1fee1c5629b84927ffb90f21` (PR #106).
Classification: behavior-changing exception-safety defect repair, with unchanged
successful meshing behavior. No scientific policy or quality improvement is
claimed. Original failures remain in `build/domain-failure-audit/` and
[the original audit](DOMAIN_FAILURE_STATUS.md).

## Ownership contract

`DomainUvCache` exclusively owns fresh native UV faces, their three distinct
copied endpoints and midpoint caches. `MakeFace` holds each endpoint until the
native Face constructor completes; that constructor allocates its midpoint
before adopting endpoint pointers. `Append` transfers a nonnull, exclusively
owned face only after list insertion succeeds. Allocation failure destroys the
pending object and leaves the existing list unchanged. Neither physical nodes
nor arbitrary shared/copied faces are adopted. Mutable borrowers must preserve
list membership and ownership. Copy/move is disabled.

The serial Adapter declares this owner before its AFT consumer, so exception
unwinding destroys the consumer while its borrowed cache is still alive. Normal
and false-result paths clear at the original explicit points, preserving native
pop-front/delete order. UV coordinates, IDs, area summation, target-size
smoothing, retry selection, quadtree/templates/front and acceptance/stopping
remain unchanged. Native constructors, destructors and the OpenMP path are not
modified. This does not replace terminal exit with exception propagation.

## Directed observations

The C++17 fixture links fourteen actual native units. Right, equilateral and
skinny UV triangles exercise caches of 1, 3 and 8 faces, normal and throwing
borrowers, failed append into a populated prefix, repeated allocation-free
cleanup and actual AFT success/false/exception destruction. Cleanup measurements
use nonempty caches; all allocation denial ordinals are measured, not assumed.

Initial MSVC ASan and Debug CRT runs each pass 18 complete sweeps / 738 denied
allocations, nine nonempty allocation-free cases (36 faces), three preserved
prefixes and three actual AFT cases. Each instrument compares 36 original/
candidate live faces with ten finite UV/midpoint/size/quality scalars per face.
All positive CRT cases retain zero normal blocks/bytes. Actual controls detect
ASan heap-use-after-free, a deliberate CRT leak (9 blocks/408 bytes), original
complete-cache throw retention (27/1224), and original partial construction
retention (2/88). Counts describe this compiler/ABI, not portable constants.
Ten independent checker tests reject missing/ambiguous measurement windows,
wrong profiles, missing/nonzero CRT checkpoints, missing/zero denial coverage,
empty cleanup, lost prefixes/consumers, false instrument controls and incomplete/
nonfinite live observations.

Three GNU serial Book CLI observations reuse the independently controlled
interposer with current production objects. The normal control preserves all
four Book states. Exceptions before and after actual AFT execution now release
152/152 cached Face allocations each, versus original 0/152; the pending mesh
storage is released and the outer curve-sample scope destructor runs once.
These injected cases are not natural numerical failures or whole-process heap
measurements. Small reports and raw logs are retained in `build/domain-uv-cache/`.

The first static-analysis fixture run rejects an unread borrower setup; the
fixture now checks that its throwing borrower is attached to the complete live
cache. Initial compiler logs also retain the corrected fixture-only shadowing
and CRT print-format diagnostics. No diagnostics are suppressed.

## Delivery gates and limits

Require exact-head/main C++17 builds, 59/59 CTest with zero failures/skips and
120 Python controls; twelve expected ASan/CRT outcomes; full adapter/fixture
tidy and format; whitespace/inventory/staged checks; fixed scientific source/
inputs and fresh Eistute/Book accepted/rejected mesh, boundary, metric and CSV
comparison. Record commands, revisions, trees, input/executable/log identities,
remote refs/open PR/check observations and report hashes in the delivery PR.
Initial observations above do not substitute for these exact-revision gates.
Prior isolated batteries whose production inputs are unchanged retain their
existing qualification; this bounded delivery does not repeat a stage closure.

Caller regeneration candidates still use raw pointers before adoption. Fatal
process exit skips outer owners, and broader rollback/retry, metadata/history,
full-process, parallel, LSan and UBSan remain unqualified. Stage 3 stays open;
no qualified memory-slice count is incremented. The reverse-direction experiment
remains unapproved and unexecuted. Next single work: measure caller candidate
ownership on controlled failure before changing exception propagation.
