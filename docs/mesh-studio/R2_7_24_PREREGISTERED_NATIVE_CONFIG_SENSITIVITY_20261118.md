# Mesh Studio R2.7.24 — predeclared single-factor native C++ configuration sensitivity

**Preregistration date:** 2026-11-18. **Branch:** `feature/mesh-studio-r27-bvh-20261116`; **PR #239:** research draft, not merged. **Evidence classification:** separate exploratory parameter treatments; *not* article-replication results and *not* a new geometric LOD.

## Scientific hypothesis and experimental controls

R2.7.23 established why the original article configurations cannot
currently support two genuine accepted epochs: Eistute native step 4
lowered the estimated error by 83.86%, but failed actual active
stable-Mode-0 transition-coherence, imbalance and triangle-quality
criteria. Book native steps 2 and 3 increased the estimated error by
300.43% under the nonstable Mode-0 policy.

The original native generator's expression
`score_ok || small_mesh_progress_override`, its policy configuration
parsing, the C++ accepted scope's `Commit()` behavior, original mesh
input files, and original article configurations are **not** edited.

The experiment tests only whether **source-side generation controls**
(not acceptance thresholds) influence the observed candidate
quality, transitions and number of genuinely accepted commits.
Two separately executed models or two different configuration
processes are **never** spliced into a false two-epoch history.

### Exactly two predeclared treatments

| Trial ID | Original model and control | Exactly one changed generation control | Original → exploratory value | Causal hypothesis, not expected outcome |
| --- | --- | --- | --- | --- |
| `eistute_curve_growth_stepn_half` | `configs/eistute/article.conf`, model `input_models/eistute2.fixed.bp` | `CURVE_POINT_GROWTH_STEPN` | **4.0 → 2.0** | Reduce post-first-step curve point budget so native step-4 refinement may avoid severe between-patch transition imbalance and weak TRI elements |
| `book_adaptive_intensity_half` | `configs/book/article.conf`, model `input_models/book_v7a.bp` | `ADAPTIVE_INTENSITY` | **0.02 → 0.01** | Reduce generation intensity to determine whether the nonstable Mode-0 step-2 candidate error increase can be avoided |

These treatments were selected **before** obtaining their empirical
native outcome report. A zero- or single-accepted-epoch outcome is a
valid *negative experimental finding*, not a failed research purpose.
Further parameter exploration, if justified, must be labelled
as a subsequent separate treatment and source commit, not quietly
inserted into this two-trial matrix.

**Exact original Git-blob source controls**:
Eistute article configuration
`bd368dbad5b61515106b5d74d28cbde159780cd6`;
Book article configuration
`d88116054728311df74a6ece1d38d0cd23a64466`.
The original model SHA-256 values and compiled C++ executable SHA
are recalculated at runtime from the independently accepted
R2.7.12 original source records. Every variant intention configuration
must differ from the article configuration by **exactly one**
recorded line. The actual execution configuration differs additionally
only in two isolated I/O path selectors: absolute
`INPUT_MODEL` (same byte-hash source input) and a disposable
absolute `OUTPUT_PREFIX` (no original project output overwrite).

## Execution and evidence isolation

`tools/mesh_studio/native_controlled_sensitivity.py` runs the
**same actual C++ serial research instrumented generator executable**
twice, once per original model. Each process has a unique temporary
output directory and a unique accepted-source sidecar directory.
It records:

- Exact original article Git-blob and SHA-256, one-line variant
  configuration bytes and SHA-256, full resolved execution config
  and SHA-256, original native model byte hash and exact executable hash.
- Complete original C++ stdout and stderr, including the R2.7.23
  acceptance predicate vector for each real native
  `(step, retry)`, plus R2.7.18 adapter provisional
  boundary-close telemetry when present.
- Every **actually accepted** native per-face TRI NDJSON sidecar,
  independently checked for original patch/curve source topology,
  native patch-local node IDs, finite XYZ/UV, a typed outer
  accepted scope, native step/retry and SHA-256. A rejected
  candidate cannot enter this folder as an accepted epoch.
- Original C++ `real_generator_outcomes` accepted/restored counts
  crosschecked against all positive precommit decisions,
  independently accepted sidecar steps and rejected/restored
  step groups.
- An explicit boolean for **at least two real postcommit
  accepted steps *within this one treatment process***,
  which is distinct from any potential cross-process
  comparison or original article run.

The underlying `quad_generator_outcome_probe` research harness still
requires at least one accepted and one restored native step for a
successful process exit. A zero-accepted-step outcome would therefore
be retained only as raw nonzero-exit diagnostic logs and be marked
**unqualified**, not silently promoted to a valid certified
postcommit trial. The separate pure-python accepted-step auditor
supports zero receipts, but does not override the C++ harness contract.
A nonzero process error, missing original source bytes,
incomplete or inconsistent accepted sidecar, nonfinite
native gate, changed source model/configuration/acceptance
policy, or unaccounted retry causes a **fail-closed** outcome.

The independent `native_sensitivity_audit.py` reopens the
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

```bash
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
```

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
on lower error or on a `predicted_branch_accept_not_committed`
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

## Exact original C++ native results — source-verified negative sensitivity

