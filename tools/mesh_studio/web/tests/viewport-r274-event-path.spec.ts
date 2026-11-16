import { expect, test } from '@playwright/test';
import { mkdir, writeFile } from 'node:fs/promises';
import type { Locator } from '@playwright/test';

const SOURCE_SHA='cbf6cd6308ba54544d06c5d562c491eb7d43ddb216365e0e9d188fd3430295e0';
const GRID=[.25,.30,.35,.40,.45,.50,.55,.60,.65,.70,.75];
const ROUNDS=12;
const WARMUP=3;

function percentile(values:number[],f:number) {
  const ordered=[...values].sort((a,b)=>a-b);
  return Math.round(ordered[Math.ceil(ordered.length*f)-1]*1000)/1000;
}
function summarize(rows:{wallMs:number;roundTripMs:number;cpuMs:number}[]) {
  return {
    n:rows.length,
    callback_p50_ms:percentile(rows.map(r=>r.wallMs),.5),
    callback_p95_ms:percentile(rows.map(r=>r.wallMs),.95),
    roundtrip_p50_ms:percentile(rows.map(r=>r.roundTripMs),.5),
    roundtrip_p95_ms:percentile(rows.map(r=>r.roundTripMs),.95),
    worker_cpu_p50_ms:percentile(rows.map(r=>r.cpuMs),.5),
    residual_p50_ms:percentile(rows.map(r=>Math.max(0,r.roundTripMs-r.cpuMs)),.5),
  };
}

type Pixel={x:number;y:number;sourceFaceId:number};

/** A stale diagnostic must never count as completion of a new asynchronous click. */
async function sample(host:Locator,rect:{x:number;y:number},pixel:Pixel,mode:'pointer'|'dom') {
  await host.evaluate(node=>{
    delete (node as HTMLElement).dataset.lastPickerMethod;
    delete (node as HTMLElement).dataset.lastPickerSourceId;
    delete (node as HTMLElement).dataset.lastPickerWallMs;
    delete (node as HTMLElement).dataset.lastWorkerRoundTripMs;
    delete (node as HTMLElement).dataset.lastWorkerQueryMs;
  });
  if(mode==='pointer') {
    await host.click({position:{x:pixel.x,y:pixel.y}});
  } else {
    // Dispatch on the same viewport; preserve the exact browser client coordinates.
    await host.dispatchEvent('click',{
      bubbles:true,clientX:rect.x+pixel.x,clientY:rect.y+pixel.y,
    });
  }
  await expect.poll(()=>host.getAttribute('data-last-picker-method'),{timeout:10_000})
    .toBe('EXPERIMENTAL_XYZ_BVH_WORKER');
  const raw=await Promise.all([
    host.getAttribute('data-last-picker-source-id'),
    host.getAttribute('data-last-picker-wall-ms'),
    host.getAttribute('data-last-worker-round-trip-ms'),
    host.getAttribute('data-last-worker-query-ms'),
  ]);
  if(raw.some(v=>v===null)||!/^\d+$/.test(raw[0]!))throw new Error('missing_R274_viewport_timing');
  const faceId=Number(raw[0]),wallMs=Number(raw[1]),roundTripMs=Number(raw[2]),cpuMs=Number(raw[3]);
  if(faceId!==pixel.sourceFaceId||![wallMs,roundTripMs,cpuMs].every(v=>Number.isFinite(v)&&v>=0)||
    wallMs+.2<roundTripMs||roundTripMs+.2<cpuMs)throw new Error('R274_viewport_time_or_source_mismatch');
  return {wallMs,roundTripMs,cpuMs,faceId,mode};
}

