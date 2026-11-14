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

## Controlled P1 integrated — next delivery P2 / R3

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

**Next:** P2 must retain this typed hybrid SubMesh as actual history for two
accepted adaptive epochs, including typed curvature/quality/reconstruction,
retry/rollback and export. No P2 implementation or mixed epoch claim yet.

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
