# Scientific decisions, risk ledger and adversarial review

Status: research proposal; no advisor approval and no executed technical verification inferred.

## Open decisions

| ID | Question | Provisional default (not approved) | Decision authority | Effect if unresolved |
|---|---|---|---|---|
| D1 | Is mesh-to-patches reverse engineering an independent thesis contribution or just enabling tooling? | enabling feasibility pilot first | advisors + researcher | block expansion of full STL/OBJ reconstruction scope, not corpus research |
| D2 | What minimal external demonstration constitutes generalization? | one defensible intended multi-sheet edge junction with independent source oracle as a feasibility minimum, not publication sufficiency | advisors + scientific reviewer | block claims of generalization |
| D3 | Which geometric approximation budgets apply to bicubic patch fitting? | decide using analytic fixtures and local feature scales, then freeze | CAD/numerics reviewer + advisors | block converter admission |
| D4 | Can third-party assets be copied or redistributed in the MIT repository? | default NO until per-file legal review | licensing reviewer | block asset commit; metadata remains allowed |
| D5 | Which external baseline meshers and which exact versions are comparable? | no ranking until matched domain, constraints and metrics | meshing and methods reviewer | block comparative superiority claims |
| D6 | How to label anisotropy / QUAD/TRI / all-quad scope while code evolves? | separate experimental versions and qualification receipts | method owners + advisors | block cross-method claims |
| D7 | What is the numerical meaning and representation of curve identity through splitting/trimming? | exact source feature graph + sidecar with canonical edge IDs | topology and CAD reviewers | block positive topology conversion |
| D8 | When may experimental converter enter core build/runtime? | after standalone prototype, independent oracles, fault injection and exact baseline regression | C++ owner + QA + advisors | block integration; permit independent R&D |

These decisions can remain OPEN while documentation, discovery and synthetic-negative controls are created. They must be resolved before the gate they govern.

## Risk register

| Risk | Impact | Likelihood (qualitative) | Control | Stop condition |
|---|---|---|---|---|
| R-01: geometric coincidence mistaken for shared topology | critical | high | explicit curve graph, exact incidence oracle, non-welding negative fixture | lost/gained shared source edge |
| R-02: non-manifold tag means only defects or vertex singularity | critical | high | classify edge/vertex/sheets and input defects separately | no intended >=3-sheet edge junction |
| R-03: trimmed NURBS cannot fit four-sided bicubic patches sufficiently | high | high | partition/fit with bounded feature-aware error; clear UNSUPPORTED status | no bounded topology-preserving decomposition |
| R-04: converter affects historical scientific behavior | critical | medium | standalone process, immutable BP tests, exact-head regression only when integrated | divergence in frozen comparable evidence |
| R-05: unavailable or restrictive third-party license | high | medium | exact per-asset rights, separate downloads | uncertain redistribution rights |
| R-06: overstated conclusions from easy/manifold datasets | high | high | distinct strata and denominators, held-out set | no independently verified non-manifold coverage |
| R-07: circular geometry/topology validation | high | medium | independent source oracles and algorithmically distinct checkers | only self-reported success |
| R-08: benchmark selection bias | high | high | pre-registered selection, exclusions and negative records | only successful specimens reported |
| R-09: QUAD/anisotropic comparisons are premature | high | high | versioned method-specific eligibility; no borrowed TRI evidence | method not independently qualified |
| R-10: exponential scope/cost of STL/OBJ reconstruction | high | high | staged B-Rep-first proof, explicit technical stop | unbounded manual tuning or generator refactor required |
| R-11: inconsistent source units, normalization, near-zero features | high | medium | original units, inverse transform, local feature thresholds | errors cannot be meaningfully measured |
| R-12: large hostile input / parser failure | high | medium | bounded parsing, resource and interruption controls in isolated converter | hangs, crashes or partial success without classification |

Likelihoods are expert planning estimates to prioritize investigation, NOT observed failure rates.

## Adversarial review rubric

1. Topology specialist tries to find false edge junctions, unintended welding, vertex-only singularities, and changed incidence order.
2. CAD specialist seeks failed four-sided layouts, degenerate parameterizations, trimming assumptions and unacceptable feature loss.
3. Meshing specialist challenges comparable resolutions, element types, valid acceptance states and error-vs-complexity reporting.
4. C++ engineer challenges ownership transfers, partial failures, exception safety and integration boundaries.
5. QA engineer supplies malformed, near-coincident, inverted and interrupted cases to defeat optimistic green tests.
6. Methods/statistics reviewer challenges selection bias, per-model tuning, censored failures, insufficient holdout and noncomparable baselines.
7. Licensing reviewer challenges the authority to share raw files, conversion derivatives and extracted images.
8. Advisors decide claim boundaries and thesis relevance; signoff remains absent until documented.

Each reviewer records PASS / FAIL / BLOCKED / NOT_APPLICABLE, finding ID, source SHA, expected vs observed evidence, corrective action and approval identifier. A blocked or absent independent check is not PASS.

## Review and delivery ledger

- 2026-11-14: research-only plan developed based on repository contracts and public dataset documentation. No code, original input model, baseline metric, licensed external model or scientific technique changed.
- Initial exact planning base: f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94.
- Concurrent open QUAD PRs at planning time: #223 and #214. Their state may change and must be rechecked before executing work.
- Initial proposal deliberately does not claim compilation, CTest, Python checks, generator runs, dataset download, conversion success or external reviewer signoff.
