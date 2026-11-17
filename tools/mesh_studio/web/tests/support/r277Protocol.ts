import { expect } from '@playwright/test';
import type { Locator, Page } from '@playwright/test';

/** Shared exact-source XYZ picker protocol for hosted preflight and physical desktop. */
export type Method='EXPERIMENTAL_XYZ_BVH_MAIN'|'EXPERIMENTAL_XYZ_BVH_WORKER'|'VTK_CELL_PICKER';
export type Pixel={x:number;y:number;id:number};
export type Sample={round:number;method:Method;faceId:number;
  pixelX:number;pixelY:number;
  eventToPickerMs:number;eventToTwoRafMs:number;pickerWallMs:number;
  browserVisibility:string;inspectorId:string};

export const MODELS=[
  {id:'p1',sha:'cbf6cd6308ba54544d06c5d562c491eb7d43ddb216365e0e9d188fd3430295e0',
    sourceStatus:'CONTROLLED_PHYSICAL_GENERATION'},
  {id:'band',sha:'76b0b4defecc5d534815fb9f41e1405653597a4a0bee6cc7b722ec2460d7afd6',
    sourceStatus:'STAGED_UNACCEPTED'},
] as const;
export const METHODS:Method[]=[
  'EXPERIMENTAL_XYZ_BVH_MAIN','EXPERIMENTAL_XYZ_BVH_WORKER','VTK_CELL_PICKER',
];
export const GRID=[.25,.30,.35,.40,.45,.50,.55,.60,.65,.70,.75];
export const ROUNDS=8,WARMUPS=2,FACES=3;

export function distribution(values:number[]){
  if(!values.length||values.some(n=>!Number.isFinite(n)||n<0))
    throw new Error('R277_invalid_timing_distribution');
  const sorted=[...values].sort((a,b)=>a-b);
  const pct=(f:number)=>Math.round(sorted[Math.ceil(f*sorted.length)-1]*1000)/1000;
  return{n:sorted.length,p50_ms:pct(.5),p95_ms:pct(.95),
    min_ms:Math.round(sorted[0]*1000)/1000,max_ms:Math.round(sorted.at(-1)!*1000)/1000};
}

/** Browser-local event timer excludes Playwright transport and includes two RAF opportunities. */
export async function measuredClick(page:Page,host:Locator,pixel:Pixel,method:Method){
  await host.evaluate(node=>{
    const el=node as HTMLElement;
    delete el.dataset.lastPickerMethod;
    delete el.dataset.lastPickerSourceId;
    delete el.dataset.lastPickerWallMs;
    const state=window as typeof window & {__r277Pending?:Promise<unknown>};
    state.__r277Pending=new Promise(resolve=>{
      const capture=()=>{
        el.removeEventListener('click',capture,true);
        const start=performance.now();
        const observer=new MutationObserver(()=>{
          if(!el.dataset.lastPickerMethod)return;
          observer.disconnect();
          const completed=performance.now();
          requestAnimationFrame(()=>requestAnimationFrame(()=>{
            resolve({
              method:el.dataset.lastPickerMethod,
              sourceId:el.dataset.lastPickerSourceId||null,
              pickerWallMs:Number(el.dataset.lastPickerWallMs),
              eventToPickerMs:completed-start,
              eventToTwoRafMs:performance.now()-start,
              inspector:document.querySelector('.face-id')?.textContent||null,
              visibility:document.visibilityState,
            });
          }));
        });
        observer.observe(el,{attributes:true,attributeFilter:['data-last-picker-method']});
      };
      el.addEventListener('click',capture,true);
    });
  });
  await page.bringToFront();
  await host.click({position:{x:pixel.x,y:pixel.y}});
  const result=await page.evaluate(async()=>{
    const state=window as typeof window & {__r277Pending?:Promise<unknown>};
    if(!state.__r277Pending)throw new Error('R277_click_was_not_armed');
    return await state.__r277Pending;
  }) as{method:string;sourceId:string|null;pickerWallMs:number;eventToPickerMs:number;
    eventToTwoRafMs:number;inspector:string|null;visibility:string};
  expect(result.method).toBe(method);
  expect(result.sourceId).toBe(String(pixel.id));
  expect(result.inspector).toBe('#'+pixel.id);
  expect(result.visibility).toBe('visible');
  expect(result.eventToTwoRafMs).toBeGreaterThanOrEqual(result.eventToPickerMs);
  expect(Number.isFinite(result.pickerWallMs)&&result.pickerWallMs>=0).toBe(true);
  return result;
}

/** Capture and compare exact camera poses instead of assuming identical screenshots. */
export async function camera(page:Page,sha:string){
  await page.getByTestId('save-cameras').click();
  return page.evaluate(sourceSha=>{
    const raw=localStorage.getItem('apmesh.meshstudio.camera.v1.'+sourceSha);
    if(!raw)throw new Error('R277_camera_snapshot_missing');
    const saved=JSON.parse(raw) as{source_sha256:string;camera_xyz:unknown};
    if(saved.source_sha256!==sourceSha)throw new Error('R277_camera_provenance_mismatch');
    return saved.camera_xyz;
  },sha);
}

