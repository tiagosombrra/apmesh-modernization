import { expect, test } from '@playwright/test';
import { mkdir, writeFile } from 'node:fs/promises';
import os from 'node:os';
import type { Locator, Page, BrowserContext } from '@playwright/test';

type Method='EXPERIMENTAL_XYZ_BVH_MAIN'|'EXPERIMENTAL_XYZ_BVH_WORKER'|'VTK_CELL_PICKER';
type Pixel={x:number;y:number;id:number};
type Sample={round:number;method:Method;faceId:number;eventToPickerMs:number;
  eventToTwoRafMs:number;pickerWallMs:number;browserVisibility:string;inspectorId:string};

const MODELS=[
  {id:'p1',sha:'cbf6cd6308ba54544d06c5d562c491eb7d43ddb216365e0e9d188fd3430295e0',
    sourceStatus:'CONTROLLED_PHYSICAL_GENERATION'},
  {id:'band',sha:'76b0b4defecc5d534815fb9f41e1405653597a4a0bee6cc7b722ec2460d7afd6',
    sourceStatus:'STAGED_UNACCEPTED'},
] as const;
const METHODS:Method[]=[
  'EXPERIMENTAL_XYZ_BVH_MAIN','EXPERIMENTAL_XYZ_BVH_WORKER','VTK_CELL_PICKER',
];
const GRID=[.25,.30,.35,.40,.45,.50,.55,.60,.65,.70,.75];
const ROUNDS=8,WARMUPS=2,FACES=3;

// A real desktop run is an explicit local action, never a hosted CI claim.
test.skip(Boolean(process.env.CI) ||
  process.env.APMESH_R277_PHYSICAL_DESKTOP!=='I_CONFIRM_PHYSICAL_WORKSTATION',
  'R2.7.7 requires an operator-attested physical workstation and headed Chromium.');

function distribution(values:number[]){
  if(!values.length||values.some(n=>!Number.isFinite(n)||n<0))
    throw new Error('R277_invalid_timing_distribution');
  const sorted=[...values].sort((a,b)=>a-b);
  const pct=(f:number)=>Math.round(sorted[Math.ceil(f*sorted.length)-1]*1000)/1000;
  return{n:sorted.length,p50_ms:pct(.5),p95_ms:pct(.95),
    min_ms:Math.round(sorted[0]*1000)/1000,max_ms:Math.round(sorted.at(-1)!*1000)/1000};
}

