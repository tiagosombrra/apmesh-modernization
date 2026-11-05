# Eistute function profile and selected production package

Disposition: qualified external sampling of the observed first-call prefix;
the required reuse gate remains incomplete. Starting revision:
d54ea9614039005f3a971bf525a9b6d750dc3ded. The target is the unchanged qualified
1636547 native executable, SHA-256
776bd80051ca44707ddeccb5ffd7b5eb341a006eb6a3c80f9da6600038f4a11d.
Configuration, model, PDB, production/tests, compiler checks and scientific policies
remain unchanged. No production repair, Book or additional model is run.

## Collection qualification

Adapt the existing Windows external observer with jittered intervals: 0.75-1.25 s
for Eistute, 0.075-0.125 s for the synthetic calibration. Observe only the primary
thread; process/thread CPU totals establish its scope. Stacks are weighted by the
thread CPU increment since the preceding sample. Symbolization runs after resume;
stack storage is reserved beforehand and suspension has unwind cleanup.

Admission limits were fixed before calibration: at least 20 active control samples,
dominant known hot-function fraction 55-98%, direct control suspension <=2%, observer
CPU <=10% of control CPU and fixed-work wall ratio <=1.2. Actual observation limits:
direct suspension <=1%, observer CPU <=5% of target CPU and primary-thread CPU >=95%
of process CPU. All samples must have valid contexts/stacks and matching symbols.

The live busy-thread test resolves the leaf and positive CPU; the idle control has
five captures with zero CPU increment. The exact target PDB resolves improveMesh.
One unobserved and one observed fixed integer workload execute identical work and
checksums. Its two noninline functions have a 4:1 iteration ratio; 52 active samples
assign 87.46% of their CPU weight to the dominant function. The observed control
lasts 5.4660 s versus 5.1896 s unobserved (ratio 1.0533), with 0.5186% direct
suspension and 1.1628% observer/target CPU. This paired control bounds collection
cost; it is not a production speedup or exact recovery of function CPU shares.

## One unchanged Eistute process

One fixed two-call command only, retaining the total 300-second watchdog including
suspension. The deadline is reached at 300.012075 s; termination completes at
300.029930 s. The first call remains incomplete; no second call starts. There are
18 exact prior-version partial artifacts through accepted 0/1 and rejected 2/3,
but no completed-call verification or new positive boundary-coverage claim.
Prior live output is restored byte for byte. No repeat, new model or fresh
regression campaign follows. Previous qualified evidence stays retained by identity.

The profile has 294 valid active stacks. Primary and process CPU are both
276.8125 s; sampled CPU increments cover 99.84% of primary CPU. Direct suspension
totals 1.43508 s (0.4783% of wall); observer CPU is 3.609375 s (1.3039% of target
CPU). All predeclared scope/overhead limits pass. Process CPU/wall is 92.26%.

| First production frame, including library callees below it | CPU sample weight |
| --- | ---: |
| AdvancingFront::fillMesh | 30.59% |
| PatchBezier::CalculatePointUV | 20.08% |
| CurveAdaptiveParametric::CalculatePointT | 10.34% |

These estimates weight primary-thread stacks by CPU increments, using varied
wall-time intervals from a fixed pseudo-random sequence over the observed prefix. They are not exact per-function timers or a
whole completed-process profile. Inclusive functions overlap; the table assigns
each stack to only its first production frame. Unresolved library leaf symbols
remain explicit in the raw leaf table and are not silently named as callers.

## Next package: fillMesh membership views

fillMesh occurs in 86 stacks; 73 point to its edge membership scan at line 1045,
six to the vertex scan at 1024. The code linearly searches growing observer lists
for each quadtree vertex/edge, comparing pointer identity. Its nested search cost
is source-derived quadratic; scoped hash membership views can make it expected
linear without replacing or reordering those lists.

Select one engineering package: temporary vertex/edge membership sets, preserving
pointer identity, existing-prefix duplicates, candidate order, append/publication
order and the final TransferTemplateMesh ownership commit. Never deduplicate by
coordinates or IDs, iterate the hash table to publish objects, or disable Debug
iterator checks. Preserve allocation-failure prefixes explicitly; new allocation
ordinals cannot inherit old qualification unchanged. This package is not
implemented by the profile. Timed reuse, Book, exact-delivery/main and Stage 3
remain open; the PR stays a draft.

Observer source/build, predeclared limits, qualification commands, raw stacks,
CPU data, complete function tables, hashes and restoration manifests remain under
build/eistute-function-profile/. Observer source and analysis are diagnostic
artifacts; no production file is modified.
