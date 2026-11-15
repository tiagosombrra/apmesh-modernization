# Controlled curved QUAD application

## Original curve workflow and native tree

With the same explicit experimental build, run
`ap_mesh --config configs/quad/curved_patch_original_curves.conf`.
This runs the original serial generator's initial TRI evaluation, curve
discretization, native tree construction and original retry/acceptance logic.
It captures the last locally selected source attempt with a recorded global
TRI outcome, then replays that actual boundary and tree for typed interior
QUAD plus original exterior AFT. No fixed sampling or prescribed tree depth
is substituted. Source nodes, intervals, parametric midpoint/length and the
post-refinement edge phase are checked; original sample pointers are not kept.

The initial controlled profile measures 12 boundary intervals, 16 native leaves,
37 physical nodes, 16 QUAD and 28 AFT TRI, with four nonuniform source sides.
These are measured outputs, not required topology constants. The original
global TRI candidate at source step 2 is rejected by its existing hybrid
criterion; the OBJ records `reference_tri_accepted=0`. That rejection is
retained. The exported initial research QUAD layout does not override the TRI
decision or implement a scientifically accepted mixed adaptive transition.
`mixed_adaptive_epochs=0`; global mixed acceptance/history remain open.
The interior vertex-mean rule remains experimental, not literal 1993 identity.

OBJ comments include the complete original per-curve partition, oriented
source intervals and original source IDs/XYZ; physical node IDs are also
exported. Existing output/pending publication is refused before the original
workflow executes. `QUAD_VERIFY_ROLLBACK=1` exercises a failed replacement
while preserving the nonempty mixed owner, ordered observers and OBJ bytes.
The unchanged fixed16 case below remains a separate regression.

`python tests/quad/test_real_boundary_application.py --exe <ap_mesh> --directory <results>`
checks independent Bernstein geometry, physical topology/source intervals,
normal/rollback traces, nine corrupted OBJ/witness cases per run and refusal
to overwrite an existing result. `quad_real_boundary_source_contracts` accepts
the same configuration and checks native source/tree replay, valid reversed
curve geometry and nine corruptions per captured native attempt.

## Fixed16 regression

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
