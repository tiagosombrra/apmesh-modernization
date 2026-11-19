# PR240 review readiness and retained-finding disposition proposal

Date: 2026-11-18 Fortaleza. Engineering validation routing and closure preparation,
not independent approval or a scientific change. Exact source15e2915,
tree57e98001503559e458bf42cb3e3a1b8e594d1686; canonical starting93ae272,
common ancestor868f518. Modernization main ef40c0f remains untouched.
[Evidence](evidence/PR240_REVIEW_READINESS_20261118.json) binds the24 changed
files, current native images, commands/logs, source hashes and unresolved gates.

## Closure matrix for the unchanged candidate

| Gate | Status and exact scope |
| --- | --- |
| Source/tree/configuration identity | All24 changed file hashes match15e2915; clean primary tree |
| Local baseline and MSVC native | Retained exact15e2915:85/85 and20/20, unchanged inputs; not rerun |
| Exact hosted checks | Run44440173309 reverified4/4 success; no new run claimed |
| Local GNU13.3 Release | Fresh build/current source, source contracts, front/smoothing contracts and all five existing application cases pass |
| Local Clang18.1 ASan/UBSan/leak | Same actual current-source cases/contracts pass with unchanged sanitizer options |
| Raw failure inventory | Old DrvFS partial runs and full-fixture enum diagnostic preserved |
| Complete changed-file quality | Whitespace24 files and C++ format14 files pass, without fixes |
| Integration preflight | git merge-tree finds no conflict; proposed tree differs from candidate only in QUAD documentation |
| Independent ownership/scientific reviews | Not started; user choice between two separate reviewers and external human review pending |
| Integration/post-merge gates | Not executed; PR stays draft/unmerged |

The retained source checks include actual frozen Eistute5/Book4 OBJ/acceptance/
boundary equivalence and527 hosted tooling controls. Do not relabel retained
checks as new local executions or a new source qualification. No root/native
baseline campaign is repeated solely for this documentation checkpoint.

## Linux output-route qualification

The old GNU/Clang runs on the Windows mount failed renaming a pending output
directory. Preserve their original b434034 prefixes, source identity, partial
inventories and unstarted later cases. They are not successful qualification.

Rebuild current15e2915 with the same configured source checkout, compilers,
build profiles, flags and fixed cases. Move only this qualification's output
root explicitly to `/home/apmesh/quad-pr240-review-20261118-15e2915`.
`statfs` reports ext2/ext3 for output and v9fs for the source checkout. No generator
publication workaround, permission change, fallback or altered timeout is added.
Each child retains the existing300-second bound and its checker-specific limits.
The process stops on the first failure, kills/reaps its process group on timeout
and leaves subsequent profiles unstarted if that occurs. No failure occurs here.

Actual start23:11:53 Fortaleza, total242.285seconds. Both profiles execute13
steps: compiler/filesystem receipt, application/source-contract build, separate
front and smoothing contract builds/runs, source contracts, then article, old
live-pair, domain-bounds, fixed16 and original-boundary application histories.
GNU image SHA256:
2c60d795ee8c7866e193623b730da2807ebb2d6120b4514bd560ae3ade1d54ad.
Clang sanitizer image SHA256:
97fb91ffede9d63f1d19ba1f0471606693033131d2b76f031e3283c6ee6fc0ce.

Both article reports match the current MSVC report: stages33/281/689 nodes,
24/249/630 QUAD,8/52/102 TRI,183 prospective commits,11 front/clearance forgeries,
5 smoothing forgeries,3 centroid forgeries and nonempty rollback. Every actual
pass remains independently replayed/lifted/checked by the existing checker.
The existing front contract includes rejection/precommit-abort/retry; smoothing
includes fixed contour, simultaneous arithmetic, opposite QUAD corners, failure
preservation/retry and five malformed controls. Sanitizers report no failure
for these executed cases. This is not full historical/native-CRT/general-geometry
or unrelated instrument calibration closure.

This establishes current native-Linux-filesystem qualification. It does not
prove a causal diagnosis or repair of the previous DrvFS rename denial, nor
qualify arbitrary WSL/Windows-mounted output routes. That platform limitation
remains visible for the independent review's scoped integration disposition.
Raw Linux artifacts are copied without overwriting older prefixes to
`build/quad-pr240-review-20261118/linux-output/`.

## Enum diagnostic: proposed technical classification

The additional complete adversarial-dispatcher clang-tidy scan retains exit1 at
`static_cast<InteriorTemplateMode>(127)` in the unsupported-mode negative test.
That test, enum declaration and dispatcher source are byte-unchanged from11dcaa7
to15e2915. The14 native dispatcher outcomes include rejecting this input before
selection publication. Do not remove the control, add a fake enumerator, disguise
the cast or suppress the diagnostic merely to obtain a clean scan.

The [Clang checker documentation](https://clang.llvm.org/docs/analyzer/checkers.html#optin-core-enumcastoutofrange-c-c)
states that it also flags values without a corresponding enumerator and that
this is not necessarily undefined behavior. Here the scoped enum has fixed int
underlying type and127 is representable. The C++ draft explains fixed underlying
enum values in [dcl.enum](https://eel.is/c++draft/dcl.enum) and the corresponding
conversion in [expr.static.cast](https://eel.is/c++draft/expr.static.cast).

Proposed disposition: an intentional negative-input/style-checker diagnostic,
not evidence that this cast itself has undefined behavior or corrupts a mesh.
The raw full-fixture analysis remains nonzero. This is a technical interpretation
for independent review, not unilateral waiver of a required gate or a whole-unit
analysis pass. Configured changed production/header/positive scopes retain their
own measured passes. No first-party source or checker configuration is changed.

## Review package and next action

`build/quad-pr240-review-20261118/review-packet.json` pins all24 changed paths.
Ownership review must cover temporary values, callback throws, source observers,
physical owners, staged exports and nonempty rollback. Regression review must
cover default TRI, explicit UV0.2/S1.5/centroid/five-pass decisions, independent
trace arithmetic, source history/error/quality counterevidence and exact gate
identities. Neither technical review is advisor approval or a claim of historical
numeric reproduction. Current GitHub reviews are empty.

A concrete choice is presented to the user for two separate reviewers or an
external human review; the earlier authorization concerned PR238. Pending that
choice, no reviewer is started and no self-audit is called independent approval.
No new generation rule, estimator, balancing controller or Blender change.
The qualification generates only the existing fixed-case test outputs.

**Next:** start the selected independent review route on exact15e2915; resolve
its concrete findings and retained-finding disposition, then perform required
exact research integration/post-merge gates. Full historical identity, mixed
global curvature error/accepted adaptation0 and wider native/CRT/oracle coverage
remain open. No merge or whole-stage closure is claimed by this checkpoint.
