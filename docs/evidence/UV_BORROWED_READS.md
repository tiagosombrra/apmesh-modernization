# Borrowed quadtree reads in the native AFT pipeline

Entry: PR #180 main `80b44a347719270a6aa7489827debf5852a4cf8e`.
Classification: engineering-only removal of redundant list snapshots, supporting
F3-01/F3-03 and C10. The [compact record](stage3/uv_borrowed_reads/summary.json)
binds source, native images, allocation measurements and delivery requirements.

## Production result

The native AFT pipeline copied entire quadtree lists to read front edges, template
vertices/edges/faces and the leaf count. Add four const-reference observers and a
nonallocating count, then use them at those five call sites. The existing public
by-value getters remain unchanged. No owner, object, list order, duplicate, pointer
identity, membership policy or arithmetic expression changes. Borrowed containers
remain valid only while their tree lives; their contents can change, and owner
lists become empty at transfer. Pointed-to objects gain no lifetime extension.
All iteration completes before transfer and no borrowed iterator escapes.

The existing checked-MSVC transfer fixture measures **515 -> 342 allocations**:
173 fewer (about 34%) in that operation. Every remaining ordinal is denied once;
tree owners remain complete before commit, ordered observer prefixes remain valid
and helper-local retry transfers each object once. These measured counts are not
portable budgets. The other three read sites also avoid their list snapshots;
their allocation savings are not separately quantified. No end-to-end timing or
speedup claim follows.

## Change-relevant validation and closure

Reuse the prior qualified native transfer image/log only as the 515-allocation
baseline, bound to this entry. Current ASan/CRT runs retain the existing native
identity/order/duplicate, transfer, tree, terminal failure and actual UAF/leak/hook
controls. One added no-allocation scope reads all five queries on a real populated
tree. Compile-time guards preserve old getter types and require const references
and noexcept queries. Existing transfer-order controls observe the same container
identities before/after transfer and empty source owners. No new test target or
independent instrument campaign is introduced.

Require 21 current expected native outcomes, complete 342 transfer denials,
unchanged six-site root adoption and 3,470 tree denials, exact original/current
registration/tree traces, and the existing six analytic UV callers (17 prefix /
12 complete outcomes under GCC and checked MSVC). Current application images need
fresh frozen Eistute/Book comparisons on both ABIs. Keep their accepted/rejected
traces and positive independent boundaries. Require configured full production
analysis and added positive fixture/header analysis, 519 other protected inputs,
43 original evidence artifacts, and 75 CTest /526 Python on exact head and main.
Guarded main checkout, canonical MSVC rebuild, current artifact identities and
fresh remote/check audits remain required. No unrelated copy/loader campaign runs.

Two full-unit analysis attempts reached the local 180-second controller budget;
both remain unqualified records. Final full analysis has one explicit 600-second
tool budget with identical configured diagnostics. Native/scientific process caps
are unchanged. Integration requires the completed final analysis report; no pass
is inferred from a timeout or from the separate native results.

Code, tests, contracts and documentation describe this bounded production change.
The existing F2 corpus blockers, F3 sharing/replacement/recovery/retirement gaps,
F4/F5/F6/F7 dependencies and all ten original stage dispositions stay open.
This completes the removal of these five redundant read snapshots, not F3 or
Stage 3. Integration requires the actual local
build/uv-borrowed-reads/delivery/integration-verification.json receipt.
