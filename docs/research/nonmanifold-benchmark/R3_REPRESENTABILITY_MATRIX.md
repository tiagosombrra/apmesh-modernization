# R3 representability matrix — explicit evidence and stop conditions

Updated 2026-11-15. The categories here are **research-case classifications**, not releases or verified external benchmark admissions.

| Case | Source scope | Shared-curve topology | Exact bicubic BP | Current classification | Blocking issue |
|---|---|---|---|---|---|
| Four planar interfaces | R2 locally authored source mirror / reconstructed sheets | one constructed 4-face TopoDS edge; four BP uses of same 4 C0 controls | demonstrated with 4 bicubic patches | CONTROL_PASS | Not external source admission or generation |
| Four curved ruled sheets | R3 **synthetic deformation**, not original cuboid CAD | one constructed 4-face TopoDS Bezier edge; 4 uses, one parametrically reversed | demonstrated by polynomial construction; 324 BP samples and native face checks | CONTROL_PASS | Not CAD import or general reverse conversion |
| Curved face shifted 2e-5 above 1e-8 tolerance | adversarial native control | must not create single 4-face edge | not attempted | NEGATIVE_PASS | Bounded offset test only |
| Ordinary sewing of four curved sheets | adversarial native control | no 4-incidence edge | not attempted | NEGATIVE_PASS | Native mode deliberately differs |
| Cubic spine + sine perturbation at the same parameter t | authored nonpolynomial analytic negative | geometry may have contact | exact polynomial bicubic in the **fixed parameter** impossible (fourth derivative nonzero) | EXACT_NOT_REPRESENTABLE | Approximation/reparameterization/decomposition not tested |
| T-Junction partial overlapping CAD faces | upstream Fusion source mirror | face overlap/split not qualified | not attempted | BLOCKED | Needs explicit trim/imprint feature splitting |
| Cross-Junction partial overlapping CAD faces | upstream Fusion source mirror | face overlap/split not qualified | not attempted | BLOCKED | Needs explicit interface semantics and splitting |
| HexMe/MAMBO STEP candidates | named upstream original CAD source | no explicit 3+ edge in eight structurally traversed source graphs | not attempted | BLOCKED | Original per-asset rights, native topology, CAD source-to-patch mapping |
| Periodic torus (VERTEX_LOOP) | named upstream original STEP | static STEP reference screen incomplete | not attempted | BLOCKED | Seam/periodic CAD kernel treatment |
| Trimmed NURBS with holes | no admitted asset | no measured source | not attempted | NOT_EVALUATED | No bounded four-sided decomposition or certified fit |

**Scientific separation:** exact existence of an analytic bicubic representation for author-constructed controls is NOT a proof that an arbitrary STEP face admits the same representation. Curved R3 geometry is a synthetic deformation of a contact pattern, not a representation of the source cuboids. Sampling evidence does not substitute for certified distance bounds on arbitrary curved/trimmed CAD.

**Admission thresholds:** external G1/G2 (source rights/topology), R3 geometric feasibility, R4 conversion completeness, R5 accepted runtime generation and future method-specific QUAD/anisotropy qualification are separate review gates. Zero newly admitted external models; 40 catalog entries remain DISCOVERED.
