# Mesh Studio R2.7.15 — native sampled shared-curve geometry, UV and node-ID audit

**Date:** 2026-11-17. **Research scope:** original real Eistute and Book
serial TRI accepted snapshots, with no scientific generator changes.
**Review:** draft PR #239; branch
`feature/mesh-studio-r27-bvh-20261116`, not `main`.

## Research question

R2.7.14 qualified the canonical original curve-to-patch **incidence
graph**. Sharing a source curve is not proof that generated TRI
interfaces use identical boundary samples, that their XYZ coincide,
or that their nodes share a physical allocation. R2.7.15 tests the
sampled boundary geometry and original **logical** native node IDs,
rather than promoting a source-curve graph into a physical welding
claim.

The original C++ `src/adapter/adapter.cpp` explicitly maps its four
local patch sides to UV equations `v=0`, `u=1`, `v=1`, `u=0`.
The source `PatchCoons::IsCurveReversed` flag maps local curve
parameter `t` to canonical `1-t` for reversed incidences. The
existing Adapter copies boundary samples into patch-local submeshes
while retaining their native node IDs; equal IDs may correspond to
**different C++ node objects**. In particular, `native_node_id`
is not evidence of global pointer sharing.

## Audited algorithm

`tools/mesh_studio/native_seam_samples.py` first revalidates the
**actual original native accepted** R2.7.12 retained NDJSON, original
source summary and all SHA-256 pins via independent existing parsers.
It does not consume OBJ face ordinals or synthesize faces.

For each canonical original source curve owned by more than one
source patch in the R2.7.14 graph, it:

1. Selects **real accepted TRI face edges** whose two source UV
   vertices lie on the corresponding original patch side, using an
   explicitly stated UV tolerance `1e-9` in normalized parameters.
2. Recovers canonical curve parameters using the native incidence
   orientation, and keeps the **original native node IDs and XYZ**.
   Repeated native IDs with inconsistent original per-corner UV/XYZ
   are rejected.
3. Builds the set of original local boundary edges. It independently
   reports repeated edges, zero-length-in-parameter edges, duplicated
   parameter nodes, missing endpoints, and incomplete/branched edge
   coverage. Recovered ordered chain must have endpoints near
   `t=0,1` and exactly the edges of consecutive recovered nodes.
4. Compares all pairs of distinct owning patches for equal sample
   counts, canonical parameter differences, original native logical
   node IDs and Euclidean XYZ displacement. The explicit XYZ rule is
   `distance <= 1e-9 + 1e-9*(local two-side XYZ bounding-box diagonal)`, not a
   proof that a common CAD curve has zero continuous error.
5. Marks `sampled_uv_xyz_logical_id_concordance_observed=true`
   **only when both native side chains are complete and all
   corresponding observed samples agree** within the declared
   tolerances. Missing/invalid chains remain nonconcordant and are
   recorded with diagnostics rather than omitted.
6. Emits exact observed counters and per-source-curve diagnostics.
   The output explicitly retains
   `physical_node_welding_certified=false`,
   `continuous_geometric_error_certified=false`,
   `cross_epoch_lineage_certified=false` and
   `scientific_lod_qualified=false`, regardless of sampled agreement.

Matching sampled **logical IDs, coordinates and UV** is valuable
evidence for conforming observed boundary discretizations. It does
**not** establish shared in-memory native pointers, globally welded
mesh topology, full nonmanifold sheet adjacency, analytically
continuous Bézier geometry, or cross-epoch face descent. A difference
in native node IDs with coincident XYZ is reported as an **ID
discrepancy**, not automatically repaired through coordinate welding.

## Test and native execution gates

`test_native_seam_samples.py` exercises synthetic fixtures only:
all four original UV side equations, direct/reversed incidence,
matching observations, deliberate XYZ drift, different native IDs
at equal XYZ, incomplete/duplicated boundary edges, inconsistent
native-ID geometry, tolerance limits and deterministic output.
These isolated tests are not scientific generator evidence.

The native-lineage CI job runs the real compiled serial Eistute/Book
GeneratorAdaptive first, captures exact original accepted source-face
NDJSON, rechecks bytes and source metadata, and then creates
`build/r2715-native-sampled-seams.json`. The 14-day GitHub Actions
artifact is named `mesh-studio-r2715-sampled-seams-<commit>`.
Numerical OFF/ON parity and independent Linux/Windows scientific
regressions continue to run without any source acceptance threshold
change.

Reproduce after real R2.7.12 native capture:

```bash
python -m unittest tools.mesh_studio.test_native_seam_samples -v

python -m tools.mesh_studio.native_seam_samples \
  --directory build/r2712-native-evidence \
  --output build/r2715-native-sampled-seams.json
```

**Admission rule:** mark this step PASS for *sampling audit execution*
only when its exact new CI source SHA, all four jobs, actual native
R2.7.15 report and denominator counters have been observed. A
successful audit is not automatically evidence that all native
seams are conforming. The numbers and any source discrepancies
must be reported separately.

**Independent blockers:** second genuinely accepted adaptive epoch per
original model, independently validated cross-epoch face/curve
ancestry, structural node welding/nonmanifold mesh-sheet proof,
continuous source-surface error bounds, real physical Windows GPU
present/RSS/VRAM measurements. Therefore R2.8 scientific LOD stays
**BLOCKED**, VTK picker stays default, experimental BVHs stay
opt-in/bounded, and PR #239 stays draft/unmerged. No generator
policy change, default-on switch, tag or release.

## Certification status

The first R2.7.15 workflow is an experimental qualification gate.
A result is never inferred from new source commits alone. Await
specific successful CI and actual emitted native counters before
updating the outcome here.
