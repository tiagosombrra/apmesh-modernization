# Controlled curved QUAD application

Build serial C++17 with `AP_MESH_ENABLE_EXPERIMENTAL_QUAD=ON`,
`AP_MESH_USE_MPI=OFF` and `AP_MESH_USE_OPENMP=OFF`. The default build keeps
the original TRI dispatch and refuses experimental QUAD execution.

Run `ap_mesh --config configs/quad/curved_patch.conf` from the repository root.
The output prefix must have an existing parent directory and no existing OBJ.
This explicit case uses the original `Models3d::ModelCurvaBezier` surface,
16 oriented source boundary intervals, depth-2 interior with one depth-3 leaf,
and the named experimental vertex-mean rule. It does not run AdaptCurve,
reproduce the 1993 algorithm or implement repeated adaptive history.

The app creates a connected, typed physical SubMesh, validates UV coverage,
seam winding, pairwise overlap, physical facet orientation/quality and exports
an OBJ with UV records and separate QUAD/TRI_AFT groups. Successful publication
registers the owning mesh with the real Patch. No global multipatch welding is
performed. Whole-surface Jacobian or self-intersection certification is open.

Set `QUAD_VERIFY_ROLLBACK=1` to retain a first valid, nonempty generation and
inject failure before a second candidate is published. Expected exit is 1,
with `QUAD_ROLLBACK preserved=1 previous_nonempty=1`; the first OBJ and accepted
owner/observers remain valid. This is a rollback test, not an adaptive epoch.

`python tests/quad/test_controlled_application.py --exe <ap_mesh> --directory <results>`
executes the application and independently checks the production control net,
UV/XYZ orientation, topology and original boundary, plus refusal controls.
