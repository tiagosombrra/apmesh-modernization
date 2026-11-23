# V5.11 — proposed third-party notices: bounded local reviewer, not distribution clearance

**Protocol date:** 2026-11-23. **Scientific/code scope:** NO original C++ execution and NO scientific R2.8 qualification. **License/legal status:** DRAFT FOR HUMAN REVIEW ONLY. No right to release, package, sign, publish, or merge into main is inferred.

## One explicitly bounded prospective handoff profile

The hypothetical installation/profile being examined is limited to:

1. The **seven byte-certified immutable HTML/JS/CSS assets** of the existing local V5.11 research reviewer, built with the exact npm lock and served only on loopback.
2. The **isolated minimal 13-distribution Python API** required for this local research reviewer, **not** the whole scientific Python/C++/PDF/Vtk executable/development environment.

No installer was generated; no legally reviewable assembled distributable binary exists. The candidate does NOT include the original adaptive C++ generator, scientific/PDF Python environment, research data, fonts outside this profile, public deployment or application signing. The **complete** source evidence must be evaluated for the actual packaging format before any shipment. In particular, **PyMuPDF==1.26.7** belongs to the wider scientific Python profile and has AGPL/commercial licensing implications for any distribution involving it. Its exclusion from this narrow profile is **not** permission to distribute the whole APMesh.

## Source-of-truth and contents

The generator **tools/mesh_studio/v511_notice_candidate.py** obtains its source texts exclusively from the previously certified, same-commit **[GitHub Actions #45209742219](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/45209742219)** (code SHA **fb665764143da62b9a44516654ed1057858c2639**). It downloads the Linux and Windows installed dependency LICENSE/NOTICE/README source archives together with the Vite/Rolldown final-JavaScript module/attribution archives, and **first** runs the previously certified source-to-bundle and installed-source reauditors. Before composing anything, they require the original seven-asset browser bundle SHA256 **ad6c4627090a335c0ed7e3bf1bae0c0d062ed1e48249f120b10f3ba8ff8a85f5**, the npm lock and individual package version/SRI identities and each original license byte.

Exactly **13 source packages actually present in the output JS graph** and **13 Python minimal API distributions** are included per OS, none inferred from the entire npm install tree. The proposed evidence is generated separately for Linux and Windows because original installed files must remain source-authentic.

The resulting ZIP consists of **57 files**:

- **THIRD_PARTY_NOTICES_CANDIDATE_UBUNTU_24.04.txt** — 26 source-identifiable third-party components, source attribution and complete available license text for Ubuntu.
- **THIRD_PARTY_NOTICES_CANDIDATE_WINDOWS_2022.txt** — the corresponding source-attested 26-component Windows candidate, separately generated.
- **NOTICE_EVIDENCE_LEDGER.json** — schema/version/26 source-identified entries per host, expected original source CI run+SHA, all original source byte hashes, selected source notice paths, unapproved legal choices and explicit release prohibition.
- **54 source-notice files** (27 per host, including both original vtk.js LICENSE and Copyright.txt), each written in the exact original source bytes and verified independently. The composite proposed TXT concatenates text for human readability; the separate source files are the actual byte-level provenance evidence.

**Candidate ZIP SHA256:** 83bd7d39b84bedab1ec5344cd027e9ac478db06843a141d8806eef94685e3111 (84,619 bytes). **Independent readback ZIP SHA256:** 7c74328d5b26f7bbcd2081b0b79ab8519eddb384c3eafb90cc7291d0a560cd42 (449 bytes). These are local archive SHA256 values; the GitHub artifact service may attach a different archive byte digest when retrieving through its API, but the source notice file hashes are independently checked in the CI.

### Important exceptions, explicitly retained

- **spark-md5 3.0.2:** its npm/Vite metadata expresses **(WTFPL OR MIT)** while the installed source LICENSE file used in this evidence has **WTFPL text**. No MIT path is selected or invented; the choice and attribution requirements must be decided and checked against exact original source materials by a human before integration. The candidate explicitly marks the decision as **UNRESOLVED**.
- **seedrandom 3.0.5:** Vite build.license returns **MIT identifier without license text**. The candidate's MIT text is independently extracted from the **actual installed npm source README.md**, as reauthenticated through exact version and registry SRI. The **entire** original README is separately preserved, and its MIT subsection has an individually validated SHA. The Vite omission is never silently normalized away.
- **vtk.js 38.0.9:** retains **both** the package LICENSE and **Copyright.txt**, which contain distinct attribution information, instead of incorrectly collapsing one into the other.
- **pydantic-core 2.50.5:** the original installed LICENSE is **LF on Ubuntu and CRLF on Windows**. The underlying license wording is equivalent, but **raw file SHA256 is intentionally different**; both source files are preserved separately. This was the **only original-text byte difference** among the 26 selected package records per OS.
- **Typing Extensions / PSF-2.0:** the full original installed license materials are included, rather than deducing a generic MIT grant.

## Actual independent CI and reproducibility

**[GitHub Actions #45225140186](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/45225140186): 2/2 SUCCESS**, exact implementation **fd780952df6206fd81de12200788fa1f18aa9989**. First job reopens the original 2026-11-23 certified Linux and Windows assets and emits both candidates and all 54 source notice files with an evidence ledger. The **second separate CI job** downloads both original source evidence classes directly again **and** the newly generated candidate from the first job; it regenerates each notice and compares the entire output file inventory and every output SHA256 (not merely a stated pass/fail). No software build/output is modified.

Artifacts, currently set to **90 days** (expiry approximately **2027-02-21 17:12 UTC**):
- [Proposed notice texts, provenance ledger and all 54 original license files](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/45225140186/artifacts/14842866025).
- [Readback receipt independently regenerated from original package-source bytes](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/45225140186/artifacts/14841904998).

A separate archival copy is preserved in the private doctoral Google Drive **05_Experimentos_e_Resultados**, without publishing private URLs in this public repository.

## Human gates that remain open

This is a **draft for legal review**, not a complete THIRD_PARTY_NOTICES suitable for actual redistribution. Before any release:

- Define and assemble an **exact distribution artifact**, including scripts, resource files, original native code, bundled Python wheels/runtime, third-party fonts, scientific data, packaging and optional native dependencies. The current scope covers only the hypothetical minimal research reviewer.
- Decide **spark-md5**'s alternative license path using authoritative original source notices; determine all copyright/NOTICE requirements (including possible nested vtk.js transitive and code-origin attributions), legal compatibility, source-offer obligations, installation-specific runtime licenses, and where/how notices will actually be bundled or displayed.
- Evaluate PyMuPDF AGPL/commercial implications for any **larger** scientific/PDF profile. Review and sign off the exact candidate with a qualified human before any installer/signing/distribution.
- Require independent real physical Windows and Linux reviewer signoffs ([Issue #255](https://github.com/tiagosombrra/apmesh-modernization/issues/255)); editorial/academic qualification remains adviser-dependent ([#251](https://github.com/tiagosombrra/apmesh-modernization/issues/251)); maintain source evidence beyond expiry ([#260](https://github.com/tiagosombrra/apmesh-modernization/issues/260)). [Issue #250](https://github.com/tiagosombrra/apmesh-modernization/issues/250) **remains OPEN**.

The original C++ accepted global steps remain **[1] per Eistute and Book**, no second epoch, CAD error bound, physical welding, approved QUAD or anisotropic acceptance. R2.8 remains scientifically BLOCKED. No merge to main, no release/tag, no installer or public publication.
