/** Rendering-only diagnostics. These samples never qualify APMesh algorithms. */
export interface ScriptedOrbitObservation {
  frames_requested: number;
  frames_completed: number;
  wall_elapsed_ms: number;
  scripted_orbit_throughput_fps: number;
  frame_wall_p50_ms: number;
  frame_wall_p95_ms: number;
  frame_wall_max_ms: number;
  scope: 'SCRIPTED_CAMERA_ORBIT_RAF_AND_RENDER_CALL_NOT_GPU_PRESENT_FPS';
}

export interface PickObservation {
  space: 'xyz' | 'uv';
  source_face_id: number | null;
  hit: boolean;
  picker_wall_ms: number;
  method?: 'UV_SPATIAL_INDEX' | 'VTK_CELL_PICKER' | 'SYNTHETIC_XYZ_GRID_RAY';
  spatial_candidates_tested?: number | null;
  scope: 'VTK_CELL_PICKER_SYNCHRONOUS_CALL_NOT_END_TO_END_UI_LATENCY' |
    'UV_PLANE_SPATIAL_QUERY_NOT_END_TO_END_UI_LATENCY' |
    'SYNTHETIC_XYZ_GRID_RAY_QUERY_NOT_END_TO_END_UI_LATENCY';
}

/** Return a browser-specific heap estimate; never interpret it as total RAM or VRAM. */
export function chromiumHeapEstimate(): number | null {
  const api = performance as Performance & { memory?: { usedJSHeapSize?: number } };
  const sample = api.memory?.usedJSHeapSize;
  return typeof sample === 'number' && Number.isFinite(sample) && sample >= 0 ? sample : null;
}

/** Summarize observed RAF-to-render completion intervals, not GPU presentation events. */
export function summarizeScriptedOrbit(
  frameWallMs: number[], elapsedMs: number,
): ScriptedOrbitObservation {
  if (frameWallMs.length < 8 || frameWallMs.length > 120 ||
      !Number.isFinite(elapsedMs) || elapsedMs <= 0 ||
      frameWallMs.some((v) => !Number.isFinite(v) || v < 0)) {
    throw new Error('invalid_scripted_orbit_observation');
  }
  const sorted = [...frameWallMs].sort((a, b) => a - b);
  const percentile = (p: number) => sorted[Math.min(sorted.length - 1,
    Math.max(0, Math.ceil(sorted.length * p) - 1))];
  return {
    frames_requested: frameWallMs.length,
    frames_completed: frameWallMs.length,
    wall_elapsed_ms: Math.round(elapsedMs * 100) / 100,
    scripted_orbit_throughput_fps: Math.round(100_000 * frameWallMs.length / elapsedMs) / 100,
    frame_wall_p50_ms: Math.round(percentile(0.5) * 100) / 100,
    frame_wall_p95_ms: Math.round(percentile(0.95) * 100) / 100,
    frame_wall_max_ms: Math.round(sorted[sorted.length - 1] * 100) / 100,
    scope: 'SCRIPTED_CAMERA_ORBIT_RAF_AND_RENDER_CALL_NOT_GPU_PRESENT_FPS',
  };
}
