# Mesh Studio — R2.2 scripted interaction, picking and memory preflight

Date: 2026-11-15. Isolated branch: `feature/mesh-studio-fixture-first-20261114`.
Base code under review: `9157a623c549d635347c4a81935f8b0775fb3e0a`.

## Scientific and engineering scope

- R2.2 adds scripted orbit sampling **in the actual vtk.js viewer**, for both
  XYZ and UV, with one WebGL scene and explicit source-id picking on each.
- The viewer rotates the camera by a bounded azimuth and calls
  `vtkRenderWindow.render()` after each `requestAnimationFrame`. The reported
  `scripted_orbit_throughput_fps` is **not** GPU-presented FPS, user interaction
  FPS or a stable refresh-rate guarantee. Report interval p50, p95, max, and
  total wall duration to make cadence and stalls visible.
- The same real vtkCellPicker code records duration of its synchronous `pick()`
  call and the returned synthetic face ID. It does not include React commit,
  browser paint or the entire time between physical pointer and inspector.
- Chromium CDP `Performance.getMetrics` records JS heap used/total and DOM
  count before and after, separately from the less reliable browser
  `performance.memory` approximation. Neither is GPU VRAM, operating-system
  RAM, or process-wide heap. No GPU memory figure is asserted.
- Tests exercise the generated 50,000-QUAD scene as **synthetic rendering
  stress only**, not an APMesh scientific experiment. Results are recorded
  to `test-results/r22-50k-scripted-interaction.json` and uploaded as CI
  artifacts. No numeric performance threshold is invented from one runner.
- 500,000-QUAD interactive stress is opt-in via environment variable
  `APMESH_R22_500K=1`, with a five-minute timeout and without interpreting
  the outcome as proof of all-QUAD mesh quality, anisotropy or a solver.

## Stop/go decisions

This phase is a diagnostic experiment. The developer must examine actual
CI behavior, not just successful TypeScript transpilation. Continue to
R2.3 optimization only after identifying which stage dominates: JS nested
arrays, vtk.js cell setup, renderer dispatch, picking, or GPU/driver limits.
Do not add global nonmanifold vertex welding, LOD that changes source face IDs,
or scientific result arrays in Float32. Renderer Float32 is an approximation;
the Python engine owns exact source geometry and metrics.

## Remaining open

1. Hardware Windows Chromium with known GPU/driver; multiple independent
   runs, confidence ranges and p95 latency across sessions.
2. 500k fully interacted with, in XYZ **and** UV, on the actual workstation.
3. WebGL GPU memory and end-to-end physical pointer-to-inspector paint latency.
4. Streaming/LOD preserves faces and patches with explicit resolution report.
5. Real large source model, patch topology and generator event timeline.
6. Application packaging, installer and scientific publishing UX.
