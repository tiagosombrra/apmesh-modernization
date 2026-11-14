# External corpus leads — NOT admitted models

All entries are source-level leads as of 2026-11-14. No individual external file was downloaded, topologically classified, converted or licensed by this documentation package. Do not cite a dataset-level property as proof about a specific asset.

| Source | Official/reference URL | Best role | Caveat and next check |
|---|---|---|---|
| Thingi10K | https://github.com/Thingi10K/Thingi10K | polygonal negative controls and discovery of actual edge-non-manifold candidates | 10,000 models; dataset reports ~22% non-manifold, but many have intersections/defects; check exact file ID, type and individual model license |
| ABC | https://deep-geometry.github.io/abc-dataset/ | B-Rep/parametric geometry ground truth and patch fitting | ~1M CAD models; a strong geometry oracle does not make the surface non-manifold; confirm asset rights and actual surface topology |
| MAMBO / Gmsh literature | https://arxiv.org/abs/2103.04652 | CAD/quadrilateral quality controls and published method comparisons | research describes testing on 114 MAMBO and 1000 ABC cases; obtain exact benchmark distribution/model IDs and licenses before use |
| HexMe | https://doi.org/10.1111/cgf.14608 | industrial geometry, feature curves, tagged CAD controls | 63 CAD models and 189 tetrahedral meshes; volumetric benchmark is not a direct APMesh surface-mesh baseline; per-model origin/license recorded upstream |
| Tangency Labs models | https://github.com/tangency-labs/models | potential openly licensed CAD/mesh conversion controls | repository claims CC0-1.0; individual topological suitability and non-manifold coverage unverified |
| Non-manifold all-quad literature | https://arxiv.org/search/?query=Indirect+all-quadrilateral+meshing+based+on+bipartite+topological+labeling&searchtype=all | scientific comparison and multi-volume non-manifold feature-edge examples | literature method does not imply that its original models, source files or author implementation are available for direct comparison |
| Open CASCADE reference | https://github.com/Open-Cascade-SAS/OCCT/blob/master/dox/user_guides/modeling_algos/modeling_algos.md | topology/sewing design and negative-test guidance | non-manifold sewing with too-large tolerance can merge unrelated edges; never treat sewing as an independent truth oracle |

## Selection strategy

1. Search 30-40 model leads across topological strata as a DISCOVERY target, not a success quota.
2. Select an estimated 8-12 pilot candidates only after checking exact IDs, rights and topological evidence; quota is not guaranteed.
3. Reserve intended external edge junctions for core non-manifold generalization. Use manifold ABC/MAMBO/HexMe controls for geometry fitting or quad-quality comparisons; keep defective/ambiguous Thingi10K models in negative tests.
4. Register exact source publications and executable comparison implementations separately; a published paper's method is not automatically a runnable baseline.
5. Prefer source-authorized reproducible download instructions over redistributing third-party assets by copying them into the MIT repository.

## Why no 'approved model list' yet?

Named datasets are not individual models. Even where papers test hundreds of objects, the APMesh acceptance domain requires a four-sided bicubic patch complex with explicitly shared curves and a verified source-incidence graph. Until actual files are audited, an approved list would be misleading.

## References for source claims

- Zhou, Q.; Jacobson, A. Thingi10K: A Dataset of 10,000 3D-Printing Models (2016), upstream README.
- Koch, S. et al. ABC: A Big CAD Model Dataset for Geometric Deep Learning (2019), project website.
- Reberol, M.; Georgiadis, C.; Remacle, J.-F. Quasi-structured quadrilateral meshing in Gmsh (2021), arXiv:2103.04652.
- Hex Me If You Can (2022), Computer Graphics Forum, DOI 10.1111/cgf.14608.
