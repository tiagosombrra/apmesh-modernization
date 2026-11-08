# Physical node copy state and scalar-only mesh clones

Entry: PR #182 main `ced438b8b8d7b2d6539081c889c78a7fc29d856a`.
Classification: behavior-changing allocation-failure repair and engineering
removal of discarded observer copies, F2-04/F4-04 and C04. The
[compact record](stage3/node_copy_state/summary.json) binds source, native results,
allocation costs and delivery requirements.

## Production change and preserved boundaries

Implicit NodeAdaptive assignment copied point scalars before assigning its element
list. A later allocation failure could leave both scalar state and observers
partially changed. setElements could likewise overwrite an existing list prefix
before an append allocation failed. Three original checked-MSVC scenarios expose
those mutations. Empty-target observer assignment already preserves failure state
in this library; its passed complete sweep remains positive evidence.

Both operations now prepare an independent list before any commit. Point scalar
assignment and list swap have compile-time nonthrowing checks; curvature scalars
then retain the original assignment order. Self assignment and aliased list input
do nothing and preserve list nodes. Failure preserves the old ID, seven scalar
bit patterns, ordered pointers and actual list-slot addresses. Successful list
replacement can invalidate old slot observers; it never deletes elements.

Ordinary construction remains default copying: an independent list of borrowed
element pointers, including duplicates/nulls. Those elements must remain live;
this is not automatic foreign-element retirement or a complete mesh clone.
SubMesh::SetNoh instead constructs directly from the point state and copies four
curvature scalars, avoiding a temporary foreign-adjacency copy followed by clear.
The independent owned node, ID, exact scalar bits and empty adjacency are preserved.

In the existing four-observer fixture, checked-MSVC clone allocations decrease
from 8 to 4. Strong assignment/replacement instead prepare full storage: six
allocations for populated input and two for empty input in this profile, rather
than reusing destination nodes. This is an explicit safety/cost tradeoff, not a
whole-application memory or timing improvement claim. Class layout and numerical
expressions are unchanged; scientific policies/IDs/order remain preserved.

## Finite validation and closure

The existing node probe/runner retains seven original outcomes and adds current
copy, all measured failure, self-input and actual hook controls: 22 expected
outcomes. Require 32 assignment/replacement, 10 construction and four mesh-clone
denials, complete source/target preservation and helper-local retry, zero retained
CRT blocks/bytes and zero self-copy allocation attempts. Actual ASan UAF/double-free
and CRT leak/hook controls remain. The existing Node CTest entry includes the
normal copy contracts; no test target or scientific input is added.

One original controller expected the empty-target setter to fail. Its actual pass
and failed expectation remain unchanged; raw output independently establishes the
strong empty case. Only the three unstarted original cases continue. No completed
native child is repeated after that classification error.

Require configured full changed-production/header and added-positive-fixture
analysis with actual GCC/MSVC metadata; fresh frozen Eistute/Book comparisons on
both native application images; exact-head/main 75 CTest /526 Python; 519 other
protected files and 43 original artifacts; inventory/contracts/whitespace and fresh
remote/guarded-main gates. The local integration receipt is
build/node-copy-state/delivery/integration-verification.json. Other F2 inputs/copy
families, expired foreign/curve/UV observations, F3 owner/recovery/retirement and
whole-process/domain/parallel/F8 obligations remain open.
