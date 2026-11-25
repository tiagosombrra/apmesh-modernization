# Mesh Studio — current state, runbook and plan

**2026-11-25 | Research draft | Active delivery: integrated Bézier source workspace.**
This is the sole operational plan. [History](HISTORY.md) preserves previous
checkpoints and their evidence. The [evidence registry](EVIDENCE_REGISTRY.json)
is an immutable historical snapshot; its P0_ACTIVE / NOT_RUN fields describe
its pre-run state, not the current implementation.

## Current state and useful capabilities

Audit base: `9bc721ab1fb212c9449702a2279268c636d7976b`.
[PR #262](https://github.com/tiagosombrra/apmesh-modernization/pull/262) remains
the active Draft review target. P0's bounded automated stabilization and P1's
integration proposal are historical completed scopes. The source workspace is
**IMPLEMENTED, REVIEW CANDIDATE**. Local feature and browser checks pass; the
full local Python run still has two LaTeX environment failures. Exact delivery
SHA and hosted results are recorded in the owning PR before qualification.
No previous static certificate covers a changed build.

| Available at the audit base | Scope |
| --- | --- |
| Paired XYZ / UV views, face selection and camera recipes | Controlled P1 and staged research candidates; source identity is preserved |
| Original native TRI scene and identity inspection | Retained accepted Eistute / Book evidence, with manual report import |
| Vector publication and Python metrics | Source-bound discrete observations; editorial acceptance remains separate |
| Local static reviewer | Loopback frontend and API on one port; no Vite server required |
| Integrated Bézier source inspection | Local BP import, authored Four-Sheet example, XYZ preview, patch UV, declared incidence/orientation and source-bound CSV |
| Visible workspace navigation | Bézier sources, original TRI and controlled/staged mesh views; one retained native import |

## Audit findings and decisions

The following findings refer to the immutable audit base, not to unmeasured
results of this delivery. Exact source and historical conclusions remain in the
[previous runbook](https://github.com/tiagosombrra/apmesh-modernization/blob/9bc721ab1fb212c9449702a2279268c636d7976b/docs/mesh-studio/README.md)
and [frontend entry](https://github.com/tiagosombrra/apmesh-modernization/blob/9bc721ab1fb212c9449702a2279268c636d7976b/tools/mesh_studio/web/src/App.tsx).

| Priority | Evidence at the audit base | Decision |
| --- | --- | --- |
| High | AGENTS Studio checkpoint limits feature work during P0; README lines 121–132 closes P0, while lines 379–395 defer Studio work behind scientific and external gates | Continue bounded product engineering; retain each scientific, physical and distribution gate for its own scope |
| High | README lines 238–249 records a separate Four-Sheet HTML with stub-DOM tests and no actual Chromium run | Integrate source inspection into the existing app and verify the user flow in a real browser |
| High | App.tsx starts with P1 at line 19; original TRI is a lower expandable section, and native identity uses a query flag at lines 172–188 | Make source, native and candidate workflows discoverable; reuse existing native components |
| Medium | App.tsx shows an unconditional integrity label and an R1 / PROTOTYPE label at lines 125–145 | Derive integrity from loaded data and use a current product description |
| High | NativeAcceptedTriViewer.tsx sets Z view-up after fitting a default Z-facing camera; screenshots show an empty XYZ view although counters pass | Set a nonparallel camera direction before fitting; require actual rendered-face pixel coverage |
| Medium | The 408-line runbook mixes live work with repeated historical checkpoints | Keep one finite delivery here; retain the complete previous text by immutable link in History |
| High for integration | README lines 140–177 documents a stacked PR chain, unrelated ancestry and a capped comparison with main | Preserve the review target; an eventual integration requires a complete, isolated source delta |

## Active delivery: Bézier source workspace

**Classification: engineering-only, read-only source inspection.** The user can
open a Bézier source, inspect its patches and shared curves, follow orientation
and export the observed incidence information inside the existing Studio.
This does not execute or modify APMesh generation or its acceptance policy.

The implementation contract is:

1. Provide a visible source workspace and local `.bp` import, with the authored
   Four-Sheet example available for immediate inspection.
2. Parse the supported format strictly: finite coordinates, valid integer
   indices, complete control nets and explicit input limits. Reject malformed
   files with a useful error and allow a subsequent valid import.
3. Identify curves by ordered control indices, allowing reversal. Coincident
   coordinates with different indices must remain different source identities.
   Count distinct incident patches separately from side occurrences.
4. Allow patch and curve selection, patch visibility, and canonical parameter
   inspection with the corresponding local parameter for every orientation.
5. Label the surface display as sampled source geometry. Display tessellation
   is not native TRI, QUAD, an accepted adaptive epoch or a continuous error bound.
6. Export incidence CSV with source metadata and orientation information. A
   computed hash identifies the imported bytes; it authenticates an external
   source only when checked against an independently retained reference.
7. Preserve the existing candidate and native inspection paths. Update integrity
   states only after the associated data have actually loaded and passed checks.

### Acceptance and current validation

The implemented entry is `/?workspace=bezier`; the other visible entries are
`/?workspace=mesh` and `/?workspace=native`. The legacy `?nativeScene=1` link
still works and shares the same native panel. Opening a source workspace does
not load the mesh API. File reads remain in the browser and later imports win
over stale asynchronous reads. BP limits are 2 MiB, 128 patches and 20,000
controls. The profile is indexed, non-rational bicubic BP; the CSV explicitly
records `DECLARED_BP_CONTROL_IDS`, not native post-loader topology.

Local validation on the delivery source uses Node 24.22.3 / npm 11.19.1,
Python 3.12.14 and repository Playwright 1.56.1 / Chromium 141.0.7390.37.
These are measured local environments, not the supported pinned 22/10/3.13
reviewer certificate. The owning PR records the final commit and CI disposition.
The [validation receipt](evidence/BEZIER_SOURCE_WORKSPACE_20261125.json) binds
implementation files, new static inventory, commands and retained failures to
their hashes. It does not turn a skipped or failed check into a pass.

| Actual local check | Result and limit |
| --- | --- |
| `npm run test:contracts` | Existing R2.6/R2.7 contracts, 8 report-audit tests and 13 new Bézier tests pass |
| TypeScript and production Vite build | Pass; dependencies and package lock unchanged; 7 rebuilt static assets have a new inventory |
| Affected development browser suite | 39 pass: 12 source-workspace tests, 18 existing fast checks and 9 native scene checks |
| Built, guarded single-port browser | 29 pass for source workspace, P1 and native scene; this does not certify the official install environment |
| Original Eistute/Book replay | Retained 1168/4256 TRI, 4/28 patches, source IDs and 40/336 local seam segments; post-repair screenshots inspected, zero JavaScript errors |
| Full local Python discovery | 614 enumerated: 610 pass, 2 fail, 2 skip. Both failures are missing `pdflatex.fmt`; skips require Python 3.13 and a specific historical corpus. Full local regression is not green |
| Dependency-lock audit / whitespace | Pass; no dependency or native production change |

The initial Python attempt aborted without an X display. A local Xvfb TCP
display allowed the complete run; VTK checks then passed. The incomplete TeX
installation remained failed after `fmtutil-user` produced zero formats. Tests
and tool discovery were not weakened. The first browser run also exposed a
test-only regex reading the `t` in `C(t)` instead of coordinates; it was fixed
without changing the independent analytic expected values.

The native XYZ pixel regression failed on the previous camera (0.1074% filled
coverage for both synthetic fans, required >1%), then passed after the repair.
Actual historical native screenshots were inspected separately; synthetic
camera controls do not establish new C++ science. A late-file-read test now
waits for the stale digest and React frames before checking the selected source.

Required controls include the original Four-Sheet counts (52 controls, 4 patches,
13 curves and one four-patch shared curve), reversed P1 orientation, and a
negative case that duplicates common indices while retaining equal coordinates.
Also exercise invalid/truncated input, non-finite values, out-of-range indices,
input limits, and successful recovery after an invalid import.

The browser acceptance flow opens the example, selects patches and curves,
changes visibility and parameter, imports a file, handles a rejected import,
and exports incidence data. Confirm the existing candidate/native entry points
remain usable. Type checking, production build and the affected contracts and
browser tests are required. Physical acceptance is reported separately.

## Delivery sequence

Only the first row is active. Each later item requires its own concrete source
inputs, bounded change and relevant validation; it is not an automatic audit queue.

| Order | User capability | Dependency and completion criterion |
| --- | --- | --- |
| Current | Integrated Bézier source workspace | Available authored source; the contract and browser flow above pass on the delivery revision |
| Next | Open the original native corpus with fewer manual steps | Reauthenticate the retained Eistute / Book source bundle and import compatible scene/publication files together, retaining original model/patch/curve/sample identities |
| Following | Compare source-bound samples and export figures / metrics | Explicitly comparable evidence; every result retains source, orientation and observation scope |
| MODEL-dependent | Inspect Four-Sheet native TRI and later adaptive evolution | M0/M1 and actual accepted/rejected native evidence; multiple epochs or LOD require their own demonstrated lineage |

## Independent gates and retained limits

| Gate | Current evidence and scope |
| --- | --- |
| MODEL M0/M1 | At [MODEL #225](https://github.com/tiagosombrra/apmesh-modernization/pull/225), revision `07ca312d01f960669b1dc09a2cb30b1aa9d03165`: full-checkout M0 BLOCKED, Four-Sheet native M1 NOT RUN. Recheck that owning branch before admitting new results. These are not prerequisites for read-only source UI engineering |
| Native science / R2.8 | Eistute 1168 faces / 4 patches and Book 4256 / 28; only accepted global step [1] each. No second qualified epoch, certified LOD descendants, continuous CAD error bound or inferred physical welding |
| Physical acceptance | [#255](https://github.com/tiagosombrra/apmesh-modernization/issues/255): independent physical Windows/Linux review remains NOT RUN; automated Chromium does not replace it |
| Distribution | [#250](https://github.com/tiagosombrra/apmesh-modernization/issues/250): specific artifact and human legal decision remain open; the spark-md5 alternative is not elected and the full PyMuPDF profile is not cleared |
| Editorial | [#251](https://github.com/tiagosombrra/apmesh-modernization/issues/251): adviser/venue review pending; the distinct print-layout work in PR #253 is not silently included |
| Evidence continuity | [#260](https://github.com/tiagosombrra/apmesh-modernization/issues/260): ten-file mirror and licensing evidence expire in February 2027; retained renewal target is 2027-02-10 |

No main merge, tag, release, installer, legal clearance or scientific admission
is implied by this engineering delivery. Existing scientific criteria and native
production behavior remain unchanged.

## Supported local review

Python 3.13, Node 22 and npm 10. From the repository root (Windows: substitute
`py -3.13` for `python3.13`):

```sh
python3.13 -m tools.mesh_studio.local_reviewer_launcher build
python3.13 -m tools.mesh_studio.local_reviewer_launcher preflight
python3.13 -m tools.mesh_studio.local_reviewer_launcher serve
```

Open http://127.0.0.1:8765/. Stop Vite on port 5173 first. The supported
reviewer is loopback-only. Its hash-locked minimal API environment is separate
from the full scientific/PDF/VTK environment.

For original-source review, extract the verified ten-file corpus into
`build/v59-native-reviewer/`. In `tools/mesh_studio/web`, install Chromium using
`npm exec playwright install chromium` (Linux may need `--with-deps`), then:

```sh
python3.13 -m tools.mesh_studio.v59_reviewer preflight
python3.13 -m tools.mesh_studio.local_reviewer_launcher original-smoke
```

The R2 physical-review kit requires its exact historical checkout
`4f361d9b1e754c1e128ae74a42eb4173822bcaf6` and its source corpus. Preserve the
revision guard and reviewer attestation, 13 controls and OS/GPU evidence.
See the [static review protocol](V5_11_STATIC_SINGLE_PORT_REVIEW_PROTOCOL_20261123.md)
and the [historical handoff](https://github.com/tiagosombrra/apmesh-modernization/blob/9bc721ab1fb212c9449702a2279268c636d7976b/docs/mesh-studio/README.md#p2-handoff-verification--2026-11-24).
A new workspace build does not inherit that kit's certificate.

## Architecture and regression

Python inspection, topology, metrics and publication live in `tools/mesh_studio`;
React/TypeScript/vtk.js live in `tools/mesh_studio/web`. VTK remains the default
native picker; experimental BVH and synthetic stress are opt-in. Preserve source
UV/XYZ and patch-local identities. Reuse native seam inspection rather than
introducing another interpretation of its evidence. C++ and [QUAD science](../research/quad/STATE.md)
retain their separate review routes.

Local regression commands from the repository root:

```sh
python -m tools.mesh_studio.dependency_lock_audit
python -m unittest discover -s tools/mesh_studio -p 'test_*.py' -t . -v
```

Use the platform-specific full research hash lock; Linux VTK may require Xvfb.
In the web directory run `npm ci --no-audit --no-fund`,
`npm run test:contracts` and `npm run build`. Broad developer browser tests
need same-run native artifacts; static reviewer tests use the retained original
corpus. Report absent dependencies, failures and skips explicitly.

Existing validation, fast-web, static-reviewer, installed-license and
notice-candidate workflows keep their distinct scopes. Reuse unchanged evidence
by identity and run the gates affected by the actual delta. Never weaken
negative controls or claim unavailable checks passed. Required unmeasured gates
keep the corresponding closure and integration open.

## Historical baseline and handoff

P0 tested implementation: `9977f2a88b199bbed39fd9583cbb58737a4db638`.
[Full regression](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/45363214163)
passed 4/4 jobs: Linux 609 Python / 5 skips, Windows 603 / 11 skips,
native capture/parity and 63 Chromium tests. [Fast web](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/45363214119),
[static reviewer](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/45363214240)
and [installed-license audit](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/45363214125)
retain their revision-specific results. Optional JSON Schema/LaTeX and physical
GPU coverage were not claimed. The old seven-asset inventory hash remains
`ad6c4627090a335c0ed7e3bf1bae0c0d062ed1e48249f120b10f3ba8ff8a85f5`;
it is a historical identity, not the expected hash of a changed frontend.

The complete P1 ancestry review, P2 kit caveats, Four-Sheet inspection, native
curve-count audit and 15-case OCCT preparation remain in [History](HISTORY.md).
Those preparations do not count as new native generation. Preserve failed and
rejected observations, raw provenance, fixtures and immutable evidence records.
At delivery, recheck remote changes, record the tested revision and remaining
limits, and update the owning review item. Keep private archive URLs out of
public records. Do not retarget the accumulated PR ancestry to main.
