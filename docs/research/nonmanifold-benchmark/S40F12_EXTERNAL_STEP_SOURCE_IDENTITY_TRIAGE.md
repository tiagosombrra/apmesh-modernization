# S40-F12 — External STEP source-identity screening for non-manifold benchmark admission

**Checkpoint:** 2026-11-19. **Scope:** independent external model screening only, not S40/F9 face admission or APMesh TRI/QUAD.

## Problem and source

The industrial original S40/M5/S27/M3 models remain manifold controls: no pinned source edge with three distinct face owners. An external authoring corpus, [zellyn/dodgy-step-files](https://github.com/zellyn/dodgy-step-files), offers publicly documented non-manifold Part 21 failure cases, but the *STEP representation marker, sewing expectation and true source-identity face incidence are different questions.*

Upstream repository pinned at commit `2a27aed219fbf930218aac5f24b07c131411b3de` (2026-08-14). Root `LICENSE`: MIT. Authors describe the files as controlled diagnostic fixtures, **not genuine industrial source models**. Original third-party STEP bytes and geometrically derivative BP files are **not committed** here.

## Direct original STEP EDGE_CURVE graph census

Inspected actual upstream text through the public GitHub connector. Followed `ADVANCED_FACE → FACE_(OUTER_)BOUND → EDGE_LOOP → ORIENTED_EDGE → EDGE_CURVE` and counted *distinct original face IDs*, not repeated uses by one face.

| Fixture at pinned upstream | Original faces | Distinct original EDGE_CURVE | Largest source edge face incidence | Source edge with >=3 face owners? |
|---|---:|---:|---:|---|
| `step-examples/12-3a-shells/Tsh249.stp` | 3 | 9 | 1 | **NO** |
| `step-examples/12-8-mixed/M045.stp` | 3 | 12 | 1 | **NO** |
| `step-examples/12-3a-shells/Tsh112.stp` | 3 | 12 | 1 | **NO** |
| `step-examples/12-3a-shells/Tsh022.stp` | 2 | 7 | 2 | **NO** |

Pinned upstream Git blob IDs: `Tsh249 ce612e8959c3e8954e2c0e565e291ecbbe6cd5ff`; `M045 e18ddb6dee65daf6df084af1eeab18f7b684304e`; `Tsh112 25d39741d59155786816b0ebbdaf0273f309f6d6`; `Tsh022 896025d0a95e50cff3ce1d7669b4bceab6417305`.

A `NON_MANIFOLD_SURFACE_SHAPE_REPRESENTATION` label, or a claim of non-manifold **after sewing**, does not prove that three faces refer to one original `EDGE_CURVE`. No fixture above is admitted to the required **original-source-identity 3+-incident edge positive** category.

## Distinct research lead: Tsh249 requires intentional reconciliation

The pinned source declares three separate triangle-fin `ADVANCED_FACE` #27/#55/#83 and three independent original STEP `EDGE_CURVE` #10/#38/#66. Their straight edges lie on the same X axis and span respectively **[0,6], [2,8], [4,10]** in the STEP numeric unit; the common triple overlap is **[4,6]**, of length 2 in the source coordinate unit. That is geometric concurrency, **not shared topological edge identity**.

The upstream catalog [Tsh249](https://zellyn.com/dodgy-step-files/browse/12-3a-shells/Tsh249.html) reports an OCCT 7.8.1 *non-manifold sewing* run with one resulting 3-face multiple edge, plus two 2-face contiguous edges. This experiment was **not independently reproduced here**. Treat Tsh249 as an **author-created source-fragment reconciliation candidate**, not a real industrial case, and do not count it as a positive before a new native OCCT import+sewing audit, source-to-result edge lineage, post-sewing 3-face incidence, geometry fidelity and APMesh TRI output.

## New executable source-only probe

- `probes/external_step_source_incidence.py` checks STEP source face-edge ownership by **exact entity identity**, with no epsilon-welding. It rejects malformed/missing critical references and duplicate instances, tracks repeated face-edge uses, and distinguishes original non-manifold edges from geometric overlap. Optional `--collinear-edges 10 38 66` measures exact rational source-line interval intersection, without claiming successful OCCT sewing.
- `probes/test_external_step_source_incidence.py`: **9/9 PASS** local hermetic tests on synthetic Part 21 fixtures, including 3 faces reusing one original edge, same-location different edge IDs, missing references, duplicate entity, duplicate edge use, quoted semicolon, truncated data, exact overlap and non-collinearity.
- Four **real remote STEP sources** were independently inspected as text for the table above; **the Python probe has not been executed on the downloaded original STEP bytes in this run**. The table records direct structural inspection, not native verification.

## Commands to reproduce with approved local copies

```bash
cd docs/research/nonmanifold-benchmark/probes
python -m unittest -v test_external_step_source_incidence

python external_step_source_incidence.py \
  --step /private/Tsh249.stp \
  --collinear-edges 10 38 66 \
  --require-source-three-plus \
  --output /private/receipts/tsh249_source_incidence.json
```

The last command should exit **3** because Tsh249 has no three-face edge by original source identity. Run without `--require-source-three-plus` to obtain the *classified negative* receipt with exit code 0. Neither command performs native sewing.

## Next scientific gate

1. Independently import the pinned Tsh249 original through OCCT, record source-native correspondence and orientation; test non-manifold sewing **explicitly**, auditing 3-face incidence of each output edge and changes to source geometry.
2. Distinguish **repaired-source-positive** experimental generalization from the still-unmet class of **original-source-positive** industrial non-manifold STEP.
3. Verify G1–G7 admission protocol, conversion/quad-patch semantics, accepted APMesh TRI mesh and scientific baseline. Do not merge research PR #225 to main or raise S40's admitted 22/43 original faces on this evidence.
