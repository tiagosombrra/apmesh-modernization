# Discrete curvature adjacency transfers

Classification: engineering-only private list-node transfer. Starting revision:
d9e298186f6fa951d6caac976831b74d477c7680. Implements the single package selected
in CURVATURE_COST_SELECTION.md, supporting the blocked S3-08 reuse prerequisite.

CurvatureDiscrete::AdjacencySort now splices its seed from the private working
list into the ordered list. New MoveElementLeft/MoveElementRight operations use
the unchanged first-match predicate scan and splice the selected node to the
destination tail/head respectively. The legacy erase-and-return getters remain
unchanged. Both transferred lists are distinct and use the same standard allocator.
Elements remain borrowed; source NodeAdaptive observers are untouched.

The working-list copy, saved NodeAdaptive value, unconsumed entries, original
boundary decisions and additional closed-fan push_back remain. That extra entry
is a duplicate incidence, not a transfer. Area/angle reduction, concavity, mean/
Gauss arithmetic, predicate order, virtual fallback and scientific policies stay
unchanged. The CurvatureDiscrete header/layout and existing public signatures are
unchanged. Adjacent gains two nonvirtual methods without fields/layout changes.

Whole-source reversal removes only the two new Adjacent methods and reverses
seed/left/right transfer bindings to restore the preceding units modulo identical
formatting. Each new scan separately restores its legacy counterpart by reversing
names, the destination argument and splice/erase. No formula or solver change.

## Independent reference and finite validation

Reports, exact commands, source/binary hashes and retained baseline executables:
build/curvature-adjacency-transfer/.

Before production changes, freeze the complete old constructor, sorter and
mean/Gauss implementations in a test-only reference. Source proof permits only
identifier mappings, namespace/inline linkage, comments and formatting. The
reference calls the preserved legacy getters, independently of the new transfers.
Both canonical GCC and checked-MSVC baselines pass the same 120 exact/virtual
fan comparisons. Reference bytes stay unchanged throughout implementation.

The existing 60 planar/curved, open/closed and insertion-order fixtures now compare
production mean/Gauss bits against that frozen reference for both dispatch paths.
Another 912 checks per ABI reuse those fans to verify first matches, duplicate
entry identity, remaining-list order and destination tail/head behavior, including
48 unmatched searches. Actual list-node addresses survive transfer. Existing
virtual-fallback and source-observer controls remain in place; no new model or
CTest target is added.

The same real Debug CRT observer measures complete construction, calculation and
destruction on the existing curved fan, with default iterator checking level 2.
Before the fix, both implementations use 15 allocations/frees for the open fan
and 19 for the closed fan. Afterward the frozen reference stays at 15/19 while
production uses 12/15. Mean/Gauss bits and source observers agree, every allocation
is released and a separate real new/delete control reports 1/1. The three/four
saved pairs match the selected incidence counts, including the seed. This is a
bounded allocation reduction, not whole-process accounting or a runtime speedup.

Canonical C++17 GCC and checked-MSVC builds pass. Existing 75 CTest/389 Python
controls, native controls, scoped analysis including the production/reference
headers, explicit formatting and architecture inventory/contracts pass. Frozen
GCC Eistute retains five states, 25 exact artifacts and 15 independently compared
boundary incidences: accepted 0/1, rejected 2/3/4 remain unchanged.

## Retained limitations

No long MSVC Eistute pair, Book run or retry was performed. Earlier 300-second
timeouts remain negative evidence; the combined 50.2315 s curvature phase is not
attributed to sorting and no timing resolution is claimed. Node transfer removes
allocation failure points, so previous denial ordinals cannot qualify the revised
path unchanged. Empty adjacency and broader failed-call recovery remain separate
preconditions/obligations. Revised-head timed reuse, Book, exact-delivery/main and
Stage 3 gates remain open; the candidate stays unintegrated.
