# Allocation-free face quality scratch

Base main: `31862ed72020038605bd677cb2b3e05c0ebf4050` (PR #136).
Classification: engineering-only allocation/performance correction. The measured
SP-05 process previously exceeded its fixed 60-second cap. A separate bounded
CPU/stack observation retained 59.09 CPU seconds and Face::quality in five of six
stacks, including temporary Vertex/Edge allocation and destruction. Both original
timeouts and their inputs/logs remain sealed; no completed original runtime or
general benchmark speedup is inferred.

## Bounded production change

Only src/crab_mesh/aft/face.cpp changes in production. Private coordinate pairs
hold the incenter/circumcenter results and supply the same distance expressions.
The original center arithmetic is extracted without algebraic rewriting; the
public methods still return exclusive Vertex owners. Face::quality no longer
constructs a temporary topology Edge or heap Vertex centers/caches. It keeps the
three ordered inradius comparisons, three ordered circumradius comparisons and
the final `2.0 * rInsc / rCirc` expression. Edge, Vertex, templates/front selection,
boundaries, adaptation, thresholds and stopping policies remain unchanged.

Allocation timing/counts and the opportunity to throw bad_alloc inside quality
intentionally change. No noexcept, new invalid-input guard, clamping, geometry
formula or floating-point compiler option is introduced. Public layouts and
owning center-return APIs remain unchanged. General fenv/errno equivalence and
unmeasured platforms are not qualified by these value/lifetime observations.

## Equivalence and resource observations

The focused native probe compiles the actual production geometry units. Its
separate reference executable compiles immutable original face.cpp with identical
headers and ABI/profile. Thirteen directed triangles and 128 fixed-seed dyadic
triangles, each in six permutations, cover analytic, obtuse, skinny, translated,
scaled, degenerate, extreme and signed-zero cases. No scientific model is added.

GCC C++17, MSVC/ASan RelWithDebInfo and MSVC checked Debug each compare 846 rows:
4,230 quality/public-center double bit patterns are exact per profile, including
the legacy degenerate outcomes. Independent equilateral/right-triangle values,
face endpoint/cache/identity and caller adjacency checks pass. These are paired
same-ABI comparisons, not universal cross-compiler bitwise claims.

Original quality allocations per call are 12 (GCC), 24 (MSVC/ASan) and 36 (MSVC
Debug); the candidate records zero. Each candidate executes all 846 calls again
under allocation denial with equal quality bits. A separately compiled real
allocation is actually denied. The original implementation fails the new zero-
allocation contract, independently checking that the gate distinguishes it.

The legacy Debug CRT face-quality-failure scenario now checks two actual metric
calls, zero attempts, identical geometry/value and an independent detected hook.
The qualifier requires that completion marker and zero retained blocks/bytes;
it does not accept a zero-of-zero failure sweep. Other denial scenarios and all
historical original/failure reports stay intact. A dedicated existing-suite entry
application.face_quality_scratch uses the focused candidate probe.

The first GCC reference build refused its relocated relative include. Its source
and failed log remain preserved. The focused include search now includes the
original source directory, resolving the unchanged production header without
editing the immutable reference or numerical assertions.

## One SP-05 observation

The complete 73-unit serial MSVC/ASan C++17 target is rebuilt in a separate owned
directory. The original binary/runtime/evidence stay intact. With the unchanged
admitted input/configuration and only output-prefix relocation, the candidate
runs SP-05 once under the same 60-second cap. It returns zero in 13.0484 seconds,
with empty stderr, accepted 0/1, rejected 2/3, actual retry 1, and eight positive
independent boundary-incidence comparisons. Physical/UV/analytic/refined-boundary
checks pass on the complete trace. This is one bounded observation, not Stage 9
performance qualification or a full memory/instrument inventory pass.

The old timed-out run's three completed states retain 16 exact mesh/incidence/
acceptance/quality/adaptation artifacts and three exact metrics rows. The partial
original remains a failed process, not successful generation qualification.
SP-02 and other ASan production cases are not rerun or expanded here.

## Delivery and limits

Require exact-head/main 75 CTest entries, zero failures/skips and the existing
380 nested Python controls; focused equivalence/hook/control identities; scoped
analysis and explicit formatting; source/input/contract/inventory/whitespace and
remote/staged audits. Preserve the current C++17 GCC Eistute/Book reference: nine
accepted/rejected states, 45 exact scientific artifacts and 123 boundary checks.
This existing regression does not expand the fixed ASan campaign. Reuse the one
SP-05 observation by identical production/tool/artifact/configuration identities.

The [compact evidence](stage3/face_quality_scratch/summary.json), PR and local
build/face-quality-scratch records bind source, binaries, commands, comparisons,
refusals and exact delivery revisions. Required failing/unmeasured gates block
integration. Stage 3 remains open with its prior bounded/partial dispositions;
other production cases, directed observer portability, CRT/LSan/UBSan and parallel
coverage retain their own remaining observations. No baseline or policy changes.
