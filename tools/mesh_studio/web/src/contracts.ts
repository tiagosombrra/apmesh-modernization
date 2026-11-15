export type CellKind = 'triangle' | 'quad';
export type Space = 'xyz' | 'uv';

export interface ModelEntry {
  id: string;
  sha256: string;
  triangles: number;
  quads: number;
  points: number;
  source_status: 'CONTROLLED_PHYSICAL_GENERATION' | 'STAGED_UNACCEPTED';
  accepted_adaptive_epochs: number;
  source_patch_ownership: string;
}
export interface ModelCatalog {
  schema: string;
  models: ModelEntry[];
  study_scope: string;
}
export interface MeshGeometry {
  schema: string;
  source_sha256: string;
  source_patch_ownership: string;
  coordinate_space: Space;
  points: number[][];
  cells: number[][];
  source_face_ids: number[];
  cell_types: CellKind[];
  triangles: number;
  quads: number;
  warning: string;
}
export interface FaceDetail {
  source_sha256: string;
  source_face_id: number;
  element_type: CellKind;
  group: string;
  patch_id: string | null;
  vertex_indices: number[];
  xyz: number[][];
  uv: number[][] | null;
  synthetic: boolean;
  quality_status: string;
  quality: {
    physical_area: number;
    triangle_mean_ratio: number | null;
    planar_quad_min_scaled_jacobian: number | null;
    quad_relative_planarity: number | null;
    physical_orientation: string;
  };
}
