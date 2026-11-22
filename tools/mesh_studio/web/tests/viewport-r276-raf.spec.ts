import { expect, test } from '@playwright/test';
import { mkdir, writeFile } from 'node:fs/promises';
import type { Locator, Page } from '@playwright/test';

type Picker = 'EXPERIMENTAL_XYZ_BVH_MAIN' | 'EXPERIMENTAL_XYZ_BVH_WORKER' | 'VTK_CELL_PICKER';
type Pixel = {x:number;y:number;faceId:number};
type Timeline = {eventToCallbackMs:number;eventToTwoRafMs:number;
  callbackToTwoRafMs:number;method:string;sourceFaceId:string|null;
  inspectorFace:string|null;visibility:string;twoRafCount:number};

const P1_SHA='cbf6cd6308ba54544d06c5d562c491eb7d43ddb216365e0e9d188fd3430295e0';
const grid=[.25,.30,.35,.40,.45,.50,.55,.60,.65,.70,.75];
const ROUND_COUNT=8;
const WARMUP=2;

function stats(values:number[]){
  if(!values.length||values.some(x=>!Number.isFinite(x)||x<0))throw new Error('invalid_r276_event_to_raf_observation');
  const a=[...values].sort((x,y)=>x-y);
  const p=(n:number)=>Math.round(a[Math.ceil(a.length*n)-1]*1000)/1000;
  return {n:a.length,p50_ms:p(.5),p95_ms:p(.95),min_ms:a[0],max_ms:a[a.length-1]};
}

/**
 * Capture time at the browser click event, then on picker completion wait
 * through two requestAnimationFrame callbacks without a Playwright polling gap.
 * This is a render-opportunity proxy, NOT a GPU-presented-frame timestamp.
 */
async function onePointerSample(page:Page,host:Locator,pixel:Pixel,expected:Picker):Promise<Timeline>{
  await host.evaluate(node=>{
    const element=node as HTMLElement;
    delete element.dataset.lastPickerMethod;
    delete element.dataset.lastPickerWallMs;
    delete element.dataset.lastPickerSourceId;
    const debug=window as typeof window & {__r276Timeline?:Promise<unknown>};
    debug.__r276Timeline=new Promise(resolve=>{
      const capture=()=>{
        element.removeEventListener('click',capture,true);
        const started=performance.now();
        const observer=new MutationObserver(()=>{
          if(!element.dataset.lastPickerMethod)return;
          observer.disconnect();
          const callbackAt=performance.now();
          requestAnimationFrame(()=>requestAnimationFrame(()=>{
            const ended=performance.now();
            resolve({
              eventToCallbackMs:callbackAt-started,
              eventToTwoRafMs:ended-started,
              callbackToTwoRafMs:ended-callbackAt,
              method:element.dataset.lastPickerMethod,
              sourceFaceId:element.dataset.lastPickerSourceId||null,
              inspectorFace:document.querySelector('.face-id')?.textContent||null,
              visibility:document.visibilityState,
              twoRafCount:2,
            });
          }));
        });
        observer.observe(element,{attributes:true,attributeFilter:['data-last-picker-method']});
      };
      element.addEventListener('click',capture,true);
    });
  });
  await host.click({position:{x:pixel.x,y:pixel.y}});
  const result=await page.evaluate(async()=>{
    const debug=window as typeof window & {__r276Timeline?:Promise<unknown>};
    if(!debug.__r276Timeline)throw new Error('r276_event_timeline_not_armed');
    return await debug.__r276Timeline;
  }) as Timeline;
  expect(result.method).toBe(expected);
  expect(result.sourceFaceId).toBe(String(pixel.faceId));
  expect(result.inspectorFace).toBe('#'+pixel.faceId);
  expect(result.visibility).toBe('visible');
  expect(result.eventToTwoRafMs).toBeGreaterThanOrEqual(result.eventToCallbackMs);
  expect(result.callbackToTwoRafMs).toBeGreaterThanOrEqual(0);
  return result;
}

