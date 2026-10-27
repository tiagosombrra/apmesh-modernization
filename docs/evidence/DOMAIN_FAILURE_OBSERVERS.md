# Serial domain failure observers

Reference main: `2ded6ebe49dca8ffbe32bdb169b7469b60ed8bf2` (PR #108).
Classification: behavior-changing error-state cleanup defect repair. Scientific
formulas, numerical order, synchronization, selection and acceptance/stopping
policies remain unchanged. No mesh-quality improvement is claimed.

## Original diagnosis and contract

Eleven retained runs in `build/terminal-propagation-audit/` compare current exit,
already-propagated AFT exceptions and an isolated one-statement exit-to-throw
variant. Eight corrupted observations are rejected and nine normal states / 45
scientific artifacts are preserved. A current Eistute step-2 patch-1 exception
releases observed owners/samples but leaves four live forward observations: one
new candidate and three earlier meshes. Destroying the generator while external
Geometry survives expires those observations. Normal controls also expose owner
expiry; no post-owner consumption or ASan UAF is claimed. The experimental real
CLI classifies the proposed domain error as input/configuration failure and
returns -1 rather than the existing terminal status 1. The variant is not promoted.

The supported repair boundary is the serial Generator's AdaptDomain invocation.
Geometry and owned meshes must remain live while cleanup runs. On exception,
detach every Patch-to-SubMesh link whose identity belongs to the active mesh or
retained generator mesh collection. Compare identities without dereferencing a
foreign SubMesh. Preserve null, independently live foreign and unmatched links;
skip null patch/owner slots. Repeated cleanup leaves the same state, destroys no
owner and does not allocate. Rethrow the original exception object.

The helper is a standard-library C++17 inline operation. The narrow catch is
excluded from MPI/OpenMP paths. It does not surround curve adaptation, loading,
SaveMesh transfer or reporting. Terminal exit still bypasses stack unwinding;
its replacement and dedicated CLI classification remain the next delivery.
No accepted-state restoration, metadata/history change, consumed-ID rollback or
resumable/retry contract is introduced. Normal publication and teardown remain
unchanged. Independently expired/unmatched links and SubMesh-to-Patch back
observations retain their existing lifetime limits.

## Directed controls and actual callers

The GNU fixture executes twelve nonempty helper cases: active-only,
retained-only and mixed owners, forward/reversed observer order, direct cleanup
and identical rethrow. Each has duplicate owned observations, two distinct
foreign objects, null observations, null patch slots and retained null owners.
It checks live native SubMesh/node/triangle contents and exact object release
after normal owner teardown. Cleanup runs twice while the next operator-new
attempt is denied. A separate native allocation must actually trigger the hook.

Actual pinned Book patch-0 and Eistute patch-1 AFT failures capture 28 and four
nonnull observations respectively. Eistute confirms one changed publication
before throwing. From that throw through cleanup, curve-sample release, rethrow
and generator teardown, the fixture permits no additional global operator-new
attempt. The same exception object's address is checked while it remains live.
All owned observations are null at the external catch and after owner teardown;
curve lists are empty. Eight Python controls reject lost/zero layouts, damaged
foreign/null prefixes, allocation/identity changes, missing hook/completion,
remaining observers, lost partial-state coverage and unrelated process failures.

The new fixture linked against the exact original Generator rejects both real
model cases, while its independent helper control passes. Original results have
null_after=0 and 28/four nonnull observations after owner destruction, with zero
additional allocation and preserved exception identity. The stronger contract is
therefore not satisfied by merely releasing owners or rethrowing successfully.
Original source, executable, failing logs and commands remain retained under
`build/domain-observer-repair/`.

The immutable prior observer/harness linked with repaired production objects also
confirms zero owned links at catch and zero expired links after owner destruction
for both current AFT exception paths. Native owner/sample release remains
complete within that observer's measured allocation set. These observations do
not count every process allocation. This is GNU serial qualification, without a
new ASan/CRT, whole-process, parallel, LSan/UBSan or memory-slice claim.

## Exact delivery gates and remaining work

Require exact-head/main C++17 builds, 61/61 CTest with zero failures/skips and
140 Python controls; all new helper and actual-caller controls; original caller
rejection and independent native observations; full caller/consumer and
test-header-inclusive tidy, canonical format, whitespace, inventory, staged and
source-scope checks. Fresh Eistute/Book must preserve all nine accepted/rejected
states, boundaries, physical/UV metrics and 45 scientific artifacts, excluding
runtime fields and independently checking relocated compatibility prefixes.
Record revision/tree/source/input/executable/log identities and remote refs/open
PR/check observations in the delivery PR. Initial checks alone do not authorize
integration; prior qualification remains bounded to its recorded revisions.

Stage 3 remains open and the qualified memory-slice count is unchanged. Next
single work is typed terminal domain failure propagation with real CLI status 1
and step/patch/retry/status context, after unchanged attempts. Retain the failed
prefix as failed evidence. The reverse-direction experiment remains unapproved
and unexecuted; broader recovery and post-owner use remain separate work.
