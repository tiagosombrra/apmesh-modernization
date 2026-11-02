# Owned adaptive-policy configuration

Classification: engineering-only ownership/interface change supporting S3-05 and
the bounded stage 6 engine boundary. Entry main is PR #142. GenerationContext
optionally owns AdaptivePolicyConfig: mode, adaptive and legacy step limits,
intensity, quality priority and target growth. MakeGenerationContext copies the
five corresponding RuntimeConfig values and the current legacy STEPS limit.
Parsing, ApplyRuntimeConfig and all existing global initializers are unchanged.
The six default config values match the existing runtime defaults; construction
adds no new policy, validation or clamp.

The generator retains the complete context by value. BuildAdaptivePolicyRuntime
selects these inputs and executes its original expressions in their original
order, including empty-mode fallback, stable/debug selection, the legacy/adaptive
step limit choice and all clamp/growth/quality formulas. Derived runtime state
and stable-mode mutations of other globals are unchanged. The Adapter observes
the same stationary context, as before, and receives its raw mode, intensity and
quality priority in the existing domain, degeneracy and fallback decisions.
Its original formulas require raw values; generator clamping is not moved into
the factory or reused to alter Adapter semantics.

An absent policy config keeps live legacy reads. This includes default generators,
default Adapters and existing four-string GenerationContext aggregates. The
factory supplies an engaged snapshot; later source/global changes cannot replace
its six values. Full-context callers that previously relied on mutating policy
globals after factory construction now use the explicit snapshot contract;
identity-only/default callers retain that live-global behavior. The context owner
is immovable and outlives its Adapter borrow. Extra value copies/layout/allocation
timing can change; no stable external ABI or allocation-failure equivalence is claimed.

The existing metrics probe checks empty/legacy/stable/debug modes against its
unchanged global policy path, including out-of-range raw values at existing clamp
sites. Four owned policies survive source mutation/retirement and conflicting
globals, preserving 28 exact double representations plus mode/flags/limits.
The conflicting global path must differ, while default and identity-only callers
must agree on its new values. The original metrics, identity and typed-request
controls remain. No new native target, scientific model or instrument campaign
is added. This control measures policy construction, not independently configured
complete mesh generations in one process.

Require exact-head/main C++17 GCC/MSVC builds, 75 CTest entries/385 nested Python
controls, the unchanged nine-state scientific reference (45 exact artifacts/123
boundary comparisons), real MSVC CLI negatives/analytic controls, scoped analysis,
explicit formatting/whitespace, contracts/inventory and staged/remote audits.
Source reversal compares complete generator/Adapter bodies modulo the named input
bindings and explicit helper arguments; parser/apply, CLI/request and all other
production units retain their original tokens/bytes. The [compact record](stage3/adaptive_policy_context/summary.json)
and local build/adaptive-policy-context retain source, commands, hashes and results.

Remaining numerical globals and runtime policy mutations still require serialized
execution. This isolates the six configuration inputs, not the entire adaptation
state. Full reentrancy, recovery, parallel runtime, complete-process memory and
Stage 3/6 closure remain unqualified.
