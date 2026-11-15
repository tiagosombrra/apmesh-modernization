import type { FaceDetail, MeshGeometry, ModelCatalog, Space } from './contracts';
import { decodeGeometryV2 } from './binaryGeometryV2';

async function query<T>(path: string): Promise<T> {
  const response = await fetch(`/api/v1/${path}`, { headers: { Accept: 'application/json' } });
  if (!response.ok) throw new Error(`API ${response.status}: ${path}`);
  return await response.json() as T;
}

async function binaryGeometry(id: string, space: Space): Promise<MeshGeometry> {
  const path = `models/${encodeURIComponent(id)}/geometry.v2.bin?space=${space}`;
  const response = await fetch(`/api/v1/${path}`, {
    headers: { Accept: 'application/vnd.apmesh.geometry.v2' },
  });
  if (!response.ok) throw new Error(`API ${response.status}: ${path}`);
  const result = decodeGeometryV2(await response.arrayBuffer(), space);
  if (response.headers.get('X-Source-SHA256') !== result.source_sha256) {
    throw new Error('binary_source_hash_mismatch');
  }
  return result;
}

export const studyApi = {
  catalog: (): Promise<ModelCatalog> => query('models'),
  geometry: binaryGeometry,
  face: (id: string, faceId: number): Promise<FaceDetail> =>
    query(`models/${encodeURIComponent(id)}/faces/${faceId}`),
};
