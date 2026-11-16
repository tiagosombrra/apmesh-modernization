/** Opt-in BVH instrumentation: neither source Float32 nor worker timing is a scientific oracle. */
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

export interface BvhBuildMeasurement {
  preparationWallMs: number;
  readyRoundTripMs: number;
  workerBuildWallMs: number;
  copiedInputBytes: number;
  nodeCount: number;
  scope: 'COPIED_TYPED_INPUT_AND_WORKER_CPU_NOT_HEAP_RSS_VRAM';
}

export interface BvhPickMeasurement {
  outcome: BvhPick;
  workerQueryWallMs: number | null;
  roundTripWallMs: number;
  status: 'completed' | 'timeout' | 'unavailable';
  scope: 'WORKER_MESSAGE_ROUND_TRIP_NOT_REACT_PAINT_OR_GPU_PRESENTATION';
}

export interface XyzBvhWorkerClient {
  readonly ready: Promise<boolean>;
  isReady(): boolean;
  coverage(): BvhCoverage | null;
  buildMeasurement(): BvhBuildMeasurement | null;
  pickWithMeasurement(near: [number,number,number], far: [number,number,number],
    showTri:boolean, showQuad:boolean): Promise<BvhPickMeasurement>;
  pick(near: [number,number,number], far: [number,number,number],
    showTri:boolean, showQuad:boolean): Promise<BvhPick>;
  dispose(): void;
}

const MEASUREMENT_SCOPE: BvhPickMeasurement['scope'] =
  'WORKER_MESSAGE_ROUND_TRIP_NOT_REACT_PAINT_OR_GPU_PRESENTATION';

/** Transfer only copied buffers, never source-owned or VTK view arrays. */
export function createXyzBvhWorker(mesh: MeshGeometry): XyzBvhWorkerClient | null {
  const started = performance.now();
  const payload = prepareBvhPayload(mesh);
  if (!payload) return null;
  const preparationWallMs = performance.now() - started;
  const copiedInputBytes = payload.vertices.byteLength + payload.polys.byteLength +
    payload.offsets.byteLength + payload.arities.byteLength + payload.sourceIds.byteLength;
  let worker: Worker;
  try { worker = new Worker(new URL('./xyzBvh.worker.ts', import.meta.url), {type:'module'}); }
  catch { return null; }

  let available = false, closed = false, nextId = 1;
  let coverage: BvhCoverage | null = null;
  let buildProfile: BvhBuildMeasurement | null = null;
  let settleReady: (value:boolean)=>void = () => {};
  const ready = new Promise<boolean>((resolve)=>{settleReady = resolve;});
  const inflight = new Map<number,{
    resolve:(v:BvhPickMeasurement)=>void;
    timer:ReturnType<typeof setTimeout>;
    started:number;
  }>();

  const unavailable = (elapsed:number, status:'timeout'|'unavailable'='unavailable'):
    BvhPickMeasurement => ({outcome:UNSUPPORTED, workerQueryWallMs:null,
      roundTripWallMs:elapsed, status, scope:MEASUREMENT_SCOPE});

  const fail = () => {
    if(closed) return;
    closed = true; available = false; coverage = null; buildProfile = null;
    clearTimeout(buildTimer);
    settleReady(false);
    for(const [,request] of inflight) {
      clearTimeout(request.timer);
      request.resolve(unavailable(performance.now()-request.started));
    }
    inflight.clear();
    worker.terminate();
  };
  const buildTimer = setTimeout(fail,BUILD_DEADLINE_MS);
  worker.onmessage = (event: MessageEvent<{
    type:string;qualified?:boolean;id?:number;outcome?:BvhPick;
    faces?:number; indexedFaces?:number; excludedQuadFaces?:number; nodes?:number;
    workerBuildMs?:number; workerQueryMs?:number;
  }>) => {
    if(closed) return;
    const response = event.data;
    if(response.type === 'ready') {
      clearTimeout(buildTimer);
      const {faces,indexedFaces,excludedQuadFaces,nodes,workerBuildMs} = response;
      available = response.qualified === true &&
        Number.isSafeInteger(faces) && Number.isSafeInteger(indexedFaces) &&
        Number.isSafeInteger(excludedQuadFaces) && Number.isSafeInteger(nodes) &&
        faces! > 0 && indexedFaces! > 0 && excludedQuadFaces! >= 0 && nodes! > 0 &&
        indexedFaces! + excludedQuadFaces! === faces! &&
        typeof workerBuildMs === 'number' && Number.isFinite(workerBuildMs) &&
        workerBuildMs >= 0;
      if(available) {
        coverage = {sourceFaces:faces!,indexedFaces:indexedFaces!,
          excludedQuadFaces:excludedQuadFaces!};
        buildProfile = {preparationWallMs, readyRoundTripMs:performance.now()-started,
          workerBuildWallMs:workerBuildMs!, copiedInputBytes, nodeCount:nodes!,
          scope:'COPIED_TYPED_INPUT_AND_WORKER_CPU_NOT_HEAP_RSS_VRAM'};
      }
      settleReady(available);
      if(!available) fail();
    } else if(response.type === 'result' && typeof response.id === 'number') {
      const request = inflight.get(response.id);
      if (!request) return;
      inflight.delete(response.id);
      clearTimeout(request.timer);
      const raw = response.outcome;
      const validHit = raw?.kind === 'hit' &&
        Number.isSafeInteger(raw.sourceFaceId) && raw.sourceFaceId! >= 0 &&
        Number.isSafeInteger(raw.testedFaces) && raw.testedFaces >= 0;
      const validNonhit = (raw?.kind === 'miss'||raw?.kind === 'ambiguous') &&
        Number.isSafeInteger(raw.testedFaces) && raw.testedFaces >= 0;
      const queryMs = response.workerQueryMs;
      request.resolve({
        outcome:(validHit || validNonhit) ? raw! : UNSUPPORTED,
        workerQueryWallMs:typeof queryMs === 'number' && Number.isFinite(queryMs) &&
          queryMs >= 0 ? queryMs : null,
        roundTripWallMs:performance.now()-request.started,
        status:'completed',scope:MEASUREMENT_SCOPE,
      });
    }
  };
  worker.onerror = fail;
  worker.onmessageerror = fail;
  try {
    worker.postMessage({type:'build',payload},[payload.vertices.buffer,payload.polys.buffer,
      payload.offsets.buffer,payload.arities.buffer,payload.sourceIds.buffer]);
  } catch { fail(); }

  const pickWithMeasurement = (near:[number,number,number], far:[number,number,number],
      showTri:boolean, showQuad:boolean):Promise<BvhPickMeasurement> => {
    if(!available || closed || inflight.size>=4) return Promise.resolve(unavailable(0));
    const id = nextId++, pickStarted = performance.now();
    return new Promise<BvhPickMeasurement>((resolve)=>{
      const timer=setTimeout(()=>{
        inflight.delete(id);
        resolve(unavailable(performance.now()-pickStarted,'timeout'));
      },PICK_DEADLINE_MS);
      inflight.set(id,{resolve,timer,started:pickStarted});
      try {worker.postMessage({type:'pick',id,near,far,showTri,showQuad});}
      catch {
        clearTimeout(timer); inflight.delete(id);
        resolve(unavailable(performance.now()-pickStarted));
      }
    });
  };
  return {
    ready,
    isReady:()=>available && !closed,
    coverage:()=>coverage,
    buildMeasurement:()=>buildProfile,
    pickWithMeasurement,
    pick(near,far,showTri,showQuad) {
      return pickWithMeasurement(near,far,showTri,showQuad).then(x=>x.outcome);
    },
    dispose:fail,
  };
}
