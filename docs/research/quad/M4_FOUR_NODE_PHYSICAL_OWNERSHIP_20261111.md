# M4 research — four-node physical QUAD ownership and lifecycle (2026-11-11)

**Delivery status:** feature implemented and merged in [PR #205](https://github.com/tiagosombrra/apmesh-modernization/pull/205) at `4ffd9cdac09d99352e0500df8a0b5467054949c3`; the exact feature head `1366ce697a5d04156ba58bb890c989f711d39f93` passed four-job [Actions #42999207821](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42999207821) (81/81 CTest, 527/527 Python tooling, seven CLI denials, native Linux/Windows QUAD and frozen Eistute/Book scientific equality). The named ownership test passed and [ownership artifact #13846190675](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/42999207821/artifacts/13846190675) was uploaded. Exact [postmerge Actions #43000273810](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43000273810) is pending final verification. See [evidence](evidence/M4_FOUR_NODE_PHYSICAL_OWNERSHIP_20261111.json). This is a *research-only four-node physical element*, not
production QUAD generation, historical 1993 validation, nor arbitrary CAD
boundary conformity.

## Concrete implementation

- `research/quad/physical_quadrilateral_adaptive.h/.cpp` introduces
  `apmesh::quad::research::QuadrilateralAdaptive final : ElementAdaptive`.
  It observes exactly **four unique live `NodeAdaptive*`**, with
  per-corner UV, a caller-provided physical patch orientation and no owned
  node pointers. Its `ElementAdaptive` normal is the sum of both unnormalized
  triangle cross products; its area is half the sum of their magnitudes.
  Every UV face must split into two positively oriented subtriangles and
  both physical subtriangles must agree with the supplied chart normal.
  This policy is a bounded positive-orientation research guard, not a
  universal curved finite-element Jacobian or nonplanar integration rule.
- The constructor validates nonnull/distinct nodes, finite/valid [0,1] UV,
  finite XYZ, patch normal and positively oriented geometric triangles
  **before** registering any node observer. It registers exactly one
  `ElementAdaptive*` per node and unregisters on all supported exceptions.
  A deterministic research-only fault hook rejects at any of four observer
  registration slots to exercise partial-commit rollback. Its destructor
  retires all four registrations without allocation. Copies/moves of the
  borrowed-address element are deleted. The `GetNoh` 1–4 snapshot does
  **not copy NodeAdaptive's foreign observer list**, unlike a normal node
  value copy.
- `tests/quad/physical_quad_ownership_probe.cpp` uses the actual M4
  native 19-leaf C++ Quadtree plus M5 research Lawson hybrid output and
  a Geometry-owned `Models3d::ModelCurvaBezier`. It uses **one owned
  `SubMesh`** with exactly **69 `NodeAdaptive`** nodes, **42 research
  four-node QUAD** and **36 existing production `TriangleAdaptive`**
  borrowing those same physical nodes. Expected node IDs, face IDs and
  **276 reverse observer links** are compared before and after two owning
  `SubMesh` moves, including self-move. Live external-node tests verify
  all four destructor detachments and no leftover observer after each
  partial-construction failure.
- The outer 16 edges are checked against the UV model domain and all
  20 QUAD/TRI interface edges retain opposite incidence orientation.
  Physical nodes are checked against the actual production
  `PatchBezier::Parameterize` at their existing UV IDs. An independent
  Bernstein/derivative/normal and curved-chord auditor from M4 remains the
  precondition, and it runs again for both unapproved centroid rules.
- `tests/quad/test_m4_quad_ownership.py` orchestrates those validated
  C++-generated native and curved inputs, and adds three corrupt physical
  OBJ mutations per centroid choice, six file-level rejects total.
  Invalid borrowed node, duplicated node, invalid UV, inverted UV/normal,
  collapsed geometry, failure-after-registration and out-of-range access
  are also tested by the C++ executable.

## Scope limits

This does **not** change `include/` or `src/`, production `ap_mesh`,
existing default TRI mode, accepted/rejected adaptation, or the scientific
reference model. The new research quadrilateral lives under a distinct
namespace and is never linked to the production CLI. The prototype only
checks that **physical polygonal faces** represented by corner nodes are
well oriented and owned correctly on a **single built-in curved patch**;
it does not provide exact curved element integration, a historical centroid,
full 1993 Delaunay/contour contraction, imported CAD synchronization,
multipatch observer resolution or all-QUAD selection.

## Required exact-head gates

```sh
cmake --preset local-serial
cmake --build --preset local-serial --parallel 2
ctest --preset local-serial --output-on-failure --no-tests=error
python3 -m unittest discover -s tests/tooling -p 'test_*.py'
python3 tests/quad/test_m3_dispatch.py build/local-serial/bin/ap_mesh
```

New root research CTest: `quad.m4.four_node_ownership`. Expected **81/81**
root CTest after adding one test, **527/527** tooling Python, seven CLI
denials, unchanged QUAD native Linux GCC/Windows MSVC 13/13 each, and the
frozen five Eistute/four Book scientific mesh states (byte-identical OBJ,
acceptance and boundary results). The unchanged root M4 test remains
required. The CI's new bounded ownership manifest/artifact does not imply
native ASan/Windows CRT leak checks, which remain separately pending.

**Next after qualification:** verify exact post-merge research SHA, then
perform independent curved boundary conformity for actual patch-to-patch
curve sharing and physical element lifetime under rejected adaptation
attempts. Do not enable production QUAD or all-QUAD until historical
scientific choices and the remaining production gates are resolved.
