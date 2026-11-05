# Contiguous AFT face incidences

Classification: engineering-only temporary-storage optimization supporting the
unintegrated S3-05/06/08 adaptive-reuse candidate. Starting head:
8edbb2bd283b5c4ca3c96587e6dc548225e3f07a.

Corrected GCC stage accounting identifies patch reconstruction at 5.32355 of
6.19113 full-generation seconds. Prior native stack sampling also reached
poorRegionShapeSmoothing. The scoped face index still allocates and traverses a
linked-list node for each incidence in these topology-stable smoothing passes.

Replace those temporary incidence lists with per-vertex contiguous pointer
sequences. A structural endpoint pass counts each distinct endpoint once per
mesh entry; reserve one buffer per populated vertex; a second identical pass
appends face observers in original mesh order. Duplicate mesh entries stay
duplicate and repeated endpoints within one entry contribute once. Hash iteration
only reserves storage. Nothing is cached from coordinates, quality or scores.
Missing keys return an immutable empty sequence. RAII releases every container
on return/unwind; face and vertex ownership stays outside the index.

The three smoothers and local score use the new sequence/iterator types. Reversing
only those types and one alias restores the entire AFT implementation after
identical clang-format normalization. All arithmetic, comparisons, face and vertex
orders, trial/acceptance logic, edge adjacency, mesh owner lists, topology and
scientific policies remain unchanged. The internal template's result container
changes; public mesh getter types, front/generator layouts and virtual interfaces do not.

## Bounded evidence

Exact commands, sources, binary identities and reports: build/aft-contiguous-incidences/.
The existing adjacency control crosses the container boundary using size plus
ordered equality, retaining every existing oracle and negative control.

One actual checked-MSVC Debug CRT observation on the same five-entry fixture
counts 28 allocations/frees through the old index and 17 through the new one.
Counts and order-sensitive sums match; the separate real new/delete positive
control counts 1/1. Both implementations run in the same process against the same
live objects. This is a bounded construction/traversal/destruction comparison,
not process-wide allocation accounting or an end-to-end speedup benchmark.

Canonical GCC/checked-MSVC builds, 75 CTest/389 controls, existing native controls,
scoped analysis including the modified header, source-order proof and inventory/
contracts pass. Frozen GCC Eistute retains five states, 25 exact artifacts and
15 independent boundary comparisons, accepted 0/1 and rejected 2/3/4.

The first source proof rejected formatting-only line wrapping; its diff is kept.
The local allocation harness initially failed to compile on an undeclared Windows
TRUE macro; changing its hook return to integer 1 fixes that setup without adding
Windows dependencies or changing production. No failed runtime control is promoted
to qualification. The original CRT stdout bytes are retained alongside UTF-8 JSON.

## Fixed MSVC reuse observation and limits

One new-binary Eistute pair preserved the same input/configuration, Debug iterator
checks, assertion hook and total 300-second cap. The first call completed with
five independently checked states, 15 positive boundary comparisons and all
25 prior-version scientific artifacts exact. Accepted 0/1 and rejected 2/3/4 stay
unchanged. The second call remained incomplete at the deadline (300.011 s;
300.038 s including termination). No retry or Book run followed. Buffered native
return markers were not flushed; no two-call archive/FindUV equality is claimed.
Prior live output was restored byte for byte and all earlier failures remain.

The repaired first-call MSVC summary reports patch reconstruction 82.6533 s,
curvature 50.2315 s, curve update 18.9422 s and full generation 152.153 s, excluding
2.19173 s output accounting. These are diagnostic phase totals, not separately
measured call wall times or a speedup comparison. The curvature slot combines
analytical and discrete work; it does not attribute that time to node copies.
This valid ABI-specific evidence constrains further production selection. Do not
automatically add another container/evaluator rewrite or repeat this campaign.

The local allocation reduction is demonstrated; sufficient whole-process timing
improvement is not. Timed reuse, revised-head Book, exact-delivery/main and
remaining Stage 3 obligations stay open. The candidate remains reviewable but
unintegrated; this package does not close the stage.
