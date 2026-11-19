# Mesh Studio R2.7.27 — observed original Eistute step-4 transition-coherence obstruction

**Scientific scope:** original serial C++ native Eistute source and separately preregistered `CURVE_POINT_MIN 11→13` variant. These source bytes and accepted postcommit sidecars were independently validated by **all four successful jobs** of R2.7.26 [CI #44421753186](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/44421753186) on exact source-code commit `5f9eb7ca52804b0be79dafd38f4241aeae11c88b`. No new C++ numerical run was conducted for R2.7.27; [its prior forensic protocol](R2_7_27_ORIGINAL_TRANSITION_COHERENCE_FORENSICS_PROTOCOL_20261118.md) was committed before implementing the new independent auditor.

**R2.7.27 software qualification:** original compiled source and fixed raw observation data are genuine **R2.7.26-certified input**. The *new* R2.7.27 Python auditor and its fail-closed tests require a **separate passing GitHub Actions run** before being called CI-certified. Do not confound the two.

## Forensic question and proven numerical observations

The original `GeneratorAdaptive` source has an unmodified stable-mode step-4 conjunction:

- `stable_transition_ready = underresolved_fraction <= 0.25 && transition_imbalance_max <= 0.18`.
- `transition_coherence_ok = transition_penalty <= 0.42`.
- `transition_penalty = 0.55*Clamp01(underresolved_fraction) + 0.30*Clamp01(imbalance_mean/0.35) + 0.25*max(overshoot_ratio-1,0) + 0.10*Clamp01(curve_aux)`.
- Therefore all terms are nonnegative and **`transition_penalty >= 0.55*underresolved_fraction`**, irrespective of the omitted individual penalty components.

Actual R2.7.26 retained C++ source stderr `R2723_NATIVE_ACCEPTANCE_GATE` records, matched on step 4 and retry 0/1:

| Original source-generated measurement | Eistute original | Eistute single-factor min=13 |
| --- | ---: | ---: |
| Underresolved transition fraction, raw original CPP | **1.000000** | **1.000000** |
| Necessary penalty floor `0.55*fraction` | **0.550000** | **0.550000** |
| Actual coherence penalty | **2.066691338423361** | **0.9506125443945653** |
| Coherence cap, unchanged source | 0.42 | 0.42 |
| Actual maximum transition imbalance | **0.2975224485013183** | **0.059701563231568056** |
| Readiness cap for maximum imbalance | 0.18 | 0.18 |
| `transition_coherence_ok` | **false** | **false** |
| `stable_transition_ready` | **false** | **false** |
| `quality_gate_ok` | false | **true** |
| `stable_late_explore_accept` | false | **true** |
| Genuine second accepted C++ source TRI epoch | **NO** | **NO** |

**Interpretation:** the actual min=13 source variation improved the measured maximum imbalance enough to clear *that* readiness subcondition (0.0597 < 0.18), and changed quality and late exploratory flags, but left the actual underresolved fraction at exactly 1. The **1.0 fraction alone** therefore (i) violates the required `<=0.25` readiness fraction; and (ii) forces a coherence penalty of at least **0.55**, already strictly greater than its **0.42** cap. **Two necessary source acceptance predicates remain false regardless of any reduction in the other nonnegative penalty terms**. Both step-4 retries repeat these source values and **are not independent accepted epochs or independent statistical replicates**.

The original Eistute run additionally violated the max imbalance threshold (0.2975 > 0.18); that failure is absent in the variant, whose source still rejects step 4 for the independently sufficient underresolution obstruction. This does not show which specific CAD patches contribute to the aggregate fraction, how many eligible transition patches the denominator contains, or what change would be sufficient to obtain two same-run accepted epochs. The source records do not expose the necessary patch-level mapping.

Book `research_debug` is a **non-stable-mode control**: in this source mode the stable transition-coherence gate is bypassed even if the raw penalty is numerically large. Applying Eistute's step-4 caps to Book would produce a false diagnosis. The new independent R2.7.27 auditor explicitly checks the original source's mode-dependent bypass.

## Immutable source evidence and consequences

- Original generator Git blob: `844673ea764f3092330e5e9ebb01d8eb339869bc`. Original exact native precommit event parser Git blob: `f415a2f1410b1c41411aeebbc383d9497753cfd1`.
- R2.7.26 accepted source/variant run audit ZIP: GitHub Actions [artifact #14483101697](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/44421753186/artifacts/14483101697), ZIP SHA256 `d192f3a111bbac9bbaa0c8f96330ce7a959c00ba23f284c2ea668be53b3dd9e2`.
- R2.7.26 independently paired original same-run compiled C++ source ZIP: [artifact #14482777304](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/44421753186/artifacts/14482777304), ZIP SHA256 `04c35180afc0abb9412ad912c8965dfa514b5706d6ce69e10d55614f8666dccb`.
- Both artifacts are retained and bytewise verified after download from the personal doctoral Drive. The public repository report does not include private Drive links.

**Next research gate:** an optional read-only, source-attested per-patch transition observer would be needed to identify source *patch slots* that actually contribute to the underresolution fraction. It must be preregistered separately, retain OFF/ON numerical parity and original C++ postcommit acceptance, and not change source or production acceptance behavior. Not performed by this analysis.

**Nonclaims:** no causal sufficiency, no patched original generator, no acceptance-gate relaxation, no fake LOD from rejected candidates, no inherited across-run epochs, no certified cross-epoch native face/curve ancestry, no continuous source-surface error bound, no certified physical Windows GPU-present/RSS/VRAM. **R2.8 BLOCKED; PR #239 DRAFT, unmerged.**
