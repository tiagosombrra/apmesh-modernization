import type { FaceDetail, MeshGeometry, ModelCatalog, Space } from './contracts';

async function query<T>(path: string): Promise<T> {
  const response = await fetch(`/api/v1/${path}`, { headers: { Accept: 'application/json' } });
  if (!response.ok) throw new Error(`API ${response.status}: ${path}`);
  return await response.json() as T;
}

export const studyApi = {
  catalog: (): Promise<ModelCatalog> => query('models'),
  geometry: (id: string, space: Space): Promise<MeshGeometry> =>
    query(`models/${encodeURIComponent(id)}/geometry?space=${space}`),
  face: (id: string, faceId: number): Promise<FaceDetail> =>
    query(`models/${encodeURIComponent(id)}/faces/${faceId}`),
};
