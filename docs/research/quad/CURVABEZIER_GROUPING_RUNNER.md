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
