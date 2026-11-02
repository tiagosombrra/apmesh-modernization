# Owned stopping and retry criteria

Classification: engineering-only caller/configuration ownership change, supporting
S3-05 and the bounded stage 6 engine boundary. Entry main is PR #143.
GenerationContext optionally owns StopRetryConfig with eleven generator criteria:
global/local error targets, minimum improvement, patience, retry count/shrink,
growth factor/absolute limits, error floor and absolute/per-element drop thresholds.
The factory copies six RuntimeConfig values and the five remaining legacy growth/
saturation thresholds. Defaults match the existing runtime; parsing, validation,
ApplyRuntimeConfig and global initializers are unchanged.

Nonallocating scalar accessors feed the original stop/retry comparisons, local
error gates, diagnostics and reports. BuildStopRetryRuntime returns the effective
criteria by value. Existing diagnostic strings and report keys stay intact.
Stable mode still promotes the retry count with max(1,count) at its original
conditional location. With owned criteria, promotion writes a separate optional
effective count in the generator; the raw context count is retained. Without
owned criteria, the original global assignment remains. Subsequent decisions and
reports consume the effective count, including retry-enabled and budget-policy
fields. No stable minimum, clamp, rejection or loop order is changed.

Default generators and contexts without stop_retry keep live global reads/writes.
This includes existing identity-only and adaptive-policy-only aggregates. Factory
contexts intentionally retain copied criteria across later source/global changes.
The remaining numerical globals still require serialization. EPSYLON reads in
point equality remain untouched; this lot isolates generator criteria, not every
geometric tolerance. Step limits are already in adaptive_policy. Relaxation,
budget controls, current retry indices and other stable-mode mutations remain
outside this lot. Copy/layout/allocation timing may change; no external ABI or
allocation-failure equivalence is claimed.

The existing native metrics probe checks three raw criteria cases, including
disabled/positive thresholds and direct-caller count boundaries. It compares
27 exact double representations plus integer values with the live legacy path.
Owned values survive source mutation/retirement and conflicting globals. The
actual promotion helper must retain raw count and foreign global state for owned
criteria, while default and identity-only callers must update the global count.
The existing friend fixture exposes that helper only to this test; no production
test switch is added. Prior context/policy/request and eight-attempt/132-field
metric oracles are unchanged. No scientific input or instrument campaign is added.

Require exact-head/main C++17 GCC/MSVC builds, 75 CTest entries/385 nested Python
controls, the frozen nine-state scientific comparison (45 exact artifacts/123
boundary comparisons), existing real MSVC CLI controls, scoped analysis, explicit
format/whitespace, contracts/inventory and staged/remote checks. Source reversal
preserves complete generator formula/branch/order/literal tokens modulo the
named accessors and original promotion assignment. Other production units,
parser/apply/global defaults and CLI/request remain unchanged. The [compact record](stage3/stop_retry_context/summary.json)
and local build/stop-retry-context retain commands, hashes and results.

This qualifies the bounded criteria contract and existing process regressions.
Same-Generator recovery, independently configured complete generations in one
process, concurrent/parallel execution, complete-process memory and Stage 3/6
closure remain unqualified.
