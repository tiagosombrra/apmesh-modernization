# Mesh Studio R2.7.19 — experimental native nonwelded identity inspector

**Date:** 2026-11-17. **Scope:** actual compiled original serial TRI
Eistute/Book native accepted source evidence; read-only browser import.
**Branch:** `feature/mesh-studio-r27-bvh-20261116`.
**PR:** #239 draft/unmerged, not `main`.

## Why this is not an overlay of the existing viewer

The normal Mesh Studio P1 XYZ/UV viewports and staged candidate scenes
are **different scientific inputs** from the actual serial Eistute
and Book accepted adaptive steps. Assigning Eistute/Book original
source-curve slot or node IDs to a P1 face would create false
provenance. R2.7.19 therefore displays an explicitly separate
symbolic **source-incidence fan** and read-only original local node
table; it does **not** position natively accepted Eistute/Book
triangles inside the current P1 XYZ/UV canvases.

The normal viewer, its source face picking, VTK native default,
camera state, fallback, optional BVH flags and model catalog are
unchanged.

## Scientific source and export protocol

The original R2.7.12 postcommit native NDJSON, native process stderr,
full source-bound accepted receipt, original model configuration
and native experimental binary remain independently verifiable.
R2.7.14 measured canonical original source curve patch incidence;
R2.7.15 measured original face UV and XYZ sampled chains;
R2.7.16 derived read-only source-scoped sample groups;
R2.7.17 observed original curve endpoint IDs and actual accepted
UV(0,0) identity; R2.7.18 observed real provisional
`Boundary::close()` executions and live postcommit
`SubMesh` C++ node pointer relations.

`tools/mesh_studio/native_identity_inspector.py` rereads
and independently verifies **all original source evidence** through
the existing qualified native audit functions; it joins
R2.7.16 and R2.7.18 **only by native model, real accepted
adaptive step and exact original accepted NDJSON SHA-256**.
It refuses missing original patch-node owners, incomplete sampled
incidences or inconsistent actual native corner IDs.

It emits one bounded, separate read-only JSON bundle
(`build/r2719-native-inspector.json`). Each qualified source
curve contains its **original source curve ID/slot**, complete
original incident patch slots, sample ordinal and canonical
parameter, per-patch **original native logical node ID**, original
XYZ and original local edge slot. Only the accepted UV(0,0)
sample receives the actual C++ owner adjacency and C++ pointer
reuse observation. Non-observed samples explicitly contain
`null`, **not false**. The export also retains the original
model input/config/NDJSON/process stderr digests and a
separate provenance classification.

No new original native ID is created; no source samples are
welded or renumbered; no physical C++ pointer addresses or
failed/unauthenticated candidates are serialized. No synthetic
test fixture is included in the real native artifact.

## Opt-in UI and limitations of browser trust

The new browser component remains **completely absent** unless
the user explicitly opens Mesh Studio with the URL query
`?nativeInspector=1`. No native artifact is automatically
downloaded or loaded from an unrelated model.

Inside this independent panel, import the R2.7.19 **JSON**
from the preserved GitHub Actions artifact. Select original
Eistute/Book model and truly accepted native step, original
source curve, source sample ordinal and original incident patch.
The symbolic SVG fan keeps **all** original 4/28 patch
incidences and does not claim Euclidean positions. The read-only
table displays original patch-local IDs, sampled canonical t,
XYZ and the direct C++ owner observation (if it was actually
recorded for that precise native corner).

`nativeIdentityContract.ts` performs bounded structural
validation on the client: known real source model sizes,
source-specific SHA-256 syntax and accepted step, complete
unique patch incidences, every sample membership, original
native node ID relation classification, finite XYZ/parameter,
actual pointer witness only at the witnessed corner, and all
no-welding/no-LOD exclusions. The browser **does not** rehash
the raw original NDJSON from this JSON import. Its validation
establishes structural compatibility only, **not independently
authenticated scientific provenance**. Scientific
provenance requires the accompanying original raw sources
and the independent original native Python/C++ CI audit.

The inspector is designed to have **zero runtime dependency**
on the current API's P1 model, no native file upload to the
backend, no C++ mesh mutation and no implied source equality
with the two existing VTK viewports.

## CI and reproducibility

