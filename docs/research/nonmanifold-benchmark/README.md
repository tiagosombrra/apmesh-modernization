# Non-manifold benchmark corpus and reverse-patch feasibility

Status: RESEARCH PROPOSAL / DOCUMENTATION ONLY
Date: 2026-11-14
Baseline main: f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94
Research branch: research/benchmark-corpus-reverse-patches

## Purpose

Establish a defensible external corpus for the APMesh non-manifold parametric patch method, and separately assess whether CAD or polygon meshes can be converted into an APMesh-compatible patch complex. No algorithmic result is claimed by these documents.

The published, author-created Book, Eistute, and Decor Shelf models remain an immutable historical regression corpus. The existing C++17 meshing algorithm, input model files, scientific oracles, production sources, and active Stage 3 / QUAD work are out of scope for this documentation phase.

## Read in order

1. [Execution plan](PLAN.md): phase gates, work packages, output artifacts and dependency boundaries.
2. [Model admission protocol](MODEL_ADMISSION_PROTOCOL.md): topology taxonomy, hard blockers, minimum independent evidence and reproducible admission.
3. [Candidate sources](CANDIDATE_SOURCES.md): sourced datasets and what they do **not** establish.
4. [Risk and decision register](RISK_AND_DECISION_REGISTER.md): open advisor decisions, mitigation and review roles.
5. [Model candidate register](candidate_register.csv): schema only until actual models and licenses are inspected.

## Corpus partitions

- HISTORICAL: the three article models, preserved bit-for-bit as published scientific baselines.
- SYNTHETIC_POSITIVE: controlled patch complexes with analytically known incidence and geometry, for engineering oracles (not external generalization evidence).
- EXTERNAL_POSITIVE: third-party, individually admitted models with verified intended non-manifold junctions and a demonstrably compatible patch representation.
- MANIFOLD_CONTROL: CAD / surface benchmarks that test geometry conversion and quad quality but do not claim non-manifold coverage.
- NEGATIVE_UNSUPPORTED: intentionally malformed, ambiguous, self-intersecting, vertex-only singular or unrepresentable cases used to prove correct rejection.

Each sample belongs to one partition for a given experiment. Moving it to a different partition requires recorded evidence and review.

## Scientific hypotheses (not conclusions)

H1: selected external edge-junction complexes can be represented as bicubic Bezier patch networks with shared boundary controls without changing their declared incidence graph.
H2: the existing triangular APMesh workflow can mesh admitted converted inputs while retaining shared-curve agreement and its historical regression outcomes.
H3: later TRI/QUAD, all-quad and anisotropic research extensions, if separately qualified, may be evaluated against the same controlled source geometries.

Reverse engineering polygonal meshes into patches is a distinct research hypothesis. Do not silently include it within H1/H2.

## Not authorized

No benchmark assets copied into this repository without individual rights review; no fake success if zero shared boundaries are compared; no hidden welding or manifoldization; no modification of published input files; no production integration, benchmarks, performance claims, or merge from this proposal alone.

## Review rule

The documentation proposal may be discussed in a draft PR. Scientific expansion, external data redistribution, converter implementation and eventual production integration require additional explicit review and the respective gates in PLAN.md.
