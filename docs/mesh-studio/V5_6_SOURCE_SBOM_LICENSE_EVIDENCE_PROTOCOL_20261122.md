# Mesh Studio V5.6 — bounded source-locked SBOM and license evidence preflight

**Date:** 2026-11-22. **Engineering-only, isolated, not released.** Branch:
`feature/mesh-studio-v56-sbom-license-ledger-20261122`. Based on V5.5 pinned-action review branch, not `main`.
No AFT, Adapter, source C++ accepted step, native model, geometry, original numerical policy, PDF recipe, or native VTK default changed.

## Source and method

1. First run the existing V5.4 independent manifest/hash-lock admission on the exact committed bytes. Any missing or drifted npm direct package, Python pin, Python hash, invalid registry, or mutable malformed lock is rejected before emitting the inventory.
2. Read the canonical Node 22/npm 10 `package-lock.json` **as a lock inventory**, not as a claim of a browser runtime installation. Retain every recorded logical installation path, even nested duplicates; attach exact name/version/path and npm integrity's decoded SHA-512/SHA-384/SHA-256 **of the recorded tarball**.
3. Read all Python 3.13 Linux API, Windows API, Linux native-PDF hash lock profiles. Retain one component per pin/profile. Store the count and SHA256 digest of the **set of permitted wheel/sdist hashes**; do not claim any one permitted hash identifies the wheel actually installed on a specific runner. Preserve lock-file + direct-manifest SHA256 in CycloneDX metadata.
4. Generate deterministically, with no clock-dependent timestamp or network request, `mesh-studio-v56-source-lock.cdx.json` (CycloneDX 1.6 component inventory) and `mesh-studio-v56-license-evidence.json`. Every schema property is rooted in the source lock or a clearly labeled admission limitation. A separate read-only, SHA-pinned CI job validates and archives the raw machine files; no automatic PR merge or publication.
5. Keep the evidence classification explicit. A npm `license` field is a **package-lock declaration, not verification of the actual shipped license text or attribution obligations**. Python pip-compile locks do not contain license identifiers: mark all Python entries **unavailable**, not compatible/approved. A lock inventory does not claim full installed dependency graph, application distribution manifest, C++ third-party license compatibility, malware/CVE triage or signed build.

## Initial lock-derived scope

| Lock/profile | Component records | License certainty |
| --- | ---: | --- |
| npm v3, Web | **141** package/install-path entries | **140 declarations**, 1 missing |
| Python 3.13 API / Linux | **32** | No license text in lock |
| Python 3.13 API / Windows | **32** | No license text in lock |
| Python 3.13 native PDF / Linux | **15** | No license text in lock |
| **Total by profile (not unique releases)** | **220** | **79 Python profile records have no verified license** |

The same Python package appearing under multiple profiles is **counted separately by design**; 220 is not the number of unique packages and does not imply 220 packages in any one deployment. npm optional/platform-specific/dev packages in the lock are not automatically shipped to users.

### npm declared-license buckets (not legal approval)

| Literal npm lock declaration | Install-path records |
| --- | ---: |
| MIT | 72 |
| Apache-2.0 | 28 |
| ISC | 18 |
| BSD-3-Clause | 5 |
| MPL-2.0 | 12 |
| Python-2.0 | 1 |
| CC-BY-4.0 | 1 |
| (MIT AND Zlib) | 1 |
| (WTFPL OR MIT) | 1 |
| 0BSD | 1 |
| Missing | 1 |

**Next legal/redistribution triage, not a license violation finding:** `rechoir` has no npm lock declaration; `caniuse-lite` declares CC-BY-4.0; `argparse` declares Python-2.0; `pako` and `spark-md5` have composite/alternative expressions; `lightningcss` and its 11 OS-specific optional binaries declare MPL-2.0. For each, obtain actual immutable tarball license text, notices, linked-source obligations, and confirm whether it is in the browser bundle vs development toolchain before assigning risk or product signoff. Assess all direct and transitive Python licenses from independently sourced wheel/sdist metadata before distribution.

## Verification gates

- Audit exact V5.4 manifests/locks, reject direct Python drift and absent/malformed hash.
- One deterministic CycloneDX component per source-locked npm path and per Python profile entry; never silently deduplicate cross-platform entries.
- Source-pinned npm SHA512 values must base64-decode to the correct digest length. Invalid integrity, duplicated Python name, or missing Python distribution hash must fail closed.
- Byte-exact repeated generated JSON and stable raw file digests.
- V5.5 workflow immutable-action source guard remains separately enforced.
- Hosted CI outputs must refer to the exact V5.6 source commit; pre-existing V5.4 and V5.5 scientific runs **cannot** certify the new SBOM code implicitly.

## Explicit exclusions

This is **NOT** signed software, a verified SPDX license audit, source code disclosure analysis, a vulnerability scan, a release package, an installed-environment SBOM, a Windows physical GPU memory audit, a new accepted original TRI epoch or R2.8 LOD acceptance. All original research PRs remain Draft; no `main` merge, tag, release or scientific method relaxation.

**Next bounded tasks:** independently review the generated JSON and receipts, then qualify actual dependency/license notices and complete the paper Book figure typography/splitting with the professors and target venue rules. Original Book overview remains unchanged until a separately validated source-preserving publication-layout recipe passes original PDF geometry auditing.
