import { expect, test } from '@playwright/test';
import { mkdir, writeFile } from 'node:fs/promises';
import type { Locator, Page } from '@playwright/test';

type Method = 'EXPERIMENTAL_XYZ_BVH_MAIN' | 'EXPERIMENTAL_XYZ_BVH_WORKER' | 'VTK_CELL_PICKER';
type Pixel = {x:number;y:number;sourceFaceId:number};
type Pick = {method:Method;wallMs:number;mainQueryMs:number|null;faceId:number};
const GRID=[.25,.30,.35,.40,.45,.50,.55,.60,.65,.70,.75];
const ROUNDS=8,PIXELS=3,WARMUP=2;
const models=[
  {id:'p1',sha:'cbf6cd6308ba54544d06c5d562c491eb7d43ddb216365e0e9d188fd3430295e0',
    tri:36,quad:42,sourceStatus:'CONTROLLED_PHYSICAL_GENERATION'},
  {id:'band',sha:'76b0b4defecc5d534815fb9f41e1405653597a4a0bee6cc7b722ec2460d7afd6',
    tri:44,quad:62,sourceStatus:'STAGED_UNACCEPTED'},
] as const;

function summary(xs:number[]) {
  if(!xs.length||xs.some(x=>!Number.isFinite(x)))throw new Error('bad_R275_distribution');
  const ordered=[...xs].sort((a,b)=>a-b);
  const p=(f:number)=>Math.round(ordered[Math.ceil(ordered.length*f)-1]*1000)/1000;
  return {n:xs.length,p50_ms:p(.5),p95_ms:p(.95),
    min_ms:Math.round(ordered[0]*1000)/1000,
    max_ms:Math.round(ordered[ordered.length-1]*1000)/1000};
}

/** Complete only for an exact original-face hit and the requested picker. */
async function readPick(host:Locator,pixel:Pixel,method:Method):Promise<Pick> {
  await host.evaluate(node=>{
    delete (node as HTMLElement).dataset.lastPickerMethod;
    delete (node as HTMLElement).dataset.lastPickerSourceId;
    delete (node as HTMLElement).dataset.lastPickerWallMs;
    delete (node as HTMLElement).dataset.lastMainBvhQueryMs;
  });
  await host.click({position:{x:pixel.x,y:pixel.y}});
  await expect.poll(()=>host.getAttribute('data-last-picker-method'),{timeout:10_000})
    .toBe(method);
  const [face,ms,main]=await Promise.all([
    host.getAttribute('data-last-picker-source-id'),
    host.getAttribute('data-last-picker-wall-ms'),
    host.getAttribute('data-last-main-bvh-query-ms'),
  ]);
  if(!face||!/^\d+$/.test(face)||ms===null||Number(face)!==pixel.sourceFaceId)
    throw new Error('R275_original_source_face_disagreement');
  const wallMs=Number(ms),mainQueryMs=main===null?null:Number(main);
  if(!Number.isFinite(wallMs)||wallMs<0)throw new Error('R275_invalid_picker_time');
  if(method==='EXPERIMENTAL_XYZ_BVH_MAIN'){
    if(mainQueryMs===null||!Number.isFinite(mainQueryMs)||mainQueryMs<0||
      mainQueryMs>wallMs+0.2)throw new Error('R275_invalid_main_BVH_query_time');
  }else if(mainQueryMs!==null)throw new Error('R275_stale_sync_picker_diagnostic');
  return {method,wallMs,mainQueryMs,faceId:Number(face)};
}

/** Camera snapshot is a scientific invariant, not an assumption based on identical URLs. */
async function snapshot(page:Page,sourceSha:string) {
  await page.getByTestId('save-cameras').click();
  return await page.evaluate(sha=>{
    const key='apmesh.meshstudio.camera.v1.'+sha;
    const raw=localStorage.getItem(key);
    if(!raw)throw new Error('R275_camera_snapshot_missing');
    const data=JSON.parse(raw) as {source_sha256:string;camera_xyz:unknown};
    if(data.source_sha256!==sha)throw new Error('R275_camera_sha_mismatch');
    return data.camera_xyz;
  },sourceSha);
}

async function ready(page:Page,model:typeof models[number],mode:'sync'|'bvh'|'native') {
  const host=page.getByTestId('viewport-xyz');
  await page.goto(mode==='sync'?'/?xyzPicker=sync':mode==='bvh'?'/?xyzPicker=bvh':'/');
  if(model.id!=='p1')await page.getByTestId('model-select').selectOption(model.id);
  await expect(host.locator('canvas').first()).toBeVisible();
  await expect(page.locator('.model-foot code')).toHaveAttribute('title',model.sha);
  if(mode==='sync'){
    await expect.poll(()=>host.getAttribute('data-main-bvh-ready'),{timeout:25_000}).toBe('true');
    expect(await host.getAttribute('data-main-bvh-indexed-faces')).toBe(String(model.tri));
    expect(await host.getAttribute('data-main-bvh-excluded-quads')).toBe(String(model.quad));
  }else if(mode==='bvh'){
    await expect.poll(()=>host.getAttribute('data-bvh-ready'),{timeout:25_000}).toBe('true');
  }
  await page.getByTestId('toggle-quad').uncheck();
  return host;
}

