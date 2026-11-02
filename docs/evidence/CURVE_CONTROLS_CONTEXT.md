# Owned curve discretization and point budget controls

Classification: engineering-only caller/state ownership change supporting S3-05
and the bounded stage 6 engine boundary. Entry main is PR #146. GenerationContext
optionally owns 17 CurveControlsConfig values: adaptation policy/blend/sensitivity,
step-two sensitivity and efficiency, six point-budget/growth/blend/bound controls,
four consistency controls and the two discretization factors. The factory copies
nine RuntimeConfig fields and eight process values. Parsing, validation, defaults
and ApplyRuntimeConfig are unchanged, including differing loaded/raw step-N growth.

External/internal factors are captured independently. The internal runtime value
was initialized from a square root once; changing the external factor later did
not update it. This lot preserves that pair instead of silently recomputing it.
The typed config's default pair retains the original default expression. Adapter
observes the existing stationary context for curve and domain factor reads, with
the same owner/observer lifetime contract. Those factors do not change in the
two stable-mode updates, so Adapter's raw pair agrees with effective settings.

Point-budget and curve-consistency modes become 1 at their original distinct
locations. A shared optional instance copy preserves the first update when the
second occurs, while raw context stays unchanged. Nonallocating scalar accessors
feed the original weighting, growth, regularization, point budget and report
expressions. The point-clamp body moves to a member method called by the existing
lambda, preserving max/min order even for inconsistent direct-caller bounds.
Synchronization, point publication, transaction/rollback, IDs and scientific
selection/acceptance/stopping remain unchanged.

Without curves, default and prior partial contexts retain live global reads and
the two mode writes. Snapshots intentionally survive later source/global changes.
Other patch/quadtree/global controls still require serialized execution. Layout,
copy and allocation timing may change; no stable external ABI or allocation-failure
equivalence is claimed.

The existing native metrics probe checks three raw cases: 33 raw/33 stable exact
double representations and six integer fields survive source retirement and
foreign globals. Intermediate/final mode controls detect lost prior updates.
Actual point limiting preserves 18 integer outputs, and 12 owned Adapter double
observations retain the independent pair. The foreign legacy path must differ;
default/identity-only callers retain their global writes. The friend fixture
observes the actual private functions without adding production test switches.
Prior native and metric oracles stay unchanged. No model or instrument is added.

Require exact-head/main C++17 GCC/MSVC builds, 75 CTest/385 nested Python controls,
the frozen nine-state/45-artifact/123-boundary comparison, real MSVC CLI controls,
scoped analysis, explicit format/whitespace, inventory/contracts and staged/remote
gates. Complete source reversal preserves generator/Adapter formula/order/literal
tokens modulo named reads, original mode assignments and point-limiter boundary.
Parser/apply/defaults/other production and scientific inputs stay unchanged.
Preparation corrections for marker formatting and source reading are retained
locally; they do not change production formulas or equality oracles. The [compact record](stage3/curve_controls_context/summary.json)
and local build/curve-controls-context retain source, commands, hashes and results.

Broader curve parameter domains, independently configured complete generations,
recovery, concurrent/parallel execution, complete-process memory and Stage 3/6
closure remain unqualified.
