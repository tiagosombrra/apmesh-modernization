# Bezier FindUV array scratch

Classification: engineering-only local numerical storage replacement. Starting
revision: 836df73fb973971b73c021f288a00966aed65e6d. Only the private 3x3 scratch in
PatchBezier::FindUV changes to nested std::array in C++17. The nine coefficients
remain fully assigned before use. The public matrices, Bezier products/getters,
Hermite solver, ABI and Eigen dependency remain unchanged.

One declaration, 35 coefficient accesses and two row swaps restore the entire
preceding production file modulo identical formatting. All floating-point
expressions, assignments, pivot search/comparisons, row-reduction order, damping,
clamp, convergence/I_MAX policy, counters and diagnostics are preserved. The CPU
Eigen scalar swap path calls std::swap; array row swap exchanges the corresponding
three doubles. Row pairs are disjoint or identical, with no floating-point
arithmetic in these exchanges. This is not an alternative solver or Eigen removal.

## Finite analytic and differential validation

Exact commands, source/binary hashes and retained before-edit binaries are under
build/finduv-array-scratch/. Freeze the complete former Eigen FindUV and its three
constants before editing production. Only receiver binding, inline linkage,
comments and formatting differ in that test-only reference. Both before-edit
GCC/MSVC controls pass; its reference bytes remain unchanged afterward.

The existing metrics target runs 75 bounded cases per ABI. Six affine maps cover
three first-pivot rows, self-swaps, second-pivot fallback, a skew basis and the
exact tolerance boundary. Initial/interior/outside points use limits 1/64.
Singular first/second pivots and NaN/infinite inputs retain their original outcomes.
The existing live charge-input fixture supplies 22 more cases, independently
checked against x=u, y=v and z=(2u*u+u+2v*v+v)/24 before inverse comparison.

The controls require bitwise UV equality, identical virtual-call arguments/order,
final public U/V state, scoped call/I_MAX counts and exact diagnostic transcripts.
Analytic expectations are checked separately. Both paths record 34 I_MAX exits
over the fixed cases. A deliberately changed result bit must fail the comparator.
No new model or CTest target is introduced.

Canonical C++17 GCC and checked-MSVC builds pass. Existing regression passes
75 CTest and 391 Python controls: the original 389 plus two source-guard controls.
Frozen GCC Eistute retains five states, 25 exact scientific artifacts and
15 independently compared boundaries, accepted 0/1 and rejected 2/3/4. Scoped
analysis admits the new reference header; formatting and inventory/contracts pass.

## Preserved failures and source-guard admission

The initial suite records 73/75, with failures in the historical detached-copy and
Bezier observer preservation guards, which require the former storage syntax. Their
reports/JUnit remain retained. A new shared normalizer reverses only this exact
scratch declaration, access syntax and swaps, then requires the complete compact
previous FindUV SHA-256. Other unit tokens still match the immutable historical
baselines. All original mutation controls remain, with new checks rejecting
pivot, swap, arithmetic, iteration/counter and external damping/tolerance changes.
No diagnostic is suppressed or numerical allowance generalized.

The first normalizer calibration rejected a hash built with the Windows default
text decoder; the corrected pin explicitly reads the original UTF-8 text. Its
initial failed controls remain. Earlier preparation also rejected an incorrect
expected access count of 29 before writing production; the actual 35 accesses
are used and independently reversed. A stale C16 source anchor was corrected
before regression. These setup failures do not qualify as successful observations.

No long MSVC reuse pair, Book run or retry of that campaign was performed. Both
old and new scratch are fixed-size local storage; no allocation or runtime speedup
is claimed. Earlier 300-second failures remain negative evidence. Timed reuse,
revised-head Book, exact-delivery/main and Stage 3/full Eigen replacement remain
open; the PR stays a draft.
