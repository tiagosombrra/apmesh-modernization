# Mesh Studio S5d — independently verified real-source candidate comparisons

**Date:** 2026-11-15. **Implementation branch:** `feature/mesh-studio-fixture-first-20261114`.
**Exact new source candidate revision:** `27851df2625e0c0b37e12023af699a01f3d0304c`
([source PR #235](https://github.com/tiagosombrra/apmesh-modernization/pull/235));
source research merge `ab1dc62a815f3d56c9b25845bec00863730ddcd5`.
Source CI [run #43664129060](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43664129060)
was completed with 4/4 green jobs for the generator. **That is NOT Studio CI.**

## What was implemented

1. Copied five genuine byte-pinned physical OBJ outputs plus the original Linux
   generator JSON report from source CI into `fixtures/real_p2d1c3`. The same
   five OBJ SHA-256 values were checked against the separate Windows CI artifact.
2. Implemented `real_candidate_study.py`, a bounded verifier that independently
   reconstructs source Bezier vertices, oriented typed TRI/QUAD faces, original
   16-edge outer boundary, indexed disk, UV QUAD area, corner-normal-scaled
   quality and split-normal warpage from original vertices, not plot pixels.
3. Evaluated each actual candidate at **exactly the same 4096 source UV
   midpoints** with TRI barycentric and genuine QUAD bilinear interpolation,
   comparing unweighted RMS, source-Jacobian-weighted RMS and maximum XYZ error
   to the pinned source report. This is a **discrete source-geometry error**, not
   a PDE-error estimate, source-area integral certificate or convergence proof.
4. Reimplemented both source-specific Pareto objective profiles (7 and 8
   objectives), including the independent QUAD UV area versus number of QUAD
   faces. No candidate is accepted by the Studio or the generator.
5. Added `real_study_publication.py` and CLI for two reproducible 190x132-mm
   vector PDF/SVG figures: identical-camera UV geometry gallery and Pareto
   complexity/error projection. The 2D projection alone does NOT prove the
   high-dimensional domination relation; markers use the complete profiles.
6. Added 28 focused unit tests on source provenance, fake hashes, changed
   metric claims, invalid objective data and vector publication.

## Actual original candidate inventory, NOT independent repeated runs

| Source status | Nodes | QUAD | TRI | QUAD UV area | Common-site source RMS area-weighted |
| --- | ---: | ---: | ---: | ---: | ---: |
| Controlled initial fixed16 | 69 | 42 | 36 | 0.250000 | 0.015981265664 |
| First staged band | 93 | 62 | 44 | 0.328125 | 0.011810324643 |
| Staged west | 109 | 75 | 50 | 0.375000 | 0.009960083459 |
| Staged north | 107 | 71 | 54 | 0.375000 | 0.009233319235 |
| Staged both | 117 | 82 | 52 | 0.406250 | 0.009155128673 |

All original physical outputs retain **16 source boundary intervals** and
`adaptive_epochs=0`. A source candidate with `staged_unaccepted` status
CANNOT become an accepted adaptive epoch simply because its filename starts
with `accepted.`: that prefix labels the successful controlled application run.

- **Area-profile Pareto (seven objectives):** first band, north, both remain
  non-dominated. North weakly dominates west due to lower source RMS and fewer
  vertices at identical total face count and identical QUAD coverage.
- **QUAD-count Pareto (eight objectives):** all four are non-dominated because
  west has 75 QUAD and north only 71 at the same 37.5% UV QUAD coverage.
- Pareto ordering is **source-specific**, not universal and not an advisor-
  approved scientific policy for replacing the current Patch/SubMesh owner.
- There is **no statistical replication**. Do not construct confidence
  intervals, t-tests, efficiency claims or algorithmic convergence assertions.

## Reproducibility

```bash
python -m unittest \
  tools.mesh_studio.test_studio \
  tools.mesh_studio.test_storyboards \
  tools.mesh_studio.test_quality_analysis \
  tools.mesh_studio.test_real_p1 \
  tools.mesh_studio.test_desktop_stage \
  tools.mesh_studio.test_publication \
  tools.mesh_studio.test_multi_model_publication \
  tools.mesh_studio.test_experiment_ingest \
  tools.mesh_studio.test_real_candidate_study -v
python -m tools.mesh_studio.fixtures.validate
python -m tools.mesh_studio.real_study_cli \
  --output-dir build/mesh-studio/figures/s5d
```

All tests and vector/LaTeX evidence are recorded in
`evidence/S5D_LOCAL_VALIDATION_20261115.json`, including what remains OPEN.
Two-column pdflatex includes each PDF as a `figure*`. PDF and SVG have
no raster image elements and PDF fonts are embedded; print dimensions must
be checked in a renderer rather than inferred from file extension.

## Remaining methodological and engineering limitations

- The P2d second-band physical source is **one** actual application-controlled
  source run with multiple staged alternatives; not five independent trials.
- Source geometry units are unspecified and no genuine physical PDE solution
  or continuous error is measured.
- The fixed16 built-in Bezier chart is not production `AdaptCurve`, a globally
  welded high-valence patch complex, a true all-QUAD or anisotropic generator.
- No QUAD adaptive epoch has been accepted by a fully qualified source owner
  transaction; R3/M7 remains open in the canonical research branch.
- Exact Studio GitHub CI remains NOT RUN, and GUI S4b mouse picking / Qt widget
  lifecycle remains unqualified without native Qt dependencies.
- Exporting the same-site comparison as a formal journal experimental result
  still requires advisor approval of source-specific objective selection and
  additional independent source models, replicates and sensitivity analysis.

**Next:** S5e generalized dataset registry for multi-model and genuinely
independent future source runs, plus an explicit S4b Windows/Linux UI smoke
with PySide6, PyVistaQt and VTK. S6 source event recording requires separate
QUAD scientific review; do not modify the C++ generator from Studio.
