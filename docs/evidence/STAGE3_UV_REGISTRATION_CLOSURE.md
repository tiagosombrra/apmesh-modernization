# Stage 3 slice 4 closure

Head `ef89fd9d3305a9ed4c88548df086540d00bbadd3` integrated through PR #18 as main
`da3eed2dc351cfe1a82b117d686164686c738d95`, preserving tree `465fea56b1267644c352b1200250dc033b062188`
(784 blobs). Exact-head and implementation-main gates pass: CTest 14/14, zero
skips, 74 Python controls, UV 49/49, node 7/7, six-unit selected lint,
changed-range formatting, inventory and strict Eistute/Book regression.
Eight new sweeps inject 1,361 allocation failures; both missing-quadtree
subdivision overloads are independently qualified. Successful UV geometry,
IDs, registration order and allocation counts match the pinned original.
All nine scientific mesh states and acceptance/incidence results remain exact;
last accepted meshes retain 1,168/4,256 triangles and 189 matching CSV fields.
The original fails 12 of the 49 cases while its previous 35 remain passing.

## Scope and preserved behavior

Boundary guards pending registration and commits contour/IDs after success.
TemplateStorage owns unregistered suffixes while Quadtree owns adopted prefixes.
Face::quality protects borrowed endpoints during allocation failure. Missing
quadtree context throws std::logic_error without changing valid subdivision
criteria. Template failure is qualified for destruction, not retry or observer
consumption. Original failures, fixture/build/lint failures and an encoding
repair remain recorded. No scientific formula, threshold, input or vendor
changed. This documentation-only follow-up preserves every qualified
production/tool/test/build/input/vendor identity.

## Audits and evidence

Entry main c341ba7cb7b514b4073330e59ccef14d000e45de had 746 verified blobs,
12 branches, one open issue (#17), no open PR and no configured hosted checks
or Actions runs. PR #18 head and implementation-main were independently
compared against the complete expected 784-blob map, including both remote-only
publication binaries. No concurrent change was observed.

Required gates were run locally on matching source identities; absent hosted
checks are not described as green CI. Full exact-head and implementation-main
reports, log hashes, scientific comparisons and instrument cases are retained
in `stage3/uv_registration/head_qualification.json` and
`stage3/uv_registration/postmerge_qualification.json`. The earlier candidate
and final reports, original failures, and ADR-0005 remain part of the record.

This documentation-only closure requires exact-tree verification, CTest 14/14
and fresh inventory on its published head and final main before issue closure.
Those final commit identities and results are recorded on PR #19 and issue #17
to avoid a self-referential commit hash in repository content.

## Remaining work

The wider stage 3 remains open with four qualified slices. Next qualify
earlier tree generation/subdivision, remaining mutation/helper and curve
internal scopes, then sample/initialization/rollback ownership. Other template
patterns, full-process and parallel/LSan/UBSan scope remain open.
