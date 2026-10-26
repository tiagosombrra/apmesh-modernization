# Serial terminal domain-failure audit and status repair

Reference main: `9d2f66174379d26303aefe006e9522ac0511ee6e`. Classification:
behavior-changing fatal-error status/diagnostic repair plus engineering-only
dead-store cleanup. No meshing formula, numerical reduction, retry selection,
quadtree/template/front, synchronization or acceptance/stopping policy changes.

## Original-path observations

Nine retained original serial CLI cases use verified production objects with
explicit GNU linker fault/observation wrappers. Configurations differ from the
pinned article cases only in relocated input/output paths. Faults affect AFT
execution only at step 2, patch 0. These are controlled failure-path observations,
not naturally reproduced numerical failures, ASan/CRT or repaired-memory results.

| Original case | Exit | Cached UV face storage freed | Pending mesh storage freed | Curve-sample scope destructor |
| --- | ---: | --- | --- | ---: |
| Book control | 0 | 152/152 | yes | 1 |
| Book false before/after actual execution | 0 | 152/152 | no | 0 |
| Book exception before/after actual execution | nonzero | 0/152 | yes | 1 |
| Book deliberate one-block release control | 0 | 151/152 | yes | 1 |
| Eistute control, two local calls | 0 | 292/292 each | yes each | 1 |
| Eistute all calls false | 0 | 292/292 each | first no; second yes | 0 |
| Eistute first call false, existing fallback recovers | 0 | 292/292 for three calls | yes each | 1 |

Both unmodified controls reproduce all nine reference mesh/metric/decision
states exactly. The deliberate release control preserves Book outputs and
demonstrates detection of one unfreed cached Face block. Release observations
refer to exact cached allocation addresses and the pending owner inferred from
actual AddNoh calls; they do not count all process allocations or qualify whole
graphs. Raw observations, sources, commands, objects and hashes remain under
`build/domain-failure-audit/`.

The original false paths terminate through `exit(0)`. A successful process status
allows the ordinary verifier to accept the internally consistent step-0/1 prefix,
although the attempted step 2 never finishes. Strict comparison with the full
reference still detects the missing states. Source and observations also show
that process exit skips outer automatic owners. Propagated exceptions execute
outer cleanup but bypass the raw cached-face deletion loop. Caller regeneration
candidates remain raw until adoption, so changing exit directly to an exception
would require broader ownership qualification. No rollback/retry safety follows.

## Bounded implementation and controls

After all existing serial attempts fail, `Adapter::AdaptDomain` emits
`Error: domain generation failed (step=..., patch=..., retry=..., status=...)`
and calls `std::exit(EXIT_FAILURE)`. Termination is retained. The OpenMP path's
separate historical behavior is unchanged and unqualified.

Full adapter clang-tidy originally fails on two unused `kd_average` assignments.
Both are unconditionally overwritten with the same getters before consumption;
the unused assignments are removed without changing the consumed expression or
its ordering. No diagnostics are suppressed. The initial cleanup edit matched
the inactive duplicated OpenMP block; that method was restored exactly and only
the intended serial assignments were removed before qualification. The staged
gate requires canonical full-file C++ formatting, so the two touched C++ files
are explicitly formatted. A lexical comparison with the unformatted functional
candidate preserves 12,439 Adapter and 1,556 fixture tokens after ignoring
comments/whitespace and concatenating adjacent string literals. This is not an
AST proof; compilation and normal numerical traces provide the measured checks.
Formatting and shell-capture preparation artifacts are retained separately.

The GNU serial actual-production fixture forces false AFT outcomes without
altering production algorithms. Book invokes one attempt and Eistute two;
both now exit exactly 1 with matching step/patch/retry/status diagnostics. The
same strengthened contract rejects both zero exits when linked against the
original Adapter object. Four independent checker controls reject status 0,
crashes, missing injection, wrong context and wrong call counts. Existing probe
modes delegate to the original AFT and retain their behavior.

This test ABI is qualified only for the measured GNU serial configuration, not
MSVC, MPI or OpenMP. No new memory slice, resource-cleanup fix, safe continuation,
scientific improvement or stage closure is claimed. The reverse-direction
experiment remains unapproved and unexecuted.

## Exact delivery requirements and next work

Require the C++17 build, 58/58 CTest with zero failures/skips, 110 Python controls,
full adapter/fixture clang-tidy and formatting, whitespace/inventory/
diff checks, original status-contract rejection and fresh Eistute/Book generation
matching every retained accepted/rejected/OBJ/incidence/CSV state on exact head
and main. Keep prior scientific inputs fixed and record remote refs/checks and
report hashes in the delivery PR. A full ownership matrix is not claimed or
substituted by these status controls; the original cleanup findings stay open.

Next single work: qualify explicit ownership for temporary UV cache construction
and exception unwinding. Caller candidate ownership and terminal exception
propagation follow only after the applicable lifecycle controls pass.
