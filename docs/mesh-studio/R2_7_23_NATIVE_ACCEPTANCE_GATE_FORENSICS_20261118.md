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

## Exact scientific and regression certification — 2026-11-18

**R2.7.23 CERTIFIED for original native C++ precommit acceptance predicate
observation, independently corroborated by original postcommit accepted
TRI sidecars and restored outcomes. This does NOT certify geometric LOD.**

The final [GitHub Actions run #44379553187](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/44379553187)
finished with **all 4 independent jobs SUCCESS** at exact implementation
SHA `6c41fa07ca811661484ca3b8db824fdda878bdb8`. Earlier
preflight runs with escaped C++ output, a duplicate-field exception handler
and a historic pinned Git source mismatch were **not certified**; all were
corrected in the exact passing revision.

| Independent qualification | Actual result |
| --- | --- |
| Original compiled serial Eistute C++ source accepted-epoch + predicate audit | **1 original committed step** (step 1, retry 0); **3 restored steps**, **7** precommit local gate decisions in all |
| Original compiled serial Book C++ source accepted-epoch + predicate audit | **1 original committed step** (step 1, retry 0); **2 restored steps**, **3** precommit local gate decisions |
| Original C++ postcommit sidecar and precommit gate identity | **PASS**, exact source/run/accepted step/retry provenance |
| Historic original C++ source Git blob after removing exclusively the optional pinned observer | **Byte-identical** with immutable historical accepted C++ source blob `e0d1edd28968a684edba1e6c11a72b54e07e283a` |
| Original native scientific instrumentation OFF / ON | Eistute **21/21**, Book **17/17**, total **38/38 exact bytes identical** |
| Linux Python scientific + adversarial contracts | **363 run, 4 optional skipped, PASS** |
| Windows Python scientific + adversarial contracts | **363 run, 10 environment skipped, PASS** |
| Production TypeScript and Vite build, hosted Chromium | **PASS, 55 browser tests** |

### Real original C++ acceptance decisions

The actual original article configuration of both models uses
`AcceptanceMode() == 0`, but with different stable policies:
**Eistute stable_mode=true**, **Book stable_mode=false**.

| Model / real step | Retry observations | Error improvement relative to previous accepted state | Candidate TRI element growth factor | Genuine postcommit outcome |
| --- | --- | ---: | ---: | --- |
| Eistute 1 | 0 | **+78.26%** | **73.00×** | **Accepted** |
| Eistute 2 | 0 and 1 | **−24.92%** (error increased) | **1.719×** | **Rejected/restored** |
| Eistute 3 | 0 and 1 | **−20.23%** (error increased) | **1.880×** | **Rejected/restored** |
| Eistute 4 | 0 and 1 | **+83.86%** (error decreased) | **6.178×** | **Rejected/restored** |
| Book 1 | 0 | **+18.16%** | **38.00×** | **Accepted** |
| Book 2 | 0 | **−300.43%** (error increased) | **4.646×** | **Rejected/restored** |
| Book 3 | 0 | **−300.43%** (error increased) | **4.646×** | **Rejected/restored** |

These data are original **precommit predicate evaluations** bound to
the identical original postcommit native source, not an inference
from OBJ or saved historical candidate output.

**Most important scientific blocker — Eistute step 4.**
Candidate error falls from approximately **0.0620623**
to **0.0100167**, but this is *not enough* for the
stable-mode source acceptance policy:

- Actual observed transition-coherence penalty
  **2.06669**, while the original stable step-4
  permitted cap is **0.42**, so
  `transition_coherence_ok=false`.
- Actual maximum transition imbalance **0.29752**
  exceeds the original stable step-4 cap **0.18**,
  so `stable_transition_ready=false`.
- The original `quality_gate_ok=false`,
  `hybrid_shape_gate_ok=false`, and
  `stable_late_explore_accept=false`.
  Candidate minimum quality is approximately
  **0.12612**, with good-quality face ratio
  **0.57871**.
- Candidate TRI growth **6.178×** is a material
  *diagnostic* of aggressive refinement. Under the
  **actual Mode 0** source expression, a reported
  `target_growth_ok=false` is **not itself** an
  active acceptance conjunct. Do **not** claim that
  growth alone caused this rejection.
- Both local retries (0, 1) return the **same
  recorded metric/boolean vector** except retry
  ordinal, at each Eistute step 2, 3 and 4.
  This does **not** independently prove byte-identical
  candidate TRI meshes or that retries are physically
  identical; inspect local adaptation, curve sampling
  and quality response before concluding why.

**Book steps 2 and 3:** The original non-stable
Mode-0 acceptance policy requires
`improvement >= 0`. Both candidate errors rise
from approximately **42.18746** to **168.93236**
(**300.43% error growth**). Their failure to
satisfy that active error-improvement condition
is decisive. Recorded mode-1-like efficiency and
shape diagnostic flags **are not additional
active Mode-0 acceptance requirements** for Book,
even if false.

The accepted step-1 TRI growth values (73× and 38×)
also caution against inferring desirable geometric
LOD behavior from simple element count alone.

### Original research artifacts independently retained

The following artifacts are from that **exact passing run**, fetched
directly from GitHub Actions, uploaded to the authenticated personal
doctoral Drive research results folder, fetched back from Drive, and
verified to be **SHA-256 byte-identical** to GitHub's original ZIPs.

| Scientific source | Original GitHub Actions artifact | Original ZIP bytes | Original ZIP/Drive SHA-256 |
| --- | --- | ---: | --- |
| Full original source-bound C++ precommit gate + postcommit acceptance/rejection audit | [#14462921635](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/44379553187/artifacts/14462921635) | **2,669** | `55acd0734e0d9305c25ff0b11d82a7dc1f0db7438ac8aeed9d0769479ed3a1aa` |
| Actual raw postcommit accepted Eistute/Book NDJSON, original native stderr with all gate evaluations, original source and config SHA reports | [#14462986643](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/44379553187/artifacts/14462986643) | **281,589** | `79b6017bcd07764476b44ca59925a17d42b32a5d731b4995b86cb362895c9a96` |

The accepted original NDJSON source SHA-256 values are still:
Eistute
`57eaa949e382aee4537325e7214694fc250d1cf20eeec96beeb6f923f6b518e6`,
Book
`e5be7af26f0064a01929e33f7db9129a50a17959d20d743f09c224551358524a`.
The original C++ output is unchanged by research trace:
all 38 OFF/ON scientific output source files remain
byte-for-byte identical.

### Next research sequence, no invented LOD

**R2.7.24:** Audit Eistute source step-4 transition and quality
mechanisms, and why local retries produce indistinguishable
recorded scores. Use a preregistered *bounded configuration
sensitivity study*, varying only legitimate original generation
controls while retaining the untouched C++ acceptance policy,
source model SHA, precise configuration SHA and full attempted
vs independently committed ancestry. **Changing legitimate
generation controls still creates a different experiment from
the original article configuration, and its accepted steps
cannot be mixed across separate runs.** Apply separate
Book analysis to the actual Mode-0 error increase.

**R2.8 geometric LOD stays BLOCKED:** no second genuine
postcommit accepted epoch within a single original source
model/run; no independently qualified cross-epoch face or
curve ancestry; no continuous source-surface error bound
and no physical Windows GPU present/RSS/VRAM qualification.
No C++ scientific acceptance-policy modification, source
mesh rewrite, physical welding, `main` merge, tag
or release. PR #239 remains draft/unmerged.
