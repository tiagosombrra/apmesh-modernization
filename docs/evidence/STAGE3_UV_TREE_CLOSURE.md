# Stage 3 slice 5 closure

Head `4f0c9bed6d1d1a52b6cdab88a26a9323040614f9` integrated through PR #21 as main
`83eefa8c6006cc39dcdc35d463b8611d6f038538`, preserving tree `fa76355260fad7184d236f5680dac3ea67e5b6b6`
(818 blobs). Exact-head and implementation-main full campaigns pass: CTest
15/15 with zero skips, 74 Python controls, UV 56/56, node 7/7, six-unit selected
lint, changed-range formatting, fresh inventory and strict Eistute/Book
regression. All nine attempted states, 189 CSV fields, acceptance/incidence
results and 1,168/4,256 last-accepted triangles remain exact.

Five calibrated sweeps inject 3,470 allocation failures across initial root,
uniform subdivision, boundary-edge/old-face generation and actual neighbor
refinement. The original fails all five; its previous 49 cases and both new
success traces pass. Candidate success traces and allocation counts match
original; valid cases retain zero normal CRT blocks/bytes. Root bounds and
midpoint construction are locally owned until complete adoption. Only two
production implementation files change; no scientific expression or policy
changes. See ADR-0006 and `evidence/STAGE3_UV_TREE_CLOSURE.md`.

## Authority and scope

Entry main 4bfb31d54cdfb566a564724851d28a0bc02a93a0 was independently audited:
793 blobs, 14 branches, no open PR/issues and no hosted checks/statuses or
Actions runs. Issue #20 was the sole active work item. The published PR #21
head and implementation-main preserve the expected complete 818-blob tree,
including both immutable remote-only publication binaries. No concurrent
main change was observed before integration.

The failed original and setup failure are retained separately. The initial
neighbor fixture was already balanced and failed the positive-subdivision
assertion; the corrected fixture uses actual public subdivision to produce a
level difference of two. No assertion or scientific tolerance was relaxed.

Successful allocations and tree geometry/IDs/neighbor/leaf/edge order match
the pinned original. Failed-tree destruction is qualified; arbitrary observer
use or retry, mate/root sharing, replacement setters and full-process memory
safety are not. No hosted green-CI claim is made: required gates are local.

## Retained evidence and documentation closure

Full exact-head and implementation-main reports, raw gate logs and hashes are
`stage3/uv_tree/head_qualification.json` and
`stage3/uv_tree/postmerge_qualification.json`. Original failures, source/blob
identities, diagnostic excerpts, fixture history and ADR-0006 are retained.
The toolchain.json record preserves actual compiler metadata: GCC 16.1.0 for
the serial application, MSVC 19.44.35229.0 for both original/repaired narrow
instruments, LLVM 22.1.8 and the separate native/MSYS CMake versions. Narrow
MSVC instrumentation does not qualify the whole application for that compiler.

This documentation-only follow-up preserves every qualified production,
tool/test/build/input and vendor identity. Its published head and final main
require exact full-tree comparison, CTest 15/15 with zero skips, 74 controls and
fresh inventory. Those final commit identities and closure log hashes are
recorded on PR #22 and issue #20 to avoid a self-referential repository commit.

## Remaining work

The wider stage 3 remains open with five qualified slices. Next characterize
remaining mutation/helper temporaries and curve-internal allocation failures,
then sample/initialization/rollback ownership. Other tree/mate/setter paths,
same-tree retry/observer consumption after failure, other templates and
full-process/parallel/LSan/UBSan qualification remain open. Stages 0-2 are
closed for measured scope; stages 4-11 remain pending.
