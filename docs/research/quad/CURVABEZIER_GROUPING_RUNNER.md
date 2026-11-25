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

- `result.json` binds the selected OBJ hash to the reference or candidate.
- `selection.json` records the leaf projection and the active size requests.
- `comparison-24.json` and `comparison-48.json` retain both comparison arms.
- `baseline.steps` and `staging.steps` retain native traces and meshes.
- `--control force-reject` stages and measures a candidate and retains the
  reference as selected. `--control protect-neighbor` injects one fine-size
  request and verifies the selector veto without generating a candidate.

`QUAD_GROUPING_PLAN` is the internal opt-in path used by the runner. It
only applies with `quad_uv`, the article-front area centroid profile and
built-in CurvaBezier. The native engine retains the experimental reference
owner during staging. The runner selects an OBJ for this one comparison.
The selected file does not represent a scientifically accepted adaptive epoch.
