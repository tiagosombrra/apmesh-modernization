# Boundary close state guard

Classification: behavior-changing defect repair for invalid lifecycle calls,
S3-06/C10 and bounded invalid-call handling under S3-10. Entry is PR #176 main
`8d3230cbc0d12686818df7d714913b466c4dce88`; its exact-head/main 75 CTest / 515
Python seal is verified. The valid contour body, allocation/publication order,
formulas, templates, synchronization and scientific policies remain unchanged.
The [compact record](stage3/boundary_close_state/summary.json) binds the measured
sources, native commands, failed originals and delivery requirements.

## Reproduced defects and repair

Calling close on a default Boundary reaches boundary.back() without an owner.
The original checked-MSVC child terminates with exit 3221226505 and the exact
STL diagnostic `back() called on empty list`. A second child creates and closes
a valid triangle, then calls close again. Its original implementation exits
3221225477 (access violation); source attribution shows first was cleared by
the previous successful close and is then dereferenced during adjacency insertion.
The second failure has source attribution, not a captured debugger stack.
Both raw original stdout/stderr and executable identity are retained. Neither
failed original is successful validation or evidence of measured leak retention.

Add only `if (!first || boundary.empty()) return false;` before the existing Edge
allocation. The public declaration records the nonallocating no-active-contour
result. Before formatting, removing that guard/comment reconstructs both entry production
files exactly. The staged-file gate then requires explicit formatting of these
two legacy files. An independent lexical comparison proves the formatter changes
no C++ tokens or string literals. The valid operation tokens remain unchanged;
the remaining 520 protected source/build/input files are byte-identical.
The guard adds no minimum contour size or coordinate/orientation decision.
Existing singleton/two-vertex semantics and manual-setter consistency remain
outside this repair; no malformed scientific mesh is promoted to support.

## Native state, lifetime and valid execution

Extend the existing UV probe and required registration CTest entry. For empty
and already-closed states, both reversal flags must return false. Save actual
owner-list pointer order, IDs and endpoint EdgeSet adjacency before the calls and
require their exact preservation. Checked MSVC repeats each refusal with the next
allocation denied and requires zero attempted/denied allocations. Then append a
new triangle and require successful closing to its own first vertex, the original
ID progression and native endpoint incidence. Owners retire normally afterward.
These tests do not invent whole-operation mesh rollback or same-tree recovery.

GCC and checked-MSVC standalone state and aggregate registration calls pass.
Every checked positive child reports zero retained normal blocks/bytes. A separate
registration-trace mode runs the original successful native geometry contract
without the new diagnostic cases; its complete checked-MSVC output matches the
original executable byte for byte. All original boundary denial sweeps pass at
4 first-vertex, 14 appended-vertex and 10 closing-edge sites, with unchanged state
and original successful registration retry. The actual allocation-hook control
still detects its deliberate denial. There is no extra denial sweep campaign.

## Scientific, analysis and delivery gates

Require canonical GCC C++17 and MSVC checked-Debug builds, frozen Eistute/Book
per ABI with unchanged 300-second caps, exact accepted/rejected artifacts and
positive independent boundary comparisons. A changed production executable must
receive its own qualification; source similarity alone cannot reuse an old image.

All four current article executions pass. Per ABI, Eistute preserves five states,
25 exact scientific artifacts and 15 independent boundary comparisons; Book
preserves four states, 20 exact artifacts and 108 boundary comparisons. Accepted
steps remain 0/1; rejected steps remain 2/3/4 for Eistute and 2/3 for Book. These
are same-platform scientific preservation gates, not timing or speedup evidence.
The first four successful runs remain retained separately. Explicit formatting
changes final executable identities, so all four final images are qualified
again; neither set contains a retried failure or an increased timeout.

Configured LLVM 22.1.8 analysis of the full production unit passes through its
actual native compile commands. After formatting, the actual engine and fixture
compile entries are selected unchanged for final full-production/new-fixture
analysis; the complete changed interface header is included. Full UV probe
analysis deliberately detects the existing UAF/leak cases. Analysis of every added fixture/dispatch line and changed
header declaration passes with the same checks, header policy and warnings-as-
errors. The first Windows-separator line filter did not scope those old negative
diagnostics; its failed output is retained and the established forward-slash
filter is used. No new suppression or check relaxation is added.

The initial new fixture failed compilation because its adjacency snapshot used
EdgeList where Vertex exposes EdgeSet; only that test type is corrected before
any original native call. A local controller later used an unknown hook-control
mode; its exit/logs remain and only the unstarted actual hook/denial calls resume
with the existing allocation-hook-control name. No failed native lifecycle call
is retried, no process cap rises, and all raw failed outputs are preserved.

Require architecture/contracts/whitespace, explicit changed-source formatting,
fresh remote main/branches/PR/check audits and all 75 CTest / 515 Python on exact
delivery head and merged main. Preserve the original 43 retained-block artifacts.
After merge use the guarded same-tree checkout, repeat main regression/canonical
MSVC build and verify the qualified native artifact hashes. A local integration
seal must bind these actual final results; this document alone is not integration.

The bounded invalid-call repair does not close S3-06 or S3-10. All ten Stage 3
obligations retain three bounded-qualified/seven partial-open dispositions.
Outside-root ideal retirement, setters/mate/foreign aliases, logical rejection/
mesh retry, whole-process leak/UB/parallel and broader scientific domain remain
separate. The known documentation diagnostic inventory is unchanged.