for(const model of models){
  test('R2.7.5 real '+model.id+' TRI-only sync/worker/VTK exact-pixel A/B/C',async ({page,context},info)=>{
    test.setTimeout(210_000);
    const workerPage=await context.newPage(),vtkPage=await context.newPage();
    try{
      const [sync,worker,vtk]=await Promise.all([
        ready(page,model,'sync'),ready(workerPage,model,'bvh'),ready(vtkPage,model,'native'),
      ]);
      const bounds=await Promise.all([sync.boundingBox(),worker.boundingBox(),vtk.boundingBox()]);
      if(bounds.some(b=>!b))throw new Error('R275_missing_viewports');
      expect(Math.abs(bounds[0]!.width-bounds[1]!.width)).toBeLessThan(.1);
      expect(Math.abs(bounds[0]!.width-bounds[2]!.width)).toBeLessThan(.1);
      expect(Math.abs(bounds[0]!.height-bounds[2]!.height)).toBeLessThan(.1);
      const cameraBefore=await Promise.all([page,workerPage,vtkPage]
        .map(p=>snapshot(p,model.sha)));
      expect(cameraBefore[1]).toEqual(cameraBefore[0]);
      expect(cameraBefore[2]).toEqual(cameraBefore[0]);
      const buildMs=Number(await sync.getAttribute('data-main-bvh-build-ms'));
      expect(Number.isFinite(buildMs)&&buildMs>=0).toBe(true);

      const candidates:Pixel[]=[];
      let scanned=0;
      for(const fy of GRID){
        for(const fx of GRID){
          const x=bounds[0]!.width*fx,y=bounds[0]!.height*fy;
          await sync.evaluate(node=>{delete (node as HTMLElement).dataset.lastPickerMethod;});
          await sync.click({position:{x,y}});
          scanned++;
          await expect.poll(()=>sync.getAttribute('data-last-picker-method'),{timeout:10_000})
            .toMatch(/^(EXPERIMENTAL_XYZ_BVH_MAIN|VTK_CELL_PICKER)$/);
          if(await sync.getAttribute('data-last-picker-method')!=='EXPERIMENTAL_XYZ_BVH_MAIN')continue;
          const id=await sync.getAttribute('data-last-picker-source-id');
          if(!id||!/^\d+$/.test(id))throw new Error('R275_missing_source_face');
          const sourceFaceId=Number(id);
          if(candidates.some(p=>p.sourceFaceId===sourceFaceId))continue;
          candidates.push({x,y,sourceFaceId});
          if(candidates.length===PIXELS)break;
        }
        if(candidates.length===PIXELS)break;
      }
      expect(candidates,'Need distinct original TRI faces to avoid cherry-picking one location')
        .toHaveLength(PIXELS);
      // Qualify the same pixel in all three real picker implementations before timing.
      for(const pixel of candidates) {
        await readPick(worker,pixel,'EXPERIMENTAL_XYZ_BVH_WORKER');
        await readPick(vtk,pixel,'VTK_CELL_PICKER');
      }
      const hosts={
        EXPERIMENTAL_XYZ_BVH_MAIN:sync,
        EXPERIMENTAL_XYZ_BVH_WORKER:worker,
        VTK_CELL_PICKER:vtk,
      } satisfies Record<Method,Locator>;
      const order:Method[]=['EXPERIMENTAL_XYZ_BVH_MAIN','EXPERIMENTAL_XYZ_BVH_WORKER','VTK_CELL_PICKER'];
      for(const pixel of candidates){
        for(let i=0;i<WARMUP;i++)for(const method of order)
          await readPick(hosts[method],pixel,method);
      }
      const observations: {round:number;pixel:Pixel;values:Record<Method,Pick>;order:Method[]}[]=[];
      for(let round=0;round<ROUNDS;round++){
        const rotated=order.slice(round%3).concat(order.slice(0,round%3));
        if(round%2)rotated.reverse();
        const pixels=round%2? [...candidates].reverse():candidates;
        for(const pixel of pixels){
          const values={} as Record<Method,Pick>;
          for(const method of rotated)values[method]=await readPick(hosts[method],pixel,method);
          observations.push({round,pixel,values,order:[...rotated]});
        }
      }
      expect(observations).toHaveLength(ROUNDS*PIXELS);
      const cameraAfter=await Promise.all([page,workerPage,vtkPage]
        .map(p=>snapshot(p,model.sha)));
      expect(cameraAfter).toEqual(cameraBefore);
      const extract=(method:Method)=>observations.map(x=>x.values[method].wallMs);
      const main=extract('EXPERIMENTAL_XYZ_BVH_MAIN'),
        workerMs=extract('EXPERIMENTAL_XYZ_BVH_WORKER'),
        vtkMs=extract('VTK_CELL_PICKER');
      const receipt={
        schema:'apmesh.meshstudio.r275.real_p1_band_sync_worker_vtk.v1',
        classification:'SMALL_REAL_SOURCE_TRI_ONLY_A_B_C_PICKER_CALL_NOT_GPU_PAINT',
        model:model.id,source_sha256:model.sha,source_status:model.sourceStatus,
        indexed_original_tri_faces:model.tri,excluded_nonplanar_quad_faces:model.quad,
        mainIndexBuildMs:buildMs,scanned_candidate_pixels:scanned,
        matched_source_faces:candidates.map(p=>p.sourceFaceId),
        warmup_per_method_and_face:WARMUP,rounds:ROUNDS,exact_matched_triples:observations.length,
        main:summary(main),worker:summary(workerMs),vtk:summary(vtkMs),
        paired_main_minus_vtk:summary(main.map((v,i)=>v-vtkMs[i])),
        main_query_only:summary(observations.map(x=>x.values.EXPERIMENTAL_XYZ_BVH_MAIN.mainQueryMs!)),
        identical_xyz_camera_before_after:true,observations,
        limitations:[
          'three_concurrent_headless_browser_pages_may_shift_Worker_scheduling',
          'same_source_face_identity_and_viewport_size_not_an_independent_scientific_surface_oracle',
          'selected_interior_positive_TRI_pixels_not_unbiased_screen_distribution',
          'main_thread_build_cost_excluded_from_per_click_distributions',
          'no_input_to_visible_paint_or_GPU_or_Windows_hardware_or_total_memory',
          'native_VTK_remains_default_and_nonplanar_QUAD_must_fallback',
        ],
      };
      const file='test-results/r275-'+model.id+'-sync-worker-vtk.json';
      await mkdir('test-results',{recursive:true});
      const json=JSON.stringify(receipt,null,2)+'\n';
      await writeFile(file,json,'utf8');
      await info.attach(file.split('/').at(-1)!,{body:Buffer.from(json),contentType:'application/json'});
      console.log('R275_MAIN_WORKER_VTK='+JSON.stringify({model:receipt.model,
        matched:receipt.exact_matched_triples,faces:receipt.matched_source_faces,
        buildMs:receipt.mainIndexBuildMs,main:receipt.main,
        worker:receipt.worker,vtk:receipt.vtk,mainQuery:receipt.main_query_only}));
    }finally{await workerPage.close();await vtkPage.close();}
  });
}