/** Browser-local event timer excludes Playwright transport and includes two RAF opportunities. */
async function measuredClick(page:Page,host:Locator,pixel:Pixel,method:Method){
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
async function camera(page:Page,sha:string){
  await page.getByTestId('save-cameras').click();
  return page.evaluate(sourceSha=>{
    const raw=localStorage.getItem('apmesh.meshstudio.camera.v1.'+sourceSha);
    if(!raw)throw new Error('R277_camera_snapshot_missing');
    const saved=JSON.parse(raw) as{source_sha256:string;camera_xyz:unknown};
    if(saved.source_sha256!==sourceSha)throw new Error('R277_camera_provenance_mismatch');
    return saved.camera_xyz;
  },sha);
}

/** Optional Chromium DevTools diagnostics are not process RSS or GPU presentation. */
async function cdpDiagnostics(context:BrowserContext,page:Page){
  let gpuInfo:unknown=null;
  let performanceMetrics:unknown=null;
  try {
    const browserSession=await context.browser()?.newBrowserCDPSession();
    if(browserSession){
      try {
        const response=await browserSession.send('SystemInfo.getInfo') as{
          gpu?:{devices?:Array<Record<string,unknown>>;auxAttributes?:Record<string,unknown>};
        };
        gpuInfo={
          devices:(response.gpu?.devices||[]).map(device=>({
            vendorId:device.vendorId,deviceId:device.deviceId,
            vendorString:device.vendorString,deviceString:device.deviceString,
            driverVendor:device.driverVendor,driverVersion:device.driverVersion,
          })),
          // The GPU list does not establish physical display scanout.
          scope:'CHROMIUM_CDP_GPU_DEVICE_DESCRIPTION_NOT_PRESENTED_FRAME_OR_VRAM',
        };
      }finally{await browserSession.detach();}
    }
  }catch(error){gpuInfo={error:String(error),scope:'UNAVAILABLE'};}
  try {
    const session=await context.newCDPSession(page);
    try{
      await session.send('Performance.enable');
      const result=await session.send('Performance.getMetrics') as{
        metrics?:Array<{name:string;value:number}>;
      };
      const subset=new Set(['JSHeapUsedSize','JSHeapTotalSize','Nodes',
        'Documents','Frames','TaskDuration','ScriptDuration','LayoutDuration']);
      performanceMetrics={
        values:Object.fromEntries((result.metrics||[])
          .filter(m=>subset.has(m.name)).map(m=>[m.name,m.value])),
        scope:'CDP_RENDERER_JS_AND_TASK_METRICS_NOT_PROCESS_RSS_OR_GPU_VRAM',
      };
    }finally{await session.detach();}
  }catch(error){performanceMetrics={error:String(error),scope:'UNAVAILABLE'};}
  return{gpuInfo,performanceMetrics};
}

for(const model of MODELS){
  test('R2.7.7 operator-attested headed local desktop '+model.id+' three-picker audit',
    async({page,context},info)=>{
      test.setTimeout(240_000);
      const driver=process.env.APMESH_R277_GPU_DRIVER?.trim()||'';
      const declaredGPU=process.env.APMESH_R277_GPU_MODEL?.trim()||'';
      const hz=Number(process.env.APMESH_R277_DISPLAY_REFRESH_HZ);
      if(!driver||!declaredGPU||!Number.isFinite(hz)||hz<30||hz>500)
        throw new Error('R277_requires_GPU_MODEL_GPU_DRIVER_DISPLAY_REFRESH_HZ_operator_entries');
      const worker=await context.newPage(),native=await context.newPage();
      const pages=[page,worker,native];
      const hosts=pages.map(p=>p.getByTestId('viewport-xyz'));
      await mkdir('test-results',{recursive:true});
      const tracePath='test-results/r277-local-'+model.id+'-chromium-trace.zip';
      await context.tracing.start({screenshots:true,snapshots:true,sources:true});
      try{
        // Register long-task diagnostics before navigation; no manual profile data is inferred.
        for(const p of pages)await p.addInitScript(()=>{
          const win=window as typeof window & {__r277LongTasks?:number[];__r277LongTaskSupported?:boolean};
          win.__r277LongTasks=[];
          win.__r277LongTaskSupported=typeof PerformanceObserver!=='undefined' &&
            PerformanceObserver.supportedEntryTypes.includes('longtask');
          if(win.__r277LongTaskSupported){
            try{
              new PerformanceObserver(list=>{
                for(const e of list.getEntries())win.__r277LongTasks!.push(e.duration);
              }).observe({type:'longtask',buffered:true});
            }catch{win.__r277LongTaskSupported=false;}
          }
        });
        await Promise.all([
          page.goto('/?xyzPicker=sync'),
          worker.goto('/?xyzPicker=bvh'),
          native.goto('/'),
        ]);
        for(let i=0;i<3;i++){
          await expect(hosts[i].locator('canvas').first()).toBeVisible();
          await expect(pages[i].locator('.model-foot code')).toHaveAttribute('title',model.sha);
        }
        const environment=await page.evaluate(async()=>{
          const {captureR277BrowserEnvironment}=await import('/src/r277Probe.ts');
          return captureR277BrowserEnvironment();
        });
        if(/HeadlessChrome/i.test(environment.browserUserAgent))
          throw new Error('R277_HEADLESS_BROWSER_REJECTED_USE_HEADED');
        if(environment.webgl.softwareSuspected!==false ||
           !environment.webgl.unmaskedRenderer)
          throw new Error('R277_GPU_RENDERER_UNVERIFIED_OR_SOFTWARE_REJECTED');
        await expect.poll(()=>hosts[0].getAttribute('data-main-bvh-ready'),{timeout:25_000}).toBe('true');
        await expect.poll(()=>hosts[1].getAttribute('data-bvh-ready'),{timeout:25_000}).toBe('true');
        for(const p of pages)await p.getByTestId('toggle-quad').uncheck();
        const bounds=await Promise.all(hosts.map(h=>h.boundingBox()));
        if(bounds.some(b=>!b))throw new Error('R277_missing_real_viewport');
        for(let i=1;i<3;i++){
          expect(Math.abs(bounds[i]!.width-bounds[0]!.width)).toBeLessThan(.1);
          expect(Math.abs(bounds[i]!.height-bounds[0]!.height)).toBeLessThan(.1);
        }
        const before=await Promise.all(pages.map(p=>camera(p,model.sha)));
        expect(before[1]).toEqual(before[0]);
        expect(before[2]).toEqual(before[0]);

        const candidatePixels:Pixel[]=[];
        for(const fy of GRID){
          for(const fx of GRID){
            const pixel={x:bounds[0]!.width*fx,y:bounds[0]!.height*fy};
            await hosts[0].evaluate(node=>{delete (node as HTMLElement).dataset.lastPickerMethod;});
            await hosts[0].click({position:pixel});
            await expect.poll(()=>hosts[0].getAttribute('data-last-picker-method'),{timeout:10_000})
              .toMatch(/^(EXPERIMENTAL_XYZ_BVH_MAIN|VTK_CELL_PICKER)$/);
            if(await hosts[0].getAttribute('data-last-picker-method')!=='EXPERIMENTAL_XYZ_BVH_MAIN')continue;
            const raw=await hosts[0].getAttribute('data-last-picker-source-id');
            if(!raw||!/^\d+$/.test(raw))throw new Error('R277_nonoriginal_face');
            const id=Number(raw);
            if(!candidatePixels.some(p=>p.id===id))candidatePixels.push({...pixel,id});
            if(candidatePixels.length===FACES)break;
          }
          if(candidatePixels.length===FACES)break;
        }
        expect(candidatePixels).toHaveLength(FACES);
        // Real pointer path in all three implementations with no cherry-picked mismatch.
        for(const pixel of candidatePixels)
          for(let i=0;i<3;i++)await measuredClick(pages[i],hosts[i],pixel,METHODS[i]);

        for(let warmup=0;warmup<WARMUPS;warmup++)
          for(const pixel of candidatePixels)
            for(let i=0;i<3;i++)await measuredClick(pages[i],hosts[i],pixel,METHODS[i]);

        const samples:Sample[]=[];
        for(let round=0;round<ROUNDS;round++){
          const order=[0,1,2].slice(round%3).concat([0,1,2].slice(0,round%3));
          if(round%2)order.reverse();
          const pixels=round%2?[...candidatePixels].reverse():candidatePixels;
          for(const pixel of pixels)for(const methodIndex of order){
            const x=await measuredClick(pages[methodIndex],hosts[methodIndex],pixel,
              METHODS[methodIndex]);
            samples.push({
              round,method:METHODS[methodIndex],faceId:pixel.id,
              eventToPickerMs:x.eventToPickerMs,
              eventToTwoRafMs:x.eventToTwoRafMs,pickerWallMs:x.pickerWallMs,
              browserVisibility:x.visibility,inspectorId:x.inspector!,
            });
          }
        }
        expect(samples).toHaveLength(ROUNDS*FACES*3);
        const after=await Promise.all(pages.map(p=>camera(p,model.sha)));
        expect(after).toEqual(before);
        const distributions=METHODS.map(method=>{
          const rows=samples.filter(s=>s.method===method);
          expect(rows).toHaveLength(ROUNDS*FACES);
          return {method,eventToPicker:distribution(rows.map(s=>s.eventToPickerMs)),
            eventToSecondRaf:distribution(rows.map(s=>s.eventToTwoRafMs)),
            pickerWall:distribution(rows.map(s=>s.pickerWallMs))};
        });
        const diagnostics=await cdpDiagnostics(context,page);
        const longTasks=await Promise.all(pages.map(async p=>p.evaluate(()=>{
          const win=window as typeof window & {__r277LongTasks?:number[];__r277LongTaskSupported?:boolean};
          return{supported:win.__r277LongTaskSupported===true,
            durationsMs:win.__r277LongTasks||[]};
        })));
        const refresh=await page.evaluate(()=>({
          devicePixelRatio:window.devicePixelRatio,
          screenCSS:{width:window.screen.width,height:window.screen.height},
        }));
        const receipt={
          schema:'apmesh.meshstudio.r277.operator_attested_headed_desktop.v1',
          classification:'PHYSICAL_DESKTOP_ATTESTED_NOT_GPU_PRESENT_OR_TOTAL_RAM_CERTIFIED',
          model:model.id,originalSourceSha:model.sha,sourceStatus:model.sourceStatus,
          originalSourceFaceIds:candidatePixels.map(p=>p.id),
          exactOriginalIdMatches:samples.length,
          conditions:{quadVisible:false,rounds:ROUNDS,
            warmupsPerFacePerMethod:WARMUPS,pickerOrder:'ROTATED_REVERSED'},
          operatorAttestation:{value:'I_CONFIRM_PHYSICAL_WORKSTATION',
            declaredGpuModel:declaredGPU,declaredGpuDriver:driver,declaredRefreshHz:hz},
          host:{os:os.platform(),osRelease:os.release(),arch:os.arch(),
            cpuModel:os.cpus()[0]?.model||'UNKNOWN',
            logicalCpus:os.cpus().length,
            totalHostMemoryBytes:os.totalmem(),
            node:process.version},
          browser:environment,display:refresh,cdp:diagnostics,
          synchronousBuildMs:await hosts[0].getAttribute('data-main-bvh-build-ms'),
          longTasks,distributions,rawSamples:samples,
          qualification:{sourceIdsInTest:true,
            physicalMachineOperatorAttested:true,
            rendererNonSoftwareStringVerified:true,
            hardwareGpuPresentTimestampVerified:false,
            totalBrowserRssMeasured:false,workerRssMeasured:false,
            gpuVramMeasured:false,largeRealAcceptedPatchMeshTested:false},
          caveats:[
            'headed_browser_and_operator_GPU_declaration_do_not_prove_presented_frame_timestamps',
            'exact_same_original_TRI_only_pixels_not_uniform_screen_selection',
            'two_requestAnimationFrame_callbacks_are_render_opportunity_only',
            'CDP_JSHeapUsedSize_not_total_browser_process_RSS',
            'no_process_memory_or_GPU_VRAM_measured_by_this_harness',
            'P1_is_controlled_source_and_Band_is_staged_unaccepted_not_repeated_epoch',
            'this_report_is_not_a_speedup_claim_or_approval_for_default_fast_picking',
          ],
        };
        const json=JSON.stringify(receipt,null,2)+'\n';
        const filename='r277-desktop-'+model.id+'-abc.json';
        await writeFile('test-results/'+filename,json,'utf8');
        await info.attach(filename,{body:Buffer.from(json),contentType:'application/json'});
        console.log('R277_PHYSICAL_DESKTOP='+JSON.stringify({
          model:model.id,sourceSha:model.sha,matched:samples.length,
          browserRenderer:environment.webgl.unmaskedRenderer,
          methods:distributions,
          gpuPresentQualified:false,gpuVramQualified:false,totalRssQualified:false,
        }));
      }finally{
        await context.tracing.stop({path:tracePath});
        await worker.close();
        await native.close();
      }
    });
}
