# Stage 3 slice 3 integration closure

Issue #14, implementation PR #15. Only the primitive construction/cache commit
boundary closes here; the full stage 3 remains open.

## Authority and revisions

Entry main `0146fbd4925721a53a9b52717b82c5af8c4e0115`, tree
`8edd39eaf92f5795cea4e35bb1647cdc9bc310eb` (715 blobs).
Qualified implementation head `fce74915755d1535b89dbd280cbc1ba3813f9b91` integrated as
main `68ef4db735d3c478215815128309c6bdd7a8e90c`. Both share exact tree
`2bb4359687579a9069e162b228228dea2b1197be` (737 blobs). All 38 intended changed/new
files and all retained blobs were independently verified before publication.
Both immutable remote-only publication binaries remain preserved; no deletions.

Main, branches, open PRs/issues, checks/statuses and Actions were audited before
delivery and integration. Only issue #14 was active; no concurrent work existed.
Remote checks/Actions were unconfigured, not reported as passing CI. No hosted
workflow was added. Exact local required gates provide the observations below.

## Explicit closure audit

Reviewed three production implementations/two headers, the extended probe and
35-case runner, required normal CTest registration, source inventory, 22 contracts
and 85 anchors, ADR-0004, state/plan/work log and all failure/coverage limits.
Only demonstrated engineering defects changed: construction retention, partial
failed replacement and endpoint-alias invalid access. Both Face constructors
remain independent passing controls without direct constructor edits.

The same final probe/runner fails the pinned original in eight cases. Its old
26 cases continue to pass. New sweeps demonstrate nine blocks/336 bytes retained
by Edge construction and 55 blocks/1,936 bytes by default front construction,
failed cache-state contracts and a symbolized ASan Face alias UAF. All failed
raw diagnostics and the initial missing-header candidate build hash remain.
No failing case is relabeled expected success.

The repair guards pending caches/Boundary ownership with unique_ptr until commit.
All 53 measured primitive failure ordinals and three retained transfer failures
pass; valid Debug CRT modes retain zero blocks/bytes. Deliberate invalid-access,
duplicate deletion, allocation-denial and leak controls remain detected.
Counts are fixture observations, not portable allocation invariants.

Midpoint/vector/centroid arithmetic and order, templates/front/smoothing,
boundary partitions and adaptation/acceptance/stopping policies are preserved.
Inputs/vendor and independent scientific verifiers did not change. Only changed
production ranges are formatted, with three whitespace replacements. Selected
lint rules/configuration remain unchanged; legacy/vendor debt remains open.

## Published-head and post-merge regression

Both complete campaigns passed independently:

| Gate | Published head | Implementation main |
| --- | --- | --- |
| CTest, zero skipped | 12/12 | 12/12 |
| Python controls | 74 | 74 |
| UV ASan / separate Debug CRT | 35/35 | 35/35 |
| Previous physical-node instruments | 7/7 | 7/7 |
| Five selected production-unit lint | Pass | Pass |
| Inventory freshness, 122 files / five CMake inputs | Pass | Pass |
| Two same-command runs per article model | Exact | Exact |
| Strict entry/previous-slice continuity | Exact | Exact |
| Named CSV fields | 189 matching | 189 matching |

All nine attempted states retain positive shared-incidence coverage and zero
measured position gap. Both models accept steps 0/1. Eistute/Book keep
**1,168/4,256** accepted triangles, exact OBJ/acceptance/CSV/incidence results.
Application SHA-256:
`c8075286a4753123765f43d2f13c2e757b20ea7c8bfcdfb409f209f716987aad`.
No tolerance or oracle was relaxed.

[Head report](stage3/uv_allocation/head_qualification.json),
[post-merge report](stage3/uv_allocation/postmerge_qualification.json),
[entry report](stage3/uv_allocation/entry_qualification.json),
[failed original](stage3/uv_allocation/original_failed_qualification.json) and
[source identities](stage3/uv_allocation/source_identities.json) retain commands,
input/executable/source identities and log hashes. Toolchain and scope details:
[implementation evidence](STAGE3_UV_ALLOCATION.md).

This documentation-only follow-up preserves every qualified production,
development-tool, test, build, model, configuration and vendor blob. Its exact
head and final-main CTest/inventory/delta audits are recorded on the closure PR
and issue #14 after execution; they supplement the full campaigns above.

## Remaining work

Next qualify template arrays/object creation before registration and Boundary
registration. Other setters/helper temporaries, sample/initialization ownership
and rollback follow. Incoming endpoints may not alias a distinct cache owned
by the same primitive. Raw-copy/adoption, same-front reuse, all template types,
full process leaks, parallel modes, Linux LSan/UBSan, Decor Shelf and every
internal retry remain unqualified. Stages 0-2 are closed; stage 3 has three
qualified slices and remains in progress; stages 4-11 remain pending.
