# First article-style mixed-front output

Date: 2026-11-17. Entry revision: d5b61759dc3b8ec83195a2b078c3722006e6cbbe.
Classification: source audit and delivery-priority correction, documentation only.
No new numerical algorithm is implemented or scientifically adopted here.

## Direct primary-source comparison

Source: J. B. C. Neto, M. T. M. Carvalho and L. F. Martha, SIBGRAPI1993,
pp285-291, the seven-page scan titled "Combinacao das Tecnicas de Quadtree e
Delaunay para Geracao Automatica de Malhas de Elementos Finitos".
SHA-256: `49d297e24c1b8695e18c6d1307aa4ccbc39f14e265d251b840a16560aca98dc5`.
Printed pages288-290 were visually inspected, including Figures7/10/11 and the
active-edge update text. No scan or rendered paper page is redistributed here.

| Procedure | Article | Qualified prototype at d251f19 |
| --- | --- | --- |
| Interior | Quadtree, graded neighboring levels, templates; QUAD branch subdivides intermediate polygons using edge midpoints and a centroid | Native template integration exists; exact centroid interpretation/full M1 remains open |
| Remaining region | Between original contour and quadtree interior | Original AFT reconstructs the remaining region |
| Base triangle | Existing vertices, maximum included angle, quadtree neighborhood restriction/expansion, domain/intersection checks | Original AFT has geometry/topology phases and may create ideal vertices; historical candidate-search equivalence is not established |
| Mixed choice | Before front update, seek a neighboring triangle on either of the best triangle's two other sides | Observer selects adjacent pairs of already committed TRI; original TRI front trajectory is retained |
| Shape | Figure11 planar S = 1 + max_i(abs(90deg-beta_i))/90deg; S <= 1.5 | Experimental physical XYZ score plus UV/physical predicates and recorded deterministic ties |
| Front update | Commit chosen TRI or QUAD; remove base and toggle two or three remaining sides respectively | TRI commit and front update precede the pair observer; paired faces are reconstructed later |

The current output contains genuine TRI and QUAD faces, including selected AFT
pairs. It does not establish article-equivalent mixed contraction. Passing the
prototype's exact-head gates does not prove the missing choice/front behavior.
The article's static generation does not require an adaptive curvature/error loop.

## One functional implementation target

Add a separate, explicit opt-in research path, without silently replacing the
qualified prototype or the production default TRI path:

1. Start with original boundary discretization and the native quadtree/template
   interior. Identify the still-unmeshed region and its complete active contour.
2. Form the best base triangle using the documented existing-node, neighborhood,
   domain and crossing rules. Inspect prospective neighbors on its other two
   sides before publishing triangles or changing the front.
3. Evaluate zero, one or two possible QUAD alternatives. Apply the documented
   planar shape rule and explicit deterministic tie handling. Preserve a TRI
   when no QUAD is admissible. Distinguish specified historical rules from
   implementation tie choices and later curved-surface extensions.
4. Commit exactly the chosen polygon and its contour update as one operation.
   Preserve owner/observer, interface synchronization and failed-operation
   rollback contracts. A discarded TRI diagonal must not guide the next front.
5. Produce a planar mixed example with nonzero accepted QUAD and retained TRI
   counts, complete coverage, noncrossing edges and conforming interfaces. Audit
   prospective choices, accepted/rejected traces, default-TRI regression and
   failure rollback using independent checks and required exact-head gates.
6. Export intermediate stages and the final mixed mesh. Display them beside the
   source model and templates in Blender. Then extend/compare the curved case,
   explicitly recording any extension beyond the article's planar formulation.

This first-output scope precedes R3 mixed-error feedback, accepted adaptive
mixed epochs and local size balancing. It does not close full historical
numerical reproduction: the centroid/oracle ambiguity, candidate-search details,
unspecified tie handling and smoothing scope require explicit dispositions.
No arbitrary centroid change, forced QUAD count or new adaptive policy is
implicitly authorized. Existing scientific-alignment requirements remain.

## Session evidence and limits

Read-only source inspection: advancing_front.cpp findBestVertex/makeMesh,
live_boundary_pairing.h, owned_aft_front.cpp and controlled_patch_application.cpp.
The callback-after-TRI-update behavior is directly visible in source. The paper
update sequence is directly visible on printed p290, following Figure11.

Local rendering: WSL pdftoppm unavailable (attempt failed); installed native
Windows Poppler successfully rendered PDF pages5-6 with empty stderr. Ignored
local render/log artifacts remain under build/quad-article-goal-20261117.
No native build/test, new mesh, Blender display or algorithm change was performed.
Prior PR238 gates remain valid only at their recorded revision and scope.
