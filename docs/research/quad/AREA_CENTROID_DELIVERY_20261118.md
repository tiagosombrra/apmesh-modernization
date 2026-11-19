# Area-centroid UV policy: adopted experimental implementation and real comparison

Date: 2026-11-18 Fortaleza. Exact source `15e291579600a0a4b8076cab8d52f0c8841f3938`,
tree `57e98001503559e458bf42cb3e3a1b8e594d1686`, draft
[PR240](https://github.com/tiagosombrra/apmesh-modernization/pull/240).
[Evidence](evidence/AREA_CENTROID_DELIVERY_20261118.json) pins source/image/data
hashes, commands/log references, all measured stages and exact hosted results.

## Confirmed scientific scope

The user explicitly adopts signed-area centroid in UV as the experimental
interpretation of the1993 polygon-centroid wording, and requests real before/
after comparison. This settles the executable choice for this experiment.
It does not prove the historical software's equation; the1987 full-text and
complete historical numeric identity remain unverified. Do not ask again to
select this settled experimental formula or promote its result to full M1.

The new explicit selector `curved_bezier_article_front_area_centroid_v1` uses
the existing `ExperimentalInteriorPoint(...PolygonAreaCentroid)` implementation.
Its translated long-double triangle-fan moments, strict convex CCW/finite input
contract and relative tolerance1e-12 are reused unchanged. No fallback, threshold
adjustment or alternative formula is introduced. Calculate in UV, lift XYZ
analytically and apply the already confirmed five simultaneous mixed passes.

Keep `curved_bezier_article_front_vertex_mean_v1` executable for controlled
comparison. Other experiments still call their previous point rule; TRI defaults,
curve partitions/synchronization, native templates/order, prospective S<=1.5,
clearance0.2 and adaptive acceptance/stopping are unchanged. Root CMake adds the
existing point routine only to the opt-in QUAD engine. Configuration readers
accept the new explicitly named case; a TRI request follows its original path.

## Actual data and counterevidence

Compare the retained mean sourcebeb2aee with the final area source15e2915 using
the same input/settings, counts, connectivity, boundary and five smoothing passes.
Independently reconstruct each of222 actual source polygons and verify its
center against exact Fraction signed-area moments, separate from the C++ fan.

| Result | Step1 | Step2 | Step3 |
| --- | ---: | ---: | ---: |
| Source polygons | 4 | 62 | 156 |
| Area centers differing from vertex mean | 0 | 18 | 0 |
| UV sites changed after five passes | 0 | 271 | 0 |
| Nodes | 33 | 281 | 689 |
| QUAD / TRI | 24 /8 | 249 /52 | 630 /102 |

All original TRI OBJ files are byte-identical. All mixed face cycles, source
leaves, seed connectivity, prospective chosen polygons and original boundary
UV/XYZ remain identical. Only Step2 positions differ. The five-pass propagation
to271 interior sites does not add nodes, move contour sites or replace elements.

| Step2 diagnostic | Vertex mean | Area centroid |
| --- | ---: | ---: |
| Source-area sampled geometry RMS | 0.01289868039 | 0.01289667137 |
| Minimum physical angle, degrees | 9.58768997 | 9.59283006 |
| Minimum physical QUAD corner J | 0.224087726 | 0.223536909 |

The RMS/angle differences are small; minimum QUAD J worsens slightly. This is
not a general improvement, transition-quality solution or optimality result.
Steps1/3 are geometrically identical. Final Step3 mixed RMS0.009541730 still
exceeds TRI0.009310312 with unequal element counts. Do not infer causal QUAD
superiority or mixed adaptive convergence from these observations.

RMS remains a576-site sampled geometry distance in model units. Original TRI
global curvature errors stay0.314848/0.139436/0.0538754/0.0303172; actual mixed
global curvature error remains unavailable and mixed accepted epochs remain0.
The previous Step1/Step2 boundary explanation still holds: front contour8Q0T
versus2Q8T, and inner interface16->56 versus outer8->10. The centroid change
does not alter those decisions or resolve the measured sizing mismatch.

## Exact validation and closure audit

- Final local delivery baseline85/85; architecture/35 contracts/277 source
  anchors pass after explicitly refreshing the changed build/source hashes.
- Native MSVC Debug20/20, including existing two-rule analytic/malformed/D4
  controls. The existing point algorithm is not modified or reimplemented.
- Fresh application:183 prospective commits,186 pre-smoothing frames,15 actual
  mixed passes,11 front/clearance forgeries,5 smoothing forgeries and3 new point
  forgeries rejected, with nonempty physical-owner rollback. One new forgery
  replaces a real asymmetric Step2 area point with the old vertex mean.
- Original source contracts6 captures/3 reversed/54 negative controls; older
  live-pair application220 events/eight forgeries and nonempty rollback pass.
- New image's retained mean selector generates all eight OBJ scopes byte-
  identically to the prior source, establishing the old experiment control.
- Configured full changed-code clang-tidy passes application, entry dispatcher,
  runtime config and newly linked existing point implementation/header, using
  actual regenerated GCC compilation metadata. No suppressed diagnostics.
- Explicit three-file C++ formatting, eight-file whitespace, Python compile and
  staged whitespace pass. No required gate fails in this bounded change.
- Exact hosted run44440173309 passes all four checks. GNU ordinary, GNU
  ASan/UBSan and MSVC application reports agree on all stages/point counts and
  11+5+3 negatives/rollback. Hosted baseline85 and527 tooling Python controls
  pass. Frozen Eistute5/Book4 histories retain exact OBJ/acceptance/boundaries.

Native/source/analysis/control results all bind final15e2915; no previous
source validation is silently substituted for this new point policy.
Raw commands and logs are retained under `build/quad-area-centroid-20261118/`.

```text
python tools/validation_session.py run --scope delivery
cmake --build build/quad-contour-clearance-20261118/native-msvc --config Debug --parallel 2
ctest --test-dir build/quad-contour-clearance-20261118/native-msvc -C Debug --output-on-failure --no-tests=error
python tests/quad/test_article_front_application.py --exe build/quad-live-pair-20261117/msvc-build/bin/Debug/ap_mesh.exe --directory build/quad-area-centroid-20261118/exact/article
```

The existing point routine owns only local value vectors and returns a value;
dispatcher/front validation and staged physical publication/rollback remain.
Review covers code, source/order preservation, independent center controls,
complete histories, ownership, documentation and scientific scope. It does not
replace independent approval or close broader historical/native/CRT coverage.
Retain the prior full adversarial invalid-enum analysis finding and WSL output
publication failures for explicit disposition. No merge or whole-stage closure.

## Visualization and the next action

New personal Blender5.3:
`build/quad-area-centroid-20261118/presentation/QUAD_TRI_centroide_area_5_passadas.blend`.
Four scenes contain current TRI/mixed outputs, all real smoothing passes, six
mean-versus-area stage meshes and the earlier template catalog. The catalog is
explicitly labeled previous vertex-mean reference; it is not misrepresented as
regenerated area-centroid coordinates. The comparison render and UV plot are
inspected; the new file is observed open in its comparison scene in the GUI.
Previous files remain intact. Embedded guide explains RMS/global error and limits.

**One next action:** independent review of the complete static PR240 package,
including explicit disposition of the retained enum-analysis/WSL findings.
Then required exact research integration/post-merge gates. The adopted centroid
choice is settled for this experiment; historical identity and the later actual
mixed-global-error/adaptive package remain separate, scientifically bounded work.
No new balancing controller or broad flag sweep is introduced.
