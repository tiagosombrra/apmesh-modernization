# Owned patch generation and refinement controls

Classification: engineering-only caller/configuration change supporting S3-05
and the bounded stage 6 engine boundary. Entry main is PR #148. GenerationContext
optionally owns 37 PatchGenerationConfig values for patch generation, refinement,
quality/history weighting, spatial eligibility and micro refinement. The factory
captures three RuntimeConfig fields and 34 current process values. Parsing,
validation, defaults and ApplyRuntimeConfig remain unchanged. No new key or
normalization policy is introduced.

The generator keeps raw context values and lazily creates a separate effective
copy. Three stable update operations retain the original 13 assignments, values,
order and positions: generation modes; stepwise/micro/spatial modes; then
refinement/coarsening strengths, error/quality weighting, top-count limits and
noneligible controls. Later updates preserve earlier changes. Contexts without
the group keep live global reads and original stable writes. Consumers in the
generator use nonallocating scalar accessors; sizing, ranking, filtering,
adaptation, smoothing and diagnostic expressions retain their original formulas.

The existing native metrics probe adds three bounded cases with 84 raw/84 stable
exact double representations and nine integer fields. It checks factory capture,
source mutation/retirement, foreign-global negative controls and separate raw/
effective state. Actual ComputePatchAdaptationFactors at steps 1/2 and
SmoothPatchAdaptationFactors on the existing two-patch model supply 36 matching
scalar outputs against the live legacy path before/after stable adjustments.
Foreign globals must change the legacy outputs in all three cases. This is a
focused unit-level differential, not a new scientific parameter matrix.

Require exact-head/main C++17 GCC/MSVC builds, 75 CTest entries/385 nested Python
controls, all prior native markers, the frozen nine-state/45-artifact/123-boundary
reference and real MSVC invalid/analytic CLI controls. Source reversal restores
the complete generator body modulo the 37 settings and three original assignment
blocks. Parser/apply/defaults and other production remain unchanged. Analyze
each actual production compilation command once plus the existing probe command,
with unchanged flags. Explicit formatting is independently token-checked;
inventory/contracts, staged identity and remote gates remain mandatory.

The initial foreign-control setup selected the discrete branch and failed its
required output difference. That failure is retained; only its mode changes to the
existing continuous branch, with production and exact oracles unchanged.

Patch consistency, acceptance and other numerical/runtime controls remain shared.
Scientific formulas, ordering, boundary synchronization, quadtree/templates,
selection, reconstruction and acceptance/stopping policies are preserved. Stage 3
and stage 6 remain open. No full-generation reuse/recovery, concurrency, parallel,
complete-process memory or external ABI guarantee follows; calls remain serialized
and consumers must rebuild for layout changes. No model, native target or
instrument campaign is added. The [compact record](stage3/patch_generation_context/summary.json)
and local build/patch-generation-context reports retain commands and identities.
