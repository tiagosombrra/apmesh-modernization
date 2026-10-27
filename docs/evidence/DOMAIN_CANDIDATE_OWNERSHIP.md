# Serial domain candidate ownership

Reference main: `e675350df52bdb68648a776325d2c4aeea7bb510` (PR #107).
Classification: behavior-changing exception-safety defect repair. Successful
meshing formulas, floating-point order, selection, retry and acceptance/stopping
policies are preserved. No mesh-quality improvement is claimed.

## Original observations and bounded repair

The serial GeneratorAdaptive caller previously retained raw SubMesh pointers
between generation and consuming MeshAdaptive insertion. The original audit
retains eleven measured runs, six checker corruptions and all failed preparation
artifacts under `build/caller-candidate-audit/`. At Eistute step 4 / patch 0, both
a controlled regeneration exception and one actual 56-byte operator-new denial
leave an unadopted predecessor with 937 nodes / 1796 triangles unreleased. The
outer curve-sample destructor runs. Normal attempts release that predecessor and
the discarded 872-node / 1666-triangle replacement. These are controlled
failure-path observations, not naturally reproduced numerical failures.

Negative evidence is preserved: native step-2 allocation denials release the
observed Book/Eistute candidates; Eistute's second step-2 call is another outer
attempt, not simultaneous pending regeneration. A synthetic Book getter
exception retains 486 nodes / 708 triangles, but the native getter is allocation
free and that injected exception is not presented as a natural getter failure.

The local generation lambda now immediately wraps each fresh raw Adapter result
in unique_ptr. Initial, denser, aggressive and structurally repaired candidates
remain exclusively owned until selection/discard or consuming insertion. Reset
preserves each explicit prior deletion point; moves transfer selected ownership.
Release occurs only into InsertSubMeshAdaptiveByPosition, whose established
contract consumes on entry, including insertion allocation failure. Native
SubMesh teardown retires triangles before their owned copied nodes.

The public Adapter interface, every condition/score/stat lookup and alias,
generation arguments/retry code, ID consumption and patch publication order are
unchanged. The OpenMP implementation is unchanged apart from canonical whitespace.
Terminal process exit is retained. No orchestration rollback or safe retry follows.

## Directed tests and preservation

An explicit friend fixture seeds private caller state without adding a public
runtime setting. GNU-only linker wrappers supply fresh native SubMesh/node/
triangle candidates and stable controlled structural observations while the
actual GeneratorAdaptive caller executes its existing policies. Inactive modes
delegate to production. Thirty cases cover all three optional regeneration
branches, keep/discard, normal completion, exception before regeneration, native
allocation denial during generation, exception after return and actual failed
consuming insertion. Two additional aliased-stat cases preserve the native
lookup behavior rather than silently correcting its selection semantics.
Exact selected identity, publication, insertion count, actual denial count and
release of every observed nonempty native candidate are required. A deliberate
suppressed object deallocation must be detected; eight Python checker controls
reject incomplete/reordered matrices, wrong release/denial data, missing/duplicate
completion, process failure and broken release instrumentation.

The first fixture compilation exposes an ambiguous State name; explicit
qualification corrects it, with the failing log retained. Full caller/fixture
static analysis passes without suppression. The staged gate requires canonical
full-file formatting, so the large legacy caller/header are explicitly formatted.
Retained lexical checks compare 52,826 source and 3,488 header tokens with the
unformatted functional candidate, and reverse only the enumerated ownership
edits to compare the caller with the original. Code outside the serial method
is preserved. Comments/whitespace, adjacent strings, closing-angle spacing and
preprocessor line continuation are normalized; this is not an AST proof. Initial
checker encoding/normalization failures remain preparation observations, not
successful gates. Formatting wraps the C15 source signature; its literal anchor
is updated to the exact newline-bearing signature without changing its contract.
Compilation and numerical regression supply independent checks.

The first exact-head full build rejects a line-sensitive evaluator-extraction
boundary after return-type wrapping. The extractor now requires one exact typed
signature with whitespace allowed between return type and method name, retaining
the existing evaluator-end check. Four controls verify identical original/
wrapped extraction and reject missing, ambiguous, misplaced or damaged bounds.
The failed head report/build log is retained; it is not an integration result.

The initial actual Eistute allocation-denial observation now releases the
predecessor object, all 937 nodes and all 1796 triangles. The immutable original
observer is reused with current production objects. Reports remain under
`build/domain-candidate-repair/`; original executables/reports are preserved.

## Exact delivery gates and remaining work

Require exact-head/main C++17 builds, 60/60 CTest with zero failures/skips and
132 Python controls; all 32 directed native cases plus working release control;
actual Eistute exception and allocation-denial predecessor release; full caller/
fixture tidy/format and lexical, whitespace, inventory and staged gates. Fresh
Eistute/Book comparisons must preserve all nine accepted/rejected states,
boundaries, physical/UV metrics and 45 scientific artifacts, excluding runtime
fields and independently checking relocated compatibility prefixes. Record
revision/tree/executable/input/log identities and remote refs/open PR/checks in
the delivery PR. Initial observations alone do not authorize integration.

Qualification is GNU serial exact-address observation. Prior isolated component
qualification remains bounded to its recorded inputs/revisions; no new full ASan/CRT,
whole-process, parallel, LSan or UBSan qualification is claimed. Stage 3 remains
open and the qualified memory-slice count is unchanged. The reverse-direction
experiment remains unapproved and unexecuted. Next single work: characterize
terminal exception propagation and outer observer/state cleanup before replacing
process exit; metadata/history, repeated retry and accepted-mesh restoration
remain independent guarantees.
