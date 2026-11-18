# Confirmed mixed UV smoothing: implementation and bounded results

Date: 2026-11-18 Fortaleza. Draft [PR240](https://github.com/tiagosombrra/apmesh-modernization/pull/240).
Exact final source `beb2aee2605110ec5c7a542bb45b10cb8c876b40`, tree
`99da71296c0ebee57a02d762ff45a0bf4cb0bd3f`. Implementation is `c3ddc06`;
the final child changes only the retained CMake build-input inventory hash.
[Machine-readable evidence](evidence/MIXED_UV_SMOOTHING_20261118.json) records
source, image, inputs, commands, logs, all pass measurements and artifact hashes.
This is an explicitly confirmed experimental scientific interpretation, not a
refactor or proof of numerical identity with the historical planar method.

## Adopted contract

The user explicitly adopts the descriptive UV/distinct/five-simultaneous proposal.
Average each distinct other vertex of incident TRI/QUAD elements once, including
opposite QUAD corners. Exclude the node itself. Accumulate in retained-ID order;
compute every position from the beginning of the pass, then apply together.
Execute exactly five passes; fix original contour vertices. Recalculate XYZ on
the original Bezier patch after every pass, preserving exact source XYZ at the
fixed boundary. No relaxation factor, best-pass selection, new quality threshold,
curve rediscretization or mixed acceptance/adaptation/stopping rule is introduced.

The printed-p290 passage describes a planar incident-element coordinate average,
four/five repetitions and fixed original contour. It does not settle every
curved-surface/multiplicity/update-order detail. The adopted interpretation is
explicit; historical center identity remains a separate unresolved question.

## Code and ownership audit

`research/quad/mixed_uv_smoothing.h` holds values, sorted distinct neighborhoods
and complete snapshots. It validates finite inputs, TRI/QUAD indices, repeated
vertices and edge incidence/winding. A required callback validates each complete
pass before its history is retained. Exceptions destroy local values; the input
and existing physical owner are untouched. No shared ownership is introduced.

The application calls it only in the opt-in prospective article-front path after
the complete mixed contraction. Existing facet orientation/area, positive QUAD
UV-corner tests, physical corner quality and existing UV-overlap audit are reused
on every pass. Owned physical nodes/faces are built only after all five succeed;
the existing candidate commit and nonempty rollback remain intact. Selection
score S<=1.5, contour-clearance factor0.2, quadtree/templates, source ordering and
original TRI behavior are unchanged. No new command-line smoothing switch or
reinterpretation of source-TRI smoothing flags is introduced.

Front history retains original coordinates: all183 commits and186 pre-smoothing
OBJ frames are byte-identical to11dcaa7. New `smoothing_1.obj` through
`smoothing_5.obj` in each stage directory contain the actual native passes;
`front.json.smoothing` records fixed IDs/policy/UV positions. The main mixed OBJ
matches pass5. No animation interpolator is presented as native generation.

## Measurements, including counterevidence

Same builtin curva_bezier and retained configuration/576-site measurement rules.
The table compares each mixed output immediately before and after five passes.
RMS is a source-area-weighted sampled geometry distance in model units, not a
percentage or the adaptive global curvature error. Angles are in degrees.

| Stage | Geometry RMS before -> after | Global min angle | Boundary min angle | QUAD corner J min | Max edge ratio |
| --- | --- | --- | --- | --- | --- |
| 1 | 0.02366862 -> 0.02216857 | 28.551 -> 31.549 | 31.126 -> 31.549 | 0.5120 -> 0.4780 | 4.596 -> 6.233 |
| 2 | 0.01170360 -> 0.01289868 | 4.824 -> 9.588 | 9.832 -> 15.626 | 0.3945 -> 0.2241 | 9.239 -> 8.481 |
| 3 | 0.01182093 -> 0.00954173 | 1.418 -> 1.870 | 10.367 -> 9.149 | 0.3284 -> 0.2108 | 15.084 -> 11.053 |

Counts/connectivity remain33/281/689 nodes,24/249/630 QUAD and8/52/102 TRI.
Minimum global angle and TRI area-Q improve in all three stages; QUAD minimum J
falls in all three. Stage2 RMS worsens, stage3 boundary angle worsens and stage1
maximum edge ratio worsens. Intermediate values are not monotonic; all five
approved passes are retained. This does not solve boundary/interior imbalance
or demonstrate overall mesh-quality improvement.

For the final stage, original TRI geometry RMS0.009310312 versus smoothed mixed
0.009541730 coexists with min angles1.709deg versus1.870deg and edge ratios5.305
versus11.053. Element counts differ; this is not a count-matched superiority test.
Original TRI global curvature errors remain0.314848/0.139436/0.0538754/0.0303172.
Actual mixed global curvature error remains unavailable; mixed accepted epochs0.

## Executed checks and failures

- Final beb2aee local delivery baseline85/85, including retained architecture
  and35-contract/277-anchor traceability checks. First c3ddc06 run stopped before
  CTest because the retained CMake hash was stale; preserve its failed report.
- Native MSVC Debug20/20, five malformed controls, injected pass3 exception,
  deterministic fresh retry, opposite QUAD corner, fixed boundary and simultaneous
  arithmetic. The tiny arithmetic fixture does not claim geometric acceptance;
  the application supplies actual geometry validation.
- Fresh original-curve application:183 prospective commits,15 smoothing passes,
  eleven rejected front/clearance forgeries, five smoothing forgeries and actual
  nonempty physical-owner rollback. Independent Bernstein lifting and synchronous
  neighborhood recomputation agree; preflight/final UV difference2.22e-16.
- Original source-boundary contracts:6 captures,3 reversed,54 negative controls.
  Old live-pair path:220 events,8 forged records rejected, nonempty rollback.
- Configured clang-tidy on full changed application, new header and new native
  fixture passes using actual GCC compilation metadata. No diagnostic suppression.
- C++ format, five-file whitespace, Python compile and staged whitespace pass.
  Initial application build failure (array versus FaceUv) is retained and corrected.
- Exact hosted run44408768431: all four GNU/MSVC/sanitizer/frozen-TRI/baseline jobs
  succeed. GNU ordinary and ASan/UBSan application reports agree on all three
  stages,183 commits,11+5 forgeries and rollback; Windows agrees as recorded.

Native/application/analysis executions bindc3ddc06. Reuse atbeb2aee is explicit:
the only diff is the architecture JSON hash; all code/test/configuration/image
bytes are unchanged. `preservation-and-reuse.json` verifies those identities.
The full85-test baseline and hosted tests execute on finalbeb2aee itself.
The previous full adversarial-dispatcher analysis still reports the deliberately
out-of-range enum test; it is not rerun, hidden or counted as green here. Prior
WSL output-publication failures and wider native/historical obligations remain.

Commands and raw retained logs are under `build/quad-mixed-smoothing-20261118/`:

```text
python tools/validation_session.py run --scope delivery
cmake --build build/quad-contour-clearance-20261118/native-msvc --config Debug --parallel 2
ctest --test-dir build/quad-contour-clearance-20261118/native-msvc -C Debug --output-on-failure --no-tests=error
python tests/quad/test_article_front_application.py --exe build/quad-live-pair-20261117/msvc-build/bin/Debug/ap_mesh.exe --directory build/quad-mixed-smoothing-20261118/exact/article
```

## Visualization and closure audit

New personal Blender5.3 file:
`build/quad-mixed-smoothing-20261118/presentation/QUAD_TRI_suavizacao_5_passadas.blend`.
Three scenes show eight actual TRI/mixed stage outputs,18 before/pass states,
and the retained18-panel TRI/QUAD/source-polygon catalog. The initial step is
explicitly unsmoothed; the later three stages use pass5. Two rendered views are
inspected and the new GUI file is observed open. Embedded Portuguese guide
defines RMS/global curvature error/Q/J/UV and the negative results. Previous
presentations remain historical and are not overwritten.

Code, arithmetic/negative tests, value ownership, complete histories, boundary
identity, documentation and scientific scope are audited for this slice. It is
implemented and tested, still draft/unmerged. Independent review, the old enum
analysis disposition, historical center identity, general geometry/full native
CRT/oracle scope and exact research-integration/post-merge gates remain open.
No whole-stage closure or modernization-main change is claimed.

**One next action:** resolve the retained template-center interpretation against
the primary article/source. Explain any remaining scientific alternatives before
changing the current vertex mean. Then finish independent static-package review
and exact research integration before the separately aligned mixed-global-error
and actual mixed adaptive package. No new balancing law or broad flag sweep.
