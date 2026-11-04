# Registered Patch/SubMesh observer retirement

P4 engineering lifecycle repair, starting at main
a97105da94fc18ad80eb08c5201ca4f411985455 (PR #159).
The admitted defect is normal owner retirement in either order: a Generator
can die while its caller's Geometry survives, or Execute can destroy its local
Geometry while the outer Generator retains physical meshes. Previously the
survivor kept an expired pointer. The unchanged three-patch Bezier reader fixture
reproduces both through the real Generator and typed Execute, without failure
injection. Safe identity/null observations establish the defect; they do not
consume expired objects or claim an original whole-process sanitizer failure.

SubMesh::SetPatch now registers a null or live Patch in an intrusive observer
list. The Patch borrows every registered SubMesh, including archived/rejected
meshes, while its existing forward link identifies only the current mesh.
SubMesh destruction or explicit rebinding removes its registration and clears
the former Patch's forward link only when it still equals that SubMesh. Patch
destruction clears every registered back pointer. Neither path allocates or
deletes the borrowed object. Physical elements still retire before their nodes.
No generator algorithm, formula, ID, reconstruction, synchronization, selection,
acceptance or stopping policy changes.

Object moves keep the existing pointer-value contract: a moved-from SubMesh
retains its Patch observer; the destination gains a separate registration.
Move assignment still destroys old elements before replacing their nodes and
does not rebind foreign forward links. Patch moves copy the original ID/forward
values but leave registrations attached to the original object addresses.
Pointer-copy construction remains detached. Layout changes require rebuilding
consumers. SetPatch requires an actual live Patch, rather than an opaque address;
the existing move probe now uses real objects while preserving its identity,
adjacency, scalar and teardown checks.

Patch::SetSubMesh remains a borrowed assignment. Arbitrary forward-only, copied
or unmatched foreign links are not registered by that operation and remain the
caller's lifetime responsibility. Retirement compares such values without
dereferencing them. This package does not repair geometry caches after public
mutation, transfer observers across moves, establish Generator recovery/reuse,
or qualify concurrent/parallel generation.

## Finite validation and delivery gates

The original executables and logs under build/patch-submesh-retirement show both
public-caller results false and the isolated retirement oracles failing. The
initial isolated launcher named a nonexistent path; no process ran there. That
launcher record is retained separately; the generated bin path was then used.
The repaired callers require positive registration of all three patches and
null surviving observations in both orders. The existing metrics CTest includes
these two normal caller paths; its previous controls are preserved.

The existing SubMesh lifetime probe covers both teardown orders, multiple retained
meshes, head/middle/tail removal, idempotent/null rebinding, foreign-forward
preservation, both move directions, self-move and detached pointer copies.
The existing MSVC ASan/Debug CRT runner retains its 28 controls and adds three
registered-observer observations, including denial of every allocation during
the new operations. Require all 31 outcomes, zero retained normal blocks and
working actual UAF/leak/allocation-denial controls. This instruments the seven
actual patch/mesh/node/element/triangle/point/vector units; it is not a new
complete-process qualification campaign. Stop at the first unexpected failure.

On exact delivery head and merged main require the canonical GCC/MSVC C++17
builds, existing 75 CTest entries/389 Python controls, existing native negative
controls and all 14 context markers. Preserve the frozen nine Eistute/Book states,
45 exact artifacts and 123 positive boundary comparisons, including accepted/
rejected traces and IDs, plus all three same-profile FindUV summaries. Require
the existing 23 MSVC invalid CLI controls and one analytic state/boundary.
Source identity proves all other production and all scientific inputs unchanged;
reviewed lifecycle slots, explicit token-preserving formatting, scoped analysis,
inventory/contracts, whitespace, staged and remote gates remain mandatory.
Commands, revisions, binaries, logs and integration seal are recorded locally.

This closes the named registered Patch/SubMesh retirement sub-obligation of
S3-05/07. The seven partial/open row statuses remain: foreign forward arrangements,
mutation/cache validity, broader callers, UV paths and complete-process instruments
retain their independent requirements. Stage 3 is open; its closure audit is P5.
