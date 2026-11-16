/** Opt-in real-geometry BVH client: failures and latency always fall back to native VTK. */
import type { MeshGeometry } from './contracts';
import { prepareBvhPayload } from './xyzBvh';
import type { BvhPick } from './xyzBvh';

const BUILD_DEADLINE_MS = 15_000;
const PICK_DEADLINE_MS = 250;
const UNSUPPORTED: BvhPick = {kind:'ambiguous',testedFaces:0};

export interface BvhCoverage {
  sourceFaces: number;
  indexedFaces: number;
  excludedQuadFaces: number;
}

export interface XyzBvhWorkerClient {
  readonly ready: Promise<boolean>;
  isReady(): boolean;
  coverage(): BvhCoverage | null;
  pick(near: [number,number,number],far: [number,number,number],
       showTri:boolean,showQuad:boolean): Promise<BvhPick>;
  dispose(): void;
}

/** Worker receives copies: source vertices, source IDs and active VTK buffers remain owned by UI. */
export function createXyzBvhWorker(mesh: MeshGeometry): XyzBvhWorkerClient | null {
  const payload = prepareBvhPayload(mesh);
  if (!payload) return null;
  let worker: Worker;
  try { worker = new Worker(new URL('./xyzBvh.worker.ts', import.meta.url), {type:'module'}); }
  catch { return null; }
  let available = false, closed = false, nextId = 1;
  let coverage: BvhCoverage | null = null;
  let settleReady: (value:boolean)=>void = () => {};
  const ready = new Promise<boolean>((resolve)=>{settleReady = resolve;});
  const inflight = new Map<number,{resolve:(v:BvhPick)=>void;timer:ReturnType<typeof setTimeout>}>();
  const buildTimer = setTimeout(() => fail(),BUILD_DEADLINE_MS);
  const fail = () => {
    if(closed) return;
    closed = true; available = false; coverage = null;
    clearTimeout(buildTimer);
    settleReady(false);
    for(const [,promise] of inflight) { clearTimeout(promise.timer); promise.resolve(UNSUPPORTED); }
    inflight.clear();
    worker.terminate();
  };
  worker.onmessage = (event: MessageEvent<{
    type:string;qualified?:boolean;id?:number;outcome?:BvhPick;
    faces?:number;indexedFaces?:number;excludedQuadFaces?:number;
  }>) => {
    if(closed) return;
    const response = event.data;
    if(response.type === 'ready') {
      clearTimeout(buildTimer);
      const {faces, indexedFaces, excludedQuadFaces} = response;
      available = response.qualified === true &&
        Number.isSafeInteger(faces) && Number.isSafeInteger(indexedFaces) &&
        Number.isSafeInteger(excludedQuadFaces) && faces! > 0 &&
        indexedFaces! > 0 && excludedQuadFaces! >= 0 &&
        indexedFaces! + excludedQuadFaces! === faces!;
      coverage = available ? {sourceFaces:faces!, indexedFaces:indexedFaces!,
        excludedQuadFaces:excludedQuadFaces!} : null;
      settleReady(available);
      if(!available) fail();
    } else if(response.type === 'result' && typeof response.id === 'number') {
      const promise = inflight.get(response.id);
      if (!promise) return;
      inflight.delete(response.id);
      clearTimeout(promise.timer);
      const outcome = response.outcome;
      promise.resolve(outcome && (outcome.kind === 'hit'||outcome.kind === 'miss'||outcome.kind === 'ambiguous')
        ? outcome : UNSUPPORTED);
    }
  };
  worker.onerror = fail;
  worker.onmessageerror = fail;
  try {
    worker.postMessage({type:'build',payload}, [payload.vertices.buffer,payload.polys.buffer,
      payload.offsets.buffer,payload.arities.buffer,payload.sourceIds.buffer]);
  } catch { fail(); }
  return {
    ready,
    isReady:()=>available && !closed,
    coverage:()=>coverage,
    pick(near,far,showTri,showQuad) {
      if(!available || closed || inflight.size>=4) return Promise.resolve(UNSUPPORTED);
      const id=nextId++;
      return new Promise<BvhPick>((resolve)=>{
        const timer=setTimeout(()=>{inflight.delete(id);resolve(UNSUPPORTED);},PICK_DEADLINE_MS);
        inflight.set(id,{resolve,timer});
        try {worker.postMessage({type:'pick',id,near,far,showTri,showQuad});}
        catch {clearTimeout(timer);inflight.delete(id);resolve(UNSUPPORTED);}
      });
    },
    dispose: fail,
  };
}
