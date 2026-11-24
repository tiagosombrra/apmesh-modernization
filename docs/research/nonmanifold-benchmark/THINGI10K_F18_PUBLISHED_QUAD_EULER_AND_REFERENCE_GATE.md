# S40-F18 — QuadWild literature-to-input topology screening and independent QUAD output gate

**Audit date:** 2026-11-22. **Project:** `tiagosombrra/apmesh-modernization`, research branch `research/benchmark-corpus-reverse-patches`, draft PR #225. **Evidence level:** 12 published aggregate QUAD V/F counts matched to 12 original STL file IDs via the pinned catalog; no genuine QUAD output bytes were retrieved. **Scientific status:** CONDITIONAL_EULER_PRECHECK_ONLY, **not** an accepted comparative meshing result.

## Scientific comparison question and source

Pietroni, Nuvoli, Alderighi, Cignoni and Tarini, *Reliable Feature-Line Driven Quad-Remeshing*, ACM Transactions on Graphics 40(4), article 155 (SIGGRAPH 2021), DOI [10.1145/3450626.3459941](https://doi.org/10.1145/3450626.3459941), **Figure 29 and Table 1**, identify 12 exact Thingi10K model file IDs and give output quadrilateral vertex count (`#V`), face count (`#F`), irregular vertices (`#I`), angular deviation (`AD`), edge-length deviation (`ED`) and average Scaled Jacobian (`SJ`). The **original authors'** output numbers are stored in the pre-existing frozen [12+11 literature roster](THINGI10K_LITERATURE_COHORT.csv), with no claim that they are APMesh measurements.

The official [authors' Quad Mesh Dataset download](https://www.quadmesh.cloud/thingi10k-quad-dataset.zip) and a separate [Hugging Face QuadWild NPZ archive](https://huggingface.co/datasets/Thingi10K/Thingi10K/blob/aaae0bb650cf464eb6c7d86d5ce39597cb71e106/Thingi10K_quadwild_npz.tar.gz) are **identified, not downloaded or enumerated per member**. The latter advertises **4.4 GB** and SHA-256 `79d213585fce31c61f661221266c967b26c5eb446e394d2022280f5a02399011`; this SHA is taken from the published archive listing, **not** independently computed from a local full download. No individual source-to-output file pair or output mesh integrity has been established.

The authors' own [README](https://github.com/nicopietroni/quadwild#run) specifies that QuadWild first processes triangular OBJ/PLY input; the output files include `*_quadrangulation.obj`, `*_quadrangulation_smooth.obj` and intermediate chart decomposition, features, corners and directional fields. Its *patch layout* may contain nonquadrilateral charts and T-junctions, whereas the claimed **final surface tessellation** is pure-quad and conforming. The readme cautions that subsequent code changes can yield different results from the original article. The paper explicitly reports splitting non-manifold input edges and removing non-orientable components, so a published pure-quad may represent a **topologically changed preprocessed domain**, rather than an unmodified original source.

## What can be established without downloading the QUAD output?

For a **triangulated closed 2-manifold**, every edge has two incident triangles, so `E_in = 3 F_in / 2` and `chi_in = V_in - F_in / 2`. This applies to source **catalog counts** only if all the required closed/manifold/orientability/component flags are correct; for **#58012**, the raw STL has additionally been byte-verified and its edge/vertex-link graph independently audited in F17.

For a **pure-quad closed 2-manifold**, `E_out = 2 F_out` and `chi_out = V_out - F_out`. For a **connected, orientable** closed surface, `chi = 2 - 2g`. Therefore, equal Euler characteristic is a **necessary, not sufficient**, test for preservation of surface topology, and the output genus `g` is **hypothetical** until the real output mesh is independently checked for closure, connectivity, orientability and singular vertices.

| Thingi10K ID | Source evidence | Input `chi` | Paper's QUAD `#V` | Paper's QUAD `#F` | Hypothetical output `chi` | Hypothetical output genus | Necessary Euler match |
|---|---|---:|---:|---:|---:|---:|---|
| **58012 — Canopy Test** | **Audited original STL** | **−80** | 113,799 | 113,879 | **−80** | **41** | **YES, necessary only** |
| **67792 — Dual Dodec** | Pinned source catalog flags | −120 | 16,615 | 16,735 | −120 | 61 | YES, conditional |
| **81877 — BOARD** | Pinned source catalog flags | −120 | 35,185 | 35,305 | −120 | 61 | YES, conditional |
| **94884 — Container Sphere Two Hundred** | Pinned source catalog flags | −350 | 47,116 | 47,466 | −350 | 176 | YES, conditional |

The **other eight** published entries do **not** have V/F counts compatible, by themselves, with a **single connected closed orientable pure-quad surface**: IDs `44503`, `128001`, `61394`, `69975`, `230923`, `364256`, `423069`, `498974`. This does **not** mean the outputs are incorrect or that QuadWild failed. They may be open, disconnected, modified during cleanup or otherwise outside the strict single-closed-component hypothesis. Model #61394 has a directly audited original source STL with **61 3+/4+-incident edges**, 86 singular vertex links and invalid triangles; treating it as a simple closed surface would be especially inappropriate. **Do not label these eight as negative-generation results.**

### Strongest current case: #58012

- Pinned source ZIP Git blob `67f266dad4f41137d7036d45c1d82774a2feea15` and decompressed original STL SHA-256 `2c7c322af76b46a307e67af451ebba9e6609e6932a2829f4c596853dbf122d4b`, from F17.
- Independently computed input graph: **9,090** unique exact-coordinate vertices, **27,510** unique edges, **18,340** triangular facets; every edge has two face owners, vertex links are cyclic, one connected component, no duplicated or zero-area faces, zero edge winding conflicts. `chi_in = 9090 − 27510 + 18340 = −80`, `g_in = 41`.
- Pietroni et al. Table 1: `#V = 113799`, `#F = 113879`, `#I = 7977`, AD=15.49°, ED=12.28%, SJ=0.93. **Under the conditions** that the reported output is a connected closed orientable pure-quad 2-manifold, its `chi_out = 113799 − 113879 = −80`, `g_out = 41`.
- The equality makes #58012 a strong **priority for actual QUAD output extraction and mesh-level correspondence**. It **does not prove** that the archive contains a specific output file, that it was generated from this exact STL revision, that surface topology was preserved, or that any APMesh metric matches.

## New fail-closed implementation

- [F18 independent QUAD output gate](probes/thingi10k_f18_quad_reference_gate.py) validates **expected output SHA-256 and source STL SHA-256**, filename/file-ID, and published output `#V/#F` before publishing any actual reference receipt. It accepts bounded indexed **pure-quad OBJ or NPZ** only (NPZ must contain numeric `vertices[N,3]` and integer `faces[M,4]` arrays; unknown NPZ schemas are rejected). Its independent quad-edge incidence, winding, vertex-link cycle, component, Euler, genus and valence-defect checks reject wrong or unsupported topology. It never silently welds, repairs, converts or accepts a matching file merely because the numerical V/F counts fit the paper.
- [F18 adversarial Python tests](probes/test_thingi10k_f18_quad_reference_gate.py): **40/40 PASS** locally, using synthetic closed genus-0 cube and genus-1 torus, open boundaries, triple edge, vertex-only singularity, duplicate/inverted quads, malformed OBJ/NPZ, missing source identity, tampered SHA, false published numbers and raw-audit/catalog contradictions. **No real QuadWild output was executed through the gate**.
- [F18 offline published-only reproducer](probes/thingi10k_f18_published_receipt_cli.py) and [its fail-closed tests](probes/test_thingi10k_f18_published_receipt_cli.py) independently recalculate the four necessary matches using immutable Git-blob identity checks for the existing literature CSV, the 12-row catalog slice and the F17 7-model source audit. The runner never fetches an output mesh or promotes its status.
- [12-model F18 source-catalog slice](evidence/thingi10k/thingi10k_f18_original_source_catalog_12.json) pins the catalog Git blob `ac376cc8604436f9460cac39b5171ce8d99b2e74`, already used by F15. The **real** 12-paper-ID join and four matches are recorded in [machine-readable 12-case receipt](evidence/thingi10k/thingi10k_f18_published_quad_euler_12.json) and [condensed CSV](THINGI10K_F18_PUBLISHED_QUAD_EULER_12.csv). F18 uses **original real F17 raw STL receipts** for #58012; the other three necessary Euler matches rely on published output counts and source **catalog assumptions**, not examined source STL bytes.

### Re-run for an actual authorized reference mesh

```bash
cd docs/research/nonmanifold-benchmark/probes
python -m unittest -q test_thingi10k_f18_quad_reference_gate test_thingi10k_f18_published_receipt_cli
python thingi10k_f18_quad_reference_gate.py \
  --published-csv ../THINGI10K_LITERATURE_COHORT.csv \
  --model-id 58012 \
  --actual-quad /private/authorized/58012_quadrangulation_smooth.obj \
  --expected-quad-sha256 <actual-64-char-hex-from-authorized-output> \
  --source-stl-sha256 2c7c322af76b46a307e67af451ebba9e6609e6932a2829f4c596853dbf122d4b \
  --output /private/new-output-f18-58012.json
```

To recompute the **paper-only** necessary Euler precheck without actual QUAD mesh data:

```bash
python thingi10k_f18_published_receipt_cli.py \
  --published-csv ../THINGI10K_LITERATURE_COHORT.csv \
  --catalog-subset ../evidence/thingi10k/thingi10k_f18_original_source_catalog_12.json \
  --f17-source-audits ../evidence/thingi10k/thingi10k_f17_source_archives_23_and_raw_audits_7.json \
  --output /private/new-paper-only-precheck.json
```

Use the actual verified SHA after acquiring the output; do not substitute the placeholder with an invented value. If the final author dataset is NPZ, the gate requires the explicit pure-quad `vertices`/`faces` schema and refuses incompatible files, and the published paper's result configuration must be reconciled with the exact archived variant.

## Remaining hard scientific gates

1. **F19 acquisition:** authorize and retrieve a real source-output QUAD pair (initially #58012). We have not read the 4.4-GB archive or verified individual members; do not inflate 'archive link found' to 'per-model output available'. Verify data licenses and provenance separately for source mesh and derivative outputs.
2. **F19 topology proof:** read the real QUAD indexed topology; check it is pure quad, closure, orientation, vertices, components, Euler, genus, valence distribution, exact source graph correspondence, and feature edges. Check whether author preprocessing split/removed source components.
3. **F20 geometric comparisons:** independent source-to-QUAD distance/Hausdorff approximation with convergence, shared feature coverage and a consistent Scaled Jacobian definition. Evaluate APMesh stage costs separately from comparator pre-processing.
4. **F21 APMesh execution:** construct bounded bicubic Bézier patch representation of the *same admissible source*, with shared curve indexing and Jacobian constraints; run actual C++ TRI and supported QUAD modes, verify accepted-state outputs. No claim of pure-QUAD APMesh support unless demonstrated by an executed run.
5. **Generalizability:** retain all 12 QuadWild literature IDs and 11 Badia IDs as frozen denominators; preserve open, singular and non-manifold source cases as adversarial, blocked or unsupported, rather than removing them after the fact.

**No original copyrighted STL/ZIP/QUAD mesh bytes or rendering assets are committed. No new license approvals, APMesh-accepted mesh, S40 face admission, modification of M5/S40/S27/M3/Book/Eistute/Decor Shelf/Tsh249 or merge to main. The scientific PR #225 remains DRAFT.**
