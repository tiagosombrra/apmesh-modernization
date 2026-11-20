# Thingi10K — S40-F15: pinned 23-file metadata/topology/rights screening
**Checked:** 2026-11-20. **Type:** public catalog metadata audit, **not** raw STL mesh topology validation, a copyright clearance, an output mesh or a quad comparison.

## Inputs frozen and independently joined
- Research literature roster: [23 candidate IDs](THINGI10K_LITERATURE_COHORT.csv) (**12 QuadWild/Pietroni; 11 Badia/Martorell/Verdugo**), frozen before this audit.
- Public third-party visual/archive catalog: [larsbrubaker/Thingi10K](https://github.com/larsbrubaker/Thingi10K), path `docs/data/models.json`, commit `6c29395a9c14766eb04a9a27746f681e2eb584c7`, **Git blob SHA-1 `ac376cc8604436f9460cac39b5171ce8d99b2e74`**, 9,997 records. This is a **metadata mirror**, not independently validated source meshes or per-asset legal opinion.
- The whole pinned source catalog was fetched and parsed, and all **23/23 ID joins succeeded** with exact numeric ID correspondence; `thing_id` points to the Thingiverse *Thing*, whereas `id` is the **individual Thingi10K file** and must be used for matching published mesh/quad results. Do not accidentally merge two distinct files of the same Thing.
- The original input STL triangle counts listed for **all 11 Badia models match 11/11 catalog counts exactly**. The 12 QuadWild Table 1 output *quad faces* must **not** be equated with the catalog *input triangle faces*.

## Quantified catalog topology flags (only metadata claims)
| Population | Files | Closed | Edge-manifold | Vertex-manifold | Single component | Degenerate triangles reported | Duplicate triangles reported | All conservative clean flags |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Pietroni/QuadWild F29 | 12 | 8 | 9 | 6 | 9 | 2 | 3 | 4 |
| Badia F10 | 11 | 11 | 11 | 11 | 9 | 0 | 0 | 9 |

The conservative screening condition requires all of **closed, edge-manifold, vertex-manifold, single-component, PWN (consistently oriented)** true and both **degenerate_faces** and **duplicated_faces** false. A metadata **PASS is only a screening lead**, not independently verified topology, no 3+-incident intentional edge evidence and not APMesh admission. The badia examples #252119 and #65904 are labeled **multiple components**, even though their other flags pass. The four catalog-clean QuadWild IDs are **58012, 67792, 81877, 94884**.

## Per-file licensing gate

The upstream [Thingi10K original README](https://github.com/Thingi10K/Thingi10K) explicitly distinguishes its **Apache-2.0 code license from the different licenses of its individual Thingiverse objects**. The `license` labels in the pinned third-party catalog are **declarations to be independently verified against each original object's page and applicable terms**. We cannot assume a blanket license for input meshes, remeshed outputs or surface BP derivatives.

- **ID 230923:** catalog declaration `Creative Commons - Attribution - No Derivatives`; **HOLD** for legal/rights review before remeshing-derived distribution.
- **Noncommercial review:** IDs `44503, 58012, 81877, 252119`. These may remain eligible for permitted research uses, but no blanket derivative publication or commercial usage is asserted.
- **GPL review:** ID `37266`.
- **Share-alike and attribution:** review credits, exact version, source distribution terms and derived redistribution requirements individually; do not infer rights solely from the catalog.
- No source STL mesh files, model preview screenshots, or geometry-derived output were included in this research commit.

## Updated bounded pilot (predeclared, not a cherry-picked success sample)

1. **P0 regular QuadWild cohort:** **67792** (`dual dodec`) and **94884** (`container sphere two hundred`): metadata-closed single-component, edge/vertex manifold, no reported degenerate/duplicate triangles; catalog declarations are Creative Commons Attribution. **Still require T0 object-specific rights verification and T1 raw STL hash**.
2. **P0 low-complexity representation controls:** Badia **293137** (`Bunny LowPoly`, 292 input triangles) and **37881** (`Input Pinion`, 3,400), to measure early STL→features→bicubic Bézier partition feasibility independently of output quad claims.
3. **P1 complex/negative QuadWild case:** **61394** (`millennium falcon top`, 6,747 original triangles), reported open, multiple components, edge/vertex non-manifold, and duplicate/degenerate triangles. Retain it as **adversarial input**; do not silently clean and compare its new output against unverified original-paper results.
4. **P1 valid but noncommercial-license review:** QuadWild **58012** and **81877**; both pass the conservative topology flag screen, but use restrictions must be reviewed first.
5. **P1 vertex singularity controls:** QuadWild **423069** and **498974**: closed, edge-manifold, but catalog **vertex_manifold=false**. Distinguish vertex-only from edge-nonmanifold hypotheses.
6. **HOLD rights:** **230923** until the `No Derivatives` restriction is resolved. Maintain all **12 QuadWild** and **11 Badia** named IDs as the separate frozen denominators, including blocked/failed samples.

## Reproducibility and limitations

New [per-ID joined catalog manifest](THINGI10K_CATALOG_METADATA_23.csv), [JSON receipt](evidence/thingi10k/thingi10k_source_catalog_metadata_audit_2026-11-20.json), and executable [metadata gate](probes/thingi10k_literature_metadata_gate.py) with [hermetic unit tests](probes/test_thingi10k_literature_metadata_gate.py).

Locally executed **17/17 hermetic Python tests PASS** using synthetic 23-entry fixtures, checking source Git-blob identity, lost/duplicated IDs, false admission, Big Badia original triangle mismatch, malformed topology and license caution. Separately, the **actual entire 9,997-entry public catalog was parsed and joined** during this live metadata audit using the GitHub connector. **The Python CLI itself has not been run on the full original 3.2-MB JSON bytes in the local container**, so do not report an end-to-end 23-model file download or a successful raw STL mesh audit.

To rerun locally using a separately acquired copy of the **exact frozen `docs/data/models.json` bytes**:

```bash
cd docs/research/nonmanifold-benchmark/probes
python -m unittest -v test_thingi10k_literature_metadata_gate
python thingi10k_literature_metadata_gate.py \
  --catalog-json /private/pinned/models.json \
  --cohort-csv ../THINGI10K_LITERATURE_COHORT.csv \
  --receipt /private/new/thingi10k_metadata_receipt.json
```

The gate fails closed for wrong catalog blob SHA, changed published Badia counts, incomplete IDs, unreviewed gates being falsely marked as approved, malformed metadata or pre-existing receipt destination.

**Next:** T0 verify each original Thingiverse per-asset license; T1 securely acquire and SHA-pin the prioritized STL bytes; T2 independently recompute indexed edge and vertex-link incidence, component count, degeneracy and feature graph; T3 verify same-file QuadWild input/output pairs and recompute published metric definitions; T4 attempt exact-shared-curve bicubic patch conversion then a real APMesh TRI / supported QUAD run; T5 matched-resolution quality/error/timing comparisons including failed and blocked cases. Existing M5/S40/S27/M3, historical Book/Eistute/Decor Shelf and F13 Tsh249 remain unchanged. PR #225 DRAFT; do not merge to `main`.
