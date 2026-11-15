import type { CellKind, MeshGeometry } from './contracts';

export interface RenderCells {
  points: Float32Array;
  polys: Uint32Array;
  colorBytes: Uint8Array;
  sourceIds: number[];
}

export function asVtkCells(
  payload: MeshGeometry,
  showTriangle: boolean,
  showQuad: boolean,
): RenderCells {
  if (payload.cells.length !== payload.source_face_ids.length ||
      payload.cells.length !== payload.cell_types.length) {
    throw new Error('invalid_cell_identity');
  }
  const points = new Float32Array(payload.points.flat());
  const polys: number[] = [];
  const colors: number[] = [];
  const sourceIds: number[] = [];
  for (let i = 0; i < payload.cells.length; i += 1) {
    const kind: CellKind = payload.cell_types[i];
    if ((kind === 'triangle' && !showTriangle) ||
        (kind === 'quad' && !showQuad)) continue;
    const corners = payload.cells[i];
    if (corners.length !== (kind === 'triangle' ? 3 : 4)) throw new Error('invalid_cell_arity');
    if (!corners.every((value) => Number.isSafeInteger(value) && value >= 0 && value < payload.points.length)) {
      throw new Error('foreign_cell_index');
    }
    polys.push(corners.length, ...corners);
    // Direct cell colors distinguish original QUAD from native AFT TRI.
    colors.push(...(kind === 'quad' ? [51, 151, 177, 255] : [224, 168, 94, 255]));
    sourceIds.push(payload.source_face_ids[i]);
  }
  return { points, polys: new Uint32Array(polys),
    colorBytes: new Uint8Array(colors), sourceIds };
}
