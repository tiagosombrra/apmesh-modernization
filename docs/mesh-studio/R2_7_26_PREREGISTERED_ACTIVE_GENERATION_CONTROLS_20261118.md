# Mesh Studio R2.7.26 — preregistered bounded active generation-control study

**Preregistered:** 2026-11-18, before running any R2.7.26 native variant. **Research-only** branch `feature/mesh-studio-r27-bvh-20261116`, PR #239 DRAFT, not main. This is an independent exploratory intervention, not a replication of the original article or an accepted scientific LOD.

## Why a different study

The exact R2.7.25 compiled-source audit found the Eistute step-N curve growth cap 4→2 did not bind the actual component, post-consistency targets, sampled points or effective element targets across seven original attempts (13 curves each); geometric-spacing floors dominated growth in 78/91 source witnesses. Book intensity 0.02→0.01 changed nominal policy growth but not its effective generated budget: `budget_driven=0` and `element_target_mode=0`; the source curve budget was inactive in all 255 witnesses.

A new parameter value is not accepted as "active" merely because the parser reads it. R2.7.26 asks whether a bounded intervention in a proven *executable generation path* changes actual per-curve sampling or actual precommit TRI geometry/quality, not whether we can force acceptance.

## Two EXACT, prospectively selected source-controlled treatments

| Independent process | Original article configuration | Sole generation parameter | Baseline → treatment | Measured mechanism / falsification |
| --- | --- | --- | --- | --- |
| `eistute_curve_min_13` | `configs/eistute/article.conf` pinned Git blob `bd368dbad5b61515106b5d74d28cbde159780cd6` | `CURVE_POINT_MIN` | **11 → 13** | `LoadRuntimeConfig` parses the key; original `GeneratorAdaptive::ClampCurveTarget` applies it to curve targets. Test actual original per-attempt curve targets, sampled points, same-process postcommit faces and all restored quality gates; do not presume point counts change. |
| `book_aft_one_local_pass` | `configs/book/article.conf` pinned Git blob `d88116054728311df74a6ece1d38d0cd23a64466` | `AFT_LOCAL_POSTPROCESS_PASSES` | **inherited parser default 0 → explicit 1** | This key is absent from Book article config. `LoadRuntimeConfig` uses default 0; `AdvancingFront::PostprocessPasses()` gates `poorRegionShapeSmoothing` in `improveMesh()`. Measure actual native precommit quality/acceptance and face bytes; do not assume postprocessing is invoked or improves quality on every patch. |

**Why this is single-factor:** Eistute changes exactly one existing source-config line. Book inserts exactly one previously absent parsed setting immediately after the pinned `ADAPTIVE_TARGET_GROWTH=1.05` anchor; the only effective difference is the inherited default 0 versus explicit value 1. An added key is **not** misdescribed as a one-line replacement. An independent source verifier must fail if the original Book blob, parser default, insertion anchor, input model, any unrelated policy value or old generation key differs. It must not treat a missing file or unrecognised config field as a valid trial.

Original source article configs and input .bp models are **never edited**. Only isolated variant intention .conf and temporary absolute I/O selectors are permitted. Both treatments use the **same prebuilt source-attested serial research C++ executable** already qualified in R2.7.25; research capture remains opt-in, source hashes and exact retained C++ stderr/stdout are required.

## Scientific hypotheses, limits and preregistered interpretation

- **H-E (Eistute):** minimum 13 may raise some pre-consistency targets originally at 11, but geometric floors and structural consistency can dominate; actual final sampled curves or generated faces can remain unchanged. A higher minimum does **not** prove lower transition imbalance, overall TRI quality or native acceptance.
- **H-B (Book):** one additional local AFT smoothing pass may alter final candidate vertex coordinates/triangle quality if eligible poor inner-vertex neighborhoods exist. No presumption of changed element counts or a second accepted epoch. If the path is not reached, or the smoother is a no-op, the correct finding is negative.
- Response variables: actual source C++ (step,retry) attempts and genuine postcommit accepted source steps; original precommit gate predicate vectors and quantitative quality/error values; per-curve pre- and post-consistency targets and actual sampling; native source element/patch/curve IDs, exact sidecar SHA, geometry/quality when available. Compare only matching step/retry prefixes, never concatenate processes or label rejected candidate state as accepted.
- Fail closed for nonzero native execution, missing original compiled binary/source, second unrelated config change, unverified parser default, invalid/missing source-bound sidecar, ambiguous event ordering, nonfinite metrics, unsupported schema, log truncation, incorrect source counts, or unbounded runtime. Preserve logs of failures separately rather than relabel them a successful experiment.
- Observed effective differences do not imply statistically general improvement. A second genuine commit in *one* trial remains exploratory and cannot become an article epoch. Independent face/curve cross-epoch descendants and a **continuous surface error bound** would still be required for R2.8.
- Do not change `score_ok || small_mesh_progress_override`, predicates, original acceptance parameter thresholds, C++ topology ownership, welding, default VTK/BVH, production build behavior, main, tags or releases.

## Design decisions and independent gates

1. Archive this preregistration in Git **before** writing the R2.7.26 treatment runner or executing native variants. Pin its prior Git SHA in the later evidence.
2. Extend only the reusable R2.7.24 *config-intent builder* to accept Book's explicitly whitelisted omitted-default key, with R2.7.24 replacement-only behavior unchanged. Require original UTF-8/LF exact Git-blob identity.
3. Reuse R2.7.24's real compiled `run_treatment`, source hash checks, genuine accepted per-face sidecars, exact precommit gate checks, and independently re-opened raw-file auditor; retain the R2.7.24 original sensitivity suite unchanged.
4. Add R2.7.26-specific tests to reject a forged baseline/default/anchor, multiple appended settings, changed model, false two-epoch claim, invalid or incomplete source C++ budget and fake retained artifact. Synthetic tests are **not** accepted native research data.
5. Execute separate original-model C++ treatments in the exact native CI, compare against real archived original C++ R2.7.25 attempts, retain original and variant raw bytes (not just summaries), and execute Linux/Windows/Chromium independently. Preserve the exact final artifact on the personal doctoral Drive with SHA-256 readback before temporary Actions retention expires.
6. Publish positive **or negative** findings with *exact* code SHA, actual source input SHA, executable SHA, concrete accepted/rejected counts, source geometry and quality evidence; no causal claim from one trial alone. Keep PR in DRAFT and unmerged.

**Pretrial status:** NO R2.7.26 native variants executed or certified in this preregistration. R2.8 **BLOCKED**.
