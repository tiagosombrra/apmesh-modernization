# Mesh Studio R2.7.8 — shared browser protocol and offline desktop receipt audit

**Date:** 2026-11-17. **PR:** #239, still an isolated research draft.
**Scope:** qualification **of the measurement protocol**, not qualification of new
mesh geometry, hardware GPU output, or accepted adaptive stages.
**Validated code SHA:** `5c507fb84b002241aca0f39190aed54ec4233940`.
**Passing CI:** https://github.com/tiagosombrra/apmesh-modernization/actions/runs/44048544999
(**40 Chromium tests passed, 5 intentionally skipped**, plus **5/5 offline
receipt-audit unit tests**; Linux and Windows scientific regressions,
TypeScript/Vite build and R2.6/R2.7 contracts PASS).


## Motivation and failure modes closed

R2.7.7 correctly blocks its headed physical-desktop suite on the hosted
GitHub runner. However, that also meant changes to its browser event and
camera measurement helper were not exercised by the standard CI.
This stage removes duplicated timing logic and adds a lower-cost
**CI dry-run of the exact same shared helpers**, with the results
explicitly classified as unqualified software-browser measurements.

Another potential route to invalid data was the local runner's previous
ability to forward arbitrary CLI arguments to Playwright. An operator
could unintentionally override `--config` and run a different test
profile under the same physical-GPU-sounding command. The launcher
now forbids all extra CLI options and the negative guard is tested.

Lastly, an independently collected desktop report requires a
reproducible **internal** audit. Claims of 72 successful samples,
correct source IDs, controlled camera, and p50/p95 values should
be recalculated rather than accepted from hand-edited JSON.

## Exact source and protocol code

- `tests/support/r277Protocol.ts`: shared source SHA whitelist,
  P1 controlled-vs-Band staged status, three methods
  (`?xyzPicker=sync`, `?xyzPicker=bvh` and default VTK), browser-local
  actual Playwright pointer click-to-picker and two-RAF proxy, camera
  snapshot, and nearest-rank distributions.
- `tests/viewport-r277-desktop.spec.ts`: imports those exact helpers.
  Its **real headed** 8-round × 3-face × 3-method = **72** measured
  samples **per source model** remain gated on an operator-attested
  desktop; source SHA, quad visibility, method order and camera checks
  remain unchanged. The JSON now contains `cameraXYZ` and
  `cameraPreserved=true`, enabling later independent audit.
- `tests/viewport-r278-shared-preflight.spec.ts`: executes those same
  helpers under hosted Chromium for **both** P1 and Band. This is a
  deliberately reduced (2 distinct face IDs × 2 rounds × 3 methods
  = **12** measured picks per model, plus qualification/warm-up calls)
  functional preflight. Exact source IDs, inspector texts, source
  checksums, matching cameras, visibility and method identity must all
  agree. It does **not** certify a physical machine.
- `scripts/run-r277-desktop.mjs`: rejects unattended CI, missing
  operator attestation, missing machine metadata and **any CLI flags**,
  including alternate Playwright config or silent headless overrides.
  No fast-path default or build cap is changed.
- `scripts/audit-r277-report.mjs`: a **read-only** Node.js report
  validator, not a physical hardware authentication tool. It checks
  the current P1/Band exact SHA and statuses, source face IDs,
  valid camera pose, all 72 unique method×face×round combinations,
  nonnegative timings, picker/RAF consistency, inspector identity,
  displayed visibility, expected per-method quantiles, original
  report scope, and deliberately unmeasured GPU/RSS/VRAM flags.
  It reports a SHA-256 digest of each input report for integrity.
  It does not rewrite/upload the reports and does not change
  the `hardwareGpuPresentTimestampVerified` gate.
- `scripts/test-r278-report-audit.mjs`: in-memory **fabricated test
  fixtures** and negative mutations check rejection of invalid or
  duplicate samples, forged source hashes, invalid camera, mismatched
  percentiles, altered inspector IDs, false GPU-present flags,
  manufactured RSS, software renderer claims and legacy-source
  substitutions. These are tests of the auditor only; no artificial
  fixture is ever published as research timing.

The standard `npm run test:contracts` now includes the R2.7.8
offline audit unit suite, alongside the unchanged R2.6/R2.7 contracts.

## Executing a real, local collection and audit

