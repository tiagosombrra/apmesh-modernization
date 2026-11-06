# PR #163 post-merge validation attempt

Date: 2026-11-05, Fortaleza. Classification: engineering-only qualification and
checkpoint update. No production, test, scientific input, compiler option,
formula, ordering, selection, acceptance, retry or stopping policy is changed.

Current disposition: the reviewed continuation below completes compilation and
ordinary regression but stops at a native fixture directory-rename failure.
Main qualification remains blocked. The initial build attempt is retained below
as historical failed evidence, not the current compilation blocker.

## Identity and disposition

PR #163 merged at `0df31939e19b86c8486c0f01df414316c263913b`.
Qualified head `69582bbb2663ffc0249d79d648421c616763fffe` and main share
tree `419f0964cadd84ce9f6d8a47429318531f1d06ab`. The worktree was clean at
entry. Remote main and all branch heads were queried; no open PR or configured
hosted check was found at preflight. The existing exact-head report remains
qualified; it does not qualify the integrated main.

The initial fixed main attempt stopped at its first build gate. That attempt
did not complete compilation or measure a scientific failure. No later gate or
scientific process started in that attempt. The subsequent reviewed continuation
has its own admission record, rebuilt identities and failed disposition below.

## Execution and retained evidence

```text
python build/pr163-delivery/validate_phase.py main 0df31939e19b86c8486c0f01df414316c263913b
cmake --build build/windows-gcc17 --parallel 2
```

The GCC build ran from approximately 22:36:29 to 22:46:29 Fortaleza. It reached
the unchanged 600-second cap at 600.080528 seconds, with driver exit 124. The
last logged action was 329 of 532. No compiler error marker was found in the
retained log; build completion and the remaining actions were not measured.
No build/compiler descendants remained when checked after the timeout.

| Gate | Observed disposition |
| --- | --- |
| Initial revision, source/control/input and pinned binary identities | Pass; the main tree equals the qualified head tree. |
| Remote branch heads and PR #163 state | Pass; PR merged at the expected main revision. |
| Canonical GCC build | Failed: 600-second timeout, exit 124; incomplete. |
| MSVC builds, CTest, native/negative/CRT and quality gates | Not started in this main attempt. |
| Frozen GCC science, GCC reuse and fixed MSVC Eistute/Book pairs | Not started in this main attempt. |
| Integration seal and stage closure | Absent / not established. |

Post-stop checks found all 2,284 tracked files unchanged and every pinned
executable/PDB hash equal to its entry value. Intermediate build files were
partially rebuilt; this is not a completed-build identity claim. The following
checkpoint edits change documentation only after that source comparison.

Complete local commands, timestamps, identities and diagnostics remain under
`build/pr163-delivery/`: `head/report.json`, `main/entry.json`,
`main/report.json`, `main/build-gcc.log`, `main/build-process-identities.json`
and `main-blocker.json`. A read-only Ninja dry run was retained separately; it
stopped at its manifest/glob recheck and does not establish a remaining-action
count or the cause of the broad rebuild.

| Record | SHA-256 |
| --- | --- |
| Qualified head report | `dbf32c35dc226e17592cc0bf42b26e3f8e181282291664b40240360e2f88c520` |
| Failed main report | `4279d481e269331f98eb33e32723d9b014b963de4ba79d0f5e81b9dd1a34437e` |
| Main entry manifest | `f88accb8a30aa6dd14ad06dd4e65eba5dd22bdcfca8902a3165a12b05ce18219` |
| Incomplete GCC build log | `d9c93e3e5a507a1eed3741d3c2c83a2c810fec9bd08806d8fc2fdb4bd9f27b49` |

## Initial stop decision

Review the incomplete build prerequisite and artifact identities before admitting
another qualification attempt. Preserve this failed unchanged-revision run;
do not automatically retry it, increase its cap, weaken a required gate or start
the next production implementation. No lifecycle defect or optimization is
selected from this build timeout.

## Reviewed build continuation and current blocker

Three still-pending object records identify first-party dependencies newer than
their outputs. For example, patch_bezier.cpp objects from approximately 06:22
depend on source and triangle_adaptive.h timestamps from 20:27. The dependency
hashes equal the qualified source manifest. This bounds a cache-invalidation
explanation; it does not attribute all 532 original actions or establish a
compiler performance result. The original failed report and log remain intact.

After explicit review and renewed continuation, the existing incremental build
completed its remaining 203 actions, with parallelism 2 and the same 600-second
cap. The five documentation files were preserved in a local stash, leaving the
actual main revision clean through execution, and restored byte for byte after
the stop. The stash remains preserved. No production, fixture, oracle or input
content changed. Rebuilt executable/PDB hashes differ from their predecessors;
the current observations bind the new artifacts, not the old binary hashes.

