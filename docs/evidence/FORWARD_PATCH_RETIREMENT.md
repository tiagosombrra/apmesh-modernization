# Independent Patch/SubMesh forward observer retirement

Entry: PR #181 main `150ec6a5c3d19ff77d3d42361507bd69dac68bb5`.
Classification: behavior-changing observer retirement repair, F4-01/F4-04 and
the Patch/SubMesh part of F2-04. The [compact record](stage3/forward_patch_retirement/summary.json)
binds the original observations, source, current images and required delivery.

## Defect, admission and production change

The existing foreign-forward/move arrangements in CheckPatchObservers leave a
Patch observing a SubMesh whose independent back link can name another Patch or
be null. Extending those same live-object arrangements through observed-mesh
retirement exposes expired forward pointers. Six original semantic observations
fail under both ASan and CRT; old registered observer controls still pass. The
probe compares pointer values without dereferencing expired objects. It does not
claim an original sanitizer UAF or heap leak: original CRT retention is zero.

Patch::SetSubMesh now registers its forward borrow in an independent intrusive
list owned by the observed SubMesh. Rebinding/destruction unlinks that registration;
mesh destruction clears all surviving forward borrows. The existing back-observer
list and its direction remain separate. No reciprocal link is synthesized and
no borrowed object is deleted. Retirement and mutation allocate no memory.
The shared unlink helper uses only Patch links and the supplied list head; it
introduces no additional out-of-line link dependency in isolated native targets.

Patch moves preserve the previous ID/forward pointer values, including the
source's forward pointer, and register each destination object separately. Back
registrations stay at their original addresses. SubMesh moves retain forward
observers on the original target object addresses. Pointer-taking Patch copies
remain detached. Self-move, same/null rebinding and unrelated live forward links
retain their old behavior. Nonnull setters require actual live objects.
Private layout changes require consumer rebuilds. Direct protected-field writes,
already-expired input pointers and concurrent mutation are not qualified here.

## Finite validation and closure

The existing SubMesh probe/runner retains all 34 controls and adds three expected
outcomes: both instrument profiles and one all-allocation-denied scope for the
six forward histories. Require all 37, zero final CRT blocks/bytes and zero
allocation attempts during the new operations. Actual UAF/leak/hook controls
remain mandatory. The existing required SubMesh CTest entry also runs these
forward histories; no target or model is added. Preserve the original seven-flag
registered observer trace exactly within each ABI.

Require 95 current detached Bezier/Hermite patch-copy outcomes with the existing
independent numeric/topology oracles, all nonallocating scopes and actual controls.
Full changed-production/header analysis and added positive probe analysis use
unchanged diagnostics and actual GCC/MSVC compile metadata. Analyze one actual
canonical engine entry per production unit instead of duplicate target entries.
Fresh application images require frozen Eistute/Book comparisons on GCC/MSVC;
preserve accepted/rejected traces, IDs and positive boundary comparisons.

Require exact-head/main 75 CTest /526 Python, 518 other protected source/build/input
identities, 43 original evidence artifacts, inventory/contracts/whitespace, fresh
remote audits and guarded same-tree main checkout. The actual integration receipt
is build/forward-patch-retirement/delivery/integration-verification.json.
This closes the named unmatched public Patch/SubMesh forward-retirement boundary.
Other copied/foreign curve and UV links, cache mutation, F2 raw corpus, F3 owner/
recovery/retirement and whole-process/domain/parallel/F8 obligations remain open.
