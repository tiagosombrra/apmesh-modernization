# ADR-0036: initialized detached patch copies

Status: bounded initialization defect repair candidate; full exact-head/main gates required.

## Context

C22's original audit found no literal production pointer-copy call outside the
constructor base chain. These public paths nevertheless expose partial numeric
copies with empty curves and null SubMesh. Bezier's basis and seven load/process
metadata fields, and Hermite's four internal direction flags, were omitted.
The original audit deliberately did not evaluate those indeterminate fields.
Ordinary C++ derived copy/move remains unavailable. No complete clone is implied.

## Decision

Preserve the pointer-taking signatures, layout, base ID copy, detached topology
and every already-defined control/transformed-matrix/scratch value. Bezier keeps
its four copied directions and constructs the existing StartBezierMatrix basis.
Reset its five load metrics and two process/patch IDs to zero, matching the
existing default metadata state. Never read source load metadata: fully
constructed geometric sources can themselves lack initialized load metadata.
These metrics describe the detached destination's fresh operational state.

Hermite continues constructing the existing Hermite basis and copying corners,
tangents, twists and transformed/scratch matrices. Initialize its four internal
direction flags true without reading source flags. The inherited public
IsCurveReversed fallback remains false, including for sources constructed with
different internal flags. A detached copy has no curve incidence to orient.
No curves, reciprocal observers or current physical SubMesh are transferred.

Require a live non-null source with initialized numeric payload/scratch and,
for Bezier, initialized direction flags. Default/control-only objects do not
meet that geometric precondition merely because their control setters were used.
Repeated copies of a qualified detached copy satisfy the same precondition.
Do not change null-source behavior or silently add a complete-clone API.

## Evidence and limits

Require actual production-unit instruments, analytic fixture points, nonempty
original/candidate bitwise payload/derivative/incidence pairs, source/copy and
repeated-copy lifetime, zero metadata and explicit basis/direction observations.
Measure nonallocation with a working denial hook and reject independent corrupt
basis, metadata, topology and direction observations. Preserve original records
without evaluating originally indeterminate members. Guard all four production
files and reject numerical/control/topology/API mutations; retain the earlier
construction and observer guards and their negative controls.

Full exact-head/main prior regression, accepted/rejected traces and remote
audits block integration until passed. Source preparation, geometric/default
constructor metadata, complete cloning, arbitrary publications, foreign/current
patch rebinding and ordinary Hermite observer retirement remain separate.
No scientific formula, floating-point order, synchronization, tolerance, budget,
adaptation/acceptance/stopping policy, full-process/parallel or LSan/UBSan
qualification follows. No external-client or binary-compatibility guarantee.