The two separate preregistered exploratory treatments were
executed by the actual original serial C++ generator at tested
source/code SHA `196527356695b7a8d8b22ab7d58378bd173ef0e4`.
The independent native-source job is **SUCCESS** in
[Actions #44409265558](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/44409265558).
The final four-job certification status must include the hosted
Chromium job separately.

| Genuine source model | Original article control | Exact single-source treatment | Real accepted steps in treatment process | Real restored steps | Original actual accepted step-1 source |
| --- | --- | --- | --- | ---: | --- |
| Eistute | 1 accepted, 3 restored | `CURVE_POINT_GROWTH_STEPN=4.0→2.0` | **[1] only** | **3** | **1,168 native TRI; accepted NDJSON SHA unchanged** |
| Book | 1 accepted, 2 restored | `ADAPTIVE_INTENSITY=0.02→0.01` | **[1] only** | **2** | **4,256 native TRI; accepted NDJSON SHA unchanged** |

Both original accepted per-face NDJSON SHA-256 digests are
**byte-identical** to the original article controls:
Eistute
`57eaa949e382aee4537325e7214694fc250d1cf20eeec96beeb6f923f6b518e6`;
Book
`e5be7af26f0064a01929e33f7db9129a50a17959d20d743f09c224551358524a`.

The source-bound precommit native decision records were
**independently compared field-for-field against the
previous original R2.7.23 raw process logs**:
all **7/7** original Eistute records and all **3/3**
original Book records were identical. This includes error
ratios, quality and transition metrics, active acceptance
decisions and original restored outcome counts. The
comparison **does not prove that all rejected physical
candidate geometries are byte-identical** because their
full original TRI face snapshots were not committed, nor
does it prove the controls were not parsed. The runtime
configuration parser does parse both tested keys.

The exact variation intention config SHAs:
- Eistute:
  `2c8ed5bd89ecefcee98706e2b937a61542b92f33e7821e5fa015cc182e591e36`.
- Book:
  `db7011afc42e80198b22f105f4e5bf664599a7944c19a52a18a17b49f2b5bb40`.

Original native model input SHAs stay Eistute
`fdce4714524b88f536ec9f8eddc467e54e638dc6e765784ab68edc9a366a0a3f`
and Book
`3c4255cbd2f46bd2dce5f0e86b8e7ee9ac0c58df949d4563dd821deedcd8412d`;
the *same compiled original generator* SHA
`9227c49a65ede72a5229df5bf2ac4fd89ec1bd2b6a6e79f17eab6f3e96b7b67d`
was reused in both trial processes and in the original native
controls. The original article `.conf` files remain byte-unchanged;
`.gitattributes` explicitly enforces LF in those two files on
Windows and Linux, without normalizing arbitrary scientific sources.

The original compiled generator remains numerically identical
with lineage instrumentation OFF and ON: Eistute **21/21** and
Book **17/17** original scientific CSV/JSON/OBJ files exact
byte equality, **38/38 total**. Linux **379 tests, 4 optional
skips PASS**, Windows **379 tests, 10 environment skips PASS**.
These tests include 16 **synthetic negative contracts** that
cannot be used as positive experimental evidence.

### Research interpretation and mechanism to investigate next

**Negative result of the preregistered two-treatment matrix:**
neither changed generation control created two genuine
committed epochs. Do not cherry-pick restored attempts
or concatenate accepted original and variant snapshots.
Both variants are scientifically separate processes
from the original article run, despite equal source
input and original accepted face bytes.

One *plausible*, not independently proven,
masking mechanism for Eistute is found in
`GeneratorAdaptive::AdaptCurve()`:
the branch for
`BudgetDrivenAdaptation()==1 && CurvePointBudgetMode()==1`
uses the configured `CurvePointGrowthStepN()` cap
for steps 2+, but its final target may be increased by
priority-patch minimum increments, sensitive-curve
minimum increments and the source curve's geometric
spacing budget
`max(target_curve_points, geometric_target)`.
This can make the smaller configured cap nonbinding.
A future **read-only source effective-target trace**
should observe which exact floor dominates, not
assume a causal mechanism from equal final metrics.

For Book, nonstable `BuildAdaptivePolicyRuntime()`
still computes a policy intensity and step-one target
growth, but the source's nonstable element target
branch may use other explicit
`Step1ElementTargetGrowth()` /
`Step2ElementTargetGrowth()` values.
The *observed* unchanged precommit vectors do not
establish which policy knob dominates all downstream
adapter attempts. A future trace of the effective
target and per-patch source sampling budgets is required.
Book's nonstable execution also uses legacy step
count semantics rather than treating
`ADAPTIVE_MAX_STEPS=4` as an accepted epoch count.

The next investigation should measure **effective
generation controls and actual clamp/priority
contributions**, not silently loosen the native
acceptance policy. Even if a subsequent controlled
configuration obtains multiple genuine same-run
commits, R2.8 also requires cross-epoch native
face/curve ancestry and certified continuous
geometric error bounds.

### Source artifact identity

The actual R2.7.24 same-run original compiled
native experiment and independent audit artifact is
[GitHub Actions #14477052478](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/44409265558/artifacts/14477052478),
ZIP **291,251 bytes**, SHA256
`2b66604d5ca51800527fb050cdfd6ed69b9fb1ffbc5325db304eb03b9f1b5d94`.
It contains 14 original source-linked files:
the two precise variant intention and resolved
execution configs, two complete real process
stdout/stderr logs, both genuine per-face accepted
TRI NDJSON, two per-treatment reports,
the preregistered scope index and the separate
source-rebuilding independent audit.

The exact ZIP was archived in personal doctoral
Google Drive folder
`Doutorado/DOUTORADO_APMESH_ACOMPANHAMENTO/05_Experimentos_e_Resultados`,
then **downloaded back**. ZIP length and SHA256 were
independently verified byte-identical to GitHub.
Private Drive URLs are not placed in this
potentially public research repository.

## Outcome status

**Experiment preregistered in source. Actual experimental
outcomes and the exact source SHA remain pending
until all 4 CI jobs and the source-bound native artifact
can be checked.** Do not substitute guessed results.
