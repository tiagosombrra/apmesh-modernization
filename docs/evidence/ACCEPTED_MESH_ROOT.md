# Explicit serial accepted mesh root

Base: main `802eab2a2a77e15867b9398612eadf8a01089133` (PR #111).
Classification: behavior-changing accepted-state identity/ownership defect repair.

The report archive includes rejected meshes. The original caller selected its last
entry as accepted_mesh on every outer iteration. The native audit reproduces bad
anchors in Eistute steps 3/4 and Book step 3, affecting five trials and final patch
bindings. Original source/traces, two nonempty correct prefixes and eight corrupted
trace controls remain in `build/outer-rejection-audit/`; that restoration contract
fails and is not relabeled as successful restoration.

The serial root is initialized from the initial accepted mesh and advanced only
by Commit in the unchanged acceptance branch. AcceptedMeshScope moves an active
unarchived root into a temporary owner, keeping it alive across candidate retries.
On rejection it returns that owner to mesh_; on acceptance it retires the previous
unarchived root. Archived roots stay owned by the existing report history. During
exceptional unwinding of a held root, owned active/root patch observations are
detached before candidate retirement, preserving null/foreign observations and the
propagating exception without additional allocation. Parallel branches keep their
prior behavior. No criteria, formulas/order, directions, synchronization, templates,
front behavior, rejected report inventory or intentional last_candidate_* memory
are changed. Attempted global/local error and stopping guards are not repaired.

Twenty-two native scope cases cover archived/unarchived ownership, rejection and
commit, two observation orders, exceptions before/during/after construction,
allocation denial, consecutive rejections, retries and acceptance after rejection.
Require observed native storage release, zero allocation during cleanup, foreign/
null preservation and release-control detection. Eight Python checker controls
reject incomplete or corrupted case output. A uniquely named faulty scope that
destroys rather than returns the accepted owner must fail, avoiding a conflicting
class definition with the production Generator.

Complete-caller probes use reversible diagnostic insertions into the actual
Generator, including every restoration and curve/domain seed. Normal probes use
the original computed decision. Separate controlled flow cases force only the
test copy's decisions at steps 1/4 and extend its test limit to 5 to exercise an
acceptance after consecutive rejections and the following seed. They are branch/
ownership tests, not scientific results or changes to production policy. Require
CLI h/m/q and unarchived library execution, zero rejected roots, a retained active
accepted owner when unarchived, original caller rejection, and actual typed
terminal-failure cleanup measured by the immutable prior observer. CLI validation
still rejects empty/unsupported modes; retained preparation failures do not count
as numerical validation. The library test clears WRITE_MESH after loading valid h
configuration, following the existing library fixture convention.

Fresh scientific h cases require independent physical/UV metrics and boundary
checks on all nine states. Both models retain accepted steps 0/1 and rejected
later steps. States 0-2 are exact before rejected archive reuse. Seven OBJ states
are exact; Eistute step 4 and Book step 3 differ. Thirty-one of 45 scientific
artifacts remain exact and fourteen change. Original strict equality fails and is
retained; reproducibility against the first repaired observation is a separate
witness, not a historical baseline update. Normal instrumented and production
outputs must agree independently. Extra anchor/seed/owner failures are rejected.

Initial mixed results for the final rejected candidate are retained below.
Ratios are exported percentages; these are not changes to the retained accepted
mesh and do not establish a global quality improvement.

| Model | Elements old/new | Error old/new | Physical q_min old/new | Poor percent old/new |
| --- | --- | --- | --- | --- |
| Eistute step 4 | 7184 / 7216 | 0.0104806 / 0.0100167 | 0.130023 / 0.126117 | 2.39421 / 2.43902 |
| Book step 3 | 19830 / 19774 | 168.476 / 168.932 | 0.0951287 / 0.0951287 | 10.0706 / 10.1042 |

Require exact-head/main C++17 build, 64/64 CTest with zero failures/skips, 164 Python
controls, all component/native/control/scientific gates, full caller/fixture/test-
header analysis, source preservation, formatting, whitespace, contract/inventory,
staged and remote audits. Record revision/tree/input/executable/command/log/report
identities in the delivery PR. Initial checks alone do not authorize integration.
Evidence and all preparation failures remain in `build/accepted-root-repair/`.

Stage 3 stays open, without a new qualified memory-slice count. No full-process,
new ASan/CRT, parallel, complete rollback or resume claim follows. Next audit:
accepted versus attempted global/local error at stopping guards after rejection.
Reverse-direction trials remain unapproved and unexecuted.
