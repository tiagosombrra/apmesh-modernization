# CurvaBezier grouping trial runner

Use a serial C++17 build with `AP_MESH_ENABLE_EXPERIMENTAL_QUAD=ON` and
Python 3. The runner uses the tracked CurvaBezier article-front configuration,
the Stage 3 retry 0 mixed mesh and its trace. Run from the checkout or pass
the full path to the script. The output directory must be new.

```text
python tools/quad_grouping_trial.py --exe <path-to-ap_mesh> --out <new-directory>
```

The runner generates the reference TRI and mixed histories, selects the
two adjacent groups on the new trace, and asks the native executable to
stage a detached candidate. The staging run must reproduce the reference
histories and original curve witness. The comparator uses the frozen
footprint and the two common grids. On eligibility, the runner replaces
`selected.obj` with the candidate. The original meshes and logs remain
available. See the [decision protocol](GROUPING_ADMISSION_AND_TRANSFER_20261124.md).

- `result.json` records the authoritative selection, with hashes of the
  reference and selected OBJ and native fronts. The runner records the baseline
  before staging and replaces the record before materializing `selected.obj`.
- `selection.json` records the leaf projection and the active size requests.
- `comparison-24.json` and `comparison-48.json` retain both comparison arms.
- `baseline.steps` and `staging.steps` retain native traces and meshes.
- `--control force-reject` verifies that the native attempt restores the
  reference owner and OBJ after a temporary candidate link. It then stages
  and measures a retry and retains the reference as selected. `--control protect-neighbor` injects one fine-size
  request and verifies the selector veto without generating a candidate.

The runner passes the plan path through `APMESH_QUAD_GROUPING_PLAN` only
to its staging subprocess. The experimental application accepts it on the
built-in CurvaBezier article-front area-centroid path. The native engine retains the experimental reference
owner during staging. The runner selects an OBJ for this one comparison.
The selected file does not represent a scientifically accepted adaptive epoch.


## Recovery after a stopped process

If the runner stopped after writing a selection record, or the selected copy
is missing, run:

```text
python tools/quad_grouping_trial.py --recover <trial-directory>
```

Recovery verifies the retained mesh, curve and front identities before
recreating `selected.obj`. A stopped candidate without a recorded selection
leaves the baseline authoritative. The recovery command reads the current
record format and should be used after the original process stops. The
protocol covers interrupted processes and makes no power-loss guarantee.

## Replay measured geometric size requests

Use a completed eligible grouped trial as input and select a fresh output
directory. The command recovers the recorded native identities and generates
matched successors, with the source contour fixed:

```text
python tools/quad_geometric_feedback_trial.py --exe <path-to-ap_mesh> --source <completed-trial> --out <new-directory>
```

For each source mesh it applies one split to each distinct actionable leaf,
uses the original 2:1 balancing and preserves the captured depth cap.
The runner retains the request and leaf traces, any staged candidate and
common-site measurements. The selected source remains authoritative during
the trial. A staged successor is an experimental comparison.

Optional feedback comparisons use the recovered arm. `--mode previous-search`
keeps the refined tree while replaying the original search boxes only after
exact seed and contour equality. `--mode curve-and-tree` uses one native
binary split per interval requested by the recorded geometric sizing replay.
`--mode guarded-curve-and-tree` measures the same inputs with the retained
guarded smoothing comparison and writes its control and guarded frames.
Compare each result against its recorded predecessor. The lookup replay and
the independent smoothing arms are research observations.


## Portable single-patch feedback

The same experimental entry can now reconstruct a predecessor directly from
an accepted TRI attempt on a single Bezier patch without requiring a grouping
plan. Pass the original indexed one-patch source and the step to reproduce.
The built-in Bezier remains available as a second input. This runs the
existing pilot with guarded predecessor and successor smoothing.

```sh
python tools/quad_portable_feedback_trial.py --exe <quad-ap_mesh> \
  --model builtin:curva_bezier --step 3 --out <new-dir>
python tests/quad/test_portable_feedback_application.py --exe <quad-ap_mesh> \
  --directory <new-dir>
```

The driver retains each invocation's plan, input, logs and output. The
native attempt requires byte-identical `tri.obj`, `source.obj` and
`source_tree.txt` from the earlier capture before applying requests.
It retains the selected step, attempt identity, complete cell layout and
leaf order, along with the original curve samples in the typed OBJ.
The integration test exercises CurvaBezier Step 3 and the original control
net of Ribbed Bracket patch 12 at Step 2 through one application image.
It also supplies a changed tree binding and requires rejection before
candidate generation.

Results report the native tree edits, capped requests, old/new curve
partitions, guarded smoothing frames and paired analytic samples.
A staged successor does not increment mixed adaptive epochs.

