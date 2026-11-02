# Owned element budget controls

Classification: engineering-only caller/state ownership change supporting S3-05
and the bounded stage 6 engine boundary. Entry main is PR #145. GenerationContext
optionally owns ElementBudgetConfig with 32 controls: eleven step budget/pressure/
retry controls, six patch-local limits/scales, four growth-mode/scale controls,
five budget-driven/target controls and six patch-allocation controls. Int modes
and double count/ratio/weight/scale units retain their original semantics/defaults.

The factory samples the current process values. These controls had no RuntimeConfig
fields/parser keys; none are added. A typed caller may explicitly set element_budget
before constructing the generator. Existing configuration parsing, validation,
ApplyRuntimeConfig and global initializers stay unchanged. Factory snapshots
deliberately retain values across later source/global changes.

At the original stable-mode location, separate effective instance state receives
the same five ordered writes: budget-driven, target mode, growth-target mode and
patch allocation become 1; patch top-k-only becomes 0. Raw context values stay
unchanged. Nonallocating scalar accessors feed existing step limits, pressure,
retry scaling, growth targets, local budgets and allocation expressions, including
their reporting and curve-coupling uses. The existing target-clamp function takes
explicit effective bounds through a member wrapper, preserving its arithmetic.
Budget counters, pressure and current targets remain in their existing members.

Contexts without element_budget keep live global reads and the original five
stable writes. This includes default and prior partial contexts. Curve-point,
quadtree, patch-generation and refinement controls remain outside this lot and
shared execution remains serialized. No formula, threshold, acceptance/retry rule,
expression order or diagnostic changes. Layout/copy/allocation timing can change;
no external ABI or allocation-failure equivalence is claimed.

The existing native metrics probe checks three raw cases: 72 raw and 72 stable
exact double representations plus eight integer fields. Owned settings survive
source retirement and conflicting globals. The real target limiter preserves
18 exact output representations before/after stable overrides, while the foreign
legacy path must differ. Owned adjustments preserve raw config and foreign state;
default/identity-only callers retain the five global writes. The original control
failed because its legacy stable path retained the foreign raw configuration:
only five modes are overridden. Failure source, message, process/binary identities
are retained; restoring the same raw case fixes setup without changing equality
or target oracles. No scientific model was run in that failed control.

Require exact-head/main C++17 GCC/MSVC builds, 75 CTest/385 nested Python controls,
the frozen nine-state/45-artifact/123-boundary scientific comparison, existing
MSVC CLI negatives/analytic controls, scoped analysis, explicit format/whitespace,
inventory/contracts and staged/remote gates. Source reversal preserves complete
generator formula/branch/order/literal tokens modulo the named reads, five exact
stable assignments and target bounds. Other production, parser/apply/defaults and
scientific inputs stay unchanged. The [compact record](stage3/element_budget_context/summary.json)
and local build/element-budget-context retain source, commands, hashes and results.

Unit cases do not qualify a new complete-generation parameter matrix. Recovery,
concurrent/parallel execution, complete-process memory and Stage 3/6 closure
remain unqualified. No test target, scientific model or instrument campaign is added.
