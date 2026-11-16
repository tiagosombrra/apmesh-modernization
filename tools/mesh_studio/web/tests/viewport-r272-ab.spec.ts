import { expect, test } from '@playwright/test';
import { mkdir, writeFile } from 'node:fs/promises';

type PickSample = { x:number; y:number; sourceFaceId:number; workerPickerCallMs:number };
type NativePair = PickSample & { nativeSourceFaceId:number|null; nativePickerCallMs:number };
const fractions = [.25,.30,.35,.40,.45,.50,.55,.60,.65,.70,.75];

// These are real source models but not independent source-generator experiments.
test('R2.7.2 two real models multi-pixel XYZ BVH and VTK source-face agreement', async ({ page }, info) => {
  test.setTimeout(150_000);
  const receipts = [];
  for (const model of [
    { id:'p1',sha:'cbf6cd6308ba54544d06c5d562c491eb7d43ddb216365e0e9d188fd3430295e0',
      originalTri:36,originalQuad:42,status:'CONTROLLED_PHYSICAL_GENERATION' },
    { id:'band',sha:'76b0b4defecc5d534815fb9f41e1405653597a4a0bee6cc7b722ec2460d7afd6',
      originalTri:44,originalQuad:62,status:'STAGED_UNACCEPTED' },
  ]) {
    await page.goto('/?xyzPicker=bvh');
    await page.getByTestId('model-select').selectOption(model.id);
    const xyz=page.getByTestId('viewport-xyz');
    await expect(xyz.locator('canvas').first()).toBeVisible();
    await expect(page.locator('.model-foot code')).toHaveAttribute('title',model.sha);
    await expect.poll(()=>xyz.getAttribute('data-bvh-ready'),{timeout:25_000}).toBe('true');
    expect(await xyz.getAttribute('data-bvh-indexed-faces')).toBe(String(model.originalTri));
    expect(await xyz.getAttribute('data-bvh-excluded-quads')).toBe(String(model.originalQuad));
    await page.getByTestId('toggle-quad').uncheck();
    const rect=await xyz.boundingBox();
    if(!rect)throw new Error('source_viewport_bounds_missing:'+model.id);
    const samples: PickSample[]=[];
    let attempted=0;
    for (const fy of fractions) {
      for (const fx of fractions) {
        const x=rect.width*fx,y=rect.height*fy;
        await xyz.evaluate(node=>{
          delete (node as HTMLElement).dataset.lastPickerMethod;
          delete (node as HTMLElement).dataset.lastPickerSourceId;
        });
        await xyz.click({position:{x,y}});
        attempted++;
        await expect.poll(()=>xyz.getAttribute('data-last-picker-method'),{timeout:5_000})
          .toMatch(/^(VTK_CELL_PICKER|EXPERIMENTAL_XYZ_BVH_WORKER)$/);
        if(await xyz.getAttribute('data-last-picker-method')!=='EXPERIMENTAL_XYZ_BVH_WORKER')continue;
        const rawId=await xyz.getAttribute('data-last-picker-source-id');
        const wall=Number(await xyz.getAttribute('data-last-picker-wall-ms'));
        if(!rawId||!/^\d+$/.test(rawId)||!Number.isFinite(wall)||wall<0)
          throw new Error('invalid_measured_worker_hit:'+model.id);
        const id=Number(rawId);
        if(samples.some(s=>s.sourceFaceId===id))continue;
        samples.push({x,y,sourceFaceId:id,workerPickerCallMs:wall});
        if(samples.length===3)break;
      }
      if(samples.length===3)break;
    }
    expect(samples.length, 'A/B requires distinct real source faces, not background or duplicate clicks')
      .toBeGreaterThanOrEqual(2);

    await page.goto('/');
    await page.getByTestId('model-select').selectOption(model.id);
    const native=page.getByTestId('viewport-xyz');
    await expect(native.locator('canvas').first()).toBeVisible();
    await expect(page.locator('.model-foot code')).toHaveAttribute('title',model.sha);
    await page.getByTestId('toggle-quad').uncheck();
    const matched:NativePair[]=[];
    for(const s of samples){
      await native.evaluate(node=>{
        delete (node as HTMLElement).dataset.lastPickerMethod;
        delete (node as HTMLElement).dataset.lastPickerSourceId;
      });
      await native.click({position:{x:s.x,y:s.y}});
      await expect.poll(()=>native.getAttribute('data-last-picker-method'),{timeout:5_000})
        .toBe('VTK_CELL_PICKER');
      const source=await native.getAttribute('data-last-picker-source-id');
      const wall=Number(await native.getAttribute('data-last-picker-wall-ms'));
      const nativeSourceFaceId=source&&/^\d+$/.test(source)?Number(source):null;
      expect(nativeSourceFaceId,'Exact original source-face IDs must agree at identical pixels')
        .toBe(s.sourceFaceId);
      expect(Number.isFinite(wall)&&wall>=0).toBe(true);
      matched.push({...s,nativeSourceFaceId,nativePickerCallMs:wall});
    }
    receipts.push({
      modelId:model.id,sourceSha:model.sha,sourceStatus:model.status,
      sourceFaces:model.originalTri+model.originalQuad,
      indexedTriFaces:model.originalTri,excludedWarpedQuadFaces:model.originalQuad,
      attemptedPixels:attempted,distinctWorkerHits:matched.length,
      allOriginalIdsAgreed:true,
      observations:matched,
    });
  }
  const receipt={
    schema:'apmesh.meshstudio.r272.multipixel_real_ui_ab.v1',
    classification:'CONTROLLED_REAL_P1_AND_STAGED_BAND_VISUAL_PICK_ONLY',
    viewer:'CHROMIUM_HOSTED_CI',
    scope:'PICK_CALL_WALL_TIME_NOT_CLICK_TO_PAINT_OR_GPU_LATENCY',
    originalFaceIdAgreement:true,
    models:receipts,
    limitations:[
      'selected_nonboundary_pixels_not_unbiased_random_sample',
      'small_diagnostic_sample_not_a_statistical_speedup_claim',
      'one_controlled_real_run_and_one_staged_unaccepted_candidate',
      'quad_layer_hidden_and_curved_quad_BVH_remains_unqualified',
      'no_native_process_RSS_or_GPU_VRAM_or_physical_Windows_GPU',
    ],
  };
  const json=JSON.stringify(receipt,null,2)+'\n';
  await mkdir('test-results',{recursive:true});
  await writeFile('test-results/r272-multipixel-real-ui-ab.json',json,'utf8');
  await info.attach('r272-multipixel-real-ui-ab.json',{
    body:Buffer.from(json),contentType:'application/json',
  });
  console.log('R272_REAL_UI_AB='+JSON.stringify(receipts.map(x=>({
    id:x.modelId,attempted:x.attemptedPixels,distinctMatches:x.distinctWorkerHits,
    sourceFaceIds:x.observations.map(y=>y.sourceFaceId),
    pickCallMs:x.observations.map(y=>({worker:y.workerPickerCallMs,native:y.nativePickerCallMs})),
  }))));
});
