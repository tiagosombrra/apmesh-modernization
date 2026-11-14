# R2c-21 — detached original QUAD/AFT patch topology (research)

Status at authoring: implemented candidate, hosted exact-source gate pending. This does not qualify global QUAD/TRI connectivity or authorize a merge.

Scope: original R2c-10 Eistute/Book physical OBJ exports with per-patch disconnected ownership. The new independent indexed-edge checker reuses the existing exact model-SHA-bound source inventory guard and measures each chart's oriented paired halfedges, local manifold edge incidence, edge-connectivity, boundary vertex degree, duplicate face identity and finite Newell-normal direction. Seven adversarial controls exercise reversed/same orientation, overfull edges, disconnected faces, duplicate and foreign faces, cross-chart ownership and nonfinite XYZ. A local patch violation fails CI without relaxing the legacy TRI gate.

Run: python3 tools/verify_r2c21_detached_chart_topology.py --directory build/local-serial/r2c10_original_detached_meshes --output build/local-serial/r2c21_patch_topology

Not covered: source UV coordinates, original Bezier differential surface-normal sign, geometric self intersections, globally approved high-valence sheet/edge twins or physically shared nodes. Eistute curve valence 4 and Book valence 28 remain for the Creto/Bento scientific decision. Preserve the original 1993 numerical point rule as an independent approval gate. Next step: source-UV and surface-normal evidence per owned patch face, with exact model provenance and adversarial direction controls.