test('R2.7.5 original P1 QUAD visibility forces native VTK and preserves source',async ({page})=>{
  await page.goto('/?xyzPicker=sync');
  const host=page.getByTestId('viewport-xyz');
  await expect(host.locator('canvas').first()).toBeVisible();
  await expect.poll(()=>host.getAttribute('data-main-bvh-ready'),{timeout:25_000}).toBe('true');
  await host.click({position:{x:170,y:180}});
  await expect.poll(()=>host.getAttribute('data-last-picker-method'),{timeout:10_000})
    .toBe('VTK_CELL_PICKER');
  const result=await page.evaluate(async ()=>{
    const {studyApi}=await import('/src/api.ts');
    const {createBoundedXyzBvhMain,MAIN_BVH_MAX_FACES,MAIN_BVH_MAX_VERTICES}=
      await import('/src/xyzBvhMain.ts');
    const mesh=await studyApi.geometry('p1','xyz');
    const originalBytes=mesh.packed!.vertices.byteLength;
    const originalIds=mesh.packed!.faceIds.slice();
    const main=createBoundedXyzBvhMain(mesh);
    if(!main)throw new Error('R275_source_rejected');
    const fallback=main.pick([.3,.3,2],[.3,.3,-2],true,true);
    const noTri=main.pick([.3,.3,2],[.3,.3,-2],false,false);
    const tooManyFaces=createBoundedXyzBvhMain({
      ...mesh,packed:{...mesh.packed!,faceIds:new Uint32Array(MAIN_BVH_MAX_FACES+1)},
    });
    const tooManyVertices=createBoundedXyzBvhMain({
      ...mesh,packed:{...mesh.packed!,vertices:new Float32Array((MAIN_BVH_MAX_VERTICES+1)*3)},
    });
    return {fallback,noTri,tooManyFaces:tooManyFaces===null,
      tooManyVertices:tooManyVertices===null,
      bufferIntact:mesh.packed!.vertices.byteLength===originalBytes,
      idsIntact:originalIds.every((id,i)=>id===mesh.packed!.faceIds[i]),
      covered:main.profile,sourceSha:mesh.source_sha256};
  });
  expect(result.fallback.kind).toBe('ambiguous');
  expect(result.noTri.kind).toBe('miss');
  expect(result.tooManyFaces).toBe(true);
  expect(result.tooManyVertices).toBe(true);
  expect(result.bufferIntact).toBe(true);
  expect(result.idsIntact).toBe(true);
  expect(result.covered).toMatchObject({sourceFaces:78,indexedFaces:36,excludedQuads:42});
  expect(result.sourceSha).toBe(models[0].sha);
});
