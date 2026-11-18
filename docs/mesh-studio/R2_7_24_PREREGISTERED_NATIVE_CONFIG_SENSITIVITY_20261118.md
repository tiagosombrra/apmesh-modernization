# Mesh Studio R2.7.24 — predeclared single-factor native C++ configuration sensitivity

**Preregistration date:** 2026-11-18. **Branch:** \`feature/mesh-studio-r27-bvh-20261116\`; **PR #239:** research draft, not merged. **Evidence classification:** separate exploratory parameter treatments; *not* article-replication results and *not* a new geometric LOD.

## Scientific hypothesis and experimental controls

R2.7.23 established why the original article configurations cannot
currently support two genuine accepted epochs: Eistute native step 4
lowered the estimated error by 83.86%, but failed actual active
stable-Mode-0 transition-coherence, imbalance and triangle-quality
criteria. Book native steps 2 and 3 increased the estimated error by
300.43% under the nonstable Mode-0 policy.

The original native generator's expression
\`score_ok || small_mesh_progress_override\`, its policy configuration
parsing, the C++ accepted scope's \`Commit()\` behavior, original mesh
input files, and original article configurations are **not** edited.

The experiment tests only whether **source-side generation controls**
(not acceptance thresholds) influence the observed candidate
quality, transitions and number of genuinely accepted commits.
Two separately executed models or two different configuration
processes are **never** spliced into a false two-epoch history.

### Exactly two predeclared treatments

| Trial ID | Original model and control | Exactly one changed generation control | Original → exploratory value | Causal hypothesis, not expected outcome |
| --- | --- | --- | --- | --- |
| \`eistute_curve_growth_stepn_half\` | \`configs/eistute/article.conf\`, model \`input_models/eistute2.fixed.bp\` | \`CURVE_POINT_GROWTH_STEPN\` | **4.0 → 2.0** | Reduce post-first-step curve point budget so native step-4 refinement may avoid severe between-patch transition imbalance and weak TRI elements |
| \`book_adaptive_intensity_half\` | \`configs/book/article.conf\`, model \`input_models/book_v7a.bp\` | \`ADAPTIVE_INTENSITY\` | **0.02 → 0.01** | Reduce generation intensity to determine whether the nonstable Mode-0 step-2 candidate error increase can be avoided |

These treatments were selected **before** obtaining their empirical
native outcome report. A zero- or single-accepted-epoch outcome is a
valid *negative experimental finding*, not a failed research purpose.
Further parameter exploration, if justified, must be labelled
as a subsequent separate treatment and source commit, not quietly
inserted into this two-trial matrix.

**Exact original Git-blob source controls**:
Eistute article configuration
\`bd368dbad5b61515106b5d74d28cbde159780cd6\`;
Book article configuration
\`d88116054728311df74a6ece1d38d0cd23a64466\`.
The original model SHA-256 values and compiled C++ executable SHA
are recalculated at runtime from the independently accepted
R2.7.12 original source records. Every variant intention configuration
must differ from the article configuration by **exactly one**
recorded line. The actual execution configuration differs additionally
only in two isolated I/O path selectors: absolute
\`INPUT_MODEL\` (same byte-hash source input) and a disposable
absolute \`OUTPUT_PREFIX\` (no original project output overwrite).

## Execution and evidence isolation

\`tools/mesh_studio/native_controlled_sensitivity.py\` runs the
**same actual C++ serial research instrumented generator executable**
twice, once per original model. Each process has a unique temporary
output directory and a unique accepted-source sidecar directory.
It records:

- Exact original article Git-blob and SHA-256, one-line variant
  configuration bytes and SHA-256, full resolved execution config
  and SHA-256, original native model byte hash and exact executable hash.
- Complete original C++ stdout and stderr, including the R2.7.23
  acceptance predicate vector for each real native
  \`(step, retry)\`, plus R2.7.18 adapter provisional
  boundary-close telemetry when present.
- Every **actually accepted** native per-face TRI NDJSON sidecar,
  independently checked for original patch/curve source topology,
  native patch-local node IDs, finite XYZ/UV, a typed outer
  accepted scope, native step/retry and SHA-256. A rejected
  candidate cannot enter this folder as an accepted epoch.
- Original C++ \`real_generator_outcomes\` accepted/restored counts
  crosschecked against all positive precommit decisions,
  independently accepted sidecar steps and rejected/restored
  step groups.
- An explicit boolean for **at least two real postcommit
  accepted steps *within this one treatment process***,
  which is distinct from any potential cross-process
  comparison or original article run.

A zero-accepted-step result is retained as such; no artificial
minimum-one-epoch rule is imposed on the exploratory treatment.
A nonzero process error, missing original source bytes,
incomplete or inconsistent accepted sidecar, nonfinite
native gate, changed source model/configuration/acceptance
policy, or unaccounted retry causes a **fail-closed** outcome.

The independent \`native_sensitivity_audit.py\` reopens the
raw retained native artifacts, recomputes the model/executable
and both config hashes, restores the one-line article config
identity, validates the resolved runtime config changed only
the two expected I/O fields, re-parses all original C++
gate vectors and actual native accepted per-face source
records, independently recomputes accepted/restored counts
and source step chronology, and refuses mixed-process
acceptance histories.

Original article replay evidence and 38-file ON/OFF
scientific byte parity remain mandatory **separate**
workflow gates. The exploratory trials are **not** used
to change the original Eistute/Book accepted source SHAs,
their figure outputs or their previous R2.7.12–R2.7.23
scientific certification.

## CI and archival contract

The existing native job compiles the original research-only
GeneratorAdaptive once and separately executes the real
article configurations and R2.7.23 source audit. Only
then may it execute these two predeclared source variations:

\`\`\`bash
python -m tools.mesh_studio.native_controlled_sensitivity \
  --exe build/r2712-native/bin/quad_generator_outcome_probe \
  --root . \
  --original-directory build/r2712-native-evidence \
  --out-dir build/r2724-controlled-native-treatment-evidence

python -m tools.mesh_studio.native_sensitivity_audit \
  --exe build/r2712-native/bin/quad_generator_outcome_probe \
  --root . \
  --original-directory build/r2712-native-evidence \
  --treatments build/r2724-controlled-native-treatment-evidence \
  --output build/r2724-controlled-native-sensitivity-audit.json
\`\`\`

The native job archives the exact original exploratory
trial intention/execution configs, full stdout/stderr,
actual accepted TRI sidecars, per-treatment source reports,
trial index and independent audit as one SHA-scoped Actions
artifact. The Linux and Windows Python jobs exercise
synthetic negative contracts only; they do not fabricate
C++ empirical results. All original R2.7.22 55 hosted
Chromium tests, original native source certification
and source-byte numerical parity continue to be
required, with no change to default P1/VTK/BVH behavior.

## Interpretation and scientific admission

The response variables are observed original C++
accepted and restored step counts, local retry
decisions, model-specific original error,
coherence/imbalance, quality and growth diagnostics
in each **distinct** treatment process.
No treatment is declared a success based merely
on lower error or on a \`predicted_branch_accept_not_committed\`
flag. The postcommit accepted sidecar is mandatory.

**Even if one treatment has two genuine accepted
steps, the scientific R2.8 LOD does not become
qualified automatically.** Original cross-epoch
native face/curve descendants, physical patch
compatibility, nonmanifold interface consistency
and a certified continuous source-surface
approximation error bound must be independently
established before making any LOD claim.

Physical Windows GPU-present, RSS, per-process
VRAM and native desktop qualification remain
open and must not be inferred from hosted CI.
The PR stays draft/unmerged, no main merge,
tag, release, C++ acceptance-policy change or
physical node welding.

## Outcome status

**Experiment preregistered in source. Actual experimental
outcomes and the exact source SHA remain pending
until all 4 CI jobs and the source-bound native artifact
can be checked.** Do not substitute guessed results.
