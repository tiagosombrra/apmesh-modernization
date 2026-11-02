# Owned patch and group consistency controls

Classification: engineering-only caller/configuration change supporting S3-05
and the bounded stage 6 engine boundary. Entry main is PR #149. GenerationContext
optionally owns 18 PatchConsistencyConfig values: equivalence tolerances,
neighborhood/group limits, budget/h/depth constraints, group controls and the
consistency contribution to acceptance. The factory captures current process
values. Parser, validation, defaults and ApplyRuntimeConfig stay unchanged.
The two dormant legacy controls remain stored without activating new behavior.

The generator retains raw context and lazily creates a separate effective copy.
Two original stable writes still set patch consistency and its acceptance mode
to 1, at their distinct positions around EnableCurveConsistency. The second
update preserves the first. Scalar getters supply the original grouping,
regularization, dispersion, penalty, report and acceptance expressions without
changing formulas, comparison order or literals. Missing settings retain live
global reads and the original writes. No observer or low-level tree change is needed.

The existing native metrics probe checks three bounded cases: 33 raw/33 stable
exact double representations, seven integer fields, source mutation/retirement,
foreign process values and intermediate/final effective modes. Actual
RegularizeEquivalentPatchBudgets on the existing native two-patch model at steps
2/3 supplies 144 matching outputs before/after stable updates: budgets, h,
depth caps, group IDs, dispersion, penalty and active status. Cases include the
disabled mode and minimum group size guard. Foreign controls must form an actual
two-patch group, clamp and change the outputs. Raw context and foreign process
settings stay unchanged by owned updates; identity-only callers retain writes.

Require exact-head/main C++17 GCC/MSVC builds, 75 CTest/385 nested Python controls,
all prior native markers, the frozen nine-state/45-artifact/123-boundary reference
and real MSVC invalid/analytic CLI controls. Source reversal restores the complete
generator body and the two assignment positions modulo explicit setting bindings.
Parser/apply/defaults and other production stay unchanged. Analyze actual canonical
production commands once each plus the existing probe, with unchanged flags.
Explicit formatting is independently token-checked. Inventory/contracts, staged
identity and remote gates remain mandatory. No model, target or instrument
campaign is added. The [compact record](stage3/patch_consistency_context/summary.json)
and local build/patch-consistency-context reports retain commands and identities.

Scientific formulas, ordering, boundary synchronization, quadtree/templates,
selection, reconstruction and acceptance/stopping policies are preserved.
The single-group unit check does not establish multi-group dispersion coverage
or a complete acceptance matrix. Other acceptance/AFT controls remain shared.
Stage 3/6, recovery/reuse, concurrency/parallel and complete-process memory
obligations stay open. Calls remain serialized; layout changes require rebuilding
consumers and introduce no external ABI guarantee.
