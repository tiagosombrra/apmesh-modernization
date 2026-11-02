# Owned quadtree limits and saturation controls

Classification: engineering-only configuration/lifetime change supporting S3-05
and the bounded stage 6 engine boundary. Entry main is PR #147. GenerationContext
optionally owns 19 QuadtreeControlsConfig values: saturation/hard saturation,
depth/cap/scale limits, negative-depth resolution and three quality thresholds.
The factory copies six RuntimeConfig fields and thirteen current process values.
Parsing, validation, defaults and ApplyRuntimeConfig are unchanged. Dormant
legacy flags remain stored without activating new behavior.

The generator initializes a separate effective value before moving its context.
The existing immovable owner keeps that value stationary. Adapter's additional
constructor observes it; the original default/one-argument constructors remain
valid. Four stable writes retain their original values/order/positions: cap mode
becomes 1, then face quality 0.40, low-quality factor 0.85 and poor-template score
0.45 at the later original location. Raw context stays unchanged. Depth estimation
and negative-depth resolution receive explicit inputs with their original formulas,
including explicit nonnegative caps and the original clamp asymmetry.

Before each existing AFT attempt, Adapter copies the three effective quality
values into the tree. Low-level QuadtreeQualityControls has no application-module
dependency and is owned by value. Cells use their existing tree observer to read
the same settings. Face-quality subdivision and template statistics keep their
original formulas/order. Template selection, root domain, geometry, synchronization,
IDs and acceptance/retry/stopping policies are untouched. Adapter's effective
borrow retires before its generator owner; tree settings can outlive that owner.

Contexts without quadtree settings keep live global reads and the four original
stable writes. Unconfigured standalone trees keep legacy quality globals; a
standalone Adapter with context uses raw settings unless given an effective view.
Other controls still require serialization. Layout/copy/initialization timing can
change; source rebuild is required and no external ABI guarantee is claimed.

The existing native metrics probe checks three cases: 27 raw/27 stable exact
double representations and ten integer fields survive source/global changes.
Actual estimation/resolution gives 42 matching depth results. A bounded native
face/cell checks nine subdivision/template-stat observations with foreign-global
negative controls. Three configured trees retain those results after generator
retirement. Previous metrics/native oracles and scientific inputs are unchanged.
These controls do not reopen the outside-root Vertex investigation or qualify a
new scientific quadtree parameter matrix.

Require exact-head/main C++17 GCC/MSVC builds, 75 CTest/385 nested Python controls,
the frozen nine-state/45-artifact/123-boundary comparison, real MSVC CLI controls,
scoped analysis, explicit format/whitespace, inventory/contracts and staged/remote
gates. Complete source reversal preserves generator/Adapter/tree/cell arithmetic,
branches, order and literals modulo settings/explicit depth inputs. The missing
global-declaration build failure is retained and corrected. Initial analysis
replayed thirteen commands per shared tree source; its partial log is retained,
and analysis selects each unchanged production command once plus the probe.
Touched legacy formatting is independently token-checked. The [compact record](stage3/quadtree_controls_context/summary.json)
and local build/quadtree-controls-context retain source, commands and hashes.

Full quadtree domains, repeated-generator recovery, concurrency/parallel operation,
complete-process memory and Stage 3/6 closure remain unqualified. No model,
test target or instrument campaign is added.
