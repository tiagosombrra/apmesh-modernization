# P2d-1c4a — reversible real QUAD/TRI owner transaction rehearsal

Date: 2026-11-15 Fortaleza.
Canonical research predecessor: [PR235](https://github.com/tiagosombrra/apmesh-modernization/pull/235),
merge `ab1dc62a815f3d56c9b25845bec00863730ddcd5`.
Full scientific R3/M7 issue [#221](https://github.com/tiagosombrra/apmesh-modernization/issues/221)
remains OPEN.

## Ownership and publication audit

`Patch::SetSubMesh(SubMesh*) noexcept` registers a non-owning forward observer.
`SubMesh::SetPatch(Patch*) noexcept` independently registers the reverse observer.
Neither function **owns** the other object. `SubMesh` privately and exclusively
owns nodes and elements, whose borrowed adjacency consists of ordered
`NodeAdaptive::GetElements()` lists. The owner must outlive all dependent nodes;
the patch and its original curves must remain valid for actual adaptive elements.

The original controlled CLI `RunControlledPatch` first exports its P1
69-node/42-QUAD/36-native-AFT-TRI mesh and only then publishes its
`Patch/SubMesh` owner. All preceding P2d-1b2 and P2d-1c2 physical
candidates were **staged in memory/OBJ before that P1 ownership
publication** and cannot be counted as accepted previous-state-driven
adaptive transitions.

Before changing the owner state machine, this P2d-1c4a code **starts
from the real, already published P1** `Patch::GetSubMesh()` and
rebuilds the next 28-leaf native tree selected by *its actual P1
worst original-AFT source residual* near UV(0.2,0.1). It reconstructs
the original full native AFT and real physical 93-node / 62-QUAD /
44-AFT-TRI typed `SubMesh`, then validates independent
`CheckTypedIncidence` and clones a self-contained typed replacement
with new node and element addresses. It does not attach the original
staged object or copy foreign node observer pointers.

## Bounded failure injection

Exact five faults, all **before any forward owner swap**:

| ID | Fault site | Preservation requirement |
| --- | --- | --- |
| 0 | Before native Quadtree/AFT generation | Original live P1 owner and OBJ bytes unchanged |
| 1 | After real native AFT/typed physical mesh reconstruction | Original live P1 owner and OBJ bytes unchanged |
| 2 | After partial typed history clone, before 7th element | Original nodes/elements/ordered observer links unchanged |
| 3 | After new `SubMesh::SetPatch` *reverse* back-observer staging, before forward adoption | Original `Patch::GetSubMesh` still the published owner |
| 4 | Immediately before the `noexcept` forward swap | No owner publication, output mutation or implicit epoch increment |

For each rejected attempt, the C++ source checks **all** previous
node addresses, element addresses, node IDs, XYZ values, exact ordered
observer sequences and old published OBJ bytes. Foreign/dangling
observer leakage or any changed owner causes failure. A genuine
sixth full native AFT typed candidate is cloned and **temporarily**
attached using the two existing `noexcept` registration functions.
Its independent node/element graph is validated in place, the
original accepted owner is restored, reverse registration retired
and previous owner identity/observers/OBJ bytes rechecked.
A non-throwing restoration guard reattaches the previous pointer
even if a validation assertion throws during the rehearsal.

The controlled application prints exactly:
`QUAD_OWNER_TRANSACTION_REHEARSAL source=published_previous_P1_real_AFT
prior_nodes=69 prior_quads=42 prior_triangles=36 next_nodes=93
next_quads=62 next_triangles=44 injected_failures=5
temporary_noexcept_swaps=1 reverted_to_previous_owner=1
ordered_node_observers_preserved=1 previous_obj_bytes_unchanged=1
accepted_adaptive_epochs=0`.

The independent Python regression checks the complete record
and runs it for **both** the normal original P1 CLI publication
and existing injected nonempty `--rollback` CLI run, with
actual `accepted.obj` and `rollback.obj` topology preserved.

## What this stage does not prove

A reversible **pointer-level owner rehearsal is NOT** a scientifically
approved accepted mixed adaptive epoch. It deliberately restores the
old P1 owner and publishes **no next OBJ**. It is not a fully atomic
filesystem + in-memory transaction and does not approve a cost/error
stopping rule. The original fixed16 chart boundary has not been
replaced with the production `Adapter::AdaptCurve` sampling.
It is a single curved Bézier source chart, not a model-wide welded
high-valence nonmanifold mesh.

Still mandatory for a genuine P2d-1c4b accepted transition: pre-register
an advisor-reviewed scientific selection policy, immutable source
control-net/curve fingerprint, make candidate preparation and safe
output publication one auditable transaction, keep each previously
accepted mixed owner archived with correct ordered observers,
test rollback after *every* transactional publication boundary,
and demonstrate two distinct later mixed source-error-driven
adaptations with independent same-site physical quality/error
witnesses. No unqualified automatic epoch counter increment;
`adaptive_epochs=0` and R3/M7 open.

Required CI before any research merge: exact feature Linux GCC and
Windows MSVC native + real `ap_mesh` controlled application, Linux
ASan/UBSan/leak, original frozen Eistute/Book TRI equivalence,
85 root CTests and 527 Python tooling controls. This is an isolated
research branch; no production TRI/`main` change.
