# Keyed edge counts in AFT statistics

Classification: engineering-only container optimization, starting at
f73e3c84a8cfd9fa5b68b58a9a6a908fd6053089. Main remains d1619137.

ComputeStageFaceStats previously used an ordered tree for canonical endpoint-pair
counts. No consumer traverses that tree: each face only increments or queries its
three keys. Use a local unordered_map with exact endpoint equality, a pointer-pair
hash and capacity reserved from the face count. The counting work changes from
O(F log E) tree lookup to expected O(F) hashing; worst-case hash complexity is not
claimed to be constant.

The two existing face/edge loops, canonicalization expression, unsigned counter
type, every increment, query, floating-point expression and classification rule
remain unchanged. Duplicate face occurrences and repeated edges are still counted
individually. Hash iteration never drives a reduction. All storage is local and
non-owning; no geometry, IDs, synchronization or scientific policies change.

## Change-relevant validation

Commands, hashes and compact reports: build/aft-edge-count/.

- Canonical GCC/checked-MSVC C++17 builds pass with unchanged compiler/runtime
  settings. Scoped analysis uses the actual compilation commands.
- The existing AFT fixture is shared by both native probe builds. Its 65 checks
  cover empty input, all 16 duplicate-face masks, both face traversal directions
  and swapped edge endpoints. Known boundary/transition/internal counts agree.
  The fixture's original smoothing payload and prior native controls remain.
- Existing regression: 75 CTest/389 Python controls pass. Frozen GCC Eistute
  retains five states, 25 exact artifacts and 15 independent boundary comparisons,
  including accepted 0/1 and rejected 2/3/4.
- Whole-unit source comparison admits only the container, endpoint equality/hash,
  reservation and include changes. The initial byte comparison rejected an extra
  blank line; its diff is retained. Explicit formatting preserves tokens.
  Inventory/contracts are current; no baseline or scientific oracle is relaxed.

## Fixed Eistute observation

One new-binary checked-MSVC two-call process, same input/configuration/assertion
hook, Debug iterator checks and total 300-second cap. No Book or additional model
run, timeout increase or automatic retry. Original live output is archived for the
observation and restored byte-identically. Prior binaries and failures remain.

The process reaches its deadline at 300.001 s; termination completes at 300.005 s
during the second call. The first call preserves five independently verified states,
25 exact prior-version artifacts and 15 positive boundary comparisons, with the
same accepted 0/1 and rejected 2/3/4 trace. The second call remains incomplete and
unqualified. There is no further execution, and the original live output is restored
byte-identically. Reports: preflight.json, source-proof.json and
msvc-eistute/process.json plus verification.json.

The keyed-count container change is retained as a reviewable engineering package;
it does not establish a measured end-to-end speedup or resolve the timed reuse gate.
This package does not by itself close Stage 3 or qualify the remaining delivery,
Book, memory/parallel or main gates.
