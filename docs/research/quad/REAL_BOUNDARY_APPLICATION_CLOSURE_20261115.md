# Original-curve QUAD/AFT application candidate

Classification: engineering integration in the opt-in research application.
Default TRI formulas, curve policies, native tree construction, acceptance,
retry/stopping rules and historical inputs are unchanged. The interior
vertex-mean rule remains the existing experimental rule; no 1993 identity,
global welding or accepted mixed-adaptation policy is claimed.

## Implemented path

`curved_patch_original_curves.conf` executes the original serial Generator
on the original curved Bezier source and records actual Adapter-native refined
tree attempts. The original algorithm, not a fixed sample count, produces the
curve partition. The last locally selected attempt with a complete global TRI
outcome supplies a value-only source snapshot. Initial QUAD generation does
not impose the global acceptance of a separate TRI mesh as a prerequisite;
the actual accepted/rejected TRI outcome is retained in the OBJ and receipt.
Neither outcome increments accepted mixed epochs.

Original curve nodes are retired by the Generator's existing lifetime scope.
Only copied parameters, IDs, XYZ, oriented intervals, source tree boxes/levels
and scalar controls survive. Replay uses the native subdivision implementation
to reproduce every original cell, bound and level. Source parametric midpoint
and normalized arc length are checked, then the original post-generation
`len=-1` phase is restored. Original curve control geometry remains borrowed
from the enclosing Geometry, which outlives the replayed native trees and typed
physical owners. No sampled-node, AFT-edge or source-cell pointer escapes.

The follow-up preserves cell identities, the allocation counter and exact
ordered leaves as well as bounds/levels: original child IDs reconstruct native
subdivision chronology, and every resulting cell/leaf sequence is compared.
This avoids substituting DFS creation order for original native order.

The existing dispatcher emits QUAD interior and the existing owned front calls
original geometric/conditional topological exterior AFT. The typed physical
mesh preserves each original boundary node ID/XYZ and directed interval.
Interior identities use a noncolliding range. Fixed16 retains its old values
and OBJ bytes; immutable layout IDs replace its sequential-only identity
assumption in the shared incidence verifier.

Output/pending-prefix refusal precedes the original workflow. OBJ publication
uses the existing staged export and only then attaches the new owner. Normal
and injected replacement-failure paths retain independent ordered observers
and exact prior output bytes. This is still not the durable multi-epoch
memory/filesystem transaction required for P2d-1c4b. Original `fillMesh` and
`improveMesh` are not invoked on the mixed owner.

## Initial measured GNU evidence, before exact candidate qualification

- Native C++17 GNU application: **37 nodes, 16 QUAD, 28 original AFT TRI**;
  **12 source intervals, four nonuniform sides, 16 original native leaves**.
  Normal and rollback outputs have SHA-256
  `3fbb0c312b81406fb60813caa3ef4b3e76b0b7922208801494b2be61d9d5b03a`.
- Original reference step 1 retains a coarse 4-interval/4-leaf source without
  interior templates. Original step 2 supplies the nonuniform source; its TRI
  candidate is rejected by the unchanged hybrid criterion. This negative
  outcome stays `reference_tri_accepted=0`; mixed adaptive epochs stay zero.
- Native source contracts: **12 actual captures**, including **six reversed
  curve captures**, **108/108 corrupt source/tree attempts rejected** while
  retaining the original Patch owner. The reversed fixture has the same
  original physical surface, with one source curve traversed in reverse.
- Independent Python Bernstein/source/OBJ checks pass normal and rollback
  geometry, exact source IDs/XYZ/intervals, topology and nine corrupted
  artifacts per run. The later existing-output preflight requires its own
  final exact-revision run; initial results do not certify that addition.

These are initial implementation measurements, not exact-head qualification
or integration. Final native, sanitizer, baseline/tooling, frozen TRI and
remote results must identify their own candidate revision in the canonical
STATE/SESSION_LOG checkpoint. Required unmeasured gates block stage closure.

## Failures retained and bounded corrections

Raw development outputs are retained locally, not rewritten as passes:
legacy non-const Vertex getters required a mutable local observer; config
admission initially lacked the new opt-in case; source-edge validation first
mistook the original post-refinement `-1` sentinel for an invalid arc length;
requiring every real partition to be nonuniform incorrectly rejected a valid
original result; demanding a globally accepted TRI source selected only the
coarse source with no interior; shared identity checks still assumed IDs 1..N;
one Python negative initially changed an unconstrained interior ID rather
than the source boundary identity it intended to exercise. Corrections preserve
original policies and expose the reference rejection rather than tuning it.

