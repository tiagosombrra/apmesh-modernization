# APMesh QUAD — current state

Updated 2026-11-15 Fortaleza. Canonical branch: `quad-templates`.
Remote main is `ef40c0fc16e6913eb8941f2860ef0deb1ee6bd89` (concurrent documentation-only PR237).
Frozen research reference remains `f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94`.
## Active: review the curvature-driven per-step delivery; mixed feedback remains open

**Execution priority:** deliver this functional integration. Isolate a concrete
defect or necessary prerequisite when it blocks progress, make the bounded
correction and required validation, then return directly to this objective.
Further fixed-fixture experiments, repeated audits or planning are not the
default successor. Preserve scientific authorization, negative evidence and
all required closure gates; report delivered capability and remaining work.

### 2026-11-15 - refinement jump and same-site error comparison measured

Read-only comparison of the existing e90d5a3 exports: curved-side step1 has9
points; step2 curve pass17 then surface pass65, an8x interval increase. On the
same16,384 analytic source sites, area-weighted geometric RMS normalized by
source corner diagonal is TRI/mixed0.2147235%/0.1987092% at step1 and
0.03841344%/0.02185673% at step2. Step3 repeats step2. Mixed uses165 versus63
nodes at step1 and953 versus337 at step2: no equal-cost efficiency claim.
The original TRI curvature indicator instead worsens0.125829 ->0.382516;
these objectives differ and no approved mixed curvature value is inferred.
Grid64/128 ordering, exact existing mixed-kernel agreement and an uncovered-face
negative control were checked. No native generation/tests, policy changes,
integration or new accepted epoch. [Comparison](TRI_MIXED_SAME_SITE_ERROR_20261115.md)
and [receipt](evidence/TRI_MIXED_SAME_SITE_ERROR_20261115.json). The next mixed
criterion must distinguish geometric gain, curvature and cost; do not choose an
arbitrary growth cap from these two refinements alone.

### 2026-11-15 - curvature clipping corrected; four physical steps exported

