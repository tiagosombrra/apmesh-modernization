# Candidate source families — investigation inventory, NOT admitted models

**Updated 2026-11-14:** The model-level register and evidence boundaries are in [R1 discovery](R1_DISCOVERY_REPORT.md). The following are families / leads, not qualifying individual-model proofs.

| Family | Original location | Observed assets and role | Critical caveat |
|---|---|---|---|
| HexMe | https://github.com/cgg-bern/hex-me-if-you-can | original/ contains 63 named CAD files, meta/ stores per-file provenance; 29 individual files recorded in R1 | geometry is a volumetric hexahedral-meshing benchmark; cannot infer valid >=3 shared surface edge |
| MAMBO | https://gitlab.com/franck.ledoux/mambo | MAMBO-origin files present via HexMe (`i01o_m1`, `i03o_m3`, `s09o_bridge`, etc.); CAD and quality controls | counting identical MAMBO models under two dataset names duplicates geometry |
| Fusion Energy model_benchmark_zoo | https://github.com/fusion-energy/model_benchmark_zoo | six pinned source scripts, notably three touching cuboids, T/cross junctions; a useful multi-body parametric test family | scripts produce models only when executed; body contacts, CAD imprints and an actual shared >=3-sheet edge are still unknown |
| Thingi10K | https://github.com/Thingi10K/Thingi10K | 10,000 3D-printing models; five upstream errata IDs added as negative-leads | dataset reports ~22% non-manifold, not necessarily intentional edges; each thing has independent license |
| ABC | https://deep-geometry.github.io/abc-dataset/ | large CAD with B-Rep/STEP ground truth, suitable for geometric reverse-fit controls | no specific ABC archive member extracted or admitted here; Onshape source rights require review |
| Tangency Labs models | https://github.com/tangency-labs/models | CC0 repository policy and format-directory READMEs confirmed | `step/`, `obj/`, `stl/`, `iges/` had **no model files**, only README files, at pinned revision |
| Mesh-to-CAD literature/examples | https://github.com/gregfranco/mesh2cad | potential independent reconstruction-method comparator, not yet benchmarked | no established preservation of APMesh >=3-sheet curve incidences |
| Non-manifold all-quad literature | https://arxiv.org/search/?query=Indirect+all-quadrilateral+meshing+based+on+bipartite+topological+labeling&searchtype=all | comparison motivation for non-manifold multiple-volume junctions | literature method does not guarantee runnable code, identical input domain or reusable assets |

## Specific methodology

- Source-ID existence, declared provenance, independent rights, topology, four-sided bicubic representability and actual generator success are distinct gates.
- Each admitted candidate requires a raw byte hash (SHA-256), units, source-topology oracle, typed junction/sheet graph, declared curve IDs, valid BP export plus sidecar, geometric error and a separate independent APMesh output report.
- Never presume a valid CAD solid is non-manifold; never presume an arbitrary non-manifold triangle mesh is compatible with the current patch domain.
- No asset downloaded, copied or converted in this documentation stage.
- Refer to `candidate_register.csv` and `R1_DISCOVERY_REPORT.md` for pinned source paths and current decisions.

## Methodological references

- Zhou, Q.; Jacobson, A. *Thingi10K: A Dataset of 10,000 3D-Printing Models* (2016). https://arxiv.org/abs/1605.04797
- Koch, S. et al. *ABC: A Big CAD Model Dataset for Geometric Deep Learning* (2019). https://deep-geometry.github.io/abc-dataset/
- Reberol, M.; Georgiadis, C.; Remacle, J.-F. *Quasi-structured quadrilateral meshing in Gmsh* (2021). https://arxiv.org/abs/2103.04652
- Beaufort, P.-A. et al. *Hex Me If You Can* (2022). https://www.algohex.eu/publications/hex-me-if-you-can/