test('R2.7.6 real P1 event-to-two-RAF proxy keeps source ID across sync Worker and native VTK',
  async ({page,context},info)=>{
    test.setTimeout(180_000);
    const worker=await context.newPage(),native=await context.newPage();
    try {
      await Promise.all([page.goto('/?xyzPicker=sync'),
        worker.goto('/?xyzPicker=bvh'),native.goto('/')]);
      const hosts=[
        page.getByTestId('viewport-xyz'),
        worker.getByTestId('viewport-xyz'),
        native.getByTestId('viewport-xyz'),
      ];
      const pages=[page,worker,native];
      const methods:Picker[]=[
        'EXPERIMENTAL_XYZ_BVH_MAIN','EXPERIMENTAL_XYZ_BVH_WORKER','VTK_CELL_PICKER',
      ];
      for(let i=0;i<3;i++){
        await expect(hosts[i].locator('canvas').first()).toBeVisible();
        await expect(pages[i].locator('.model-foot code')).toHaveAttribute('title',P1_SHA);
      }
      await expect.poll(()=>hosts[0].getAttribute('data-main-bvh-ready'),{timeout:25_000}).toBe('true');
      await expect.poll(()=>hosts[1].getAttribute('data-bvh-ready'),{timeout:25_000}).toBe('true');
      for(const p of pages)await p.getByTestId('toggle-quad').uncheck();
      const rectangles=await Promise.all(hosts.map(h=>h.boundingBox()));
      if(rectangles.some(r=>!r))throw new Error('missing_r276_real_source_viewport');
      expect(Math.abs(rectangles[0]!.width-rectangles[1]!.width)).toBeLessThan(.1);
      expect(Math.abs(rectangles[0]!.width-rectangles[2]!.width)).toBeLessThan(.1);

      let pixel:Pixel|null=null;
      for(const fy of grid){
        for(const fx of grid){
          const x=rectangles[0]!.width*fx,y=rectangles[0]!.height*fy;
          await hosts[0].evaluate(node=>{delete (node as HTMLElement).dataset.lastPickerMethod;});
          await hosts[0].click({position:{x,y}});
          await expect.poll(()=>hosts[0].getAttribute('data-last-picker-method'),{timeout:10_000})
            .toMatch(/^(EXPERIMENTAL_XYZ_BVH_MAIN|VTK_CELL_PICKER)$/);
          if(await hosts[0].getAttribute('data-last-picker-method')!=='EXPERIMENTAL_XYZ_BVH_MAIN')continue;
          const id=await hosts[0].getAttribute('data-last-picker-source-id');
          if(!id||!/^\d+$/.test(id))throw new Error('missing_original_face_id');
          pixel={x,y,faceId:Number(id)};
          break;
        }
        if(pixel)break;
      }
      expect(pixel,'requires a real interior TRI pixel').not.toBeNull();

      for(let i=0;i<WARMUP;i++)for(let m=0;m<3;m++)
        await onePointerSample(pages[m],hosts[m],pixel!,methods[m]);

      const observations:{round:number;method:Picker;timeline:Timeline}[]=[];
      for(let round=0;round<ROUND_COUNT;round++){
        const modes=round%3===0?[0,1,2]:round%3===1?[1,2,0]:[2,0,1];
        if(round%2)modes.reverse();
        for(const m of modes){
          const timeline=await onePointerSample(pages[m],hosts[m],pixel!,methods[m]);
          observations.push({round,method:methods[m],timeline});
        }
      }
      const distributions=methods.map(method=>{
        const rows=observations.filter(x=>x.method===method).map(x=>x.timeline);
        expect(rows).toHaveLength(ROUND_COUNT);
        return {
          method,
          event_to_callback:stats(rows.map(x=>x.eventToCallbackMs)),
          event_to_two_raf:stats(rows.map(x=>x.eventToTwoRafMs)),
          callback_to_two_raf:stats(rows.map(x=>x.callbackToTwoRafMs)),
        };
      });
      const receipt={
        schema:'apmesh.meshstudio.r276.event_to_two_raf_proxy.v1',
        classification:'REAL_P1_TRI_ONLY_BROWSER_RENDER_OPPORTUNITY_NOT_GPU_PRESENTATION',
        originalSha256:P1_SHA,originalSourceFaceId:pixel!.faceId,
        quadVisible:false,warmupPerMethod:WARMUP,rounds:ROUND_COUNT,
        measuredSelections:observations.length,allOriginalIdsMatched:true,
        distributions,observations,
        caveats:[
          'requestAnimationFrame_twice_is_not_a_guarantee_of_GPU_present_or_visible_pixels',
          'browser_event_capture_and_DOM_attribute_completion_not_OS_hardware_input_time',
          'one_controlled_P1_source_face_under_one_hosted_chromium_instance',
          'three_concurrent_pages_can_change_event_queue_workload',
          'source_face_and_inspector_text_are_observed_after_second_raf',
          'no_physical_Windows_GPU_memory_or_native_worker_RSS',
        ],
      };
      await mkdir('test-results',{recursive:true});
      const json=JSON.stringify(receipt,null,2)+'\n';
      await writeFile('test-results/r276-event-to-two-raf-proxy.json',json,'utf8');
      await info.attach('r276-event-to-two-raf-proxy.json',
        {body:Buffer.from(json),contentType:'application/json'});
      console.log('R276_TWO_RAF_EVENT_PROXY='+JSON.stringify({
        originalFaceId:pixel!.faceId,samples:observations.length,distributions,
      }));
    }finally{
      await worker.close();
      await native.close();
    }
  });