| Continuation gate | Observed result |
| --- | --- |
| GCC remaining build | Pass, 266.601197 s, 203 actions. |
| MSVC serial / metrics / UV builds | Pass, 106.047404 / 4.660125 / 15.586926 s. |
| CTest / nested controls | 75/75 and 391 pass; zero failures/errors/skips, exact JUnit inventory. |
| Native/diagnostic/invalid-input controls | Pass, including all 23 invalid CLI controls. |
| UV/CRT fixture controls | Pass, including all 515 allocation denials and zero fixture-retained blocks/bytes. |
| Scoped analysis identity / format / whitespace / inventory / diff | Pass; prior scoped analysis reused only after unchanged source and actual compiler-command checks. |
| Ordinary frozen GCC Eistute/Book | Pass: nine states, 45 exact artifacts and 123 independent boundary comparisons, with accepted/rejected traces. |
| MSVC aligned analytic control | Pass: one state, one independent boundary comparison and preserved FindUV summary. |
| GCC same-Generator reuse | Fail: native directory rename from live to first returns Permission denied, exit 3221226505 after 5.457609 s. |
| Book reuse / second Eistute call / MSVC reuse pairs | Not started after the failure. |

There are 24 passed commands followed by the failed GCC reuse gate. The native
exception occurs at tests/attempt_metrics_probe.cpp's archival boundary after
Execute returns, before the second call. Native return/counter output was
buffered and absent at abort; do not manufacture a successful caller status.
The retained first-call directory contains 25 scientific artifacts byte-identical
to the frozen reference and matching relocated compatibility metadata. These
are prefix preservation observations, not successful reuse qualification.

The live path is 124 characters and the longest retained file path is 173;
these measurements do not support a MAX_PATH explanation. A read-only post-stop
open/close access probe found no current DELETE-access failure. A separate native
sibling control renames a directory successfully with its stream closed, and
reports generic error 13, Permission denied, with a deliberately held input
stream. That establishes a sharing-failure control, not the identity of the
original blocking handle or process. The actual permission/sharing cause at
the failed archival boundary remains unresolved; no new mesh run was launched.

Local records under `build/pr163-delivery/main-continuation/` include
`decision.json`, `run/{entry,report}.json`, `run/postbuild-binaries.json`,
`run/gcc-reuse/report.json`, native stderr, `archival-failure-diagnosis.json`,
`rename-control.json`, `checkpoint-restored.json` and `summary.json`.

| Continuation record | SHA-256 |
| --- | --- |
| Reviewed continuation report | `678ff463eff0adf3f2503e00bdc2477d9a4bcb2180148249a3383615b95f1da6` |
| Continuation admission decision | `722771f5f97e1436102f739a801643af3192bd223ad7042267e5836e84932faf` |
| Failed GCC reuse report | `6d1546b5729a13dcb53680ac17f84602a4ded36c0ad25282c5bc6faf890e6aa0` |
| Native stderr | `96b2e462d11e4d7d579f047dba9cc806f264b71ec8262c486a9440c184af7960` |

## Archival stop decision and preserved limits

Capture the native archive error and file-sharing ownership at the existing
reuse probe boundary before admitting another scientific execution. Preserve
the initial timeout, the reviewed build continuation, all 24 passed commands
and the native archival abort. There was one build continuation and zero
scientific retries. Do not infer main qualification or start another P4 package;
the integration seal remains absent. No supported meshing defect is established
by the archival error alone.

All ten Stage 3 dispositions remain: three bounded-qualified, seven partial/open.
Earlier ASan evidence stays artifact-specific; full-process CRT/UB/leak,
caller/mutation/cache/recovery/domain and parallel obligations remain open.
The earlier Doxygen gate still fails with 2,718 diagnostics. The passed head
regression and scientific observations retain their recorded identities; no
result is transferred to this incomplete main attempt.

## Subsequent diagnostic repair

The [test-only archive diagnostic repair](REUSE_ARCHIVE_DIAGNOSTICS.md) is the
next bounded dependency. Its closed/occupied/self-held/external-owner controls
pass on GCC and checked MSVC. A calibrated standalone diagnostic Eistute pair
also completes with exact scientific artifacts and positive boundaries; the
archival failure was not reproduced and its original owner remains unattributed.
These observations do not rewrite either failed main report or establish main
qualification. The revised fixture must pass its own exact-head/main delivery
gates before the next production package.
