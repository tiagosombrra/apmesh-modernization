# Portable pointer order for AFT edge counts

Classification: engineering-only pointer-identity canonicalization. Entry main:
`dfcfea67df41890e6eb838014a041cd7a75ef358` (PR #173). This removes a concrete
portability gap in the existing production ComputeStageFaceStats helper; it does
not claim a reproduced numerical error or introduce a scientific policy change.
The [compact evidence](stage3/aft_pointer_order/summary.json) identifies commands,
native controls, exact source scope, scientific comparisons and limitations.

## Production change and invariant

Two loops canonicalize an undirected edge before counting or looking up its uses.
Both previously used built-in relational comparison of Vertex pointers that can
refer to independently allocated objects. Such comparisons do not supply the
required total-order guarantee. The standard-library pointer specialization of
std::less supplies an implementation-defined strict total order. See the primary
draft clauses [relational operators](https://eel.is/c++draft/expr.rel) and
[comparison objects](https://eel.is/c++draft/comparisons.general).

Replace exactly those two expressions with std::less<Vertex*>. The existing
functional include suffices. The full production file otherwise remains byte
identical to the entry revision. Pointer equality/hash, duplicate incidence
counts, face traversal, floating-point evaluation, thresholds and classification
branches remain unchanged. No pointer-to-integer conversion, coordinate/ID key,
container replacement, new ownership or public signature is introduced.

The canonical direction is an internal key choice. Hash-table iteration never
determines the quality reduction order; the existing face list still does.
Live-endpoint and valid-caller preconditions remain. This change neither repairs
expired pointers nor expands the supported scientific input domain.

## Independent native contracts

Extend the existing AftContextProbe edge-count control, keeping its original
65 empty/duplicate/orientation/order cases. Add 72 bounded heap-identity cases:
six allocation orders, six face-list arrangements and both traversal directions.
Vertices are independently owned and include distinct objects with identical
coordinates and IDs. The arrangements include reversed shared incidences,
duplicate face entries and geometrically coincident but distinct endpoints.
These are diagnostic classification inputs, not newly qualified accepted meshes.

The new reference counts each undirected incidence by direct pointer equality
against every face edge. It neither sorts pointers nor hashes them. The right
isosceles control geometry has no transition-classified interior faces; expected
boundary/internal counts follow independently from those incidences. Face owners
detach borrowed endpoints before destruction; vertex owners outlive them.

Before production edits, the augmented probe passes all 137 cases against the
preserved GCC and checked-MSVC engine archives. Candidate probes link the actual
rebuilt engine archives and pass the same contracts with exact aggregate output.
A separate deliberately wrong ID-order variant changes only the two comparisons
and relocates its two includes. Each ABI rejects it with the expected independent
edge-multiplicity diagnostic and exit 1. The incorrect variant never runs a model
or enters the production delivery tree. No selector, tolerance or expected count
is substituted to make a control pass.

The standalone controls reuse the complete canonical archives, C++17 and their
actual Release/checked-Debug ABI. They add no central CTest target. The new
--aft-edge-counts entry belongs only to the existing test executable; its normal
required application control also runs the expanded cases.

## Finite validation and delivery

Require canonical GCC/MSVC builds, native baseline/candidate controls and both
wrong-order negatives, read-only configured LLVM analysis and explicit formatting.
Use the existing frozen Eistute/Book references with unchanged 300-second caps:
per ABI, nine states, 45 exact scientific artifacts and 123 positive boundary
comparisons, retaining accepted and rejected decisions. No timing or speedup
claim follows. Preserve completed captures and inspect a failure before any
further native execution.

The working candidate passes both canonical builds, all 137 native cases per ABI,
both expected wrong-ID-order rejections and all four frozen article executions.
GCC and MSVC each preserve nine states, 45 exact scientific artifacts and 123
positive boundary comparisons. Configured LLVM 22.1.8 analysis passes the full
production unit and test fixture without user-code diagnostics; configuration and
warning policy are unchanged. Formatting is explicit and confined to the new test
additions. The architecture inventory refresh changes only the production file's
hash/byte count, preserving 164 files, 35 contracts and 276 anchors. All other 521
protected production/build/input files and all 43 original retained-block artifacts
remain byte-identical. Exact delivery/main regression is still required below.

Require the complete 75 CTest / 495 Python baseline on the exact delivery commit
and merged main, source/contract/inventory/whitespace and fresh remote gates.
After merge, use the guarded same-tree checkout, retain its receipt, repeat main
regression/builds and check the qualified native artifact identities. Changed
artifacts require their affected gates; source equality alone is insufficient.

Prior Linux UB/leak, ASan/CRT and ownership observations retain their recorded
artifact/caller scopes. This package changes no allocation/publication operation
and adds no independent instrument campaign or broad safety claim. The original
43 retained-block artifacts and earlier rejected/failed evidence remain intact.
The ten Stage 3 dispositions stay three bounded-qualified/seven partial-open;
broader callers/domain/mutation/foreign observers/recovery/parallel and known
documentation obligations remain open.