First follow the separate, documented R2.7.7 physical workstation
setup: `docs/mesh-studio/R2_7_7_PHYSICAL_DESKTOP_QUALIFICATION_PACKAGE_20261116.md`.
Then, on the **physical** desktop, in `tools/mesh_studio/web`:

```powershell
# Run the unchanged headed, guarded physical-workstation protocol
npm run test:r277:desktop

# Audit both produced local receipts without sending them to GitHub
npm run audit:r277:desktop -- test-results/r277-desktop-p1-abc.json test-results/r277-desktop-band-abc.json
```

The audit output is JSON with
`R278_REPORT_INTERNAL_CONSISTENCY_PASS_NOT_PHYSICAL_HARDWARE_CERTIFICATION`,
method/face record count and source SHA. **Passing this auditor does not
prove actual physical GPU hardware, display presentation, driver identity
or memory usage**: those require independent platform/OS instruments
and explicit records. The local Playwright trace ZIPs must also be
reviewed for private system and browser information before sharing.

## Rules preventing misinterpretation

- Original P1 SHA:
  `cbf6cd6308ba54544d06c5d562c491eb7d43ddb216365e0e9d188fd3430295e0`
  is one controlled generator result, not repeated adaptive epochs.
- Band SHA:
  `76b0b4defecc5d534815fb9f41e1405653597a4a0bee6cc7b722ec2460d7afd6`
  remains **staged/unaccepted**.
- Eistute stage-4 reference is **not** admitted as accepted or as a
  source-ID-qualified test. Historical `MANIFEST.sha256` discrepancy
  and verified Git blob identity remain documented in R2.7.6.
- The default XYZ picker remains **VTK native**. Synchronous BVH is
  opt-in and bounded to 2,048 faces; Worker BVH is separately opt-in;
  nonplanar/ambiguous QUADs remain native VTK fallback.
- The CI dry-run is a protocol test under hosted Chromium,
  likely using SwiftShader. Its own receipt states
  `physicalGPUQualified=false`. It does not change the
  **physical workstation / VRAM / process RSS / GPU-present** gates.
- Even under a headed physical browser, two
  `requestAnimationFrame` callbacks are only a render-opportunity
  proxy, **not** an OS/GPU presented frame timestamp.

## Gates still open

Obtaining an operator-run, multiple-machine desktop campaign and its
audited raw JSON and trace outputs remains a real action outside CI.
Cross-browser independent sessions, process-level renderer/Worker RSS,
trustworthy VRAM counters, GPU-present timestamps, larger accepted
real source mesh with per-face generator lineage, Bezier geometry
error/anisotropy, shared curves and scientific R2.8 LOD remain blocked.
This stage neither merges the PR nor tags/releases the project.

## Final observed evidence and disposition

At CI #44048544999, the R2.7.8 browser preflight executed the **same
`measuredClick()` and `camera()` functions** imported by the
operator-gated physical-desktop campaign.

| Source model | Verified original source faces | Measured picks per method | All method/source ID matches |
| --- | --- | ---: | --- |
| Controlled original P1 | 68, 76 | 4 (12 all methods) | PASS |
| Staged/unaccepted Band | 94, 104 | 4 (12 all methods) | PASS |

Thus the preflight's **24 measured source-face selections** agreed
for the named positive TRI pixels. There is no claim that this is a
uniform or exhaustive hit/miss/occlusion distribution. The normal
R2.7.5 48-triple source tests and R2.7.6 source/provenance controls
also remained in the passing 40-test Chromium suite.

The receipt auditor's **five in-memory unit tests** passed, including
strict negative mutations for copied/omitted samples, camera and SHA
provenance, computed percentiles, source IDs, forged memory/GPU claims
and synthetic/legacy model substitutions.

Hosted Chromium reported
`ANGLE (Google, Vulkan 1.3.0 (SwiftShader Device (Subzero) (0x0000C0DE)), SwiftShader driver)`
and `softwareSuspected=true`.
All CI receipts explicitly retain
`physicalGPUQualified=false`. The two desktop tests were **intentionally
skipped**, alongside three pre-existing optional tests.

**Decision:** R2.7.8 protocol/code and report-consistency gates PASS
in CI. Physical Windows/Linux GPU-present measurements, process and
Worker RSS, GPU VRAM, additional independently qualified larger
source-face meshes, and R2.8 continuous geometric LOD proof remain
**OPEN**, not passed. Do not enable experimental picker defaults,
increase synchronous index caps, change the C++ generator, merge PR
#239 or publish a release based on these results.