The existing isolated native job must execute actual original
Eistute/Book C++ serial generator acceptance first, then
R2.7.12–R2.7.18 independent source gates, and finally:

```bash
python -m tools.mesh_studio.native_identity_inspector \
  --directory build/r2712-native-evidence \
  --output build/r2719-native-inspector.json
```

The original JSON bundle is a GitHub Actions artifact
`mesh-studio-r2719-native-inspector-<source-sha>`
(14-day retention). Independent Linux/Windows Python
unit suites include **6 synthetic negative controls** for
the R2.7.19 exporter. The actual Chromium browser suite
includes **4 synthetic UI tests** checking hidden-by-default
behavior, independent viewer preservation, 4-owner and
28-owner source fan selection, per-node ID changes, pointer
unknown state and explicit rejection of false welding and
missing source membership. The UI tests do **not** claim
to have run Eistute/Book scientific geometry.

For a local demonstration, run the unchanged Mesh Studio
Vite/API workflow, open `http://127.0.0.1:5173/?nativeInspector=1`,
download/extract the current R2.7.19 GitHub Actions
manifest artifact and select its sole JSON in the import input.

## Original scientific export observed (2026-11-17)

The authentic original serial native source job in
[GitHub Actions #44213335142](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/44213335142),
at exact implementation SHA
`8dd59928e3368336de8846de3d1a9755b1eb0488`,
completed **SUCCESS** and generated separate original inspector
artifact [#14386564751](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/44213335142/artifacts/14386564751).

The original source-bound archive was downloaded, inspected,
then archived in the authenticated personal doctoral Drive
`Doutorado/DOUTORADO_APMESH_ACOMPANHAMENTO/05_Experimentos_e_Resultados`
and downloaded again. Original Actions artifact and Drive
readback ZIP byte-hash **exactly match**:

`a092bfba0ab436b05b6e8ffcd1c40652cb42f054da708d596ad3125ff417b242`

ZIP length **4,725 bytes**; contained original bounded
`r2719-native-inspector.json` manifest length **204,629 bytes**
(SHA-256 `74a35639a7f3ecbebc0ceaca7e4a8dd8528683350a90070e6242518461e30962`).
The manifest's original native source SHA is separately retained:

| Real source | Accepted TRI step | Original source NDJSON SHA | Source curve / owners / samples |
| --- | ---: | --- | --- |
| Eistute | **1** | `57eaa949e382aee4537325e7214694fc250d1cf20eeec96beeb6f923f6b518e6` | slot **3**, **4** source patches, **11** source samples |
| Book | **1** | `e5be7af26f0064a01929e33f7db9129a50a17959d20d743f09c224551358524a` | slot **3**, **28** source patches, **13** source samples |

In both authentic native sources the first canonical sample has
**different logical original native IDs across the incident
patches** (example Eistute **21 vs 90**, Book **141 vs 181**);
all other original source samples in the shared curve have the
same logical ID across those patches. Only the actual accepted
UV(0,0) source-sample rows have true live C++ SubMesh owner
observations; later sample rows have **null/unknown C++ pointer
identity**, not an inferred false or a welded-node claim.

The real manifest separately passed an independent local
structural preflight for unique patch incidence, monotonic
source parameters, exact source member counts, observed
native-ID relation classes, finite original XYZ and explicitly
restricted C++ witness fields. This is **manifest structure
and original source provenance verified by the native job**;
it is not a browser UI test or physical GPU qualification.

The new independent scientific regression suites on
this run returned **Linux: 322 Python tests, 4 optional skips
PASS**; **Windows: 322 tests, 10 environment skips PASS**.
The original C++ serial generator also independently re-passed
the R2.7.13 OFF/ON source file byte parity.

## Qualification status

**Await the exact four-job GitHub Actions run** before marking
R2.7.19 certified. The source-bound native artifact, its own
source SHA and actual model/sample/patch counts must also be
checked. A green build alone is not a claim that the browser
has independently authenticated the original raw NDJSON.

The scientific LOD R2.8 remains BLOCKED: no second genuine
native accepted epoch per source model, no certified
cross-epoch face/curve descendants, no continuous geometry
error bound and no physical Windows GPU/RSS/VRAM validation.
The original VTK picker stays the default; both experimental
BVHs stay opt-in/bounded; no release, tag or merge to `main`.
