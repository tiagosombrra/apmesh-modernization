# Non-manifold benchmark corpus and reverse-patch feasibility

**Status:** R0 documented; R1 discovered 40 source leads; R2 **partially screened, G2 NOT PASSED**. Date: 2026-11-14.
**Frozen planning base:** main `f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94`.
**Research branch:** `research/benchmark-corpus-reverse-patches`, draft PR #225.

## Evidence and review sequence

1. [R0 baseline audit](R0_BASELINE_AUDIT.md): historical Book/Eistute/Decor model identity, frozen main and concurrency; **no fresh production regression**.
2. [R1 source discovery](R1_DISCOVERY_REPORT.md): 40 individually traceable candidates (29 HexMe original CAD files, six Fusion Energy procedural scripts, five upstream Thingi10K invalid-input leads).
3. [R2 topological screening](R2_TOPOLOGY_SCREEN.md): eight structurally traversable original STEP edge-use graphs; one torus/vertex-loop limitation; five local CadQuery pinned-source mirrors. Explicit STEP edge identity is **not** the same as geometrically coincident edges from separate solids.
4. [Candidate register](candidate_register.csv): all 40 are still DISCOVERED; 13 are annotated with screening observations and one extra torus limitation, but no G2 or complete G1-G7 admission.
5. [Execution plan](PLAN.md), [model admission protocol](MODEL_ADMISSION_PROTOCOL.md), [candidate source inventory](CANDIDATE_SOURCES.md) and [risk/decision register](RISK_AND_DECISION_REGISTER.md).

## Limited research probes

Located under `probes/`; not part of the production CMake build:

```sh
python -m unittest discover -s docs/research/nonmanifold-benchmark/probes -p "test_*.py" -v
python docs/research/nonmanifold-benchmark/probes/export_source_mirror.py --output-dir build/research-r2
python docs/research/nonmanifold-benchmark/probes/cadquery_contact_probe.py
python docs/research/nonmanifold-benchmark/probes/step_structural_screen.py path/to/permitted/original.step
```

The STEP scanner requires Python; the CadQuery probes additionally require CadQuery/OCP. Local prototype checks do not certify the exact committed revision or a native source model. See R2 report for command scope, results and missing gates.

## Corpus partitions

HISTORICAL (three original author-created article baselines), SYNTHETIC_POSITIVE (analytic engineering controls), EXTERNAL_POSITIVE (**none admitted**), MANIFOLD_CONTROL (independently classified CAD quality/fitting controls), NEGATIVE_UNSUPPORTED (invalid/ambiguous/vertex-contact cases).

## Scientific boundaries

No production C++, published `.bp`, scientific acceptance policy or numerical oracle has been changed. No third-party raw asset is committed. No external 3+-sheet patch-edge source has been verified. Future reconstruction, conversion, TRI qualification and QUAD/TRI/all-quad/anisotropy work require independent gates and advisor decisions before scientific claims.
