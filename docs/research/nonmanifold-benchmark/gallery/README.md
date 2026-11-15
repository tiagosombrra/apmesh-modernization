# Scientific model gallery — evidence-indexed, not a claim of meshing success

**Status 2026-11-14:** R0-R1 sources cataloged, R2 constructed non-manifold BRep control, R3 exact **planar analytic** bicubic BP pilot; no APMesh TRI/QUAD/all-quad/anisotropic meshes generated on the new pilot. No historical input changed.

## 1. Source → reconstructed geometry → Bezier representation

![Annotated exact analytic XY cross-section](three_cuboids_r3.svg)

This diagram is an analytical XY cross-section, **not** a photograph or a generated mesh. A, B and C occupy three quadrants; the fourth region is VOID. C0 runs in the Z direction; the four surface sheets are A/B, A/C, B/VOID and C/VOID. R3 retains one canonical shared cubic boundary represented by control vertex IDs 0-3 in all four bicubic patches.

- [Source image: Three Touching Cuboids (Fusion Energy)](https://raw.githubusercontent.com/fusion-energy/model_benchmark_zoo/main/images/three_touching_cuboids.png)
- [Source implementation (pinned)](https://github.com/fusion-energy/model_benchmark_zoo/blob/3a2e69fe62209e33a1e176d816609d69a2aebadc/src/model_benchmark_zoo/three_touching_cuboids.py)
- [R2 native BRep proof](../R2_VALID_NONMANIFOLD_BREP.md)
- [R3 exact 4-patch BP fixture](../fixtures/four_sheet_planar.bp)
- [R3 measured representation proof](../R3_ANALYTIC_BICUBIC_PILOT.md)

## 2. Historical and candidate image references

| Model | Official image/reference | Experimental role | Claimed status |
|---|---|---|---|
| Eistute | [APMesh original representative image](https://github.com/tiagosombrra/apmesh-modernization/blob/main/assets/grsi_representative.png) | Historical article TRI reference | Historical; Stage 4 OBJ is retained **rejected candidate**, not accepted |
| Book | [Historical input](https://github.com/tiagosombrra/apmesh-modernization/blob/main/input_models/book_v7a.bp) | Historical article reference | Image not newly validated; no fabricated render |
| Decor Shelf | [Historical input](https://github.com/tiagosombrra/apmesh-modernization/blob/main/input_models/ribbed_bracket_nm_decor.bp) | Historical article reference | Image not newly validated; no fabricated render |
| Three Touching Cuboids | [Source image](https://raw.githubusercontent.com/fusion-energy/model_benchmark_zoo/main/images/three_touching_cuboids.png) | Geometry contact, four-sheet controlled R2/R3 reconstruction | Local analytic control; external G1/G2 **blocked** |
| T Junction | [Source image](https://raw.githubusercontent.com/fusion-energy/model_benchmark_zoo/main/images/t_junction.png) | Partial overlap and feature splitting | Discovered; not converted |
| Cross Junction | [Source image](https://raw.githubusercontent.com/fusion-energy/model_benchmark_zoo/main/images/cross_junction.png) | Multi-body partial interface contact | Discovered; not converted |
| Two Touching Cuboids | [Source image](https://raw.githubusercontent.com/fusion-energy/model_benchmark_zoo/main/images/two_touching_cuboids.png) | Contact control | Discovered; not converted |
| Tangent Spheres | [Source image](https://raw.githubusercontent.com/fusion-energy/model_benchmark_zoo/main/images/tangent_spheres.png) | Point-contact negative control | Discovered; not converted |
| HexMe/MAMBO | [HexMe official catalog](https://hexme.algohex.eu/catalog/) | CAD shape, curvature and QUAD controls | Individual image/model approval pending |

## 3. Required image sequence per final accepted model

Keep the following scientific states separate, with evidence-verified labels and hashes: source CAD/BRep; edge/sheet graph (source vs reconstructed topology); exact or bounded bicubic BP control net; TRI mesh and accepted/rejected stages; mixed QUAD/TRI; all-quad; anisotropic metric and resulting mesh. At present only the initial source/control/Bezier stages have evidence for the three-cuboid pilot. **Do not draw future mesh results as if they have been computed.**

Image and raw model licensing follow source-file rights review; linked upstream images are not copied or redistributed in this Git repository. MATLAB/Matplotlib renderings in downloadable local research packages are author-generated geometry illustrations, not additional independent dataset assets.
