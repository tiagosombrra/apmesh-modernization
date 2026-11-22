# Mesh Studio R2.7.29 — genuine original C++ classifier discrepancy, source-bound audit

**Status (2026-11-19):** Original compiled serial C++ native + independent fail-closed source provenance audit **PASS**; Windows **445 Python tests PASSED, 10 expected environmental skips**; Linux host did **not** reach Python tests because Ubuntu APT repository returned HTTP **503 Service Unavailable** for original OpenGL packages; the same-run browser job was still processing when this report was first authored. **DO NOT claim 4/4 workflow success from this run.** Exact analyzed source-code SHA `e8c4fa099e95477d293e4f6d74991f0cb6b09ff8`, [Actions #44520562326](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/44520562326). The first original R2.7.28 4/4 CI [#44436886832](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/44436886832) remains fully certified for all genuine C++ input source bytes, with **434 Python tests** and **55 hosted Chromium tests** at its own exact code SHA.

This result follows, without changing, the prior preregistration [R2.7.29](R2_7_29_PREREGISTERED_ORIGINAL_AFT_TRANSITION_SEMANTICS_20261119.md) and prior source-native [R2.7.28 original local CSV evidence](R2_7_28_ORIGINAL_EISTUTE_PATCH_CSV_RESULTS_20261119.md). R2.7.29 adds **one read-only source semantic auditor and synthetic negative test module**, no modification to any C++ generator, AFT numerical policy, original CAD input, acceptance gate, original source config or visual renderer.

## Rerun status — original GitHub Actions attempt 2

On [run #44520562326, rerun attempt 2](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/44520562326/attempts/2), the previously failing Linux job **PASSED all 445 Python regressions, with four optional skips** after the APT mirror recovered. Windows still **PASSED 445 tests, ten environmental skips** and the true original C++/independent R2.7.29 numeric source-audit job remains **PASSED**. The hosted Chromium job was still running its external dependency installation during this update; **4/4 full workflow success is not asserted pending its final result**. Original test code SHA `e8c4fa099e95477d293e4f6d74991f0cb6b09ff8` and source-scoped research bytes are unchanged. This update does not rewrite the failed first attempt or confuse the external APT mirror outage with a scientific result.

## Critical original-source distinction

The original native `AdvancingFront::ComputeStageFaceStats` (source `src/crab_mesh/aft/advancing_front.cpp`, immutable Git blob `1bd430d1bd1079e6f55f3bc7488ff9313e4bb82b`) computes **stage-1, post-AFT** `transition_element_ratio` as a count over ALL source faces of **nonboundary TRI whose maximum/minimum edge-length ratio exceeds 1.8**, determined by a pointer-based edge incidence map. A shape-regular interior triangle is NOT called a transition face by this AFT classifier merely because it lies near the boundary. `internal_element_ratio` counts the other nonboundary faces. The three original stage-1 proportions `boundary_element_ratio + transition_element_ratio + internal_element_ratio` sum to approximately one.

In contrast `Adapter::ComputeRegionalPatchStats` (source `src/adapter/adapter.cpp`, immutable Git blob `78f821411f33a8ca7594c8e357bbe4a79e5d33f9`) computes **post-generation regional face counts**: a nonboundary face is called a region-of-transition face if **either** its UV centroid is within a local target-size-dependent near-boundary width (`0.08–0.32` in normalized patch UV coordinates) **OR** its edge aspect ratio is greater than `1.8`. This regional classification uses UV-coordinate edge grouping rather than the AFT's pointer incidence, and is calculated separately after obtaining the generated mesh. These are therefore **distinct classifiers, potentially distinct stages and distinct edge-incidence semantics**. They cannot be numerically interchanged, even when by coincidence their proportions would be equal in an isolated row.

The original **local retry** criterion is based on **the AFT stage-1 shape ratio**, *not* `transition_elements/generated_faces` from the separately named regional statistics:

```cpp
const bool interior_dominant = aft_stats.internal_element_ratio > 0.66;
return interior_dominant &&
       (aft_stats.transition_element_ratio + 1.0e-9 < transition_floor);
```

The unmodified `PatchNeedsFallback` includes this `IsTransitionUnderresolved` as an **OR clause**, so an original shape-metric violation is by itself sufficient to request another local attempt, regardless of the differently defined regional count. The original C++ status is `curve_transition_needs_retry` if this underresolution flag is true, provided the original patch fallback condition holds. The subsequent original C++ global acceptance predicates remain separate.

## Independently re-opened real source-local Eistute findings

The R2.7.29 original compiled native CI job actually re-ran both independent Eistute C++ processes on original accepted source models, retained original C++ stdout/stderr and accepted-face sidecars, and **recomputed** the complete R2.7.28 independent audit before separately opening both original `_domain_adaptation.csv` files. The exact original source config/model/executable/accepted-face SHA checks remained valid.

| Original C++ step-4 source-local observation | Article Eistute | Existing min13 Eistute variant |
| --- | ---: | ---: |
| Original local Adapter CSV rows (all steps) | **104** | **112** |
| True original step-4 local observations | **64** | **64** |
| Mean source AFT stage-1 nonboundary elongated TRI fraction | **0.0403832375** (4.04%) | **0.0566191625** (5.66%) |
| Mean later regional spatial-or-elongated TRI fraction | **0.2950029440** (29.50%) | **0.3450277192** (34.50%) |
| Mean regional-minus-AFT fraction (percentage points) | **25.46 pp** | **28.84 pp** |
| AFT shape-fraction values meeting their respective original `transition_floor` | **0 / 64** | **0 / 64** |
| Separately classified regional-fraction values exceeding the same numerical floor | **64 / 64** | **64 / 64** |
| Original source C++ `transition_underresolved=1` local observations | **64 / 64** | **64 / 64** |
| Source accepted C++ steps IN THE SAME process | **[1]** | **[1]** |
| Globally rejected/restored original C++ steps | **3** | **3** |

The region-fraction count is **descriptive contrast, NOT a counterfactual accepted gate**. Replacing the actual shape ratio by the regional fraction in the unchanged C++ predicate has **not** been implemented and would in any case leave other, independently failing original global acceptance predicates. These are separate source-versus-variant executions, **not** two original accepted adaptive epochs.

**Scientific conclusion warranted by these bytes:** the original late-step structural retry condition is evaluated against a fraction of **elongated nonboundary stage-1 faces**, not against the spatial transition-band coverage the metric name may suggest. The original source therefore can report `transition_underresolved` even when a substantial fraction of faces is regionally classified as boundary-adjacent-or-elongated. This resolves an important semantic ambiguity in the previous R2.7.27/28 descriptive reports. It **does not prove** which physical transition topology, geometry or numerical sampling algorithm is defective, nor that a different predicate would be correct. A proposed requirement for a minimum fraction of elongated triangles could conflict with some shape-quality goals, but that is a **testable hypothesis**, not a validated defect or justification to relax source acceptance criteria.

**Earlier wording correction:** the previous phrase *insufficient geometric transition band* is too strong when derived only from `aft_stats.transition_element_ratio`. The correct evidence is **insufficient fraction of elongated nonboundary TRI under the original AFT classifier**. Spatial coverage, interface conformity and mathematical quality still require their own independently qualified definitions.

## Preserved native forensic chain

- Native source AFT blob `1bd430d1bd1079e6f55f3bc7488ff9313e4bb82b`, Adapter blob `78f821411f33a8ca7594c8e357bbe4a79e5d33f9`, GeneratorAdaptive blob `844673ea764f3092330e5e9ebb01d8eb339869bc`; preregistration original Git blob `7b0da51d3e17578b7b3fc808e554d58e8d241679`. No scientific C++ code or original acceptance policy modifications.
- Original Eistute genuine per-local CSV SHA-256 `abffa8ff24699b636be5feb6285105b5e10128ad15b467e2704ba756d98e26d5`; separate preregistered min13 variant original source CSV SHA-256 `2b2dd1e50a4f924282ece4a05391a3b6b69fc11c5f35cd31044a421ff9f29de9`. Both corroborated by the original already-archived R2.7.28 complete native ZIP SHA-256 `77b81c52c9e059dce7002abb99d55ce340d0afd87bd12640c701420b9cf6667d`.
- New [original native R2.7.29 source-classifier report Actions artifact #14528391114](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/44520562326/artifacts/14528391114): **2,778 bytes**, whole original ZIP SHA256 `a7608c4fec7504921631c700c7b5972fa4b8c57290ebacc693ec14a2051b546f`. The JSON's source-attested original and variant reaudits and 64/64 per-source comparisons passed the compiled C++ native job. Uploaded to the user's existing **personal doctoral Google Drive** folder `Doutorado/DOUTORADO_APMESH_ACOMPANHAMENTO/05_Experimentos_e_Resultados` and independently downloaded and SHA256-verified bytewise. The filename explicitly marks **Linux APT 503** to avoid presenting partial CI as four-job PASS. Personal Drive URL deliberately omitted from public repository document.
- The R2.7.29 CI Linux job failed **before regression tests** on transient HTTP 503 from Ubuntu APT mirrors while installing `libegl1`, `libosmesa6` and related OpenGL libraries. This was **not** a Python assertion, Windows regression failure, failed generator source audit or source numerical mismatch. Re-run this one failed job when possible; do not publish a 4/4 certification unless it actually completes successfully.

## Future research boundary

Next R2.7.30 must be a **new prospective, preregistered** study before numerical intervention: define a spatial and topological transition-quality observable with source-face/curve continuity and direct selected-local-candidate provenance, test it against both original source and min13 real C++ outputs, and determine if the AFT shape-classifier's implicit elongated-fraction preference is scientifically appropriate. The source must still honor global acceptance gate, exact OFF/ON numerical parity, original postcommit face ancestry and rigorous geometric error conditions. Do not silently change the acceptance predicate to force a second epoch.

**Nonclaims:** no accepted two-stage native TRI mesh, no cross-epoch welding, no continuous source-surface error bounds, no physical Windows GPU-present/RSS/VRAM qualification. **R2.8 scientific LOD remains BLOCKED, PR #239 DRAFT and main unchanged.**
