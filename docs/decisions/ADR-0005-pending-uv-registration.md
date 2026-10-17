# ADR-0005: pending UV resources remain owned through registration failure

Status: engineering defect repair, stage 3 slice 4, issue #17.
Entry main: `c341ba7cb7b514b4073330e59ccef14d000e45de`.

## Demonstrated problem

Boundary creates vertices/edges and adjacency before its owner lists are ready.
Allocation failure leaks pending objects and consumes IDs or changes adjacency
and contour state. Template creation similarly uses raw temporary buffers and
objects before registration. A failed owner-list insertion leaves objects
without an owner. Face::quality also leaks temporary centers and can delete
borrowed input vertices when its temporary Edge unwinds after a later allocation
fails. These failures are reproduced on the immutable entry source snapshot.

## Decision

Boundary retains new vertices and edges in local owners. PendingEdgeDeleter
removes provisional adjacency and detaches borrowed endpoints before deletion.
If the edge owner node was inserted but the vertex owner node fails, the edge
node is removed before the guards unwind. IDs, contour start and outgoing side
state commit only after owner-list insertion succeeds. Successful creation,
adjacency, curve evaluation and registration order remain as before.

TemplateStorage retains the original separate heap pointer buffers, allocation
order and object creation/registration sequence. It tracks successfully adopted
prefixes. On failure it destroys only the unregistered faces, edges and vertices
in dependency order, then the buffers. Registered prefixes remain owned by
Quadtree. On success only buffers are destroyed, in their original order. The
common guard applies to all seven template branches without changing formulas,
candidate scoring, template selection, IDs or owner-list ordering.

Outer vertices register through a local owner before publishing shared pointer
views; outer edges retain a local guard until their owner-list insertion. The
edge creation helper guards both adjacency insertions. Face::quality uses owned
centers and a stack scope to detach its temporary edge before destruction;
the existing arithmetic and successful allocation/deallocation order remain.

## Qualification and limits

The same final 49-case probe/runner fails the pinned original and passes the
repaired campaign. Eight new sweeps deny 1,361 observed allocations,
including Boundary first/append/close, quality temporaries, outer vertices/
edges, and one real type-1 and type-4 template. Counts are measured fixture
facts. The old 35 cases and deliberate instrument controls remain required.
Two public subdivision overloads also reproduce ASan null access when the cell
has no quadtree. They now throw std::logic_error for this missing context; valid
owned-cell subdivision criteria remain unchanged. Eight inherited pointer-null
diagnostics are repaired manually without changing diagnostic rules.
The complete address-free successful UV trace matches original in both ASan
and Debug CRT. Required article and exact-revision regression remain separate.

Boundary failures are qualified for unchanged state and retry in the null-curve
fixture. A failed template tree is qualified for destruction, not retry or
consumption of its partially published observer views. Earlier tree generation/
subdivision, other template patterns, curve internals, general setters/helper
paths, sample/rollback and full-process/parallel/LSan/UBSan remain open. Do not
generalize bounded cleanup evidence into universal exception safety.
