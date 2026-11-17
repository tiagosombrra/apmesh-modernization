# Opt-in domain factor-bound repair - 2026-11-16

Classification: behavior-changing defect repair of configured-factor semantics,
restricted to a new explicit research application case. No new curvature formula,
error estimator, acceptance criterion or stopping policy is introduced. Historical
TRI and the existing original-curves/fixed16 research cases retain their behavior.
This is not scientific adoption or stage closure.

The historical ranked-patch step2 override can reduce the actual domain factor
below PATCH_FACTOR_MIN, even when both configured bounds are1.5. The new
curved_bezier_bounded_domain_vertex_mean_v1 case projects that override back into
the existing configured interval. It uses the original curve passes, native
quadtree, QUAD templates and exterior AFT reconstruction. The source history is
still TRI-driven, with no accepted mixed feedback epochs.

Example: configs/quad/curved_patch_bounded_domain.conf. Output paths must be new;
the application refuses to replace existing exported histories.

The end-to-end domain-factor test retains the failing original1.0 witness and
requires actual step2 factor1.5 in the opt-in case. It compares the in-range
control byte-for-byte, checks every adapted TRI/QUAD-TRI source and disk, retains
accepted/rejected provenance, rejects nine corrupted witnesses, and verifies
nonempty rollback. Local development observation: coarse step2 nodes615 ->281,
QUAD548 ->242, source leaves136 ->67; step1 remains33 nodes. Step3 still grows to
797 nodes, so the repair alone is not a growth controller or an optimal mesh.

Consult canonical STATE.md on quad-templates for exact-revision compiler,
regression, geometric error and quality evidence. Development observations do
not qualify a delivery. Preserve previous failures and source evidence.
Do not use fewer nodes as evidence of adequate geometry or scientific acceptance.
