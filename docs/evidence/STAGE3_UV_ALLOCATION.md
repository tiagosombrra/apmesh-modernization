# Stage 3 slice 3: UV primitive allocation commit

Issue #14. Entry main `0146fbd4925721a53a9b52717b82c5af8c4e0115`, tree
`8edd39eaf92f5795cea4e35bb1647cdc9bc310eb` (715 blobs). This is an engineering
defect-repair boundary. The full stage 3 remains open.

## Authority, entry and failed original

Remote main, ten branches, open PRs/issues, checks and Actions were audited.
No concurrent PR/work item existed. Remote checks/Actions remain unconfigured;
no hosted workflow was created. All 713 available local text blobs match entry;
the two immutable remote-only publication binaries are preserved. Entry CTest
11/11, 74 Python controls, previous UV 26/26, node 7/7, selected five-unit lint,
article repetitions and strict previous-slice comparison passed.

The narrow target still compiles 14 actual UV/curve/numerical production units,
without stubs. A separate 416-file original source/header/vendor snapshot is
verified against entry Git blobs. The same final probe and strict 35-case runner
are used for original and candidate; the original remains **failed**, with
eight failing cases. All previous 26 cases still pass on the original entry.

| New control | Pinned original | Repaired observation |
| --- | --- | --- |
| Edge construction, six measured failure sites | Nine CRT blocks / 336 bytes retained across the sweep | Zero retained blocks/bytes |
| Default front construction, 32 sites | 55 CRT blocks / 1,936 bytes retained across the sweep | Zero retained blocks/bytes |
| Primary and explicit-endpoint-midpoint Face construction, three sites each | Pass, zero retained blocks | Pass; no direct constructor edit |
| Edge setVertices, six sites | Failed replacement changes live state | Endpoints, midpoint identity/geometry, vector length and scalar state preserved |
| Face setVertices, three sites | Failed replacement changes live state | Endpoints, midpoint identity/geometry and scalar state preserved |
| Face old midpoint aliases an endpoint | ASan heap-use-after-free during centroid calculation; CRT contract fails | Endpoint remains borrowed; correct centroid and caller lifetime |
| Normal primitive geometry/identity and null caches | Alias part fails | Pass in ASan, Debug CRT and required normal CTest |

These are **53 separately injected allocation ordinals**, plus the three retained
transfer-preparation failures from slice 2. Counts include real MSVC container/
cache construction and are measured fixture facts, not portable invariants.
The hook has a deliberate-allocation control. Deliberate UAF/duplicate endpoint
deletion and a three-block/112-byte Vertex leak remain detected independently.
No failed product case is relabeled an expected success.

## Repair and audit

Edge/Face prepare caches in local unique_ptr owners from the requested endpoints
before changing live state. Edge construction consequently unwinds its first
cache if the second fails. Public raw-returning makeMid/makeVector keep their
caller-owned contract; private overloads share the unchanged arithmetic.
Face discards only a distinct old owned cache, preserving an old endpoint alias.
Default front construction guards Boundary until Quadtree construction adopts
it. See [ADR-0004](../decisions/ADR-0004-uv-primitive-allocation-commit.md).

Successful setters retain their previous endpoint-rebinding policy; they do not
delete discarded endpoints. Caller/container lifetime remains explicit. New
endpoints must not alias a distinct cache owned by that same object. Individual
setV1/setV2/setV3 and parametric-midpoint mutation are outside this repair.

Production changes are restricted to three AFT implementations and two headers.
Only changed production ranges are formatted (three whitespace replacements);
the extended probe is formatted in full. Diagnostic configuration is unchanged.
The first candidate GCC build exposed the missing explicit memory header; it was
added and the final source rebuilt. Its failed log hash is retained. Existing
vendor/legacy warnings are not reported as resolved.

The midpoint/vector/centroid formulas and operation order are unchanged.
Template/front selection, boundary partitions, smoothing, adaptation/acceptance/
stopping policies, inputs, vendor and independent scientific verifiers are
preserved. Source review and independent article comparison are both required.

## Candidate validation

GCC 16.1 serial C++17 Release, MPI/OpenMP/LTO off; CMake/CTest 4.4.3; LLVM
format/tidy 22.1.8; MSVC 19.44.35229 ASan and separate Debug CRT. Current CTest
**12/12**, zero skips; **74 Python controls**; UV **35/35**, node **7/7**.
Required application.uv_primitive_contracts adds normal geometry/alias coverage.
Inventory: 122 production files, five CMake inputs, 22 contracts and 85 anchors.

Both article models repeat twice with a fixed executable/configuration/command.
Strict candidate/entry and entry/previous-slice comparisons retain all nine
attempted states, positive shared-incidence coverage, zero measured position
gap, exact OBJ/acceptance/CSV/incidence results and 189 matching named CSV fields.
Both accept steps 0/1; last accepted meshes remain **1,168 / 4,256** triangles.
No oracle/tolerance change. Candidate application SHA-256:
`c8075286a4753123765f43d2f13c2e757b20ea7c8bfcdfb409f209f716987aad`.
Reports and raw failed diagnostics: `stage3/uv_allocation/`.

Commands follow the existing standalone ASan/Debug CRT builds and
tools/qualify_uv_lifetime.py interface in STAGE3_UV_LIFETIME.md. Use source cache
AP_MESH_UV_SOURCE_ROOT for the pinned-original target. Normal commands:

```text
cmake --preset local-serial
cmake --build --preset local-serial --parallel 2
ctest --preset local-serial --output-on-failure
python tools/inventory_architecture.py --output docs/architecture/source_inventory.json --contracts docs/architecture/contracts.json --check
python tools/quality.py tidy src/crab_mesh/aft/advancing_front.cpp src/crab_mesh/aft/boundary.cpp src/crab_mesh/aft/edge.cpp src/crab_mesh/aft/face.cpp src/crab_mesh/aft/quadtree.cpp --build build/local-serial
python tools/repeat_generation.py --exe build/local-serial/bin/ap_mesh.exe --model <eistute|book> --output <fresh-directory> --report <report.json>
```

## Closure requirements and remaining scope

Code, tests, contracts, scientific invariants and the failure/coverage inventory
are reviewed at this checkpoint. Exact published-head and post-merge gates are
required before closure. Original, entry and candidate reports retain source/
input/executable identities and raw diagnostic/log hashes.

Next: template arrays/object creation before registration, Boundary registration,
other setters and helper temporaries, followed by samples/initialization and
rollback. No arbitrary front exception, generic raw-copy/adoption, same-front
reuse, all-template-pattern, full-process, parallel or Linux LSan/UBSan coverage
is claimed. Decor Shelf and every internal retry remain unqualified. Stages 0-2
are closed; stage 3 remains active; stages 4-11 remain pending.