The latest user instruction rejected artificial point clipping and superseded
the earlier request to preserve the stable controller. Exact feature
`e90d5a30963ed0ade9683c69a530847709188fe3`, draft
[PR238](https://github.com/tiagosombrra/apmesh-modernization/pull/238), now uses
the existing original-curvature `legacy` profile in this opt-in research case.
Default TRI configurations and original formulas are unchanged. Full surface-pass
parameters reach native tree/QUAD/AFT without the stable-mode point rebuild.
The stable controller remains an explicitly executed regression control.

| Source step | Curved-side points | Straight-side points each | Physical QUAD/TRI reconstruction | Original TRI outcome |
| --- | --- | --- | --- | --- |
| 0 | 2 | 2 | 5 nodes / 0 QUAD / 4 TRI | Initial accepted reference |
| 1 | 9 | 5 | 165 nodes / 120 QUAD / 68 TRI | Accepted |
| 2 | 65 | 17 | 953 nodes / 784 QUAD / 224 TRI | Rejected for increased surface-curvature error |
| 3 | 65 | 17 | 953 nodes / 784 QUAD / 224 TRI | Same reference rejection |

All four steps are exported, with TRI and QUAD/TRI files, actual decisions,
scoped domain generation identity and original pass traces. The primary OBJ
retains accepted source step 1. Generation is separate from scientific mixed
acceptance: `mixed_adaptive_epochs=0`, TRI-driven source history, R3/M7 OPEN.
The source has one curved side and three geometrically straight Bezier sides.
The straight-side curve pass retains two points; surface-driven refinement
adds points without changing their straight shape.

Local GNU, MSVC Debug and Clang ASan/UBSan/leak pass both original-curvature
and stable-control normal/rollback/history/corruption/existing-output checks.
Each runs six real source captures, three reversed captures and 54 native
source/tree negatives. All eight original-profile OBJ files match byte-for-byte
across the three profiles. Fixed16 retains its prior hash. Exact-head local
CTest 85/85 and [CI43750977300](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43750977300)
4/4 pass, including hosted85/85 and Python527/527. Native C++ images are identical
to the already measured b0e7852 images; unchanged-code configured LLVM22 four-TU
and local frozen Eistute5/Book4 evidence is reused with hashes; final hosted
frozen TRI is independently green. [Review](CURVATURE_STEP_EXPORT_REVIEW_20261115.md)
and [receipt](evidence/CURVATURE_GENERATION_STEPS_20261115.json).

A Blender5.3 scene now contains the analytic source model before all four steps,
with source curves and actual mesh chords. The new file was saved and opening
was requested, but final visual confirmation was interrupted by user Escape;
no further UI actions occurred. Do not claim that final scene was visually
confirmed. The earlier three-step inspection was separately observed.

Earlier reports below are retained findings, superseded by this profile and
qualification checkpoint where their status differs.

### 2026-11-15 - functional discrepancy: coarse curved boundary

PR238 is now **draft / not ready to integrate**. The curved source exists,
but adaptive_stable final point budgets leave two points per side at step 1
and four at step 2. Twelve intervals is the total for four sides; the curved
side has only three segments. Step-2 targets 8/7/7/7 are clamped to 4/4/4/4;
its TRI candidate is rejected, then the bridge uses that source to generate
mixed once. The expected coarse-to-fine mixed loop is still missing.
See the [diagnosis](CURVE_DISCRETIZATION_DIAGNOSIS_20261115.md).
Prior exact-feature CI certifies bounded contracts, not this functional goal.
No new native qualification or scientific control change occurred.

### 2026-11-15 — functional candidate implemented and exact feature qualified

Original-curve QUAD/AFT application integration is implemented on
`quad/real-boundary-application-20261115`, exact feature
`79828fcbfc1c4aa20d84576e58f1a3ef8fe2592a`,
[PR238](https://github.com/tiagosombrra/apmesh-modernization/pull/238).
It reuses the original curve workflow and actual refined tree, preserves
source IDs/XYZ/intervals and exact cell identities/counter/ordered leaves,
then publishes a typed physical QUAD/original-AFT layout. Measured output:
**37 nodes, 16 QUAD, 28 TRI, 12 original intervals, four nonuniform sides,
16 native leaves**. Fixed16 remains an unchanged-byte regression.

The curve/tree snapshot comes from the original locally selected source
attempt. Its global TRI reference is **rejected** by the existing criterion
and remains `reference_tri_accepted=0`. Initial geometric publication does not
override that decision or constitute an accepted mixed adaptive epoch.

Exact feature [CI #43716128507](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43716128507)
passes **4/4**. Local GNU, MSVC Debug, Clang ASan/UBSan/leak and configured
LLVM22 analysis pass their bounded scopes. Local CTest **85/85**, hosted
CTest **85/85** and Python **527/527** pass. Local/hosted frozen Eistute five
and Book four accepted/rejected states retain identical OBJ/acceptance fields
and verified exact boundaries. See the [closure review](REAL_BOUNDARY_APPLICATION_CLOSURE_20261115.md)
and [qualification receipt](evidence/REAL_BOUNDARY_APPLICATION_20261115.json).

Earlier source/compiler, config-admission, refined-edge phase, fixed-ID and
test-target errors remain recorded. First candidate bfd501a CI was 3/4, with
zero frozen comparisons before config admission refusal; it is not a pass.
The first local adapter stopped before CTest on inventory drift 75 -> 85;
LLVM18 configuration errors are invalid analysis despite zero tool exit.
The corrected exact feature qualifies with those failures retained.

**One active item / exact next action:** review PR238's corrected original-curvature
profile, source/domain identity and per-step publication. Resolve required
open documentation checks and obtain independent approval before integration;
repeat required research-merge validation after any authorized merge. The next
functional scientific gate is a defensible mixed curvature/error and selection
policy using actual prior accepted mixed states, not a TRI reference decision.
Do not count these four reconstructions as accepted mixed adaptive epochs.
The code is visible in the primary feature checkout; canonical changes here
are status/evidence only. Integration and post-merge tests remain unperformed.
Auxiliary Doxygen generation in the nested checkpoint worktree failed on
three unchanged API references; the same failure was reproduced in the normal
primary checkout, so a nested-worktree explanation alone was insufficient. It is
not counted as a pass. Repeat required
documentation checks from a normally located checkout before integration.
Research merge and post-merge tests are **not performed**. `mixed_adaptive_epochs=0`;
R3/M7 #221 remains OPEN. Global welding, production mixed postprocessing,
1993 equivalence and wider memory/scientific coverage remain separate gates.

### 2026-11-15 clarification: source adaptation precedes one mixed generation

The Blender scene is one mixed layout built from source step 2, not a sequence
of accepted QUAD-driven refinements. `RunRealBoundaryPatch` first runs the
original TRI Generator through its configured adaptation attempts, then selects
the last locally selected curve/tree snapshot with a complete global outcome
and generates QUAD/AFT once. Recorded TRI source steps 0 and 1 each have four
boundary intervals and four triangles; step 2 has twelve boundary intervals
and 28 triangles and is globally rejected. The later mixed export has 37 nodes,
16 QUAD and 28 AFT TRI; its source boundary is inherited from that step 2.
There is no feedback from this mixed mesh into the preceding curve adaptation.
The previous user-facing description overstated completion: real source reuse
is implemented, but the end-to-end coarse-to-fine mixed adaptive loop is not.
Integration review must retain this distinction; the queued accepted-history,
mixed curvature/error and approved selection gates remain necessary. No new
algorithm, policy or native qualification was performed for this clarification.

### Earlier 2026-11-15 status review and local visualization

**Boundary/AFT clarification:** the visualized controlled case uses fixed
quarter-parameter samples (16 boundary intervals), not production `AdaptCurve`.
Its exterior TRI closure does invoke original `makeGeometryBasedMesh` and,
on the existing repeated-edge-rejection outcome, `makeTopologyBasedMesh` through
`OwnedQuadAftFront`. This bounded path deliberately omits `improveMesh` and
`fillMesh`; it is not the full original generator pipeline. PR214 retains
separate real all-side curve-adaptation experiments, not an integrated live
application contract. Fixed sampling bounds the controlled P1/P2 experiment;
it does not remove the outstanding real-boundary integration gate. No scope,
selection policy or execution order is changed by this clarification.

Reviewed canonical research `392d02c0dc1fd52bcc6cb83320469d1143636ef6`.
The clean local checkout was fast-forwarded from `3beec583` (162 commits behind);
other worktrees and branches were preserved. Live GitHub confirms PR236 merged
and both its exact feature [run #43704424433](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43704424433)
and exact research merge [run #43705007549](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43705007549)
completed **4/4 SUCCESS**. The reviewed research head has no code/test/workflow
changes relative to the qualified feature. This documentation checkpoint is
not a new native qualification or a closure of R3/M7.

Five exact Windows CI OBJ artifacts were inspected and opened in Blender 5.3.0:
P1 69/42/36 and unaccepted bands 93/62/44, 107/71/54, 109/75/50,
117/82/52 (nodes/QUAD/TRI), all with 16 boundary edges. Local replay of
the existing normal/rollback receipt verifiers rejected eight forged records
per run. No local native build, CTest, sanitizer or full historical oracle
campaign was run. See [bounded review](STATUS_REVIEW_20261115.md).

**Subsequent accepted-epoch gate:** specify P2d-1c4b accepted-state ownership/archive,
source fingerprint and memory/file publication failure matrix; record the
advisor-approved error/quality/complexity selection policy before accepting
two distinct transitions from the actual preceding accepted mixed states.
Keep `adaptive_epochs=0` until those gates pass. No policy approval is inferred
from the current Pareto profiles. R3/M7 #221 remains open.

[PR235](https://github.com/tiagosombrra/apmesh-modernization/pull/235)
merged into research `quad-templates` at
`ab1dc62a815f3d56c9b25845bec00863730ddcd5`.
Exact feature `27851df2625e0c0b37e12023af699a01f3d0304c`
passed [CI #43664129060](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43664129060)
**4/4**: Linux GCC/Windows MSVC actual native physical AFT and
independent OBJ/Pareto comparisons, Linux ASan/UBSan/leak,
85/85 root CTests, 527/527 Python tooling, original frozen
Eistute/Book TRI science; six adverse Pareto cases explicitly executed
on both operating systems and Linux sanitizer application.
The source-controlled UV-area profile finds north dominates west
among the staged 93/62/44, 109/75/50, 107/71/54 and 117/82/52
physical sources; adding *QUAD face count* as an independent objective
makes all four non-dominated. UV area is integrated directly from
each exported physical OBJ, not guessed from face counts.
This is a *profile-dependent diagnostic*, not an accepted
scientific adaptive policy. [Qualified evidence](evidence/P2D1C3_PROFILED_PARETO_20261114.json).

**Integrated [P2d-1c4a PR236](https://github.com/tiagosombrra/apmesh-modernization/pull/236)**,
feature `f55b8e4aec4c06eb6603f3cf6f6de54d3fdf1f81`,
merge `8a451eee7fad416d36604a61afd35412c65cd72a`,
qualifies a **reversible real physical-owner transaction rehearsal**.
The original 69-node/42-QUAD/36-AFT-TRI P1 `Patch/SubMesh` owner
is **actually published** before the error-driven native AFT
93-node/62-QUAD/44-AFT-TRI successor is constructed. Its
source error is independently **recalculated from the live accepted
P1 owner**, not reused blindly from an unpublished candidate.
Five real fault injections reject native/clone/prepublication
failures without changing the previous nonempty Patch forward/back
owner links, any node pointer/ID/XYZ/four curvature scalars,
element pointer/ID/area, exact ordered element observers or prior
OBJ bytes. A physically typed replacement owner is temporarily
attached using `noexcept` pointer operations and **reverted**,
with restoration guard; eight forged Python output receipts must
be independently rejected on normal and rollback app runs.

Exact-head [CI #43704424433](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43704424433)
**4/4 completed SUCCESS**: native controlled Linux GCC/Windows MSVC,
Linux ASan/UBSan/leak, frozen original Eistute/Book TRI parity,
85/85 baseline CTests and 527/527 Python tooling. The intermediate
feature `4b544600` failed real GCC compilation due to legacy
non-const `ElementAdaptive::GetId`, fixed narrowly in
`f55b8e4a`; no failed CI was falsely counted as passing.
[Bounded transaction protocol](P2D1C4A_OWNER_TRANSACTION_REHEARSAL_20261115.md).
[Qualified exact evidence](evidence/P2D1C4A_REAL_OWNER_TRANSACTION_REHEARSAL_20261115.json).

**Scientific boundary remains firm:** reversible pointer staging is
not an adopted second mixed epoch; no replacement next-OBJ output is
atomically published and no research-approved source-error/quality/
complexity choice has been adopted. `adaptive_epochs=0`; R3/M7
[#221](https://github.com/tiagosombrra/apmesh-modernization/issues/221)
OPEN. After real-boundary application integration, P2d-1c4b needs the accepted mixed history/owner
transaction, archived typed previous state, strong-exception-safe
filesystem and memory publication, explicit prior-approved selection,
and two genuinely source-state-driven distinct accepted changes.
No production `AdaptCurve`, global nonmanifold high-valence weld,
historical 1993 equivalence, all-QUAD or anisotropy.
`main` and default original TRI remain unchanged.


## P2d-1c1 and P2d-1c2 integrated — original native physical AFT history

[PR233](https://github.com/tiagosombrra/apmesh-modernization/pull/233)
merged original native source-tree second alternatives at
`15a57f3604c9fc8b072762ed10f3219aa12c9ad7` after
[exact-head #43624756858](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43624756858)
**4/4 SUCCESS**: Linux/Windows native+controlled app, ASan/UBSan/leak,
85/85 baseline CTests, 527/527 Python and frozen Eistute/Book TRI parity.
Retained first failed C++ const-correctness build separately. Using the
previous staged 93-node/62-QUAD/44-AFT-TRI physical source's distinct
worst AFT residual face103 near UV(0.8,0.1), real original Quadtree
variants yielded **31-leaf corner: rejected**, **34-leaf west: 75
UV QUAD**, **34-leaf north: 71 UV QUAD**, and **37-leaf both:
82 UV QUAD**. [Bounded native evidence](evidence/P2D1C1_NATIVE_SECOND_BAND_TRIALS_20261114.json).

**Integrated research-only [PR234](https://github.com/tiagosombrra/apmesh-modernization/pull/234)**,
feature `32e4653ff80947498c39953ce53f50af618203e9`,
merge `672aa297352d0ee316c57f347e7cd5f69e4f86d1`:
rebuild two original AFT/QUAD native source trees for each second-band
variant, run the *original* AFT closure and construct real typed physical
Bezier QUAD/TRI `SubMesh` candidates. Independently audited actual Linux and Windows physical
AFT/QUAD application and Linux ASan/UBSan/leak jobs **SUCCESS**,
frozen Eistute/Book TRI science **SUCCESS**, Linux 85/85 root CTests
and 527/527 tooling Python **PASS**. Exact-head
[CI #43663198795](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43663198795)
**4/4 completed SUCCESS**, feature merged into research only.
No accepted adaptive epoch or production `main` merge.

All original source boundary edge counts remain 16 and the
isolated corner is rejected without a physical OBJ. Measured **staged-only**
new candidates (independent same **4096 UV sites**, 64x64):
- **west:** 109 physical nodes, 75 QUAD/50 AFT TRI (125 total
  elements), 37.5% QUAD UV area; maximum error 0.02626857,
  uniform UV RMS 0.01018989 and source-area RMS **0.00996008**;
  candidate SHA-256 `ca08918f6d71fa672de22a72eb6fef7c106c90c7fd02d40cb19852972b4274ee`.
- **north:** 107 nodes, 71 QUAD/54 AFT TRI (125 total),
  37.5% UV; maximum error 0.02626857, uniform UV RMS 0.00958005,
  source-area RMS **0.00923332**;
  SHA-256 `6eb4faedeaab44fbfa3d4cb2ca1ea618a3dca513dc241871c57bcc7eae26d500`.
- **both:** 117 nodes, 82 QUAD/52 AFT TRI (134 total),
  40.625% UV; maximum error 0.02626857, uniform UV RMS 0.00945933,
  source-area RMS **0.00915513**;
  SHA-256 `b77afb530724f38ff81f0f3e7f06fca6c8dc0cb4a15562ce933a4013724bd36c`.
The first staged physical band baseline is 93 nodes/62 QUAD/44 AFT TRI,
32.8125% UV, maximum 0.05160741 and source-area RMS 0.01181032.
All three candidate SHA-256 results were reproduced on Linux and Windows;
minimum signed QUAD scaled Jacobian 0.567009 and minimum QUAD split-normal
cosine 0.997013 remain positive. These are bounded **sampled**
source approximation metrics, **not a general quality/complexity policy**.
[Preliminary exact-source evidence](evidence/P2D1C2_SECOND_PHYSICAL_AFT_TRIALS_20261114.json).

**Scientific next gate:** implement a reproducible, explicitly
profiled west/north/both multi-objective error/complexity/quality
audit without silently imposing a scientific acceptance rule;
then design an actual accepted-owner transaction with fault
injection. Compare the west/north/both
element-count/error/quality Pareto trade-offs and develop an explicit
previous-*accepted*-mixed-owner transaction with fault injection and
scientific selection policy. New physical candidates remain
`staged_unaccepted`, **`adaptive_epochs=0`**.
R3/M7 [#221](https://github.com/tiagosombrra/apmesh-modernization/issues/221)
OPEN. Original fixed16 is not full `Adapter::AdaptCurve`; no Eistute/
Book globally welded nonmanifold hybrid, literal historical1993
algorithm, all-QUAD or anisotropic production support.
`main` and original TRI production remain unchanged.



## P2d-1b3 and P2d-1c0 integrated — prior bounded source-topology gates

[PR231](https://github.com/tiagosombrra/apmesh-modernization/pull/231)
merged into research `quad-templates` at
`4b7f485a0df2c5108dbd822f337d2e38bba2947a`.
Exact source `1efb13b6a6fb46fca77deba81aa405db5bff90d5`
passed [CI #43620929978](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43620929978)
**4/4 jobs**: exact-head Linux/Windows real physical app, Linux
ASan/UBSan/leak, 85/85 root CTest, 527/527 tooling Python and frozen
Eistute/Book production TRI scientific equality. Independent Python evaluates
both first original and staged physical AFT+QUAD candidate on the **same 4096
UV sites**, not the unequal 354/486 per-element samples: max XYZ
`0.06564122093 -> 0.05160741346`, uniform-UV RMS
`0.01729520385 -> 0.01251800084`, source-Jacobian-weighted RMS
`0.01598126566 -> 0.01181032464`. These are finite-grid diagnostics
on one original Bezier model, not a continuous bound or adaptive acceptance
policy. The candidate remains `staged_unaccepted` and
`adaptive_epochs=0`. Former draft
[PR230](https://github.com/tiagosombrra/apmesh-modernization/pull/230)
was **closed unmerged as superseded**: its positive-staging requirement is
included in PR231; the extra synthetic rejection-negative control was *not*
integrated or CI qualified and remains an optional independent safeguard.

**Integrated [P2d-1c0 PR232](https://github.com/tiagosombrra/apmesh-modernization/pull/232)**,
exact feature `e0621a9b8b2675c60ba5bfd3cd0dfe0e395b01af`,
merge `a03938627ab8bf2aeadc04d1c238c2eb693d651f`,
implements **source-grid-only** topology preflight for the next
actual staged candidate's maximum original AFT residual: face103,
UV near (0.8,0.1), distinct level-2 source coordinate (3,0).
Six local Python tests passed; the prior exact feature `7a42a496`
had 4/4 green CI but did **not execute** the new test file. The corrected
exact feature `e0621a9b` passed
[CI #43624052194](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43624052194)
**4/4 jobs**, explicitly executing the six independent tests in actual
Linux/Windows/ASan controlled application, 85/85 root CTests,
527/527 Python tooling and frozen original Eistute/Book TRI parity.
[Source-bound receipt](evidence/P2D1C0_SECOND_BAND_DYADIC_PREFLIGHT_20261114.json).
Source-only predicted topology does **not** count as actual native QUAD output.
With the prior 28-leaf/21-of-64 eligible grid, the selected cell alone
predicts 31 leaves/22-of-64 QUAD UV but is correctly **rejected as a
disconnected, diagonal-vertex island**. Two bridge alternatives
(3,0)+(2,0) or (3,0)+(3,1) predict connected 34 leaves/24-of-64;
both bridges predict 37 leaves/26-of-64. These are **necessary dyadic
topology estimates, not actual original C++ Quadtree or native AFT execution**.
[Bounded protocol on draft PR232](https://github.com/tiagosombrra/apmesh-modernization/blob/quad/p2d1c0-second-error-band-dyadic-preflight-20261114/docs/research/quad/P2D1C0_SECOND_BOUNDARY_BAND_PREFLIGHT_20261114.md), not yet on canonical.

**Native implementation proposal [PR233](https://github.com/tiagosombrra/apmesh-modernization/pull/233)**,
head `7b536dc901cae1e8b9410f6fbd9f3540c20dba09`, is
**draft; candidate exact-source CI #43624756858 has Linux/Windows/ASan
success but baseline root job pending**. The first exact-source CI
#43624612764 **failed real C++ compilation** on non-const `Vertex::getX/getY`
accessors; a narrow typed-pointer fix is retained and independently retested. It takes the actual new
physical AFT source residual, reconstructs the real previous 28-leaf native
Quadtree before each trial, and attempts original native
`subdivideToLevel`, `refineAccordingToNeighbors`,
`CaptureLeafPolygons` and `EmitLeafQuads` for corner-only, west,
north and both bridge alternatives. Its real C++ records are independently
cross-checked by the P2d-1c0 dyadic Python oracle and the six negatives.
Actual native Quadtree trials on the previous first 28-leaf tree returned
isolated corner **31 leaves / 0 QUAD (rejected)**; west **34 leaves / 75 QUAD**,
north **34 leaves / 71 QUAD**, and both **37 leaves / 82 QUAD**,
with UV area respectively `0.34375`, `0.375`, `0.375`, `0.40625`.
Identical source-native results on Linux/Windows/ASan, not merely
the previous dyadic predictions. No new physical second AFT reconstruction
or accepted epoch is implemented.

**Next native gate P2d-1c1:** propagate the *current previous physical
candidate* and source-error-selected site to the real native Quadtree,
trial both minimal bridge directions and the three-cell band with original
2:1 balancing and native `EmitLeafQuads`/AFT physical reconstruction.
Independent common-site source error, QUAD Jacobian, warpage, cost,
observer/owner rollback, immutable source/OBJ identities and scientifically
pre-registered acceptance criteria are mandatory. Do not count a source-only
preflight, original fixed16 proposal, or staged physical output as an
accepted mixed history epoch. R3/M7 [#221](https://github.com/tiagosombrra/apmesh-modernization/issues/221)
**OPEN (zero accepted adaptive QUAD/TRI epochs)**; no global Eistute/Book
high-valence weld, 1993 historical reconstruction, all-QUAD or anisotropy
claim. `main` and default TRI remain unchanged.


## P2d-1b2 physically reconstructed — qualified feature CI, adaptive history still OPEN

Research-only full original native AFT physical reconstruction from the real three-leaf
error-selected connected band was merged through [PR229](https://github.com/tiagosombrra/apmesh-modernization/pull/229),
research merge `289b6be6e97f787b53471255f9d30fbf3777fbba`.
Exact feature `bada655ae68a635f4b9664a05b2ab261d2d8d94c` passed
[CI #43619762822](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43619762822),
**4/4 jobs**: Linux GCC and Windows MSVC native/real physical application,
Linux ASan/UBSan/leak application, 85/85 root CTests, 527/527 Python controls,
and frozen original Eistute/Book TRI parity. A separate exact-merge CI was not
verified at this checkpoint.

For the original curved Bezier fixed16/vertex-mean source, baseline **69 nodes /
42 QUAD / 36 AFT TRI** and the new staged, **unaccepted** physical candidate
**93 nodes / 62 QUAD / 44 original AFT TRI** both retain 16 original source
boundary edges. Independently audited source UV coverage grew from **25%** to
**32.8125%**; sampled source maximum is **0.0463899583 -> 0.0367706982**.
Sampled RMS is **0.0130653586 -> 0.0078639324**, but comparison uses
**354 vs 486 different sampled sites**, so this is NOT a same-sample convergence
proof. Candidate OBJ SHA-256 is
`76b0b4defecc5d534815fb9f41e1405653597a4a0bee6cc7b722ec2460d7afd6`;
original OBJ remains
`cbf6cd6308ba54544d06c5d562c491eb7d43ddb216365e0e9d188fd3430295e0`.
[Bounded exact-source receipt](evidence/P2D1B2_REAL_PHYSICAL_CANDIDATE_20261114.json).

**Historical P2d-1b2 handoff correction:** earlier draft
[PR230](https://github.com/tiagosombrra/apmesh-modernization/pull/230)
was **closed unmerged** after its positive physical-staging requirement
was independently covered by integrated [PR231](https://github.com/tiagosombrra/apmesh-modernization/pull/231).
The PR230-specific synthetic rejection-only negative was not qualified
or merged. Subsequent original AFT physical generation and common-site
source-error validation are integrated as PR234 and PR231 respectively,
as documented in the current checkpoint above. This historical
subsection does not override R3/M7 [#221](https://github.com/tiagosombrra/apmesh-modernization/issues/221):
`adaptive_epochs=0`, original fixed16 not production `AdaptCurve`,
no global high-valence weld, all-QUAD, anisotropy or 1993 equivalence.

## Completed bounded repair

**P0 is integrated through [PR216](https://github.com/tiagosombrra/apmesh-modernization/pull/216)**,
research merge `49c9dc3be66dab2f4839e0ab661065a1ec5c5ba3`. Physical QUAD construction now refuses concave,
collinear, crossing and inverted UV cycles using all four existing-threshold
corner checks before observer publication. Original012/023 expressions, physical
metrics, production TRI, input and boundary policies remain unchanged.

- Unchanged original source fails the new concavity witness; failure retained.
- Linux GCC13.3, Windows GCC16.1 and MSVC19.44 Debug C++17 pass20accepted and
  40rejected cases each, with observer pointer/order/list-slot preservation.
- Exact candidate `a2c42776a16cc5e03d643ce916e5c6d81f0aa5dc` and exact research merge each pass85 CTest/527
  Python with no failures/errors/skips, including both original physical model
  modes, original fault slots and negative file mutations.
- Configured source/header/whole-probe analysis passes. Candidate push/PR and
  merge remote runs each complete four jobs successfully; fresh Eistute/Book
  frozen OBJ, acceptance and positive boundary comparisons pass.

[Delivery receipt](evidence/FOUR_CORNER_ADMISSION_DELIVERY_20261114.json) ·
[Repair/evidence](FOUR_CORNER_ADMISSION_20261114.md) ·
[Roadmap](IMPLEMENTATION_ROADMAP.md) · [Milestones](MILESTONE_STATUS.md) ·
[Protocol](CONTINUATION_PROTOCOL.md) · [Journal](SESSION_LOG.md).

## Controlled P1 integrated — mixed P2 prerequisites delivered, R3 still open

[PR217](https://github.com/tiagosombrra/apmesh-modernization/pull/217) is merged at `d39bbc447f88e179c3c4ee674bd9309f59c18eed`.
The real `ap_mesh --config` controlled case produces 42 physical QUADs,
36 original-AFT triangles, 69 owned nodes and 16 source boundary intervals on the original
curved ModelCurvaBezier. Independent Bezier UV/XYZ/winding/topology checks,
positive quality, stable identities and nonempty publication rollback pass.
Exact candidate 0999769 and exact merge each pass 86 CTest /527 Python.
Linux/Windows application checks and Linux frozen TRI equivalence pass.
Clang18 ASan/leak checks and a real UAF control pass in this bounded case.
See [evidence](evidence/P1_CONTROLLED_APPLICATION_20261114.json) and
[build/config instructions](../../../configs/quad/README.md).

Default builds retain TRI and QUAD refusal. This one-shot case requires
`AP_MESH_ENABLE_EXPERIMENTAL_QUAD=ON` plus the named fixed16/vertex_mean policy;
it does not run AdaptCurve or adaptive history. First failed CI admission for
two new config assets was preserved and corrected explicitly, without weakening
reference or scientific checks. Main and the unmerged larger PR214 are preserved.

**P2 functional target:** retain this typed hybrid SubMesh as actual history
for two different accepted adaptive epochs, including typed curvature,
quality, reconstruction, retry/rollback and export. P2a/P2b/P2c and
P2d-0/P2d-1a engineering prerequisites are now integrated; no actual
mixed adaptive epoch has yet been accepted.

## Mixed-history infrastructure — P2a/P2b/P2c integrated

[P2a PR218](https://github.com/tiagosombrra/apmesh-modernization/pull/218)
merged as \`d40114ed2dc9def294b382557a571e5b62285b83\`.
It qualifies a bounded typed physical SubMesh clone, partial-construction
fault rollback, Patch observer restoration and independent element/node
identities. Original PR synthetic-merge CI: 4/4 success, Linux ASan/UBSan/leak success,
85 baseline CTests and 527 tooling Python.

[P2b PR219](https://github.com/tiagosombrra/apmesh-modernization/pull/219)
merged as \`21ba08e55e014d5c9fa7533c9f7361ad4c98c7dc\`.
It qualifies a research-only polygon-aware 3/4-node vertex-link/topology
auditor and a *triangulated metric diagnostic*, cross-checked from original
OBJ via independent Python cosine-law/Heron calculations. Five malformed
cases are refused. The real 69-node controlled patch has 16 boundary and
53 interior vertices; its barycentric angle-defect witness sums to 2*pi.
Original PR synthetic-merge CI: four successful jobs including Linux sanitizers and unchanged
frozen TRI scientific parity. Neither contribution changes the original
triangle-specific \`Adjacent\`/\`CurvatureDiscrete\` path.

**CI provenance correction:** Previous P2a/P2b PR workflows used GitHub's
synthetic pull-request merge checkout and did not assert exact feature-head
identity. Their passing checks are valid for the corresponding tested trees,
not proof that the runner checked out their stated feature SHA. P2c changes
all three candidate checkouts and artifact names to the actual PR head SHA,
with an explicit clean-worktree identity check. Do not retroactively relabel
the prior candidate runs.

**P2c integrated** via [PR220](https://github.com/tiagosombrra/apmesh-modernization/pull/220),
merge `535acf7b3ba68dd1ee1267e682f2991a89214a87`. Its real controlled
physical QUAD corner-normal metric has minimum scaled Jacobian `0.567009347`,
minimum split-normal cosine `0.999145645` and maximum physical edge ratio
`3.309653057`, each independently checked against original Bernstein-control
Bezier derivatives. Four physical-negative cases are rejected. Exact feature
source `bd6135cd4c6ec30f4e3de3bf94593d106002c8b9` passed [CI
#43603290586](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43603290586):
4/4 jobs, Linux/Windows application, ASan/UBSan/leak, 85 root CTests,
527 Python tooling and original frozen Eistute/Book TRI equivalence. The
updated workflow now confirms actual feature-head source SHA at all candidate
checkouts and labels artifacts by that SHA. The output physical OBJ SHA-256
remains `cbf6cd6308ba54544d06c5d562c491eb7d43ddb216365e0e9d188fd3430295e0`.
See [P2c scope](P2C_TYPED_PHYSICAL_QUAD_QUALITY_20261114.md).
The previous two PR CI checkout identity limits remain documented above;
P2c rechecks their integrated code in the current exact feature tree.
**P2/R3 and M7 remain OPEN:** no two distinct adapted and accepted
QUAD/TRI mesh epochs, no production mixed curvature or rejection policy. The
[next constrained implementation issue #221](https://github.com/tiagosombrra/apmesh-modernization/issues/221)
requires two real previous-state-driven accepted mixed epochs with independent
provenance, quality, rollback and default TRI equivalence.
Do not confuse P2a/P2b test passes with completed adaptive history.

## P2d-0 and P2d-1a integrated — no accepted adaptation epochs

[P2d-0 PR223](https://github.com/tiagosombrra/apmesh-modernization/pull/223)
merged at `82522e0588a650b3c6421565883506a0f0cde831`;
its exact feature source `f1ea9332fa4d322f4578d3b6c46475776efa424f`
passed [CI #43605731184](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43605731184):
4/4 jobs, Linux/Windows native, original frozen TRI, 85 root CTests
and 527 Python controls. The first run failed strict architecture
inventory after adding the native test; the retained CMake SHA-256 was
**corrected without relaxing the inventory test**, then all gates passed.
P2d-0 is a synthetic-only lineage metadata gate with fourteen negatives;
its fabricated three receipts must never count as adaptive epochs.

[P2d-1a PR226](https://github.com/tiagosombrra/apmesh-modernization/pull/226)
merged at `c78a4445424d027d7a32a54e419fb129e3ef6622`.
Exact feature `530914390c44916067f258f18e2cba1cae61959f`
passed [CI #43606747684](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43606747684):
4/4 jobs, 18 native QUAD CTests each Linux/Windows, genuine
`ap_mesh` application, Linux ASan/UBSan/leak, 85 root CTests,
527 tooling Python and frozen original TRI Eistute/Book parity.
The original physical OBJ remains byte-identical across both systems
(SHA-256 `cbf6cd6308ba54544d06c5d562c491eb7d43ddb216365e0e9d188fd3430295e0`).

This **read-only source error indicator**, evaluated on real physical
nodes, QUAD bilinear sampling and AFT TRI barycentric sampling, reports
`354` samples: `0.0026204483` maximum interior QUAD error,
`0.0463899583` maximum exterior AFT TRI error and
`0.0130653586` global sampled RMS. The maximal QUAD is face4,
native source cell13 / leaf ordinal6 / depth2; the worst TRI/AFT
is face74 near UV (0.2,0.1). An independently computed
**UV-area** audit finds only `25%` QUAD coverage versus `75%`
TRI/AFT; approximately `29.6%` versus `70.4%` of the faceted
physical area. TRI/AFT contributes `~99.53%` of the *unweighted
sampled squared* residual and `~99.84%` of a supplementary
coarse physical-face-area-weighted sampled estimate. Neither
value is a certified surface error integral or general policy.

This imbalance is structural: `CaptureLeafPolygons` excludes all
quadtree leaves touching the source boundary. Refining only an
existing interior QUAD leaf cannot by itself enlarge the current
25% UV footprint. P2d-1b must compare **actual native tree/AFT
refinement** of (a) the maximal-error QUAD interior and (b) the source
leaf containing the maximal-error AFT triangle; evaluate both
source-surface error and QUAD area coverage without pretending that
more QUAD faces imply QUAD dominance. The initial fixed16 source
boundary still does **not** run `Adapter::AdaptCurve`.

**R3/M7 remains OPEN:** no second candidate tree has been changed
or accepted here (`real_tree_edits=0 adaptive_epochs=0`). No
general nonmanifold sheet welding, literal 1993 method, all-QUAD
or anisotropic acceptance is claimed. See [bounded evidence and
independent numerical caveats](evidence/P2D0_P2D1A_QUALIFICATION_20261114.json)
and the [canonical issue #221](https://github.com/tiagosombrra/apmesh-modernization/issues/221).

## P2d-1b0 and P2d-1b1 integrated — connected native topology only

[P2d-1b0 PR227](https://github.com/tiagosombrra/apmesh-modernization/pull/227)
merged at `9259de230c3da24ffd4dbced65beae7375c3fc46`
after exact [CI #43609586259](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43609586259)
passed four jobs, Linux/Windows native tests, ASan/UBSan/leak,
85 root CTests, 527 tooling tests, and frozen original TRI.
The real Quadtree source cell #13 refinement makes a valid
54-QUAD UV region of unchanged 0.25 area; the higher-error
AFT source cell #6 refinement instead produces 0.265625
prospective area but is **rejected** as `Boundary vertex is not manifold`.
No invalid QUAD island is accepted or published.

[P2d-1b1 PR228](https://github.com/tiagosombrra/apmesh-modernization/pull/228)
merged at `092b9adfa0f9f03d4c28b5218759b7e89cf5b199`;
exact source `0c9bdc7f7562ce2c9633b4b44bb07fe7039b16a8`
passed [CI #43618564496](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43618564496)
4/4 jobs with Linux/Windows native and application, Linux
sanitizers, 85 CTests, 527 Python and strict frozen TRI parity.
A **three-leaf native source refinement band** (#6, #7, #9)
connects the previous isolated boundary child to the original
interior QUAD region: 19 to 28 actual native leaves, 62
**UV-only QUADs**, 0.328125 of the source UV area
(32.8125%, versus 25% initially). An independent exact
8-by-8 dyadic grid oracle verifies 21/64 eligible cells,
four-neighbor connectivity and absence of holes. The original
physical OBJ remains SHA-256
`cbf6cd6308ba54544d06c5d562c491eb7d43ddb216365e0e9d188fd3430295e0`
on both platforms and the sanitizer run.

**Scientific limit:** no native AFT or physical SubMesh is
regenerated from the new band in these gates.
`actual_aft_retriangulations=0 adaptive_epochs=0` remains
mandatory. A new draft [P2d-1b2 PR229](https://github.com/tiagosombrra/apmesh-modernization/pull/229)
attempts physical reconstruction and must independently
classify any failed candidate; even a physically valid
candidate is not an accepted adaptive history epoch.
R3/M7 remains OPEN.

[Bounded original-topology receipt](evidence/P2D1B0_P2D1B1_NATIVE_TREE_BAND_20261114.json)
and [canonical issue #221](https://github.com/tiagosombrra/apmesh-modernization/issues/221).

## Explicit remaining limits and history

P0 closes one UV admission defect, not whole M4 or continuous physical Jacobian,
global topology, all-QUAD or production readiness. Broader native sanitizer/
allocation-denial/general-geometry coverage, historical1993 point/formula
approval, model-wide node ownership and high-valence sheet decisions remain open.
The prior interrupted544/922 build remains unqualified; fresh successful reports
above have their own exact identities. Stale R2c19/20 legacy evidence identities
remain explicitly historical rather than silently certified.

The former state is [preserved byte-for-byte](STATE_HISTORY_20261114.md), source
3809eb7 Git blob `bbc4260a41cd92e43ecc0451830e645f4bb9f883`.
The [audit](STATE_PLAN_AUDIT_20261113.md) and append-only journal retain failures
and scope corrections. This final checkpoint changes documentation/evidence
only; its own SHA is not a new scientific or complete-process qualification.
