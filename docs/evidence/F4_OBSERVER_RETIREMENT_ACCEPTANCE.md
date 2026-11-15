# F4 observer retirement and cache validity acceptance round

Entry: PR #183 main `f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94`.
Classification: engineering acceptance and retained-evidence applicability review. No production
code, scientific model/configuration, formula, floating-point order, numerical
threshold or existing support promise changes. The [finite catalog](../architecture/STAGE3_FINITE_PACKAGES.md)
retains all four F4 exits and their links to S3-05/07 and F1/F2/F3.

## Round result and remaining dependency

| Item | Result |
| --- | --- |
| F4-01 registered Patch/SubMesh links | Qualified via [forward Patch/SubMesh retirement](FORWARD_PATCH_RETIREMENT.md). Intrusive nonallocating forward registration retires matching forward and registered back observations across both Geometry/Generator destruction orders, object moves and rebinding. |
| F4-02 ReplaceCurve observers | Qualified via [curve replacement](REPLACED_CURVE_OBSERVERS.md) and native probe verification. Old-curve observations retire when the last current incidence leaves; destination publication stays caller-managed, preserving the nonallocating synchronization commit, exact foreign observer order, and post-destruction state across Bezier and Hermite families. |
| F4-03 post-publication cache mutation | Blocked admission retained via [P4 cache mutation admission](P4_CACHE_MUTATION_ADMISSION.md). No qualified native witness of post-publication cache mutation exists; control-only loader setters operate prior to geometric reconstruction. |
| F4-04 forward, copied and rebound links | Qualified for public live Patch/SubMesh forward links in [FORWARD_PATCH_RETIREMENT.md](FORWARD_PATCH_RETIREMENT.md) and for Node value/observer state in [NODE_COPY_STATE.md](NODE_COPY_STATE.md). Expired foreign elements and arbitrary unmeasured aliases remain separate open blockers. |

This round completes the applicability review for F4-02 and establishes the F4 acceptance
status. F4 remains bounded: raw-route admission in F2, unadmitted F3 root graphs, and
broader Stage 3 memory/lifecycle obligations remain separate.

## Replaced curve observer applicability

The retained repair in `PatchCoons::ReplaceCurve` operates when a slot is assigned a new curve:
it removes all observers matching `this` from the old curve only when no other slot of the patch
still references that old curve. Repeated incidences retain observations until the final reference
leaves.

The native verification in `tests/hermite_observer_memory/probe.cpp` (`ReplacementScenario`)
exercises both Bezier and Hermite patch types with live objects:
1. Invalid slot indices (`ReplaceCurve(99, ...)`) and identical value assignments are ignored safely.
2. Repeated slots preserve observations on the old curve while partially replaced.
3. Upon replacing the final slot, old-curve observations equal to this patch are retired cleanly.
4. Foreign destination observers and unrelated/null slots maintain exact ordering.
5. Twelve point and derivative scalar values remain bitwise identical before and after replacement.
6. The synchronization commit (`CurveSynchronization::SynchronizeCurves`) remains nonallocating.
7. Resetting the patch leaves the destination and geometry observers clean.

Both Bezier and Hermite replacement scenarios pass under the required CTest target
`application.hermite_observer_contracts` and emit:
`observer_replacement=kind:hermite guards:1 repeated:1 retired:1 destination:1 numeric:1 final:1`
`observer_replacement=kind:bezier guards:1 repeated:1 retired:1 destination:1 numeric:1 final:1`

## Delivery requirements and closure

Require the existing exact-head/main GCC C++17 build, 75 CTest entries, and 526 Python
controls. Preserve the frozen scientific states, 45 exact artifacts, 123 positive boundary
comparisons, and existing contracts.
