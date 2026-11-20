# Mesh Studio R2.7.28 — certified original Adapter local patch CSV comparison

**Status: 4/4 original-source scientific CI jobs PASSED**, exact original generator code commit `b30fe96dab1f4b8d213ccd87f543350174d6ae3e`, [GitHub Actions #44436886832](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/44436886832), completed 2026-11-19 UTC. Original compiled serial C++ postcommit lineage + two separate source/variant CSV captures + independent raw-file auditor: **PASS**. Linux **434 Python tests (4 permitted skips)**, Windows **434 Python tests (10 environment-specific skips)**, actual hosted Chromium **55 passed**. Hosted Chromium does **not** establish Windows physical GPU-present, RSS or VRAM.

This report was written **after** preregistration in [R2.7.28 protocol](R2_7_28_PREREGISTERED_EXISTING_ADAPTER_PATCH_CSV_20261119.md) and explicit preserved corrections in [R2.7.28A](R2_7_28A_ORIGINAL_LOCAL_PRECOMMIT_SCOPE_ADDENDUM_20261119.md), [R2.7.28B](R2_7_28B_ORIGINAL_REPEATED_LOCAL_SCOPE_MULTIPLICITY_20261119.md). **No generation-code change, acceptance-policy change or new scientific parameter trial occurred.** The two processes replay exactly the original article config and the earlier R2.7.26 preregistered `CURVE_POINT_MIN:11→13` one-factor variant, respectively, on the same unmodified original CAD model and same compiled C++ binary.

## Subsequent scientifically material metric-meaning correction (R2.7.29)

**This 2026-11-19 correction does not rewrite any R2.7.28 observations or previous source hashes.** The separately preregistered, actual compiled C++ source re-audit [R2.7.29](R2_7_29_ORIGINAL_AFT_TRANSITION_CLASSIFIER_FINDINGS_20261119.md) established that original `aft_stats.transition_element_ratio` means **the percentage of nonboundary triangles with edge-length max/min >1.8**, counted over total faces at the AFT stage-1 capture. It does **NOT** directly mean the spatially classified region near a boundary. Separately generated `transition_elements` counts faces with **near-boundary UV position OR elongation**, by a distinct Adapter regional classifier on the generated mesh. The source step-4 mean ratios were **4.04% / 5.66% AFT stage-1 elongated faces** versus **29.50% / 34.50% spatial-or-elongated regional faces** in original/variant respectively. All 64 step-4 original and all 64 variant local observations had *regional ratio above the numerical AFT transition floor* while remaining **below** the floor under the actual source AFT shape ratio.

Therefore historical wording in the R2.7.28 text suggesting an independently proven **missing physical transition band** should be read as **the source's own elongated-face AFT transition gate being unsatisfied**. This factual distinction is necessary before interpreting adaptive quality, designing an AFT intervention, or asserting any source-interface conformity claim. The R2.7.28 original native 4/4 CI, all measurements and original SHA attestations remain unchanged; R2.7.29 native audit passed, but its Linux GitHub mirror returned external HTTP 503 during installation, so no four-job R2.7.29 certification was claimed at the time this note was authored. Neither result qualifies R2.8 scientific LOD.

## Authoritative real source evidence

- [Raw R2.7.28 Actions artifact #14488883051](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/44436886832/artifacts/14488883051) contains **16 files**: retained original/variant CSV, full real original C++ stdout/stderr, source intention/resolved I/O configs, genuine native accepted TRI sidecars, separate reports, capture index and independent JSON audit. Whole original ZIP **175,418 bytes**, SHA-256 `77b81c52c9e059dce7002abb99d55ce340d0afd87bd12640c701420b9cf6667d`. Uploaded to existing **personal doctoral Google Drive experiments folder** `Doutorado/DOUTORADO_APMESH_ACOMPANHAMENTO/05_Experimentos_e_Resultados`; downloaded again and SHA-256 plus size verified byte-for-byte. Private personal Drive file URL intentionally not included in public repository.
- Original Eistute existing C++ `<OUTPUT_PREFIX>_domain_adaptation.csv` SHA-256 `abffa8ff24699b636be5feb6285105b5e10128ad15b467e2704ba756d98e26d5`: **104 original local observation rows**. `CURVE_POINT_MIN=13` isolated C++ variant CSV SHA-256 `2b2dd1e50a4f924282ece4a05391a3b6b69fc11c5f35cd31044a421ff9f29de9`: **112 rows**. Both bound to their own full raw original `R2718_ADAPTER_BOUNDARY_CLOSE` source-event tuple **multisets** and actual native `R2723_NATIVE_ACCEPTANCE_GATE` events.
- Original step 1 source accepted TRI: **1,168 faces** and native face NDJSON SHA-256 `57eaa949e382aee4537325e7214694fc250d1cf20eeec96beeb6f923f6b518e6`. Separate min13 variant source accepted step 1 TRI: **1,400 faces**, NDJSON SHA-256 `bd04a32e362bd54d72d1c402df9160834d18c074c2862f071073cd9f94ec513d`. These exactly match the earlier independently certified R2.7.12/R2.7.26 source-accepted face bytes. They are NOT two accepted steps within a process: each actual source C++ process accepted only **[1]**, then restored/rejected **three** later global steps.
- Original `src/adapter/adapter.cpp` Git blob `78f821411f33a8ca7594c8e357bbe4a79e5d33f9`, original `src/generator/generator_adaptive.cpp` Git blob `844673ea764f3092330e5e9ebb01d8eb339869bc`, source `src/application/runtime_state.cpp` Git blob `d21ceb3397c7825bb50534be072261908c9b0e49`; no C++ source edits. Original research/study config byte identity and exact executable SHA are additionally enforced by the independent auditor.

## Observed original C++ local patch attempt metrics (NOT accepted TRI counts)

Aggregates from raw per-local-attempt CSV **including genuine repeated tuple observations**, not from synthetic test fixtures. Ratios/floors are dimensionless; values rounded here for presentation, retained original CSV keeps its full original C++ precision.

| Eistute native original Adapter metric | Original article | Existing min13 variant |
| --- | ---: | ---: |
| All local CSV rows, steps 1–4 | **104** | **112** |
| Step 1 local rows / underresolved | 24 / 0 | 24 / 0 |
| Step 2 local rows / underresolved | 8 / 0 | 8 / 0 |
| Step 3 local rows / underresolved | 8 / 0 | 16 / 0 |
| Step 4 local rows / underresolved | **64 / 64** | **64 / 64** |
| Step 4 mean `internal_element_ratio` | 0.916519 | 0.887488 |
| Step 4 mean `transition_element_ratio` | 0.040383 | 0.056619 |
| Step 4 mean `transition_floor` | 0.204313 | 0.195917 |
| Step 4 mean **transition deficit** (`floor - ratio`) | **0.163930** | **0.139298** |
| Step 4 mean `interior_transition_imbalance` | 0.297189 | 0.258042 |
| Step 4 locally observed `generation_status` | **64/64 `curve_transition_needs_retry`** | **64/64 `curve_transition_needs_retry`** |
| Native postcommit accepted steps inside this ONE run | **[1]** | **[1]** |
| Genuine step 2–4 global restored outcomes inside this ONE run | **3** | **3** |

Each step-4 run has **16 original CSV candidate observations per CAD patch (patch slots 0–3)**, and **every one of the 64 observations** in each process is structurally sub-resolved. Original step4/retry0 contributes 16 rows total and retry1 contributes 48 rows, due to original repeated local `(step,retry,patch,local_attempt)` scopes. The raw C++ `R2718` events independently exhibit identical repeated tuple counts. An internally repeated local record is not a fresh globally committed epoch.

The source original `IsTransitionUnderresolved` is exactly the conjunction of **`internal_element_ratio > 0.66`** with **`transition_element_ratio + 1e-9 < transition_floor`**. Each step-4 row satisfies both. The source `ComputeInteriorTransitionImbalance` is independently recomputed with original ostream decimal-rounding tolerance. No step-4 source or variant row is numerically borderline at the structural flag threshold.

Relative to source, the previous min13 variant lowers the **mean step-4 transition deficit 15.03%**, lowers local mean interior imbalance **13.17%** and raises mean transition-element fraction **40.20%** relative (from a small 0.040383 starting value). Nevertheless **100% of local observations remain flagged**. This is direct evidence of insufficient transition-band formation at original late step 4 *under these particular configurations*, not evidence of a universally optimal transition-band parameter.

## Original local-vs-global acceptance discipline

The actual serial C++ emits **8 Adapter outer `(step,retry)` scopes** but only **7 global R2723 gate attempts**. The Adapter-only **`(1,1)`** scope is an authentic early local preview without a corresponding native global acceptance decision. It is preserved in the CSV and never counted as a global commit/rejection. Original R2718 boundary events have genuine repeated 4-field identities: **104 events / 72 distinct tuple keys** in the article process, **112 events / 80 distinct keys** in min13. An independent **multiset equality**, not a false unique-tuple constraint, verifies original local CSV scope; the displayed per-tuple observation ordinal does **not** manufacture original C++ unique IDs or a selected fallback witness.

The original generator's **actual selected-patch aggregate** for the rejected step-4 global candidates still reads `underresolved_transition_fraction=1.0` and `transition_coherence_ok=false`. This is separately source-bound to the real native R2723 stderr. All 4 selected CAD patch slots are thus flagged at that step by the source-defined full-patch denominator, but the CSV local observations **cannot identify which fallback attempt was finally selected for each patch** from their key alone. The study does not infer per-candidate acceptance, shared physical welding, new TRI ownership, per-face cross-epoch ancestry or continuous surface error guarantees.

## Next scientifically controlled phase

Proceed to **R2.7.29 as a new preregistered observational/mechanistic study**, not silent tuning: instrument or independently cross-validate the exact original AFT/Quadtree source's **transition-band vs interior generation behavior** in Eistute step4, including the selected candidate's actual per-patch structural ratios and origin of local retry flags. Prefer already-existing source-bound log/observer channels and prove source OFF/ON numerical parity before any new instrumentation. Only after identifying a mechanism consider one bounded parameter trial **pre-registered separately**. Do **not** relax `score_ok || small_mesh_progress_override`, alter stable acceptance limits, pool processes into epochs or enable geometric LOD. Physical Windows GPU-present/RSS/VRAM also remain unqualified.

**Scientific classification:** R2.7.28 observed per-patch source-local measurements; **R2.8 scientific LOD BLOCKED**. PR #239 stays **DRAFT** and unmerged; `main` is unchanged.
