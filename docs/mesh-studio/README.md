# Mesh Studio — canonical state, runbook and plan

**2026-11-24 | Research-only V5.11 draft | P0 bounded CI regression closed; P1 review active.**
This is the sole current operational plan. [History](HISTORY.md) indexes dated
science and earlier plans; [evidence registry](EVIDENCE_REGISTRY.json) records
immutable evidence references. Do not resume old plans as live instructions.

## Admission status

| Scope | Historical certificate | Limit |
|---|---|---|
| Native TRI | [45147268663](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/45147268663) | Eistute 1168 faces / 4 patches, Book 4256 / 28; only global accepted step [1] each |
| Original ten-file mirror | [45189301366](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/45189301366), 2/2 | Reopens exact original bytes, not recompiled |
| Static V5.11 | [45189641930](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/45189641930), 3/3 | 36 Python + 4 Chromium per OS; seven static assets identical |
| Actual npm/Python attribution | [45209742219](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/45209742219), 4/4 | 13 browser graph packages and 13 minimal API distributions per OS |
| Notice candidate | [45255136596](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/45255136596), 2/2 | 58 files; original spark-md5 MIT alternative proven, not elected |
| Physical acceptance | [#255](https://github.com/tiagosombrra/apmesh-modernization/issues/255) | Independent physical Windows/Linux NOT RUN |
| Distribution | [#250](https://github.com/tiagosombrra/apmesh-modernization/issues/250) | OPEN: actual artifact and human legal approval absent; full scientific PyMuPDF profile not cleared |
| Editorial | [#251](https://github.com/tiagosombrra/apmesh-modernization/issues/251), separate PR #253 | Adviser/venue decision pending |
| Scientific R2.8 | Historical R2.7 reports | BLOCKED: no distinct second globally accepted original epoch, certified descendants or continuous CAD error bound; no physical welding |

These certificates concern their own revisions, not today's revision. Read
current CI separately; pending or skipped required checks never mean PASS.
Certified static inventory SHA256:
`ad6c4627090a335c0ed7e3bf1bae0c0d062ed1e48249f120b10f3ba8ff8a85f5`.

## Supported local review

Python 3.13, Node 22, npm 10. From repository root (Windows: substitute
`py -3.13` for `python3.13`):

```sh
python3.13 -m tools.mesh_studio.local_reviewer_launcher build
python3.13 -m tools.mesh_studio.local_reviewer_launcher preflight
python3.13 -m tools.mesh_studio.local_reviewer_launcher serve
```

Open http://127.0.0.1:8765/. Stop Vite on 5173 first. Loopback only; do not
expose raw ASGI or development Vite to the network. Minimal server uses
hash-locked dependencies, separate from scientific/PDF/VTK tooling.

For original-source review extract the verified ten-file corpus into
`build/v59-native-reviewer/`, install Chromium with
`npm exec playwright install chromium` in the web directory (Linux may
need --with-deps), then from root:

```sh
python3.13 -m tools.mesh_studio.v59_reviewer preflight
python3.13 -m tools.mesh_studio.local_reviewer_launcher original-smoke
```

For physical acceptance use the privately archived R2 reviewer kit, its
pinned checkout and exact source corpus; retain reviewer attestation,
13 controls, screenshots, OS/GPU evidence. Hosted CI is not human approval.
See [original protocol](V5_11_STATIC_SINGLE_PORT_REVIEW_PROTOCOL_20261123.md).

## Architecture and regression

Python inspection, topology, metrics and publication: tools/mesh_studio.
React/TypeScript/vtk.js UI: tools/mesh_studio/web. VTK is the default picker;
experimental BVH and synthetic stress remain opt-in. Keep source UV and XYZ
identity distinct. Native observers and discrete seam evidence are not
welding, scientific LOD or new accepted meshes. C++ scientific changes are
separate; read [QUAD state](../research/quad/STATE.md) for that research line.

| Workflow | Scope |
|---|---|
| mesh-studio-validation.yml | Complete Python research suite on both OSs, fresh native serial capture and broad browser suite |
| mesh-studio-fast-web.yml | Developer frontend smoke and contracts |
| mesh-studio-v511-built-reviewer.yml | Static original-source Windows/Linux review, security negatives, cross-OS bytes |
| mesh-studio-v511-installed-license-audit.yml | Installed sources and actual bundle attribution |
| mesh-studio-v511-notice-candidate.yml | Regenerate/reopen proposed notices from certified source |
| mesh-studio-v511-cpp-evidence-continuity.yml | Explicit original-corpus renewal |
| mesh-studio-v56-sbom.yml / v561-installed-license.yml | Wider scientific dependency inventory |
| mesh-studio-lock-bootstrap.yml | Intentional lock regeneration |
| R2.4/R2.5/R2.6 500k diagnostics | Optional synthetic stress, not native science |

Local baseline: `python -m tools.mesh_studio.dependency_lock_audit`;
`python -m unittest discover -s tools/mesh_studio -p 'test_*.py' -t . -v`
with platform-specific full research hash lock (Linux VTK may need Xvfb).
In web: `npm ci --no-audit --no-fund`, `npm run test:contracts`,
`npm run build`. Broad developer browser tests require same-run native
artifacts; static reviewer tests use the independent historical corpus.
Never weaken negatives, invent fixtures or silently drop required coverage.

## P0 regression checkpoint — 2026-11-24

The audited implementation revision is `9977f2a88b199bbed39fd9583cbb58737a4db638`. The evidence registry's
initial stabilization status is the pre-run snapshot; this section records
the live work checkpoint and links the authoritative CI results.

- [Full scientific regression #45363214163](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/45363214163):
  Python discovery PASS in both OSs: Linux 609 passed / 5 skipped and Windows
  603 passed / 11 skipped (614 enumerated each, no failures). Final result:
  **4/4 jobs SUCCESS**. Fresh Linux serial native C++ capture, source-bound
  Eistute/Book accepted TRI, OFF/ON numerical parity, SVG/PDF independent
  re-audit and R2.7.24–R2.7.34 research observer controls all passed. Dependent
  broad Chromium suite: **63 passed** (2.8 min), including actual source
  import/performance and production build; same-run source evidence recovered.
- [Fast web #45363214119](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/45363214119):
  1/1 SUCCESS, 18 Chromium tests passed.
- [Static reviewer #45363214240](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/45363214240):
  3/3 SUCCESS; 36 Python controls and 4 Chromium tests per OS, original native
  corpus reopened, no orphan ports, seven identical compiled assets with
  unchanged certified inventory SHA.
- [Installed/bundle licensing #45363214125](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/45363214125):
  4/4 SUCCESS. The source-exact notice generator and its pinned input evidence
  are unchanged from the previous certified notice run; it was not re-run by
  this documentation/CI-only push.

Inventory verification: 12 remaining workflows with 120 approved SHA-pinned
action references, no write permissions; 97 local Markdown links in the
history index resolve. All 54 Python test files and 29 browser spec files,
native code, models, frontend code and original scientific historical files
remain present. Three superseded reviewer workflows were retired, with exact
historical definitions linked from HISTORY.md. Four environment-specific
optional JSON Schema/LaTeX skips and one absent-corpus skip occur in each
ordinary Python checkout; Windows adds six unqualified GPU/VTK controls.
The dedicated static reviewer exercises the retained original corpus.

**P0 bounded automated regression CLOSED.** Final native and broad browser
jobs were independently checked via Actions job/step results and the Python
and Chromium logs. No failure to repair in this run. Exact skip reasons:
two optional JSON Schema tests, two unavailable LaTeX toolchain tests and
one original-corpus test in ordinary checkout on each OS; Windows additionally
skips six hosted WGL/OSMesa/VTK controls. The dedicated static reviewer covers
the original corpus; JSON Schema/LaTeX and physical GPU coverage are not
claimed. The remote pre-update HEAD `c87f80b7290fd424ffe028cf5f95ddbd17670f98`
is one commit ahead of the tested revision, with only this README changed.
The registry remains the immutable initial pre-run snapshot; this section is
the authoritative live status. No source or workflow change is required.
P1 review may proceed; no physical GPU acceptance, new native epoch or legal clearance.

## Priorities and handoff

1. **P0 CLOSED (bounded automated scope):** documentation consolidation,
   workflow audit and exact-candidate broad regression completed. Explicit
   environment/physical and editorial gates remain open.
2. **P1 ACTIVE:** review accumulated Draft PR chain with one active target [#262](https://github.com/tiagosombrra/apmesh-modernization/pull/262).
   Verify ancestry and review order; separate #253 editorial branch.
   No automatic merges or closures of predecessor PRs.
3. P2: independent physical reviewers, #255.
4. P3: specific distribution decision and legal review, #250. No release.
5. P4: return to scientific priorities: genuine non-manifold models, complete
   patches, original native accepted/rejected results, separate QUAD/TRI
   experiments and adviser-aligned metrics. Studio is supporting tooling,
   not a substitute for this research. R2.8 remains blocked.
6. Parallel external gates: editorial #251; renew ten-file mirror and
   license evidence before expiry, #260 (target 2027-02-10).

Maintain only this operational plan. At each meaningful session verify
remote SHA and concurrent changes; update current status and the owning
issue with exact tested revision, runs, failures, skips and next action.
Historical preregistrations, results (including rejected trials), figures,
schemas, tests and original provenance remain preserved. Archive obsolete
instructions by immutable Git link; do not create another version or
instrumentation-only milestone. No private Drive URLs in public records.
No main merge, release, tag, installer, legal clearance or scientific
acceptance without the required authorization and evidence.
