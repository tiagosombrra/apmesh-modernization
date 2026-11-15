import type { Space } from './contracts';

export interface CameraPose {
  position: [number, number, number];
  focal_point: [number, number, number];
  view_up: [number, number, number];
  parallel_scale: number;
  parallel: boolean;
}

export interface CameraRecipe {
  schema: 'apmesh.meshstudio.web_camera.v1';
  source_sha256: string;
  camera_xyz: CameraPose;
  camera_uv: CameraPose;
}

export const CAMERA_SCHEMA = 'apmesh.meshstudio.web_camera.v1' as const;

function vector(value: unknown): value is [number, number, number] {
  return Array.isArray(value) && value.length === 3 &&
    value.every((v) => typeof v === 'number' && Number.isFinite(v) && Math.abs(v) < 1e12);
}

export function isCameraPose(value: unknown): value is CameraPose {
  if (!value || typeof value !== 'object') return false;
  const v = value as Partial<CameraPose>;
  if (!vector(v.position) || !vector(v.focal_point) || !vector(v.view_up) ||
      typeof v.parallel_scale !== 'number' || !Number.isFinite(v.parallel_scale) ||
      v.parallel_scale <= 0 || v.parallel_scale > 1e12 || typeof v.parallel !== 'boolean') return false;
  const distance = Math.hypot(...v.position.map((x, i) => x - v.focal_point![i]));
  const direction = v.focal_point.map((x, i) => x - v.position![i]);
  const cross = [direction[1] * v.view_up[2] - direction[2] * v.view_up[1],
    direction[2] * v.view_up[0] - direction[0] * v.view_up[2],
    direction[0] * v.view_up[1] - direction[1] * v.view_up[0]];
  return distance > 1e-12 && Math.hypot(...cross) > 1e-12;
}

export function parseCameraRecipe(raw: string, expectedSha: string): CameraRecipe {
  if (raw.length > 8192 || !/^[0-9a-f]{64}$/.test(expectedSha)) throw new Error('invalid_camera_recipe');
  let value: unknown;
  try { value = JSON.parse(raw); } catch { throw new Error('invalid_camera_recipe'); }
  if (!value || typeof value !== 'object') throw new Error('invalid_camera_recipe');
  const recipe = value as Partial<CameraRecipe>;
  if (recipe.schema !== CAMERA_SCHEMA || recipe.source_sha256 !== expectedSha) {
    throw new Error('camera_source_mismatch');
  }
  if (!isCameraPose(recipe.camera_xyz) || !isCameraPose(recipe.camera_uv)) {
    throw new Error('invalid_camera_pose');
  }
  return recipe as CameraRecipe;
}

export function storageKey(sourceSha: string): string {
  if (!/^[0-9a-f]{64}$/.test(sourceSha)) throw new Error('invalid_source_sha256');
  return `apmesh.meshstudio.camera.v1.${sourceSha}`;
}

export function cameraLabel(space: Space): string {
  return space === 'uv' ? 'paramétrico' : 'físico';
}
