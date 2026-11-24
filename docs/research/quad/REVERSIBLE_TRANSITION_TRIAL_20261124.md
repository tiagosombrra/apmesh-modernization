# Reversible native transition trial on Ribbed Bracket

Recorded 2026-11-24 Fortaleza. [Machine-readable receipt and stage metrics](evidence/REVERSIBLE_TRANSITION_TRIAL_20261124.json).

## Native trial

The opt-in Step 2 application reproduces the once-grouped predecessor on the
individual Ribbed Bracket patch 12 in the existing 23-interval experiment.
The predecessor retains its earlier manually chosen group. Its physical OBJ,
front trace and five earlier stage OBJ files reproduce byte for byte. The
application holds the complete predecessor as the live patch owner and calls the
existing experimental Python selector on newly written front, mesh, leaf and
size-request data. The selector derives the region from the original limiting TRI
footprint. It supplies the previously observed parent 62 and children 66 through
69 without a supplied candidate ID. It also evaluates an injected fine-size
request at the center of that group, where the same selector returns no action.

The native code copies the realized tree, removes exactly the four selected
children and reconstructs the candidate through the original template
dispatch and mixed advancing front. The trial checks native physical
validity and typed incidence, retains pre-smoothing and guarded smoothing
frames and writes the complete staged OBJ. It then injects a rejection
after preparation of the candidate back-link. The predecessor patch owner,
node and element addresses and IDs, ordered observers, coordinates, curvature
fields, element areas and OBJ bytes remain identical. The candidate is
destroyed without publishing it as the active mesh. Both typed OBJ files
have identical curve witnesses and directed contours with 23 segments.

The Python selector and fine-size control run from the same invocation.
The no-action receipt is a selector veto witnessed before native
reconstruction of the positive case. No separate negative mesh is generated.
No actual owner swap or filesystem publication failure after an owner swap
was exercised. The program returns after the experimental Step 2 path and
keeps the two meshes and frame history in the staging folder.

## Measured change

| Quantity | Predecessor | Staged candidate |
| --- | ---: | ---: |
| Nodes / faces | 612 / 636 | 598 / 622 |
| TRI / QUAD | 73 / 563 | 73 / 549 |
| Regional minimum physical angle at birth and after smoothing | 6.86298 deg | 43.44078 deg |
| Patch TRI minimum physical angle after smoothing | 6.86298 deg | 6.86759 deg |
| Patch QUAD minimum physical angle and corner scaled Jacobian | 26.26014 deg / 0.32333 | 26.26014 deg / 0.32333 |
| Regional maximum physical neighbor size ratio | 5.51220 | 2.35781 |
| Patch maximum physical neighbor size ratio | 5.51243 | 5.51243 |
| Regional area-weighted geometric RMS, 292 common sites | 0.0253130 | 0.0236046 |
| Patch area-weighted geometric RMS, 576 common sites | 0.0172202 | 0.0172013 |
| Patch maximum sampled deviation, 576 common sites | 0.1027811 | 0.1027811 |

Geometric deviations are in source model units. On the denser grid the
regional RMS also falls (0.0253147 to 0.0236175, 1160 sites); the patch
sampled maximum remains equal (0.1074841, 2304 sites). The region covers the
one selected TRI footprint. The neighboring thin TRI limits progress across
the whole patch. This experiment measures area-weighted distance to the
analytical surface and leaves mixed global curvature error unresolved.

## Validation and scope

The receipt binds the source diff against 94dc35a6, executable, compiler,
config, model, staged meshes, selection and logs. Local reproducibility
assets are in the ignored trial folder under build. The exact trial uses a
local experimental patch and a fixed-path selector. The repository does
not provide a portable trial entry at this checkpoint.

MSVC 19.44 x64 Debug C++17 builds the application in 9.34 s, and the native
Ribbed invocation completes in 56.87 s. The first focused contract executable
invocation omitted its required config and exited 1. The configured invocation
reports six captures, three reversed captures and 54 negative controls.
Four comparator tests pass on the unchanged PR 263 code. The default validation
adapter reports unavailable required tools and an absent baseline receipt in
the checkpoint worktree. This run uses the existing working MSVC profile
directly. No full regression matrix, sanitizer, multi-patch or external
scientific acceptance was exercised. Accepted mixed adaptive epochs: zero.

Next align an experimental admission rule against the archived positive,
reversed and shape/error conflict controls. Keep scientific admission,
post-publication failure coverage and fresh second-geometry transfer explicit.
