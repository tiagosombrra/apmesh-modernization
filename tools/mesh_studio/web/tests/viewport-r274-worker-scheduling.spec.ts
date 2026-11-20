import { expect, test } from '@playwright/test';
import { mkdir, writeFile } from 'node:fs/promises';
import type { Page } from '@playwright/test';

const SOURCE_SHA='cbf6cd6308ba54544d06c5d562c491eb7d43ddb216365e0e9d188fd3430295e0';
const ROUNDS=24;
const WARMUP=6;

function summary(values:number[]) {
  const sorted=[...values].sort((a,b)=>a-b);
  if (!sorted.length) return {n:0,p50_ms:null,p95_ms:null};
  const p=(fraction:number)=>Math.round(sorted[Math.ceil(fraction*sorted.length)-1]*1000)/1000;
  return {n:sorted.length,p50_ms:p(.5),p95_ms:p(.95)};
}

/** Isolate Worker dispatch from React/VTK input, while keeping the exact real source. */
async function runPhase(page:Page,phase:'foreground'|'background'|'foreground_again') {
  return await page.evaluate(async ({phase,rounds,warmup,sha})=>{
    const {studyApi}=await import('/src/api.ts');
    const {createXyzBvhWorker}=await import('/src/xyzBvhClient.ts');
    const geometry=await studyApi.geometry('p1','xyz');
    if(geometry.source_sha256!==sha)throw new Error('original_P1_SHA_mismatch');
    const packed=geometry.packed!;
    const i=Array.from(packed.arities).findIndex(a=>a===3);
    if(i<0)throw new Error('source_P1_has_no_triangle');
    const start=packed.offsets[i];
    const point=(k:number):[number,number,number]=>{
      const offset=packed.polys[start+1+k]*3;
      return [packed.vertices[offset],packed.vertices[offset+1],packed.vertices[offset+2]];
    };
    const [a,b,c]=[point(0),point(1),point(2)];
    const center=a.map((v,k)=>(v+b[k]+c[k])/3);
    const e=b.map((v,k)=>v-a[k]),f=c.map((v,k)=>v-a[k]);
    const normal=[e[1]*f[2]-e[2]*f[1],e[2]*f[0]-e[0]*f[2],
      e[0]*f[1]-e[1]*f[0]];
    const size=Math.hypot(...normal);
    if(!(size>1e-12))throw new Error('invalid_original_P1_TRI');
    const near=center.map((v,k)=>v+normal[k]*.002/size) as [number,number,number];
    const far=center.map((v,k)=>v-normal[k]*.002/size) as [number,number,number];
    const sourceFaceId=packed.faceIds[i];
    const worker=createXyzBvhWorker(geometry);
    if(!worker||!await worker.ready)throw new Error('original_P1_Worker_unqualified');
    const stateBefore={visibility:document.visibilityState,hasFocus:document.hasFocus()};
    try {
      const rows=[];
      for(let n=0;n<rounds+warmup;n++) {
        const measurement=await worker.pickWithMeasurement(near,far,true,false);
        if (n<warmup)continue;
        rows.push({
          sourceFaceId:measurement.outcome.kind==='hit'?measurement.outcome.sourceFaceId:null,
          kind:measurement.outcome.kind,
          status:measurement.status,
          workerQueryMs:measurement.workerQueryWallMs,
          roundTripMs:measurement.roundTripWallMs,
        });
      }
      return {phase,originalSha:geometry.source_sha256,
        expectedFaceId:sourceFaceId,
        coverage:worker.coverage(),
        build:worker.buildMeasurement(),
        stateBefore,stateAfter:{visibility:document.visibilityState,hasFocus:document.hasFocus()},
        rows,
      };
    } finally {worker.dispose();}
  },{phase,rounds:ROUNDS,warmup:WARMUP,sha:SOURCE_SHA});
}

test('R2.7.4 compare Worker messaging under Chromium foreground/background focus',async ({page,context},info)=>{
  test.setTimeout(110_000);
  await page.goto('/');
  await page.bringToFront();
  const foreground=await runPhase(page,'foreground');
  const other=await context.newPage();
  let background;
  try {
    await other.goto('about:blank');
    await other.bringToFront();
    background=await runPhase(page,'background');
  } finally {await other.close();}
  await page.bringToFront();
  const recovered=await runPhase(page,'foreground_again');
  const phases=[foreground,background,recovered];
  for(const phase of phases) {
    expect(phase.originalSha).toBe(SOURCE_SHA);
    expect(phase.coverage).toEqual({sourceFaces:78,indexedFaces:36,excludedQuadFaces:42});
    expect(phase.rows).toHaveLength(ROUNDS);
    for(const row of phase.rows) {
      // A timeout or fallback is recorded rather than mislabeled as a fast result.
      if(row.kind==='hit')expect(row.sourceFaceId).toBe(phase.expectedFaceId);
      expect(Number.isFinite(row.roundTripMs)&&row.roundTripMs>=0).toBe(true);
    }
  }
  // Foreground must retain correct original IDs; background results are diagnostic.
  expect(foreground.rows.every(r=>r.kind==='hit'&&r.status==='completed')).toBe(true);
  expect(recovered.rows.every(r=>r.kind==='hit'&&r.status==='completed')).toBe(true);
  const receipt={
    schema:'apmesh.meshstudio.r274.chromium_worker_scheduling_focus.v1',
    classification:'REAL_P1_SOURCE_TRI_ONLY_WORKER_MESSAGE_DIAGNOSTIC_NOT_VIEWPORT_PICK_OR_GPU_TEST',
    sourceSha:SOURCE_SHA,warmupExcluded:WARMUP,samplesPerPhase:ROUNDS,
    phases:phases.map(p=>{
      const completed=p.rows.filter(r=>r.status==='completed'&&r.workerQueryMs!==null);
      return {
        phase:p.phase,
        stateBefore:p.stateBefore,stateAfter:p.stateAfter,
        build:p.build,coverage:p.coverage,
        exactOriginalIdHits:p.rows.filter(r=>r.sourceFaceId===p.expectedFaceId).length,
        timeouts:p.rows.filter(r=>r.status==='timeout').length,
        workerCpu:summary(completed.map(r=>r.workerQueryMs!)),
        messageRoundTrip:summary(completed.map(r=>r.roundTripMs)),
        noncomputeResidual:summary(completed.map(r=>Math.max(0,r.roundTripMs-r.workerQueryMs!))),
        raw:p.rows,
      };
    }),
    limits:[
      'headless_chromium_visibility_behavior_may_not_match_desktop_background_tab_throttling',
      'worker_is_rebuilt_and_warmed_independently_for_each_phase',
      'message_residual_does_not_isolate_one_way_transfers_or_queue_waits',
      'no_vtk_or_react_or_gpu_measurement_in_this_specific_test',
      'no_windows_GPU_or_native_RSS_VRAM',
    ],
  };
  await mkdir('test-results',{recursive:true});
  const json=JSON.stringify(receipt,null,2)+'\n';
  await writeFile('test-results/r274-worker-focus-diagnostic.json',json,'utf8');
  await info.attach('r274-worker-focus-diagnostic.json',{body:Buffer.from(json),contentType:'application/json'});
  console.log('R274_SCHEDULING_FOCUS='+JSON.stringify(receipt.phases.map(p=>({
    phase:p.phase,visibility:p.stateBefore.visibility,hasFocus:p.stateBefore.hasFocus,
    exactOriginalIdHits:p.exactOriginalIdHits,timeouts:p.timeouts,
    cpu:p.workerCpu,roundTrip:p.messageRoundTrip,residual:p.noncomputeResidual,
  }))));
});
