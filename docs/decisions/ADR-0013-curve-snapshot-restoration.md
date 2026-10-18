# ADR-0013: prepare the full curve sample graph before restoration

Status: candidate qualified; exact published-head and implementation-main gates required.
Issue #41. Classification: ownership/exception-consistency defect repairs and
engineering extraction, preserving successful policy.

Original restoration deletes the unique live samples, then allocates a raw node
map and per-curve lists. Twelve original failure sweeps destroy live samples at
ordinal 6; four publish partial lists at ordinal 18. Stop before consuming their
invalid graph: subsequent ordinals and CRT retention are unmeasured in those
16 cases. Four empty-to-single sweeps isolate unowned raw-node loss and complete
with six retained blocks each. The other 69 original outcomes are expected.

Collect old unique pointers without deleting. Prepare unique NodeAdaptive owners
by the same first-encounter ID policy and prepare every ordered pointer list.
Swap each live list directly, release the pending node owners, then delete each
unique old sample exactly once. Using by-value SetPoints after preparation could
still allocate during list argument construction on MSVC; direct existing-list
swap avoids that allocation. Default allocators match. The commit contains no
allocating operation for the initialized built-in curves and nonthrowing sample
destructors in scope. Failure before commit preserves original object/list-node
identities and allows retry. Success intentionally invalidates those observers.

The curves collectively exclusively own/deletably reference the current samples;
the existing successful raw sample ownership convention remains. Parameters are
neither captured nor restored. Null geometry/count mismatch remain no-ops. Reuse
by first ID preserves even conflicting-ID first-value behavior, without approving
such input. Recreated nodes retain existing zero curvature/adjacency initialization.
Independent physical mesh copies stay intact in the fixtures. Full mesh/patch
binding/history/budget/acceptance rollback and competing owners/custom subclasses
remain outside this measured contract. This does not resolve C12's broader scope.

New target: 15 actual production units, four curve kinds, five restoration
layouts and two capture layouts. Original: 14 pinned units plus mechanically
extracted, hash-verified lambda bodies with identical snapshot field layout;
not the complete old Generator translation unit. New Debug CRT target uses
consistent non-debug iterator metadata to avoid allocating proxies in noexcept
construction, retaining actual heap checks and negative controls. This is not
cross-compiler ABI or iterator-debug-level-2 recovery qualification.

Candidate 89/89 outcomes include 28 sweeps/536 denied ordinals and deliberate
use-after-free, leak and allocation-hook controls. Empty fixtures remain explicit
guards, not positive graph coverage. Original/candidate complete normal logs
match; preparation intentionally changes allocations/peak storage and timing.
Previous instrument batteries, CTest 22/22/zero skips/74 controls, selected
read-only lint and exact repeated default-model regression pass. No formula,
floating-point ordering, incidence/synchronization, verifier, tolerance, budget,
quadtree/template/front or adaptation/acceptance/stopping change. Doxygen API
warnings remain stage 8; full-process/parallel/LSan/UBSan remain unqualified.
