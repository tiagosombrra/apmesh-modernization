# Stage 3 slice 13: paired target-count curve rebuild preparation

Updated 2026-10-18 (America/Fortaleza). Issue #44; one active work item.
Entry main b7f7ebda4c206f4570f1d86fab6fac844587e188. Candidate passes;
exact published-head/main gates subsequently passed through PR #45; see
STAGE3_CURVE_REBUILD_CLOSURE.md. See ADR-0014 and
stage3/curve_rebuild/ for exact commands, identities, extraction/substitutions,
original failures and retained preliminary coverage.

Original: 24 sweeps stop before unsafe consumption at deleted-live-sample
failure, with subsequent ordinals/CRT retention unmeasured. Three two-endpoint
sweeps finish with 48 retained blocks each across their denied allocations;
90 other outcomes are expected. Candidate: 117/117, 597 denied ordinals
over 36 positive sweeps. Pending owned nodes and full paired lists precede
nonallocating swaps and deletion. All 78 complete normal traces match, including
analytic sample geometry, rounded shrink selections, endpoint identity, zero/
nonzero/null ID behavior and guards. Consumed IDs stay consumed; retry uses
subsequent IDs. Original uses 12 pinned units plus a verified context adapter;
candidate uses 13 actual units, not whole-process instrumentation.

CTest 23/23, zero skips, 74 Python controls; prior snapshots 89/89, sync 73/73,
adoption 53/53, copy 30/30, curve 19/19, UV 81/81, node 7/7 pass. Both article
models repeat twice; all nine attempted states/OBJ/acceptance/incidences and
189 named CSV fields compare exactly with positive boundary coverage/zero gaps,
last accepted triangles 1,168/4,256. Actual new-unit lint, explicit formatting
and inventory pass: 129 files, 60 units, 69 headers, 22 contracts/107 anchors;
the existing six-header cycle remains. Entry reused unchanged prior full
qualification after verifying 522 input hashes; no fresh entry campaign claimed.

Preliminary 108-case and 117-case zero-start records remain retained. Explicit
final manager initialization broadens nonzero-ID coverage without changing
manager sources. New CRT target disables iterator metadata consistently while
retaining actual heap and negative controls. Preparation deliberately changes
allocation behavior/peak storage. Distinct removable interiors must be exclusively
deletable; borrowed endpoints survive. Curve point-observer publication, full
AdaptCurve/mesh rollback, manager overflow/wrapping, arbitrary subclasses/sources,
full-process/parallel/LSan/UBSan and stage-8 API debt remain open. No scientific
formula, ordering, policy, tolerance, budget or verifier changes.
