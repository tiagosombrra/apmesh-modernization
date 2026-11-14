# Non-manifold benchmark corpus and reverse-patch feasibility

**Status:** RESEARCH DISCOVERY / DOCUMENTATION ONLY — R0 inventory and first R1 model-level discovery recorded; R2 topology checks NOT STARTED.
**Date:** 2026-11-14.
**Planning base:** main `f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94`.
**Branch:** `research/benchmark-corpus-reverse-patches`; draft PR #225.

## Goal

Build an independently auditable external model corpus for APMesh, and assess *separately* whether CAD/B-Rep or polygon meshes can be converted into four-sided bicubic Bezier patch complexes with intentional shared curves. This is an experimental scientific proposal; no new model has passed G1-G7 and no converter or meshing code has changed.

## Current evidence snapshot

- [R0 repository baseline audit](R0_BASELINE_AUDIT.md) — frozen observed main, concurrent PRs, three original model Git blob identities, existing but NOT newly executed scientific gates.
- [R1 discovery report](R1_DISCOVERY_REPORT.md) — **40 named upstream leads**: 29 HexMe CAD files with metadata, 6 procedural Fusion Energy CAD scripts, and 5 upstream-documented corrupted Thingi10K IDs. No external model has been admitted.
- [Model-level discovery register](candidate_register.csv) — IDs, pinned source and metadata URLs, upstream license declarations, current uncertainty and conservative DISCOVERED status.
- [Execution plan](PLAN.md) — R0–R7 dependencies, independent output gates, explicit stop rules.
- [Admission protocol](MODEL_ADMISSION_PROTOCOL.md) — G1–G7, edge/vertex/sheet taxonomy, hard blockers and adversarial negative controls.
- [Candidate source inventory](CANDIDATE_SOURCES.md) — model families, original links and limitations.
- [Risk / decision register](RISK_AND_DECISION_REGISTER.md) — D1–D8 decisions, specialist challenge reviews and risks.

## Corpus partitions

- HISTORICAL: Book, Eistute and Decor Shelf, author-created published baselines; frozen.
- SYNTHETIC_POSITIVE: deliberately constructed analytic controls, not independent generalization evidence.
- EXTERNAL_POSITIVE: only individually *admitted* externally sourced valid intended shared-edge non-manifold junctions (none yet).
- MANIFOLD_CONTROL: CAD and surface benchmarks for geometry fit and QUAD comparisons, not non-manifold proof.
- NEGATIVE_UNSUPPORTED: deliberately invalid/ambiguous/vertex-only/intersecting or unrepresentable examples to validate rejection.

Each sample is assigned a single experiment role, with explicit evidence. An upstream non-manifold label, a touching-solid picture, or a correct-looking generated OBJ is **not** sufficient to certify an APMesh non-manifold model.

## Scientific hypotheses (not results)

- H1: a verified intentional multi-sheet shared-edge junction can be represented by bicubic Bezier patches with compatible canonical boundary curves within declared geometric approximation limits.
- H2: the existing TRI workflow can handle such independently verified BP inputs with positive measured incidence agreement without changing its historical scientific behavior.
- H3: TRI/QUAD, all-quad and anisotropic approaches may later be compared on matched geometry after separate algorithmic qualification.
- H4 (separate): input polygon meshes can be reverse-engineered into a compatible patch graph, with measured geometry and topology preservation; this is NOT implied by H1-H3.

## Scope protections

No third-party raw models committed until per-asset rights and attribution review; no production input domain expansion, topology welding or acceptance threshold changes; no modification of historical BP inputs, formulas, generators or published numerical oracles. Active Stage 3 and QUAD work is independent.

## Approval states

R0 baseline inventory: DOCUMENTED, no fresh regression. R1 named source discovery: DOCUMENTED, per-model rights/topology/fit admission OPEN. R2: NOT RUN. No claim of approved corpus, independent real non-manifold geometry, CAD export, numerical validation, positive curve incidence or advisor signoff.

Discussion belongs in draft PR #225. Scientific scope, conversion work, core integration and final merge require appropriate explicit reviews and applicable exact-image gates.
