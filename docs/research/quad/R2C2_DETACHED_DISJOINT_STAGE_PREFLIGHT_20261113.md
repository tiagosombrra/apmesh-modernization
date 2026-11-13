# R2c-2 preflight — detached chart ownership and atomic replacement

**Research-only proof, 2026-11-13 UTC. NOT a globally joined physical
Eistute or Book QUAD/TRI mesh. NOT a scientific sheet admission.**

## Motivation and actual ownership design

The production `MeshAdaptive` owns a vector of distinct
`unique_ptr<SubMesh>`; `SubMesh` owns `NodeAdaptive` and
`ElementAdaptive` with elements borrowing nodes. Individual `Patch`
forward links and `SubMesh::SetPatch` back links are separate observer
graphs. A model-wide physical publication that modifies those patch links
one-by-one cannot be called atomic without a new explicit owner/observer
transaction. In particular, no chart may silently borrow nodes from
another patch-owned `SubMesh` when the latter can be retired earlier.

This bounded experiment builds on the already tested M4 typed four-node
`QuadrilateralAdaptive`, legacy `TriangleAdaptive`, and actual production
`SubMesh`/`MeshAdaptive` ownership APIs. It does **not** modify them.

## Source and tests

- `research/quad/disjoint_owner_stage.h`: `DisjointOwnerStage` owns
  wholly detached chart `SubMesh` instances; each chart must be
  unbound to any `Patch`, have a non-empty unique node/element inventory
  and contain only locally owned observers. For QUAD it checks all four
  node pointers; reverse node-element observer counts check both TRI and
  QUAD element arities. A duplicated source owner pointer is rejected.
- `Prepare` allocates a completely separate `MeshAdaptive`, transferring
  all charts into it. Deterministic injected faults before *every* chart
  adoption and one additional fault before publication must leave the
  **previous active model owner and each old node/element pointer exactly
  unchanged**. RAII destroys rejected candidates, retiring elements
  before their owned nodes.
- `Replace` calls `Prepare` and performs exactly one
  `unique_ptr<MeshAdaptive>::swap` after all validation and allocation
  can no longer fail. Only then is the retired root destroyed.
- `tests/quad/disjoint_owner_stage_probe.cpp` exercises synthetic
  disconnected **4-chart** and **28-chart** populations. Every synthetic
  chart independently owns seven `NodeAdaptive` instances, one typed
  QUAD and one original TRI. Their flat coordinates are deliberately
  *not* the physical Eistute/Book original source curves. The tests
  reject each stage failure, including a missing chart, check no partial
  active root mutation, publish two successive fully detached synthetic
  owners, and recheck all node-element observer graphs.
- One separate `quad.r2c2.disjoint_owner_stage` root CTest is mandatory.
  Its expected bounded output is 4-chart and 28-chart stage inventories,
  respectively **6** and **30** failures injected/rejected (the number
  of chart boundaries plus the prepublication sentinel and missing chart)
  and two successful repeated atomic root replacements per case.

## Non-goals and blocked physical obligations

1. The test operates on **synthetic flat, disjoint** QUAD/TRI charts.
   There is no source `.bp` load, no original QUAD/AFT solver, no model-
   wide UV/XYZ seam conformity or Jacobian proof. The counts 4 and 28
   are cardinality stress tests, not validation of actual global models.
2. `Patch::SetSubMesh`, `SubMesh::SetPatch` and model owner/observer
   attachment are **intentionally not performed**. This is not an
   atomic publication into the production patch graph, only a fully
   detached root exchange. The real patch-link transaction is a separate
   R2c-3 design/implementation gate.
3. The only authorized ownership model in this experiment is disjoint
   node ownership. It does not make a globally shared seam node owner;
   real high-valence junction continuations still need approved
   source-model-SHA-bound scientific decisions and a separate lifetime
   mechanism. The stage assumes valid node-element graph construction
   before adoption and does not manufacture intentionally dangling
   cross-chart borrows just to elicit undefined behavior.
4. No new production `quad_uv` mode, historical 1993 numerical rule,
   automatic `radial_next` -> `halfedge.twin` connection, merge,
   model-wide physical `SubMesh` output or release is enabled.
5. GitHub-hosted Linux root CTest gives bounded C++ runtime evidence if
   passed. It is **not** local/native ASan/UBSan validation, nor
   Windows-native memory proof of this particular root-only test.

The independent R2c-1 source-bound reviewer packets and pending policy
must continue to report `scientific_admission=false` and no shared
physical node owners. Model-wide source curve topology remains a
genuine scientific blocker. The next permitted engineering work is
testing transaction semantics for *both* sides of the
`Patch`-`SubMesh` observer relation with strict failed-epoch
restoration, but attaching nonmanifold patches and physical seams
cannot be approved merely by a disconnected staging proof.

**Qualification ledger:** report exact source SHA, root CTest count,
native QUAD Linux/Windows unaffected baselines, frozen original TRI,
both source R2c0/R2c1 negative controls, fault count and trial output.
If any required CTest fails, this stage remains unqualified.
