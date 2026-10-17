# ADR-0006: guard quadtree construction resources until adoption

Status: accepted engineering repair, stage 3 slice 5 (#20).

The entry revision is 4bfb31d54cdfb566a564724851d28a0bc02a93a0. Allocation
denial during root construction retained one or both bounds before the root
became their owner. QuadtreeCell::makeMids retained its pointer buffer and
already-created midpoint vertices when a later vertex allocation failed.

Keep root bounds in local unique_ptr owners until the complete root constructor
succeeds. Keep the midpoint buffer and five individual vertices locally owned
until the complete set is ready. Then release the exact original objects into
the existing owner fields. No new heap metadata is introduced. Numerical
expressions, successful allocation sequence, cell/leaf/neighbor ordering,
subdivision policies and IDs are preserved.

Existing cells still own successfully attached children and midpoint sets.
Failed generation or subdivision is qualified for destruction only. Observer
lists may be partially updated; no same-tree retry, querying or continued
refinement is promised. A transactional tree/neighbor rollback would require a
separate design and evidence. Mate/root sharing, external setter replacement,
arbitrary exceptions, full application and parallel paths remain unqualified.

Five independently calibrated Debug CRT sweeps cover root-only generation,
one uniform subdivision, generation guided by boundary edges, generation with
a borrowed old face and refinement of an actually unbalanced prepared tree.
Every measured allocation ordinal is denied once and must reach the caller;
subsequent destruction must retain zero normal CRT blocks/bytes. Separate ASan
and CRT successful traces compare full cell bounds, IDs, parent links, edge
associations, neighbor order and leaf order against the pinned original.
The previous UV/node controls and strict scientific regression remain required.

See ../evidence/STAGE3_UV_TREE.md and stage3/uv_tree/ for failures, identities,
instrument boundaries and closure results.
