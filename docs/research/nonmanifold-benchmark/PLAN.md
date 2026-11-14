# Execution plan: external benchmark corpus and reverse-patch feasibility

**Classification:** scientific research proposal, NOT a technique-preserving refactor.
**Frozen planning base:** main f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94 on 2026-11-14.
**Working boundary:** documentation-only research branch; active Stage 3 modernization and QUAD branches remain independent.

## Objectives, exclusions and evidence hierarchy

O1: curate a small, scientifically defensible benchmark covering intended non-manifold shared-curve junctions and appropriate manifold CAD controls.
O2: diagnose topology without silently repairing it; preserve source entity identity and record limits of reconstructibility.
O3: prove a standalone converter to the existing indexed bicubic Bezier BP grammar only for admitted geometries.
O4: qualify existing APMesh TRI execution on the new inputs without altering its algorithms, acceptance criteria or historical models.
O5: define future, separate comparisons for TRI/QUAD, all-quad and anisotropy when their implementation status supports such claims.

Evidence hierarchy: (a) upstream model and metadata identity; (b) independent source-topology oracle; (c) independent geometric-fit oracle; (d) BP validator and source-boundary oracle; (e) APMesh generator execution and exact recorded acceptance; (f) independent output validation; (g) only then cross-method comparisons.

An accepted generator state and a saved rejected candidate are different observations. A candidate OBJ, log or screenshot alone is not proof of success.

## Work packages and mandatory gates

| ID | Work package | Output | Admission / exit gate |
|---|---|---|---|
| R0 | Baseline and concurrency audit | exact main SHA, active PR inventory, current regression contracts, immutable 3-model inventory | document existing status and identify tests; no unsupported claim of having executed them |
| R1 | Scientific taxonomy and benchmark search | authoritative source list, identifiers for ~30-40 preliminary candidates (planning target, not quota), per-file rights | references traceable; source names are not substituted for model IDs |
| R2 | Independent topological classification | edge/face incidence, oriented adjacency, sheet labels, vertex links, boundary and intersection reports | intended junctions distinguished from defects; positive models have nonzero declared shared-curve incidences |
| R3 | Geometry / representation feasibility | 8-12 candidate pilot set (target, conditional), conversion feasibility report, error budget proposal | every selected case is either supported, unsupported with evidence, or blocked with reason |
| R4 | Standalone proof of conversion | source -> feature graph -> bounded four-sided patch decomposition -> indexed BP; sidecar graph metadata | BP grammar valid, all intended source shared curves represented exactly as common curve entities, no implicit topology welding |
| R5 | Controlled APMesh TRI pilot | fresh per-run config/output manifests, independent boundary checks, saved-state/acceptance classification | historical traces unchanged on qualified environment; external generation states and positive incidence coverage actually measured |
| R6 | Research extension and comparisons | separately versioned TRI/QUAD, all-quad, anisotropic evaluation recipes; negative controls | code paths and modes are qualified individually; matched geometry, constraints, output metrics and explicit noncomparability labels |
| R7 | Publication/reproduction freeze | frozen selection, train/dev vs held-out final set, source provenance, raw outputs, negative results | scientific and engineering review; advisor approval; reproducible artifact and limitations table |

R0-R3 can proceed as a documentary/diagnostic research activity without a production C++ code change. R4 is a new experimental subsystem, not a shortcut into Stage 3. R5-R7 have prerequisites and are not authorized merely because this plan exists.

## Execution order and stop conditions

1. Record exact revision and concurrent branches/PRs. Never overwrite anyone else's in-flight code; all changes occur on topic branches with explicit scope.
2. Catalogue individual model IDs and licenses. Keep raw third-party files out of Git until redistribution permissions are confirmed; a reproducible download manifest is preferred.
3. Freeze topology taxonomy BEFORE selecting only successful models. Include positive and adversarial/unsupported cases.
4. Start with an author-constructed analytic four-sided patch fixture, then one independently sourced intended multi-surface junction. Prefer known analytic / STEP B-Rep to arbitrary STL.
5. Prove a common, shared boundary graph before surface fitting. Same geometry with independently fitted near-equal edges is NOT shared-curve compatibility.
6. Produce and validate exact 16-control indexed BP records with canonical side orientation; preserve an external provenance/graph sidecar outside legacy BP.
7. Execute admitted inputs through frozen TRI reference; compare exact historical regression under matching source/binary/config/instrument conditions.
8. Only then create future method-specific QUAD/TRI, all-quad and anisotropic trials with their own eligibility and separate baselines.
9. Hold out evaluation models; log all attempted conversions, rejections, retuning and exclusions. Publish failures and limitations.

