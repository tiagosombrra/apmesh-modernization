# Owned adaptation settings and effective adjustments

Classification: engineering-only caller/state ownership change supporting S3-05
and the bounded stage 6 engine boundary. Entry main is PR #144. GenerationContext
optionally owns AdaptationConfig with relaxation, maximum delta and minimum/maximum
factor bounds copied from RuntimeConfig. Parsing, ApplyRuntimeConfig, validation
and all existing defaults remain unchanged. In particular, the loader's max-delta
default and the raw runtime default retain their distinct existing values.

The generator keeps the configured value unchanged. At the original stable-mode
location, a separate optional instance value receives the original four ordered
assignments: relaxation 0.30, max delta 0.05, factor min 0.90 and factor max 1.03.
Nonallocating scalar accessors feed the existing domain, smoothing, rate-limit
and curve-factor expressions; BuildAdaptationRuntime exposes effective settings.
Existing current_adaptation_relaxation_/max_delta_ members still carry per-attempt
values. Retry shrink, micro scaling, clamps, comparison/loop order and all formulas
are unchanged. Adapter receives computed factors through its existing arguments;
it has no direct reads of these four globals.

Without adaptation settings, the same accessors observe globals and stable mode
performs the original four global writes. This preserves default and existing
partial-context callers. Factory contexts deliberately retain copied inputs across
source/global mutation. Effective stable state is separate from raw context state;
this does not establish repeated whole-Generator recovery. Layout/copy/allocation
timing can change; no stable external ABI or failure-allocation equivalence is claimed.

The existing native metrics probe checks three settings cases against the legacy
path: 12 raw and 12 stable exact double representations survive source mutation/
retirement and foreign globals. Actual ApplyAdaptationRateLimit calls preserve
18 exact output representations before/after stable overrides. The conflicting
legacy path must change outputs, owned overrides must retain raw context/foreign
globals, and both default/identity-only paths must retain their global writes.
The existing friend fixture seeds only rate-limit history/current attempt values
and calls the actual production functions; there is no copied formula or new
production test mode. Prior ownership/policy/request/criteria and metric oracles
are unchanged. No native target, scientific model or instrument campaign is added.

Require exact-head/main C++17 GCC/MSVC builds, 75 CTest/385 nested Python controls,
the frozen nine-state/45-artifact/123-boundary scientific comparison, existing
MSVC CLI negatives/analytic controls, scoped analysis, explicit format/whitespace,
inventory/contracts and staged/remote gates. Source reversal checks complete
generator formula/order/literal tokens modulo the four reads and the exact stable
assignment block, including values extracted from the new helper. Parser/apply,
CLI/request, other production and scientific inputs stay unchanged. The [compact record](stage3/adaptation_context/summary.json)
and local build/adaptation-context retain source, commands, hashes and results.

Other refinement/budget controls and global mutations remain shared and serialized.
Independent complete generations, recovery, parallel/concurrent execution,
complete-process memory and Stage 3/6 closure remain unqualified.
