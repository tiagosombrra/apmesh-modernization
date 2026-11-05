# Temporary pointer membership in fillMesh

Classification: engineering-only lookup optimization. Starting revision:
aec5578c0c1825526db1cd1b8d4bc9d74d670cf5. The qualified function profile identified
73 of 86 fillMesh stacks at the growing edge-list membership scan. Replace only
the two nested membership scans with scoped std::set<Vertex*> and std::set<Edge*>.
For P prefix entries and Q candidates, membership work becomes
O((P + Q) log(P + Q)) instead of quadratic scans. No runtime speedup is claimed.

The ordered sets store borrowed pointers and are never traversed to publish
objects. std::less supplies pointer ordering; coordinates and IDs are not keys.
Existing list duplicates remain; candidates are still popped in source order and
only their first missing pointer is appended. The vertex index is destroyed
before edge preparation; both indexes are gone before TransferTemplateMesh.
Empty candidate lists do not construct an index. All other production bytes,
including the final nonthrowing owner-list splices, remain unchanged.

## Allocation and publication contracts

List copying, index construction/seeding/insertion and observer-list append may
throw before ownership transfer. On failure, the quadtree retains every owner;
published observers form ordered prefixes. A subsequent call rebuilds membership
from those prefixes and commits owners once. New allocations change denial
ordinals; historical fault-injection results are not inherited unchanged.

The initial unordered_set candidate is rejected. Checked MSVC 14.44's xhash
allocator-taking _Hash_vec constructor is noexcept but allocates a debug proxy;
denying that allocation terminates the process before bad_alloc reaches the caller.
The exhaustive local control reproduced the abort after the three historical
sampled denial points had passed. A retained symbolized stack locates this
constructor at xhash:261 from fillMesh's vertex index construction. Use ordered
membership to keep allocation failures catchable without disabling iterator
checks, adding a custom allocator/table or changing scientific policy. Other
pre-existing hash containers are outside this package; no general repair is claimed.

## Finite validation

Commands, source/binary hashes and reports remain in build/fill-mesh-membership/.
The earlier profile binary/PDB and pre-change application binaries are preserved.

- Before production edits, calibrate the independent former scans on GCC and
  checked MSVC. Both original loop bodies match the test reference after only
  type/receiver/local-name binding; its bytes remain frozen afterward.
- Reuse transfer-order in the existing UV probe, without a new target or model.
  Twelve cases per ABI compare exact pointer sequences, initial duplicates,
  empty/full/partial overlap, reversed prefixes, null prefix entries and distinct
  objects with equal coordinates/IDs or endpoints/IDs. Twelve repeated empty
  transfers retain owner order/multiplicity and consume source owners exactly once.
- On the same checked-MSVC fixture, all 515 measured successful-path allocation
  ordinals are denied individually. Each propagates one bad_alloc, retains all
  source owners and only ordered observer prefixes, then permits a complete retry.
  The real allocation-denial positive control, original three-point control and
  existing UV contracts pass. Debug CRT reports zero retained blocks/bytes.
- Complete canonical GCC and checked-MSVC C++17 builds pass, as do the unchanged
  native metrics controls. Existing regression passes 75 CTest/391 Python controls,
  including its negative controls. Frozen GCC Eistute preserves five states,
  25 exact scientific artifacts and 15 independently compared boundaries:
  accepted 0/1 and rejected 2/3/4.
- Whole-unit comparison permits only fillMesh membership and one include; the
  remaining production, formulas, IDs, templates, synchronization and policies
  are unchanged. Scoped analysis uses actual compiler commands for both changed
  units. Explicit formatting, whitespace, inventory and contract checks pass.

The rejected hash source/binary and initial fault report remain retained. The
initial evidence preflight also rejected UTF-16 PowerShell log bytes before any
scientific launch; explicit decoding recovers the existing native markers without
rerunning those controls. Neither failure is reported as a passing observation.

No new long MSVC reuse pair, Book run or expanded scientific campaign occurs.
The short frozen GCC case is the existing preservation gate. Earlier 300-second
failures remain negative evidence. Timed reuse, revised-head Book, exact-delivery/
main, broader memory/parallel obligations and Stage 3 remain open; the PR stays
a draft. This delivers the bounded lookup change, not integration or stage closure.
