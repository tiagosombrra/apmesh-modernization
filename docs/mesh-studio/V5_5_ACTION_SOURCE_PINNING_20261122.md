# Mesh Studio V5.5 — immutable GitHub Actions source pinning and negative controls

**Date:** 2026-11-22. **Status:** isolated engineering review; CI on new branch is required before any certification. Branch `feature/mesh-studio-v55-pinned-actions-20261122` stacks on the V5.4 review head `740a357f73d055d7e3f2f345810b8e0d885233ac`. No original C++ AFT/Adapter, model input, accepted TRI, mathematical policy, figure/PDF recipe, default VTK behavior or main branch is modified.

## Threat and bounded change

The V5.4 npm and Python transitive locks protect registry package artifacts, but three Studio workflow definitions still invoked mutable GitHub Action major tags (`@v4`/`@v5`). A tag can resolve to different workflow implementation bytes without a change to the caller source commit. V5.5 pins **all 51 action invocations in exactly these three Studio workflows** to full, GitHub-verified source commits. The five commit SHAs below were read from the corresponding official `actions/*` repositories' major-tag commits on 2026-11-22; they are not hypothetical digests.

| Official action | Immutable GitHub commit SHA |
| --- | --- |
| `actions/checkout` (v4) | `11d5960a326750d5838078e36cf38b85af677262` |
| `actions/setup-python` (v5) | `a26af69be951a213d495a4c3e4e4022e16d87065` |
| `actions/setup-node` (v4) | `49933ea5288caeca8642d1e84afbd3f7d6820020` |
| `actions/upload-artifact` (v4) | `ea165f8d65b6e75b540449e92b4886f43607fa02` |
| `actions/download-artifact` (v4) | `d3f86a106a0bac45b974a628896c90dbdf5c8093` |

Coverage by owned workflow:

- `.github/workflows/mesh-studio-validation.yml`: **41** exact-SHA action references, including three named-step `download-artifact` calls that a shallow search of `- uses:` missed.
- `.github/workflows/mesh-studio-fast-web.yml`: **4** references.
- `.github/workflows/mesh-studio-lock-bootstrap.yml`: **6** references.
- Total: **51** reviewed, full-SHA references in this limited workflow scope.

All three workflow push-trigger branches additionally admit this V5.5 isolated research branch, enabling actual actions verification without modifying the original V5.4 certified review snapshot. Source-native mandatory workflows and release constraints remain unchanged; the new branch is not a production deployment target.

## Independent fail-closed test

The new `tools/mesh_studio/test_v55_action_pinning.py` is included in the existing Linux/Windows scientific Python discovery. It independently reads all three actual workflow source files, walks **every** YAML `uses:` line (named and unnamed steps), enforces the exact approved `owner/repo@40-hex-SHA` allowlist and known occurrence counts, and fails closed on:

1. A mutable `@v4`, `@main`, `@latest` or shortened digest.
2. An unknown action owner/repository or a changed full SHA.
3. A missing or unexpectedly added `uses` reference relative to the reviewed source inventory.
4. Missing actual source files or missing new-branch trigger.

The four synthetic-only adversarial/helper controls passed local Python execution before repository commit; this does **not** attest full CI or real original scientific source. Hosted Linux/Windows workflow and source-native/Chromium receipt must be read from the exact code SHA **after** all writes finish.

## Admission and residual boundaries

- **V5.4 already certified baseline:** native/scientific 4/4 on SHA `792d9eb1031567cb8da1a8436c7529ea16e1b86e`, [original CI #45072635572](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/45072635572), 556 Linux/Windows cases and 63 Chromium passes; this is a prior source code snapshot, not an automatic V5.5 certification.
- **V5.5:** actions-source pin enforcement code committed, exact-hosted CI verification **PENDING** until distinct latest SHA jobs conclude. No mathematical outcome is inferred from an engineering checksum.
- This only covers the three named Studio workflows; other QUAD/release/root workflows are separately governed and are **not claimed pinned**. Immutable source commits do not solve malicious upstream source already at that SHA, indirect npm supply chain, untrusted native compiler/OS images, dependency CVEs, transitive licenses, signed runners, secrets hygiene or offline distribution.
- Requested independent human review is still pending. No merge, auto-merge, release, public tag or scientific R2.8 LOD admission.
- **Next independent gates:** review the SHA map and CI logs; inventory exact bundled dependencies/licenses/SBOM without replacing verified locks; then handle Book paper figure's 4.90 pt labels as a separate source-preserving editorial change with advisers' venue constraints.

Scientific acceptance remains **original Eistute/Book step [1] only**; no second same-process original globally accepted TRI epoch, no physical C++ welded seams or continuous CAD geometry error proof. **R2.8 remains BLOCKED.**
