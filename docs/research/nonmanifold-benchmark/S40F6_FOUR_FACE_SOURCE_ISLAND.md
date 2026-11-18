# S40-F6 — Atlas Bézier isolado com quatro faces originais e interfaces perpendiculares

**Checkpoint:** 18/11/2026. **Classificação:** piloto científico de reconstrução analítica a partir de entidades do STEP original, **não** admissão no atlas industrial parcial S3.Y e **não** uma execução nativa do STEP integral.

## Resultado

A S40-F6 ampliou o BP isolado da S40-F5 de duas para **quatro faces de origem**: `ADVANCED_FACE #1279`, `#1386`, `#3269` e `#3485`. A numeração por face é a do arquivo original `original/i25o_s40.step` do repositório `cgg-bern/hex-me-if-you-can`, revisão `8f00f02579037cc893042f2ee2c910b20e3fb1b0`, SHA-256 `b79eb5be1fde71b6a8d086fe14800a1ec62e3a3c4618910c81c64d23718abf3b`.

O grafo do STEP original foi novamente consultado. Ambas as novas faces têm cinco `EDGE_CURVE` do tipo `LINE`, um único contorno e suporte `PLANE`. As interfaces de origem são `#1392` (`#3269` ↔ `#1386`) e `#1365` (`#3485` ↔ `#1279`); a geometria analítica revela superfícies perpendiculares às duas faces horizontais. As cinco arestas de cada face e os vetores normais foram confrontados diretamente com as entidades originais. **Esse contraste por entidades não substitui importar o arquivo STEP inteiro no OCCT.**

| Propriedade | Resultado independente |
| --- | ---: |
| Original-source-derived faces represented in standalone pilot | **4** |
| Indexed bicubic Bézier patches | **8** |
| Declared global controls | **104** |
| Internally paired source-indexed seams | **6** |
| Indexed open source-boundary segments | **20** |
| Original F5 patches retained unchanged | **4/4** |
| Original F5 controls retained unchanged | **56/56** |
| New source vertical faces | `#3269`, `#3485` |
| New two-quad boundary split source edges | `#3299`, `#3489` |
| Cross-plane original EDGE_CURVE interfaces | `#1392`, `#1365` |
| Native reconstructed BRep interior tests on new vertical faces | **900/900 IN** |
| Native reconstructed BRep boundary tests on new vertical faces | **816/816 IN/ON**, 0 OUT |
| New original faces admitted to S3.Y | **0** |

The new five-edge polygons have odd boundary incidence and cannot become a conforming two-quad partition without a boundary split. The splitter evaluates candidate source edges in the planar YZ projection, admits only *strictly convex* two-quad partitions whose union is the original source polygon, and refuses splitting frozen interfaces from S40-F5 and S3.Y. Each selected source edge is registered as two distinguishable subsegments, retaining its original STEP `EDGE_CURVE` identity for future neighbors.

The new vertical faces are geometrically planar and their four bicubic Coons patches have numerical area matching the two reconstructed native OCCT planar faces within floating-point precision. Each new face contributes 450 `IN` interior and 408 `IN/ON` boundary samples with zero `OUT`. Source-derived native face areas are approximately **1535.691741686622 mm²** (`#3269`) and **1535.691741683782 mm²** (`#3485`). This is a **sampled native-surrogate check**, not a certified continuous CAD trim or Hausdorff equivalence claim.

## Preserving original edge identity

The 56 first global control records and four original patch ID arrays of the S40-F5 isolated BP are preserved **exactly as values**. The parent is pinned by SHA-256 `2fd7d00234aea44aefdca4fce12f8dd8b2e9397122c366ed025c77bff714810d`. A distinct byte-identical serialized prefix is **not** claimed: the combined BP grammar places all vertex records before patch records, so new control records appear before the inherited patch records.

The `#1392` and `#1365` shared sides use the *same integer-indexed global control IDs* on both incident patches and opposite CCW perimeter orientation; neither interface is joined by coordinate proximity. The independent checker, separate from the constructor, verifies every old/new patch, all six index-paired seams, source registration for all 20 free sides, preservation of the prior four patches, planar Jacobian and the two original-edge cross-plane joins.

## Regression and scope

- **S40-F6:** 37/37 unit/adversarial tests PASS, **including 16 private-source tests**. In a public-only environment, those tests explicitly SKIP, not PASS.
- **S40-F5 regression:** 33/33 PASS in a separate process with its private source-derived reference.
- **Total executed now:** **70/70 PASS**, two separate selections; this is *not* a whole-project C++ or APMesh mesh-generation regression.
- Original STEP source graph: two new five-edge wire records, normals and source-edge owners matched by independent upstream inspection.
- **Original full STEP native import for the new F6 BP: NOT RUN.** Real trimmed-face mapping and accepted S3.Y parent-BP join: **NOT RUN**; the 156-patch/22-face research baseline remains frozen. A genuine external 3+-sheet edge case remains absent (original S40 is manifold).

Original STEP file and private BP/STEP-derived geometry are **not committed**. The ZIP is a private reproduction package containing the four-face BP, the original-derived source specifications and source-identity sidecar. Public commits contain only builders, independent checkers, tests, hashed receipts and this report. Rights of upstream CAD assets must be evaluated before public derivative redistribution.

## Reproduction

The public Python files live at `docs/research/nonmanifold-benchmark/probes/`. Place the byte-locked S40-F5 private spec and the S40-F6 private vertical-face spec in a private directory, then run:

```bash
python s40f6_four_face_source_island.py \
  --f5-source-spec /private/s40f5_source_spec.PRIVATE.json \
  --f6-source-spec /private/s40f6_vertical_faces.PRIVATE.json \
  --output-dir /private/s40f6

python s40f6_independent_bp_audit.py \
  --bp /private/s40f6/s40f6_four_face_source_island.PRIVATE.bp \
  --sidecar /private/s40f6/s40f6_source_island.PRIVATE.json \
  --f5-bp /private/s40f5_1279_1386_ISOLATED_PRIVATE.bp \
  --f6-spec /private/s40f6_vertical_faces.PRIVATE.json

S40_F5_SPEC=/private/s40f5_source_spec.PRIVATE.json \
S40_F6_SPEC=/private/s40f6_vertical_faces.PRIVATE.json \
S40_F5_BP=/private/s40f5_1279_1386_ISOLATED_PRIVATE.bp \
  python -m unittest -v test_s40f6_four_face_island
```

**Next S40-F7 gate:** obtain the accepted source-native S3.Y 156-patch BP and the full byte-pinned STEP, reconcile every old F5/F6 interface against S3.Y source IDs, reconstruct native face mappings for all four faces, retest both circular bounds and native trimmed domains, and admit only candidates that pass all gates. **Do not describe this isolated 8-patch BP as 164 admitted patches or 26/43 admitted original faces.**
