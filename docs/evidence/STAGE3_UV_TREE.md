# Stage 3 slice 5: quadtree construction ownership

Issue #20; engineering repair. Entry main
`4bfb31d54cdfb566a564724851d28a0bc02a93a0`, tree
`45ec9a1ffae4a2ce78d43d49e985aaac196b16cb` (793 blobs).
Remote audit found 14 branches, no open PR/issues, no check/status contexts and
no Actions runs. The 791 available local blobs match entry; both immutable
publication binaries remain preserved remotely. No workflow is introduced.

## Reproduction and repair boundary

The complete entry campaign passes CTest 14/14, zero skips, 74 Python controls,
UV 49/49, node 7/7, six-unit selected lint and exact repeated Eistute/Book
regression against the previous qualified slice. A 460-file original snapshot
of production/header/vendor inputs is Git-blob verified. Original and candidate
compile the same final probe against 14 actual UV/curve/numerical units.

The pinned original fails five new allocation sweeps while its previous 49
cases and both new successful tree traces pass. Counts and retention below
are aggregate observations across each independently calibrated CRT sweep,
not an estimate of a single application run.

| Control | Injected ordinals | Original retained allocation | Repaired result |
| --- | ---: | --- | --- |
| Initial root (single-point contour) | 20 | 75 blocks / 2,800 bytes | Zero normal CRT blocks/bytes |
| One uniform subdivision | 80 | 105 blocks / 3,960 bytes | Zero normal CRT blocks/bytes |
| Boundary-edge generation | 1490 | 1860 blocks / 70,120 bytes | Zero normal CRT blocks/bytes |
| Generation with a borrowed old face | 1578 | 1965 blocks / 74,080 bytes | Zero normal CRT blocks/bytes |
| Actual neighbor-driven refinement | 302 | 210 blocks / 7,920 bytes | Zero normal CRT blocks/bytes |

The five sweeps inject **3,470 allocation failures**, in addition to the prior
registration and primitive controls. Every measured ordinal is denied exactly
once and must propagate std::bad_alloc. A fresh fixture is destroyed after each
failure. Full successful allocation counts must equal original counts.

Root min/max remain in local owners until the complete root constructor
succeeds. The midpoint pointer buffer and all five vertices remain locally
owned until the set is complete. Existing cell/root ownership then applies.
Only two production implementation files change. No new heap metadata,
scientific expression, threshold, uniform/neighbor refinement policy, source
model, independent verifier or vendor dependency changes. See ADR-0006.

After a failure, observer lists may be partially updated. The qualified contract
permits destruction only; querying, retrying or consuming failed-tree observers
is outside this delivery. Mate roots and replacement setters remain unqualified.

## Successful behavior and required gates

Separate ASan and CRT success fixtures record full cell IDs/levels/bounds,
parent relationships, neighbor order, per-cell edge IDs and registered leaf
order for all five paths. One uniform subdivision must create five cells/four
leaves; neighbor refinement must actually increase the cell count. These
address-free traces are byte-identical between original and candidate in each
instrument; successful allocation counts also match at every measured scope.

The regular required CTest adds application.uv_tree_contracts, for **15/15**
tests with zero skips. The 74 Python controls remain unchanged. Instrument
qualification requires **56/56 UV** and **7/7 previous node** cases. Deliberate
ASan UAF/shared-delete and CRT leak/allocation-denial controls still detect their
intended defects; a nonzero deliberate-control exit is not a valid-case failure.
MSVC ASan detects invalid accesses; separate MSVC Debug CRT checks normal
retained blocks and injects allocations. These are bounded equivalents, not
Linux LSan/UBSan or full-process memory qualification.

Selected lint covers the same six real production units with unchanged rules.
Changed-range formatting covers only the two modified production files;
the test probe is formatted separately. Inventory freshness covers 123
production files (57 translation units, 66 headers), five CMake inputs, 464
literal includes, 272 first-party edges, 22 contracts and 94 anchors. The
existing six-header include cycle and legacy warning debt remain open.

Eistute/Book require two repetitions, all nine attempted mesh states, exact
entry/previous-slice comparisons, positive shared-incidence coverage and zero
measured gap. Acceptance remains steps 0/1 and last accepted triangle counts
1,168/4,256; all 189 named CSV fields must match. Application SHA256:
`3ee790c311e7912772d8c87d9f9afb572ff797f65d229b3ecc237a391f01bee7`.
Exact published-head and implementation-main campaigns pass; see
STAGE3_UV_TREE_CLOSURE.md.

## Evidence and setup history

The first neighbor fixture used a short boundary segment, but its tree was
already balanced: the required positive-subdivision assertion correctly failed.
This is retained as a fixture failure, not a product defect. The final fixture
uses the public subdivision API to refine a real generated leaf two additional
levels, then requires neighbor-driven refinement to add cells. No assertion
or tolerance was relaxed.

Reports, source identities, pinned blob map, successful original traces,
original failed report, diagnostic excerpts and full raw log hashes are retained
under stage3/uv_tree/. Large CRT heap dumps remain local with explicit excerpts
and hashes; no excerpt is presented as a complete log. Earlier failed fixture
report and diagnostic remain separate from the final original failures.

Build and instrumentation follow STAGE3_UV_REGISTRATION.md. Original standalone
builds use build/tree0a and tree0d with AP_MESH_UV_SOURCE_ROOT pointing at the
pinned snapshot, the same compiler/configuration/flags as the repaired target.
Sweep process budgets are 180 seconds; successful instrument cases use 30.
These are test-runner budgets and do not change application stopping criteria.

## Remaining work

The wider stage 3 remains open: other tree/mate/setter paths, curve internals,
mutation/helper temporaries, sample/initialization/rollback ownership,
same-tree reuse after failure, other templates and full-process/parallel
qualification. Stages 0-2 are closed; stages 4-11 remain pending.