Stop R4 for a candidate when there is no defensible finite four-sided bicubic decomposition within a declared geometry budget or if intended junctions cannot be kept as shared entities. Mark UNSUPPORTED, do not modify APMesh input acceptance or secretly rebuild the topology. Stop integration if historical regressions fail or independent output incidence coverage is zero.

## Converter architecture (proposal only)

Raw sources (STEP / B-Rep, then OBJ / STL / PLY)
  -> versioned parser and provenance
  -> independent topology/feature graph (edges, incidences, sheets, vertex links)
  -> constrained surface segmentation and four-sided patch layout
  -> common curve fitting FIRST; compatible per-patch bicubic fitting SECOND
  -> independent geometry + topology oracles
  -> indexed BP writer plus JSON sidecar with source-to-patch mappings
  -> existing BP validator, without changes to production acceptance behavior
  -> separate APMesh execution and outputs

A B-Rep face is not necessarily a single four-sided polynomial patch. Trimmed NURBS, holes, discontinuities, singular parameterizations, periodic surfaces and arbitrary degree require explicit subdivision or must be rejected. For polygon sources, reverse fitting can be non-unique; reconstructed geometry must be identified as an approximation with measured uncertainty.

## Per-model evidence package

Original URI and file ID; author/citation; per-file rights and redistribution decision; raw SHA256; source format, units, scale and normalization transform; topology classification with edge/vertex/sheet incidence; proof of intended junctions; feature graph with labeled curve IDs; chosen conversion algorithm/parameters; BP SHA256 plus sidecar; source-to-patch map; geometric errors and worst-case feature distortion; independent checker report; supported/rejected/blocked status; runtime binaries/config hashes; actual generation acceptance decisions; complete output artifacts and validation results.

Geometry metrics: bidirectional sampled Hausdorff (with sampling convergence/disclaimer), RMS, feature-curve deviation and optional certified bounds if available. Topology metrics: exact discrete incidence and orientation identity; never blend topology and geometric tolerances. Mesh metrics: triangle quality, degenerate/duplicate faces and curve chain agreement; later quad scaled Jacobian, angle, aspect ratio and irregular vertices; metric-space quality for anisotropy. Performance: wall time, peak RSS, element count, degrees of freedom, full hardware/toolchain metadata.

Statistical methodology: stratify by topology and complexity, fixed parameters or documented per-model optimization budget, paired comparisons where domains overlap, uncertainty intervals, and results for every admitted model. Distinguish converter failures from mesher failures.

## Exit conditions and sequencing constraints

- Research documentation gate: committed proposal + risk/decision log + source leads + empty model-level register; no model acceptance claim.
- Curated corpus gate: each named file independently traced, analyzed, and rights reviewed. Dataset publicity is insufficient.
- Converter prototype gate: reproducible positive and negative fixtures; independent topology and geometry checks.
- TRI integration gate: actual accepted states, nonzero shared-incidence checks, exact qualified historical regression, absence of source changes.
- Future-method gate: method-specific numerical and topology/quality oracles; no borrowing TRI evidence for experimental QUAD/anisotropy.
- Publication gate: frozen protocol, independent scrutiny, recorded negative findings, advisor-approved scope, release/license audit.

### External review responsibilities

Computational topology: verify junction semantics, vertex links, orientation and adjacency.
CAD/geometry: validate polynomial representability, trimming and fit error.
Meshing/numerics: validate element metrics and matched baselines.
C++ architecture: approve ownership isolation and fault-injection design.
QA/security: negative controls, hostile malformed inputs, input limits and independent oracles.
Research methods/statistics: freeze datasets, failure denominator, fairness and generalization.
Open-science/licensing: provenance, individual rights, repository separation.
Advisors: decide thesis contribution and any scientific change to the generator.

No review role is claimed to have signed off yet.

## Dependencies

See AGENTS.md, docs/PROJECT_STATE.md, docs/MODERNIZATION_PLAN.md, docs/GENERATION_VALIDATION_CONTRACT.md, docs/API_CONTRACTS.md and DATA_PROVENANCE.md. Never modify the historical publication oracle to accept a new research input.
