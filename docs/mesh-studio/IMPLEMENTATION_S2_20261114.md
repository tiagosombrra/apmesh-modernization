# S2 — Geometry, topology and SPD metric analysis

2026-11-14. Viewer-only implementation on the isolated Mesh Studio branch.
No `src/`, `include/`, root CMake, production `main`, or QUAD research source
files are changed by this stage.

## New functional units

- `tools/mesh_studio/quality_analysis.py`: typed per-cell TRI/QUAD UV and
  physical measurements, independent mean-ratio and planar scaled-Jacobian
  quality distributions, optional sample-only source orientation check,
  constant/variable SPD edge metric lengths, explicit missing score values.
- `tools/mesh_studio/topology_audit.py`: edge incidence, opposite winding,
  connected components, boundary loops, Euler characteristic, indexed disk
  gate and necessary all-quad boundary parity. Patch owner sidecars are kept
  distinct from ambiguous OBJ group labels.
- `tools/mesh_studio/analyze_cli.py`: deterministic CLI producing machine-
  readable per-cell measurements and provenance, independent of Qt/VTK.
- `tools/mesh_studio/test_quality_analysis.py`: synthetic analytic oracles,
  negative physical folding/UV convexity checks, metric covariance,
  disconnected/nonmanifold cases, patch fans and a deterministic CLI.

## Formula registry and interpretation

| Name | Definition | Scope |
| --- | --- | --- |
| `triangle_mean_ratio_3d_v1` | `q=4 sqrt(3) A/(a²+b²+c²)` using 3D facet edges | `0 < q <= 1`, physical TRI **shape**; not asserted equal to published paper q |
| `physical_area` | TRI: `0.5 ||(b-a) × (c-a)||`; QUAD: sum of `(0,1,2)` and `(0,2,3)` facet areas | Discrete face approximation, not Bezier patch integral; input XYZ units squared |
| `uv_signed_area` | Positive CCW polygon area using shoelace formula | UV/parameter domain, positive four-corner turns additionally required for QUAD |
| `planar_quad_min_scaled_jacobian_3d_v1` | Minimum of `((e_next × e_previous) · n) / (||e_next|| ||e_previous||)` over four corners | Only when all 4 physical corners are planar to a strict relative tolerance; `n` is local facet unit normal, not source normal |
| `quad_relative_planarity` | Fourth-vertex distance to first-three-vertex plane divided by maximum edge length | Proxy for vertex coplanarity, **not** continuous surface curvature/validity |
| `metric_edge_length_uv_v1` | `∫₀¹ sqrt(eᵀ M(u(t),v(t)) e)dt`, with `e=b-a` | UV SPD metric; constant exact, varying approximated by 2-point Gauss–Legendre |
| `indexed_disk` | One edge-connected component, one closed boundary loop, `V-E+F=1`, edge degree ≤2 with opposite oriented pairings | Indexed chart check only; neither global surface topology nor original patch identity certification |
| `all_quad_fixed_boundary_even` | For conforming all-quad disk, `4F=2 E_interior+E_boundary` | Necessary parity check, not proof all-quad existence or source compatibility |

Every report contains the original OBJ SHA-256, source/synthetic metadata,
separate TRI/QUAD quality distributions, physical/UV units as *unspecified*,
source-normal and metric-field callback provenance, and
`source_surface_global_certification=false`. Missing scores are JSON `null`,
not fabricated zero values. A direct in-memory modified document may retain
an old provenance SHA unless caller constructs a new identity; actual imports
always use the raw OBJ hash.

## Important testing correction

The original `synthetic_curved_bezier_grid` is a separable polynomial patch:
its individual rectangular four-corner samples can be planar despite the
**underlying surface being curved**. It must not falsely qualify a nonplanar
QUAD rejection test. The numeric negative case perturbs one copied physical
vertex while retaining the original immutable fixture and its analytic source
oracle. A separate analytic derivative test validates facet normals against
`(-0.4u,-0.2v,1)` on the unmodified synthetic source. This is a useful
reminder that four coplanar vertices do **not** prove the intervening surface
patch is planar.

## Evidence and limitations

Required: existing S0/S1/S1b regressions, independent S2 tests, 10/6
synthetic fixture oracle, deterministic CLI JSON, Python syntax and supported
local runtime. The sibling `docs/mesh-studio/evidence/S2_HYBRID_SYNTHETIC_REPORT_20261114.json`
is an example **synthetic** measurement, not a recorded generator run.

Not qualified: exact original source TRI C++ regression, dynamic source-P1
output imported by the Studio, global continuous surface Jacobian and
self-intersection, real anisotropic generator, exact q equivalence with the
published historical paper, 3D Qt/VTK rendering, real event traces,
PDF/PGF/LaTeX or Windows packaging. The next functional delivery S3 is a
strict real controlled P1 artifact import and geometric inventory check.
