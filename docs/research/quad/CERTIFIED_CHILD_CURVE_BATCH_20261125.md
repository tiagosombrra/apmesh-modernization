# Apply a certified batch of child contour subdivisions

[Draft PR 289](https://github.com/tiagosombrra/apmesh-modernization/pull/289)
at `e0380de2e6517be03eda18743b8caf158670e90c` implements the pair approved
after the [transition map](TRANSITION_INTERFACE_MAP_20261125.md). The
experimental native plan allows up to three distinct first-generation
child requests, including any retained prior child split. Reject a
fourth request, duplicate directed child, missing original split or
missing certification. Resolve each child by its first-pass endpoint
IDs and require the same directed adjacency before applying the native
binary operation. Certify preservation of the complete current contour
at each step. The certificate v3 records the requests and witnesses in
plan order. The independent evaluator reconstructs each intermediate
contour. Plans with zero or one child keep the v1 or v2 outputs.

## Native Ribbed Bracket comparison

Replay `curve_child 8 0` first. Append `curve_child 8 1` and
`curve_child 2 1`. This retains all 24 control contour samples,
coordinates and IDs; the new native IDs are 561 and 562 respectively.
The sources, native requests, depth cap, grouped quadtree and selector
are identical in both arms.

| Measurement | 24-site control | Child batch |
| --- | ---: | ---: |
| Contour segments | 24 | 26 |
| Final faces | 533 | 533 |
| Minimum final transition TRI angle | 8.063° | 11.968° |
| Minimum shape score for transition TRI | 0.237448 | 0.349716 |
| Transition TRI below the frozen floors | 11 | 10 |
| Area-weighted geometric RMS, 48 × 48 | 0.020301368 | 0.020352477 |
| Maximum geometric deviation, 48 × 48 | 0.107484106 | 0.107484106 |

The projected limit was 559 faces and the profile maximum remains 601.
The top child point at UV (0.625, 1) divides its previous arc of about
1.00000009 into two of about 0.5. The bottom point at UV
(0.6876258724369109, 0) divides its arc of 0.50010814 into 0.25004746
and 0.25006068. Both are certified against the original surface.
The complete transition angles use final physical positions. Local
footprints use positive UV intersection with the exact control face.

The footprints of birth operations 51 and 68 now have QUAD, with
physical minimum angles of 64.798° and 76.729°. Operation 53's former
footprint includes a 64.798° QUAD and a 13.248° TRI, versus its old
8.063° TRI. The minimum elsewhere is still 11.968°, below the frozen
15° floor. RMS is 0.25 percent higher than the matched control.
The existing frozen profile rejects the candidate on shape.
No mixed adaptive epochs were accepted.

The v3 map locates the remaining limit at operation 58. Dividing the
only other promising first-generation child would affect a different
TRI and exceeds this batch's three-request cap. The native group that
would remove the limiting template edge is blocked by capped
geometric request 490. In the current mesh, the two incident face
sizes at that request are 0.19134 and 0.50001, both below its target
of 0.66182 model units. A read-only group projection removes the
short base and bounds the mesh at 548 faces. It does not certify the
realized physical sizes after reconstruction.

Next align a trial that preserves the existing requests and checks
their actual physical size on all affected incident faces before
considering the grouped candidate. The current blanket veto remains
in force. Shared curves, reserved cases, mixed owner reentry and the
global mixed-curvature error remain open.

## Validation and closure

- Local MSVC 19.44 x64 C++17 Debug build, native original-curve
  contracts, fifteen Python admission controls and six sizing controls
  pass. The interface map reads both v2 and v3 archives.
- Both native controls reproduce eight bound artifacts each. Five
  invalid native requests were refused before candidate publication.
  The approved Ribbed batch generated a native candidate once, with
  both new intervals and all earlier ordered samples verified.
- The exact-tree direct article rollback test failed before the
  intentional rejection. Windows denied the rename of the pending
  baseline output directory. Its first failure is retained and the
  rollback marker is absent. The local adapter still lacks its
  environment and baseline receipt. Full stage qualification,
  sanitizers and independent review remain open.
- The [PR 288 hosted checks](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/45736951313)
  and [PR 289 hosted checks](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/45738199942)
  were in progress at the checkpoint.
  [Evidence](evidence/CERTIFIED_CHILD_CURVE_BATCH_20261125.json)
  retains commands, exact identities, certificates, metrics and the
  failed rollback receipt.
