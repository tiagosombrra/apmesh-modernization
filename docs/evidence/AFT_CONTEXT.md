# Owned advancing-front and postprocess controls

Classification: engineering-only caller/configuration change supporting S3-05
and the bounded stage 6 engine boundary. Entry main is PR #151. GenerationContext
optionally owns six AftConfig values: ratio, smoothing iterations/factor and
postprocess passes/quality threshold/blend. The factory samples already-applied
process state. ApplyRuntimeConfig keeps the sole CLI clamp of smoothing iterations
to [5,7]; constructor conversion from double to unsigned stays at the original
calls. Raw typed values are not normalized by a new policy. Parser, validation
and defaults are unchanged.

The generator initializes a separate effective value before moving its context.
Its existing immovable owner keeps the value stationary. The single stable write
still sets postprocess passes to 2 at its original position. Raw context remains
unchanged. Adapter gains an independent effective-AFT observer in a three-argument
constructor; prior default/one-/two-argument signatures remain. Its existing two
front construction sites use owned ratio/smoothing inputs. Each front receives
three postprocess values before execution and owns them in low-level
AftPostprocessControls, with no application dependency. That data can outlive the
generator. Missing AFT settings and unconfigured standalone fronts use live globals.

TOLERANCE_AFT remains a shared geometric tolerance across vertices, edges, faces,
quadtree and AFT. The historical constructor tolerance parameter remains inactive.
This lot preserves all its reads and does not introduce partial tolerance
activation. Smoothing loops, quality/area comparisons, movement formulas,
statistics, selection, synchronization and acceptance/stopping policies retain
their original arithmetic, order and literals.

Three cases in the existing native metrics probe check 15 raw/15 stable exact
double representations, one integer field, source retirement, conflicting globals
and constructor factor/iteration/phi bindings, including fractional iteration
conversion. A fixed unit UV square fan invokes actual poorRegionShapeSmoothing;
36 scalar observations compare coordinates/considered/moved counts in raw,
stable and retired-generator contexts. Both enabled raw cases differ from the
disabled foreign controls; all stable cases must move a vertex. Three configured
fronts retain values and results after generator retirement. Fixture endpoints
are borrowed; pending faces detach before deletion and the front borrow of the
center retires before its unique owner. These are bounded single-pass controls;
the unchanged frozen reference supplies full-generation behavior evidence.

Require exact-head/main C++17 GCC/MSVC builds, 75 CTest/385 nested Python controls,
all prior native markers, nine scientific states/45 exact artifacts/123 boundary
comparisons and real MSVC invalid/analytic CLI controls. Source reversal restores
the complete generator/Adapter/AFT bodies modulo explicit settings, observer/value
setup and the original stable assignment. Parser/apply/defaults, the existing
smoothing clamp, tolerance semantics and all other production stay unchanged.
Analyze actual canonical production compilation commands once each plus the
existing probe with unchanged flags. Touched legacy formatting is explicit and
independently token-checked. Whitespace, inventory/contracts, staged identity and
remote gates remain required. No scientific model, target or instrument campaign
is added. The [compact record](stage3/aft_context/summary.json) and local
build/aft-context reports retain commands and identities.

Shared geometric precision and other runtime globals still require serialization.
Stage 3/6, complete precision/context isolation, reuse/recovery, concurrency/
parallel and whole-process memory obligations remain open. Source rebuild is
required for layout changes; no external ABI guarantee is introduced.
