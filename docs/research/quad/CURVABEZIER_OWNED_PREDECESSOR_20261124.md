# Native CurvaBezier predecessor retention across rejection and retry

Recorded 2026-11-24 Fortaleza. [Run receipt and identities](evidence/CURVABEZIER_OWNED_PREDECESSOR_20261124.json).

PR 265 had four successful exact checks at d6170d04 and no independent
review. [Draft PR 266](https://github.com/tiagosombrra/apmesh-modernization/pull/266)
continues the same research path with a four-file change relative to that head.
Its compatible result is also staged against the canonical research branch
for CI. Production source, configuration and build inputs match the
canonical branch byte for byte.

## Real native control

Transfer the mixed predecessor into the attempt scope by move, keeping the
same typed physical mesh and copying the original curve/tree data by value.
The patch link borrows that mesh. Under the forced rejection option, construct
a genuine native grouped candidate and check its typed incidence. Temporarily
point the patch at the candidate, then inject rejection. A scoped guard restores
the original link before the candidate is destroyed. Assert that the original
owner, node/element pointers and IDs, element areas, node coordinates and
curvature fields and ordered node observers are preserved. Its OBJ must retain
exact bytes and the rejected candidate's output directory must be absent.

In the same native process, construct the staged retry from that same retained
state and tree projection. The frozen evaluator measures the retry and the
forced Python control selects the predecessor. The normal eligible and
protected-neighbor controls exercise the same paths as PR 265. The staged
geometry and all three selected OBJ identities reproduce their earlier values.
This uses the same already approved grouping and measurements.

## Validation and next gate

MSVC 19.44 x64 Debug C++17 builds the exact reviewed tree. The real application
suite exercises three outcomes, including the new injected native transition.
The curve-source contracts run 54 negative controls, and 26 Python reporting
tests pass. The default validation wrapper lacks required tools and a
validation baseline receipt. The configured native profile supplies this
bounded evidence.
Hosted validation at checkpoint has 1 successful, 3 pending and 0 failed jobs.

The scope covers the prior owner during staging and retry. Durable accepted
history, failure after file publication, independent review, instrumented
qualification of the grouping fault and the global mixed estimator remain
open. The next engineering slice binds a durable typed predecessor and
candidate provenance to the real source before admitting an epoch. The
scientific estimator and policy needed to drive the next reconstruction
still require their own qualification under issue 221. Accepted mixed
adaptive epochs: zero.
