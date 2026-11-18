# Mesh Studio R2.7.23 — original native acceptance criteria and second-epoch research gate

**Date:** 2026-11-18. **Branch:** `feature/mesh-studio-r27-bvh-20261116`,
**PR #239:** research draft/unmerged, default source generator unchanged.

## Scientific question

The R2.7.12–R2.7.22 compiled original serial TRI C++ runs confirmed:

| Original article configuration | Model | Original patches / curves | Real accepted steps | Rejected/restored steps |
| --- | --- | ---: | --- | ---: |
| `configs/eistute/article.conf` | Eistute | 4 / 13 | **[1]** | **3** |
| `configs/book/article.conf` | Book | 28 / 85 | **[1]** | **2** |

All associated original accepted full source NDJSON hashes, per-face
native IDs and submesh observers remain pinned in the earlier
R2.7.18–R2.7.22 studies. The two *separate* model runs do **not**
constitute two adaptive epochs of one model. The accepted
C++ write happens only after an actual `AcceptedMeshScope::Commit()`;
all other candidates can be restored, written for diagnostics
or rejected and cannot become scientific LOD descendants.

## Why one accepted step does not establish LOD

In `src/generator/generator_adaptive.cpp`, a candidate is
accepted only by the original expression
`score_ok || small_mesh_progress_override`, followed by
`accepted_scope.Commit()` and an original accepted-source record.
The `score_ok` predicate is itself a conjunction of
several independent source-code conditions, depending on
`AcceptanceMode()` and the `adaptive_stable` policy.
Even when candidate error decreases, coherence, quality,
local progress, patch consistency, overshoot, growth,
efficiency or retry acceptance can block commitment.
A simple criterion such as `candidate_error < previous_error`
is **not** equivalent to the actual C++ policy.

The existing config modes are not identical:
Eistute uses `ADAPTIVE_MODE=adaptive_stable`;
Book uses `ADAPTIVE_MODE=research_debug`. Their
respective source inputs, thresholds and acceptance
conditions must remain independent. Changing a model's
configuration (even without modifying C++) produces a
**new controlled experimental treatment**, not an
additional accepted epoch of the original article run.

## R2.7.23 read-only original acceptance telemetry

A new optional C++ precommit trace is compiled **only**
under `AP_MESH_RESEARCH_NATIVE_LINEAGE` and emitted **only**
if `APMESH_RESEARCH_ACCEPTANCE_GATES=1`. The acceptance
expression is not replaced, reordered, relaxed or changed.
It emits bounded structured records for the actual
`(native_step, local_retry)` decisions, including:

- acceptance mode, stable-mode classification, original
  `score_ok` and `small_mesh_progress_override` booleans;
- error improvement, candidate/previous error, absolute
  error reduction, per-element error reduction, growth
  factor, acceptance score and triangle quality;
- coherence, local progress, consistency, quality,
  shape and transition gates, along with original
  mode-specific overshoot/target-growth checks;
- an explicit `predicted_branch_accept_not_committed`
  field that is **NOT itself scientific evidence of a
  committed epoch**.

`tools/mesh_studio/verify_native_lineage.py` enables
the optional diagnostic flag only for its actual isolated
compiled original native GeneratorAdaptive execution.
The complete original stderr byte stream, including
R2.7.18 actual provisional boundary closure, is
archived and SHA-pinned in the same original source
artifact as the original `accepted_step_*.ndjson`
postcommit sidecars. The instrumentation is absent
in the default scientific generator.

The independent `native_acceptance_gate_forensics.py`
validates original SHA-bound stderr and postcommit
NDJSON source reports, all boolean and numeric fields,
actual step/retry monotonicity, exact native
`score_ok || small_mesh_progress_override` equivalence,
and the original stable-mode predicate formula.
Every positive precommit branch event **must** match
an independently qualified accepted postcommit native
source sidecar with the same step and retry. Each
step with no positive decision must match a real
rejected/restored outcome. Any discrepancies fail
closed. A false predicate is diagnostic context,
not an automatic complete causal proof when other
predicates and overrides also participate.

This yields a bounded original scientific ledger:

`build/r2723-original-native-acceptance-gates.json`

and an independent 14-day GitHub Actions artifact
`mesh-studio-r2723-original-acceptance-gate-forensics-<source-sha>`.
Eleven synthetic adversarial tests challenge false
accepted epochs, duplicated native event keys and
JSON fields, changed stderr SHA, nonfinite metrics,
predicate formula drift, missing restorations,
wrong model classification and fabricated admission.
Synthetic cases are **never** treated as additional
original generator observations.

## Next controlled experimental stage

1. Audit actual Eistute and Book gate vectors to
   identify the **specific** source predicates
   responsible for real restored steps 2–4.
2. Design a small, preregistered, bounded
   configuration sensitivity study, changing at
   most one declared *legitimate* research parameter
   at a time, with the same source input SHA, binary
   and unchanged native acceptance expression.
   Retain each modified config's own SHA and
   distinguish it from the original article input
   configuration. Do not tune criteria after seeing
   outcomes without labelling that exploration.
3. Repeat actual original serial C++ generation
   for the controlled alternate configuration
   and independently count genuine `Commit()`
   events, sidecars, original element/patch IDs,
   restored attempts and byte-level source hashes.
   Do not combine one accepted step across
   independent runs into an artificial two-step
   adaptive sequence.
4. Only if **two distinct committed adaptive
   steps occur inside the same source-run scope**
   build native face/curve ancestry and continuous
   geometric error instrumentation. Then test
   actual patch interface compatibility and
   nonmanifold source incidence. **Only after
   those separate proofs** revisit R2.8.

Changing quality thresholds simply to force the
second commit would study a different policy,
not independently validate the current algorithm.
Likewise, reinterpreting a stored rejected step-4
OBJ as accepted is not an admissible shortcut.

## Status

**Implementation under CI validation.** The first
draft of the C++ diagnostic log had an escaped
quotation compiler problem; this was corrected
before the final native scientific gate. The
original C++ and independent Python/Chromium CI
must pass on the exact final implementation SHA
before the new original native diagnostic report
is considered certified.

**R2.8 remains BLOCKED**: no second genuine
same-run accepted epoch has yet been observed per
original model, original cross-epoch face/curve
descendants have not been certified, and no
continuous geometric approximation-error bound
has been established. No physical Windows GPU
present/RSS/VRAM result or production release
is asserted. The research PR stays draft,
`main` untouched, no tag/release.