An explicit `--relative-tolerance` adds the experimental dimensionless
trigger. Each TRI and QUAD is scored by its existing sampled maximum
geometric distance divided by the median physical edge length of that
face. At most one seed of each type is chosen, with existing face order
breaking equal scores. A seed requires a score strictly greater than the
configured tolerance. The existing neighbor rule and original curve/tree
reconstruction apply to active requests. With zero requests the archive
contains only the reproduced source and a no-action result. There is no
default tolerance for this option. It measures geometric deviation and
leaves shape assessment to the independent staged-candidate reports.


## Read-only regional quality guards

`tools/quad_regional_quality_guards.py` compares two staged physical
OBJs on the same analytical patch. It requires `--profile` with a
nonnegative `max_face_growth` fraction and `regional_floors` for six
groups: `contour_edge_TRI`, `contour_edge_QUAD`, `contour_vertex_TRI`,
`contour_vertex_QUAD`, `interior_TRI`, and `interior_QUAD`. Each group
has a `min_angle_deg` floor and a `min_shape` floor. Shape is the existing
triangle score or the minimum scaled QUAD corner Jacobian.

A new group must meet both floors. For an existing group below either
floor, that minimum has to improve if the candidate remains below it.
An above-floor minimum can fall as far as the floor; counts below it
remain visible. The receipt records absent/replaced groups. Geometry,
sampled error and grading are reported on common sites. The assessment
does not publish a mesh, decide geometric admission or increment epochs.

Use `--source-bp` and optionally `--patch` for an indexed B?zier file.
The builtin CurvaBezier remains the default analytical source.

```sh
python tools/quad_regional_quality_guards.py <predecessor.obj> <candidate.obj> \
  --profile <profile.json> --source-bp <model.bp> --patch <index>
```


## Guarded advancing-front trace

A staged successor with guarded smoothing retains
`feedback/candidate_front/front.json` with the
`apmesh.quad.article_front_guarded.v1` schema. It contains the native
leaf boxes, initial QUAD cycles, UV vertices before smoothing,
ordered active edges and actual polygon transactions. The separate
`smoothing_comparison` directory keeps the birth geometry and native
guarded/unguarded observations. The guarded trace has a null smoothing
field. Unprotected article histories still retain their original frame
and smoothing format.

The portable application test verifies the guarded trace vertices and
ordered face cycles against the actual pre-smoothing OBJ.


## Additional local-pair comparison

The portable runner's opt-in `--additional-pairs` applies only to the
successor build. It runs when the original proposal would retain a TRI.
It enumerates the apex and companion sets using the original first
nonempty local search windows, keeps S <= 1.5, and takes the lowest score.
Exact ties retain apex ID, side, and companion ID order. The original
TRI remains the fallback. Base selection, initial templates, original
curves and guarded smoothing retain their existing rules.

The guarded trace uses `apmesh.quad.article_front_guarded_pairs.v1` and
records the extra first/second triangles and score when a replacement
occurs. The original best TRI and its two prospective alternatives
remain in the same transaction. This is a reversible experimental
comparison. Regional shape and admission are observed separately.

Add `--additional-pair-error-limit 0.045` to trial the common development
ceiling. The screen uses the existing five bilinear source samples of a
prospective QUAD. It divides their maximum physical deviation by the
length of the selected physical edge. The result is dimensionless. The
screen runs only on additional shape-eligible pairs, before comparing S.
An unavailable chord or an excessive deviation excludes the pair.

The `apmesh.quad.article_front_screened_pairs.v1` trace records the limit
and every evaluated pair with its S score and relative deviation. Existing
trace schemas remain available when the ceiling is omitted. The portable
regression includes the CurvaBezier Step 3 selective run and the Ribbed
Bracket Step 2 original request profile. This ceiling does not decide
mixed epoch acceptance or alter the reference TRI generator.

The optional `--certify-boundary-refinement` checks the ordered, native
curve partition before staging a successor. The original sampled sites
must keep their curve, parameter, UV, XYZ and source ID. Each requested
interval must have one inserted analytic site strictly between its original
endpoints, with an ID beyond the previous mesh's IDs. The input owner and
attempt are bound by the existing source replay. The resulting
`boundary_refinement.json` records the parent endpoint IDs and inserted
site of each split. It is evidence of refinement, with no epoch admission.

For a directed comparison, an experimental native successor plan may add
`group_feedback_parent u0 v0 u1 v1` when the boundary certificate is enabled.
The requested parent must contain four immediate native leaf children. The
application groups them after all native refinement requests and before
template dispatch. It refuses affected refinement requests and verifies
2:1 edge balance. The optional `grouped_parent.json` records the selected
parent and leaf counts before and after grouping. The directive does not
select a parent automatically or decide mixed admission.
