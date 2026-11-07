# Qualified-tree main checkout

Entry main: `60820f327fb2f89d6218037783e11563ff9a5220` (PR #171).
Classification: engineering-only local delivery tooling; no production C++,
compiler/linker flag, numerical input or scientific policy change.

## Demonstrated workflow problem

The previous post-merge sequence switched from the qualified delivery branch to
the old local main, then fast-forwarded main to the remote merge. Changed files
were written back to old contents and then written forward again even when the
merge tree was exactly the qualified tree. Real disposable-repository controls
show the same final bytes but changed source timestamps for both modified and
newly added files. This can invalidate an already qualified native build.

The two preserved MSVC image-reuse failures in the PR #170/171 main seals remain
failed and unattributed; their actual main artifacts were qualified directly.
Those records do not prove a linker defect. Microsoft documents that
[incremental links retain padding and may add jump thunks](https://learn.microsoft.com/en-us/cpp/build/reference/incremental-link-incrementally?view=msvc-170).
This package removes an avoidable checkout rewrite; it does not change linking
or promise deterministic output for independently rebuilt binaries.

## Guarded local operation

After an authorized remote merge and fetch, checkout_qualified_main.py verifies
the exact current delivery head, old local main, fetched origin/main, two ordered
merge parents and equality of the qualified/merged trees. A clean index/worktree
and no known main checkout in another worktree are required. Only regular tracked
files are supported; the snapshot includes raw bytes, sizes and nanosecond write
times. No source, parameter or artifact is touched to force a build result.

The default is a read-only plan. Explicit --apply performs a compare-and-swap
fast-forward of refs/heads/main, then a normal git switch main. A concurrent ref
advance fails rather than being overwritten. Normal checkout hooks run. Exact
tracked file state is checked again afterward; an unexpected result stops without
reset, force, stash, rollback or hidden retry. Receipts are exclusive and must be
outside the worktree or in an ignored path, outside private/common Git metadata.
An existing receipt is never overwritten. A receipt-publication failure requires
inspection of refs before another request.

The caller retains responsibility for authorization, fresh remote PR/check audit,
complete exact-head gates, successful remote merge, and all required main checks.
The helper performs no push, remote merge or scientific qualification. The local
validation adapter remains unchanged. Canonical native builds and their artifact
identities must still be checked after checkout; preserved timestamps alone do
not establish valid binaries or permit an unmeasured stage closure.

## Finite controls and delivery

Ten real-Git fixture controls cover read-only planning; exact file preservation;
the original rewrite as a positive failure control; dirty/staged/untracked state;
wrong remote/tree/parent order; main in another worktree; concurrent ref progress;
normal hook execution; receipt immutability/path safety; and common metadata
protection from linked worktrees. No failing state is converted into a successful
checkout or automatically retried.

Require the complete 75 CTest inventory and 495 Python controls on final head and
main, source/contract/whitespace and fresh remote gates. Production and input
bytes are unchanged; reuse prior numerical/native observations only after their
source/build/input/oracle/artifact identities match. Exercise the guarded checkout
on this delivery itself after the remote merge, preserve its receipt, then run
canonical builds and require the qualified artifact identities to remain valid.
If a build artifact changes, classify it and run its affected gates explicitly.

The [compact record](stage3/qualified_main_checkout/summary.json) and local
build/qualified-main-checkout reports bind controls and delivery identities.
The final integration seal is separate. This closes one local workflow debt;
the full Stage 3, broader caller/domain, mutation/recovery, whole-process/runtime/
DLL/UB/leak, parallel and known documentation obligations remain open.

The complete iteration passes all 75 CTest entries and 495 Python controls without
skips/failures. Its first invocation stops at the missing compact-report link
before any native build/test; that failed report remains preserved and the real
report is added before the revised invocation. No link check is weakened and no
scientific process is repeated for this documentation ordering correction.
