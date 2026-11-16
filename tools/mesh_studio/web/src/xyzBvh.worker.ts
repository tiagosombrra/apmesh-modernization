/** Dedicated CPU-only BVH worker; never creates source geometry or quality metrics. */
import { buildXyzBvh } from './xyzBvh';
import type { BvhPayload, BvhIndex } from './xyzBvh';

type Message =
  | { type: 'build'; payload: BvhPayload }
  | { type: 'pick'; id: number; near: [number,number,number]; far: [number,number,number];
      showTri: boolean; showQuad: boolean };

let index: BvhIndex | null = null;
self.onmessage = (event: MessageEvent<Message>) => {
  const message = event.data;
  if (message.type === 'build') {
    const buildStarted = performance.now();
    try {
      // Excluded warped QUADs remain VTK-owned whenever the QUAD layer is visible.
      index = buildXyzBvh(message.payload, {allowUnindexedWarpedQuads:true});
      self.postMessage({ type:'ready', qualified: Boolean(index),
        faces:index?.faceCount ?? 0, indexedFaces:index?.indexedFaceCount ?? 0,
        excludedQuadFaces:index?.excludedQuadCount ?? 0, nodes:index?.nodeCount ?? 0,
        workerBuildMs:performance.now()-buildStarted });
    } catch {
      index = null;
      self.postMessage({ type:'ready', qualified:false, faces:0, nodes:0,
        workerBuildMs:performance.now()-buildStarted });
    }
  } else if (message.type === 'pick') {
    const queryStarted = performance.now();
    let outcome;
    try {
      outcome = index?.pick(message.near,message.far,message.showTri,message.showQuad) ??
        {kind:'ambiguous',testedFaces:0};
    } catch {
      outcome = {kind:'ambiguous',testedFaces:0};
    }
    self.postMessage({type:'result',id:message.id,outcome,
      workerQueryMs:performance.now()-queryStarted});
  }
};
