# Coordinate snapshots for curvature adjacency

Classification: engineering-only removal of unnecessary owning-container copies.
Starting head: 11067110fc0ce59ae19cac1e6ff9d1f1418a8a6a; main remains d1619137.

The unchanged AFT-index binary completed one observed Eistute pair in 289.468 s
(283.781 CPU s), despite its retained earlier 300 s timeouts. Five valid stack
samples span curve integration, face statistics, local smoothing and discrete
curvature adjacency; suspension totaled 26.191 ms. These samples locate work,
not statistical runtime percentages or stable performance qualification. Both
completed calls preserve five states, 25 exact artifacts, 15 independent boundary
comparisons and 14,660 FindUV/1,542 I_MAX counts. Prior failures remain retained.

The discrete-curvature sample reaches NodeAdaptive destruction through repeated
GetNoh calls in Adjacent. Each getter copies a node's element-observer list even
though these consumers only compare its point coordinates or construct vectors.

TriangleAdaptive now offers a nonvirtual GetVertexPoint value accessor: copy the
PointAdaptive coordinates/ID directly, without copying node element observers.
The existing virtual GetNoh, class fields/layout and ownership operations stay
unchanged. Invalid accessor positions retain GetNoh behavior. Valid positions
require live nodes, like the existing getter.

Three Adjacent entry points admit this path only for exact runtime TriangleAdaptive
objects. Custom elements and derived triangles retain virtual GetNoh, NodeAdaptive
values and full-expression temporary lifetimes through the original value path.
No observer is returned or retained. Source comparison reverses exactly 86 call
bindings and the checked admission wrappers; every original comparison, short
circuit, arithmetic expression, ordering loop and remaining triangle token matches.
There is no formula, tolerance, synchronization, acceptance or stopping change.

## Finite validation

Commands, hashes and reports: build/curvature-point-access/. Baseline observation:
build/aft-residual-cost/. No new model, test target or instrument implementation.

- Canonical GCC and checked-MSVC C++17 builds pass. A central-header dependency
  rebuild was deliberately paused after its active compiler jobs completed, then
  resumed with three build jobs instead of two. The scheduling record and original
  log are retained; compiler options and serial runtime settings are unchanged.
- Existing metrics control: 60 planar/curved, boundary/closed-fan and insertion-order
  cases compare the snapshot path with virtual legacy-node values. Adjacency and
  concavity agree; mean/Gauss curvature and point payloads agree bit for bit. Node
  observers remain unchanged; later coordinate mutation yields a new snapshot.
  A derived triangle with virtual coordinates and null base vertices exercises the
  required fallback. These controls pass on GCC and MSVC.
- Existing regression: 75 CTest/389 Python controls pass, retaining the original
  ownership, negative and accepted/rejected controls. GCC Eistute preserves five
  states, 25 exact artifacts and 15 independent boundary comparisons.
- Scoped analysis uses actual commands for three changed translation units;
  explicit formatting preserves tokens, and inventory/contracts are current.
- A bounded real-allocation observation links the same checked-MSVC engine and
  reuses the Debug CRT hook mechanism. The hook permits actual allocations and
  independently detects one new/delete control. The identical adjacency result
  uses 30 allocations/30 frees through legacy node values and zero through point
  snapshots; source observers remain unchanged. This is one measured comparison,
  not a process-wide allocation total or runtime-speedup claim. Its initial build
  rejected an unavailable Boolean macro and then a duplicate runtime definition;
  both setup failures are retained. Neither required another generation.

## Same-case MSVC measurement

One new-binary Eistute process, same input/configuration/assertion hook, Debug
iterator checks and total 300-second cap for both calls. Prior outputs and binaries
are preserved. The deadline is reached at 300.012 s; termination completes at
300.030 s during the second call's step 4. The first completed call independently
preserves five states, 25 exact artifacts and 15 boundary comparisons against the
baseline. The second remains partial and unqualified. No repeat or Book run is
performed. The original live output is restored byte-identically.

The measured allocation reduction is retained as a production engineering
improvement. It does not demonstrate sufficient end-to-end speedup or resolve the
300-second gate; the unchanged binary's earlier 289.468 s completion also remains
an observation of timing variability, not permission to discard prior timeouts.
Reports: preflight.json, source-proof.json, allocation-observation.json and
msvc-eistute/process.json plus verification.json.

Book and remaining exact-delivery/main gates are not qualified by this package.
The PR remains a draft until those obligations pass; Stage 3 remains open.