An initial formatter invocation could not find clang-format on PATH; the
existing installed tool was selected only in the child process. Formatting was
explicitly applied to the changed C++ files, including the existing controlled
application unit. Architecture inventory was explicitly regenerated with its
35 source-backed contracts; no diagnostic, gate or frozen oracle was removed.

## First candidate qualification retained

Feature `bfd501a` passed local GNU, Windows MSVC Debug and Clang
ASan/UBSan/leak fixed16, native real-source contracts and real-boundary normal,
rollback, corrupt-source and existing-output checks. Hosted
[run #43714661426](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43714661426)
passed Linux native, Windows native and baseline/tooling (3/4 jobs), but the
frozen TRI job refused the newly added
`configs/quad/curved_patch_original_curves.conf` before any comparisons. The
follow-up admits that one explicit new opt-in asset only; all frozen model and
profile paths stay guarded. No failed job is counted as equivalence evidence.

The first local delivery adapter rebuilt successfully but stopped before CTest
because its configured inventory changed from 75 to 85. Its report remains a
failure with zero executed CTests, requiring a fresh plan from the updated
inventory. Follow-up source chronology checks and the asset admission require
their own exact-revision native and remote qualification.

## Exact feature closure review — 79828fc

Feature `79828fcbfc1c4aa20d84576e58f1a3ef8fe2592a` on
[PR238](https://github.com/tiagosombrra/apmesh-modernization/pull/238) passes
[exact CI #43716128507](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43716128507),
4/4 jobs. The [portable qualification receipt](evidence/REAL_BOUNDARY_APPLICATION_20261115.json)
records local GNU Release, MSVC Debug and Clang ASan/UBSan/leak, including
fixed16, 12 real captures/six reversed captures/108 native negatives per
profile, independent normal/rollback checks, nine corrupt artifacts per run
and existing-output refusal. All three toolchains emit the same real OBJ hash;
fixed16 retains its earlier `cbf6cd63...` hash.

| Closure scope | Exact feature evidence | Remaining limit |
| --- | --- | --- |
| Source/code and contracts | Actual original curve partition, all source IDs/XYZ/intervals, native cells/IDs/counter/ordered leaves; no sample/native-cell pointers retained | Single controlled source/profile, not general full-model scientific admission |
| Runtime and ownership | GNU/MSVC/ASan/UBSan/leak positive, negative and nonempty rollback traces | Broader allocation-denial, complete Windows CRT and full-process inventory remains separate |
| Baseline/tooling | Local 85/85 CTests; hosted 85/85 and 527 Python controls | Local adapter explicitly remains non-stage/non-integration qualification |
| Frozen TRI | Local GNU and hosted Eistute five/Book four accepted/rejected states; all OBJ bytes and acceptance fields identical; boundaries verified/exact | Not a new 1993 QUAD oracle or full mixed scientific acceptance |
| Configured analysis | LLVM 22.1.8, five actual configured C++ TUs, no emitted diagnostics under unchanged project filters | Earlier LLVM18 cannot read ExcludeHeaderFilterRegex; its zero exits are invalid analysis, not passes |
| Integration | Reviewable exact feature PR238, default TRI preserved | Independent approval, research merge and exact research-merge validation pending |

Reviewed code, value/owner/observer lifetime boundaries, test assertions,
documentation and scientific scope. No scientific formula, tolerance, default
policy, historical input or frozen oracle was changed. Reference TRI rejection
stays explicit; accepted mixed epochs remain zero. This qualifies the bounded
feature candidate, not canonical integration or R3/M7 closure. Resume the next
queued accepted-history gate only after approved research integration and its
required validation; do not open another fixed16 candidate campaign.

Auxiliary checkpoint documentation attempt: `python tools/quality.py docs`
did not pass in the isolated worktree below `build/`: initial output-directory
absence was corrected, then Doxygen could not resolve three unchanged API
evidence references. Doxyfile excludes `*/build/*`. This is not a successful
documentation build or a new code failure; required integration documentation
checks remain pending from a normally located checkout. Staged whitespace,
JSON syntax and changed-document local targets are checked separately.