test('R2.7.4 isolate real P1 viewport Worker timing for pointer vs DOM click',async ({page},info)=>{
  test.setTimeout(110_000);
  await page.goto('/?xyzPicker=bvh');
  await page.bringToFront();
  const host=page.getByTestId('viewport-xyz');
  await expect(host.locator('canvas').first()).toBeVisible();
  await expect(page.locator('.model-foot code')).toHaveAttribute('title',SOURCE_SHA);
  await expect.poll(()=>host.getAttribute('data-bvh-ready'),{timeout:25_000}).toBe('true');
  await page.getByTestId('toggle-quad').uncheck();
  const rect=await host.boundingBox();
  if(!rect)throw new Error('R274_original_P1_viewport_missing');
  let pixel:Pixel|null=null;
  for(const fy of GRID) {
    for(const fx of GRID) {
      await host.evaluate(node=>{delete (node as HTMLElement).dataset.lastPickerMethod;});
      await host.click({position:{x:rect.width*fx,y:rect.height*fy}});
      await expect.poll(()=>host.getAttribute('data-last-picker-method'),{timeout:10_000})
        .toMatch(/^(VTK_CELL_PICKER|EXPERIMENTAL_XYZ_BVH_WORKER)$/);
      if(await host.getAttribute('data-last-picker-method')!=='EXPERIMENTAL_XYZ_BVH_WORKER')continue;
      const originalId=await host.getAttribute('data-last-picker-source-id');
      if(!originalId||!/^\d+$/.test(originalId))throw new Error('missing_original_P1_TRI_id');
      pixel={x:rect.width*fx,y:rect.height*fy,sourceFaceId:Number(originalId)};
      break;
    }
    if(pixel)break;
  }
  expect(pixel,'Require a qualified original TRI hit, not a background miss').not.toBeNull();

  for(let i=0;i<WARMUP;i++){
    await sample(host,rect,pixel!,'pointer');
    await sample(host,rect,pixel!,'dom');
  }
  const observations=[];
  for(let i=0;i<ROUNDS;i++){
    const modeOrder=i%2===0 ? ['pointer','dom'] as const : ['dom','pointer'] as const;
    for(const mode of modeOrder) {
      observations.push({round:i,...await sample(host,rect,pixel!,mode)});
    }
  }
  const pointer=observations.filter(r=>r.mode==='pointer');
  const dom=observations.filter(r=>r.mode==='dom');
  expect(pointer).toHaveLength(ROUNDS);
  expect(dom).toHaveLength(ROUNDS);
  const state=await page.evaluate(()=>({visibility:document.visibilityState,hasFocus:document.hasFocus()}));
  const receipt={
    schema:'apmesh.meshstudio.r274.single_viewport_event_path.v1',
    classification:'ONE_REAL_P1_TRI_VIEWPORT_WORKER_EVENT_DIAGNOSTIC_NOT_SCIENTIFIC_PERFORMANCE_RELEASE',
    originalSourceSha:SOURCE_SHA,originalSourceFaceId:pixel!.sourceFaceId,
    quadVisible:false,warmupPerMode:WARMUP,rounds:ROUNDS,
    methodOrder:'ALTERNATING_POINTER_DOM',state,
    pointer:summarize(pointer),dom:summarize(dom),observations,
    caveats:[
      'one_headless_chromium_host_one_source_triangle_not_multihost_statistics',
      'DOM_dispatch_is_synthetic_and_does_not_represent_human_input',
      'pointer_vs_dispatch_does_not_identify_an_individual_event_loop_queue',
      'same_real_source_UI_and_Worker_not_GPU_frame_or_React_paint_measurement',
      'warped_QUAD_visibility_is_off_and_VTK_is_default_in_production',
    ],
  };
  await mkdir('test-results',{recursive:true});
  const json=JSON.stringify(receipt,null,2)+'\n';
  await writeFile('test-results/r274-single-viewport-event-path.json',json,'utf8');
  await info.attach('r274-single-viewport-event-path.json',{body:Buffer.from(json),contentType:'application/json'});
  console.log('R274_UI_EVENT_PATH='+JSON.stringify({sourceFaceId:receipt.originalSourceFaceId,
    pointer:receipt.pointer,dom:receipt.dom,visibility:state.visibility,hasFocus:state.hasFocus}));
});
