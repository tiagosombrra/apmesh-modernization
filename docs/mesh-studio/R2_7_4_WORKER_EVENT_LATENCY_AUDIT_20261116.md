# APMesh Mesh Studio — R2.7.4 Worker scheduling and viewport event-path audit

**Date:** 2026-11-16. **Isolated branch:** `feature/mesh-studio-r27-bvh-20261116`.
**Exact test implementation SHA:** `58096510522ad28344306ecfc358b9692d1ff5cb`.
**CI:** https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43918599086
**Result:** scientific Linux and Windows regression PASS, TypeScript/Vite production
build PASS, contracts PASS; real Chromium **30 passed, 3 optional skipped**.

## Problem inherited from R2.7.3

An opt-in browser Worker BVH selected original real P1 and Band AFT TRI source
face IDs correctly, but its click-callback latency p50 was approximately 20 ms
for tiny meshes, vs about 0.5 ms for native vtkCellPicker. The same source ID,
camera and visible TRI-only surface were used for both. The initial result did
not isolate the internal geometric traversal from browser Worker dispatch.

No changes to APMesh scientific C/C++ source, source face identity, QUAD solver,
shared curve incidence, default VTK selection or protected main were authorized.

## Instrumentation and invariant contracts

- Existing Worker now reports exact **Worker-local BVH query wall time**.
- The client independently records `postMessage` to response **round-trip**
  time with timeout and availability status.
- The viewport records for an actual opt-in BVH hit:
  - worker query duration;
  - full message round-trip;
  - non-compute residual = max(0, round-trip - Worker query);
  - picker-call wall time outside round-trip.
- Values are correlated with one original source ID, ray and visibility/camera
  state. Stale metrics are removed before each click. Timeout/ambiguity
  remains fail-closed to native VTK; no performance measurement is treated as
  a scientific geometry oracle.
- The full R2.7.3 two-viewport real-source paired protocol reran with the new
  metrics: 24 matching pairs on controlled P1 and 24 on staged/unaccepted
  Band, 8 rounds, AB/BA alternation and source SHA/camera verification.

## Correlated results (CI #43916928735)

Source P1 source SHA:
`cbf6cd6308ba54544d06c5d562c491eb7d43ddb216365e0e9d188fd3430295e0`.
Band source SHA:
`76b0b4defecc5d534815fb9f41e1405653597a4a0bee6cc7b722ec2460d7afd6`.

| Measurement, p50 in ms | Controlled P1 | Staged Band |
| --- | ---: | ---: |
| BVH Worker geometric query | 0.0 (resolution limited) | 0.0 (resolution limited) |
| BVH Worker geometric query p95 | 0.1 | 0.1 |
| Worker message round-trip | 18.1 | 17.9 |
| Non-compute residual (not isolated IPC) | 18.0 | 17.9 |
| Viewport callback outside message wait | 0.1 | 0.1 |
| Total BVH picker callback | 18.2 | 18.0 |
| Native VTK picker callback | 0.5 | 0.5 |

This shows **tiny Worker CPU time** relative to message response delay inside
the viewer; it does **not** prove that raw postMessage itself has 18 ms
overhead or identify the scheduling mechanism.

Repeated results from CI #43917895191 and #43918599086 had the same general
pattern, with session-to-session timing variation. Their exact raw receipts
are retained in GitHub Actions artifacts, not merged into one statistical
independent-run estimate.

## Focus/visibility isolation (CI #43917895191)

Direct source-local Worker queries used the same provenance-verified P1 model,
the same original AFT TRI and layer policy, independently warmed with six
excluded calls and 24 recorded calls per phase:

| Headless Chromium phase | document.visibilityState | document.hasFocus() | Worker CPU p50 | Round-trip p50 | Round-trip p95 |
| --- | --- | --- | ---: | ---: | ---: |
| First page initially in front | visible | true | 0.0 ms | 0.1 ms | 0.2 ms |
| Second page opened | visible | true | 0.0 ms | 0.1 ms | 0.2 ms |
| First page restored | visible | true | 0.0 ms | 0.0 ms (resolution limited) | 0.2 ms |

All 72 direct-worker source face IDs matched; no timeouts.

**Limitation:** headless Chromium reported the original page as visible and
focused in all phases. Thus this does **not** exercise a genuine throttled
background-tab state and cannot establish or refute background throttling
on physical desktop browsers.

## Actual viewport pointer vs synthetic DOM event (CI #43918599086)

Within **one** qualified Chromium viewport, the same controlled original P1
source-face **#68** was selected with original QUAD hidden. Both modalities
called the existing UI click handler and awaited the same Worker path.
Each modality was warmed for three excluded picks, then 12 paired picks were
executed with alternating order. All selected source IDs were verified.

| Same-pixel event path | Callback p50 | Callback p95 | Worker round-trip p50 | Worker CPU p50 |
| --- | ---: | ---: | ---: | ---: |
| Actual pointer click through Playwright | 20.3 ms | 21.5 ms | 20.3 ms | 0.0 ms |
| Synthetic DOM click dispatched on viewport | 0.3 ms | 0.3 ms | 0.2 ms | 0.0 ms |

The synthetic path was intentionally used **only** to isolate event context;
it is **not** human input and cannot stand in for real usability latency.

Observation: raw Worker message traffic and BVH CPU execution can be fast
for the exact same original source. The slowdown correlates with dispatch
through the **real pointer click input path** under the hosted Chromium
environment. It may include task queueing, scheduling, event processing,
render pipeline interaction or automation-specific behavior; these
experiments **do not distinguish an individual causal mechanism**.

## Correctness, performance and release decision

- Source-ID correctness in the tested visible TRI-only paths: PASS.
- Bounded Worker CPU query: FAST in these tiny real source samples.
- Performance advantage for real pointer input: **NO**. Native VTK stays
  faster, and the Worker is not authorized as default.
- Trigger-specific scheduling difference: OBSERVED, exact mechanism OPEN.
- Visible warped QUAD intersection, large provenance-verified real APMesh
  meshes, real user input-to-paint, Windows physical GPU, browser memory
  and VRAM: NOT QUALIFIED.
- Scientific curved-surface oracle, original shared-curve topology and
  geometric LOD: NOT QUALIFIED.

## Next R2.7.5 gate

Investigate the real pointer event path under a physical desktop Chromium
and a second browser; capture browser performance traces of event tasks,
Worker message dispatch and render frames, not just sampled wall clocks.
A bounded **main-thread** index prototype may be compared against
`vtkCellPicker` with strict source-ID, visibility and numerical fallback
invariants, but should remain experimental and is not automatically justified
for small meshes where VTK is already sub-millisecond.

Do not infer a large-mesh break-even threshold from these tiny fixtures or
publish a speedup claim. R2.8 geometric LOD remains blocked pending
scientific approximation and source-identity contracts.

**Branch boundaries:** Studio-only frontend/tests/docs, PR #239 draft,
no merge/tag/release, no generator source modifications.
