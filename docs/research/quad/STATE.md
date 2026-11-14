# APMesh QUAD — current state

Updated2026-11-14 Fortaleza. Canonical branch: `quad-templates`.
Main remains `f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94`.

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

## Next delivery — P1 / live curved-patch R2


**Functional candidate:** `quad/integration-live-patch-20261114`, based on8fe561b.
An opt-in build/case now executes the real application on the original curved
ModelCurvaBezier:42QUAD/36nativeAFT TRI/69physical nodes, connected UV disk and
16original sampled boundary intervals. Independent production-control-net
UV/XYZ/winding checks and nonempty publication rollback pass. Sourcef074e3a
passes86CTest/527Python and four changed-TU configured analysis checks locally.
See [measured evidence](evidence/P1_CONTROLLED_APPLICATION_20261114.json).
Final exact-head, Windows, frozen-TRI remote and integration gates remain pending.
Default build/TRI behavior remains protected; this is not adaptive history.


Refresh the older draftPR214 head7cd5014 against this qualified canonical branch
before new source changes. Reuse the native typed QUAD interior and original AFT
exterior to execute one complete controlled curved manifold patch through an
explicit application opt-in. Preserve its original boundary, demonstrate UV/XYZ/
orientation and rollback, and retain exact default-TRI evidence. `quad_uv` is
still refused by the current CLI; this functional gate remains unimplemented.

Then P2/R3 must consume that actual mixed QUAD/TRI mesh as history for at least
two accepted epochs, with typed curvature, quality, export, cloning, acceptance
and retry/rollback. Original TRI epochs do not establish mixed-history M7.

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
