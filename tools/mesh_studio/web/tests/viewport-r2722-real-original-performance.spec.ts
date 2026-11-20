import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { createHash } from 'node:crypto';
import { expect, test } from '@playwright/test';
import type { Page } from '@playwright/test';

/**
 * R2.7.22: hosted Chromium numbers from the *real, same-run C++ native source*
 * artifact. Do not label them physical Windows GPU present/RSS/VRAM metrics.
 */
const source = resolve(process.cwd(), '../../../build/r2720-native-accepted-scene.json');
const output = resolve(process.cwd(),
  '../../../build/mesh-studio/r2722-original-chromium-performance.json');

function stats(values: number[]) {
  const v = [...values].sort((a,b)=>a-b);
  if(!v.length) throw new Error('r2722_no_real_browser_measurements');
  const percentile = (p:number) => v[Math.ceil((v.length-1)*p)];
  return {
    samples: v.length, minimum_ms: v[0], median_ms: percentile(0.5),
    p95_ms: percentile(0.95), maximum_ms: v[v.length-1],
    observed_ms: values.map(x=>Math.round(x*1000)/1000),
  };
}

async function paintAfterDOM(page:Page) {
  // A double requestAnimationFrame is an approximate UI readiness boundary,
  // not proof that the GPU actually presented a completed frame.
  await page.evaluate(() => new Promise<void>(resolve =>
    requestAnimationFrame(() => requestAnimationFrame(() => resolve()))));
}

async function now(page:Page):Promise<number> {
  return page.evaluate(()=>performance.now());
}

async function browserMetricSnapshot(
  cdp:import('@playwright/test').CDPSession,
) {
  const result=await cdp.send('Performance.getMetrics');
  const map=new Map<string,number>(result.metrics.map(
    (entry:{name:string,value:number}) => [entry.name,entry.value]));
  return {
    js_heap_used_bytes:map.get('JSHeapUsedSize') ?? null,
    js_heap_total_bytes:map.get('JSHeapTotalSize') ?? null,
    dom_nodes:map.get('Nodes') ?? null,
    dom_documents:map.get('Documents') ?? null,
    layout_count:map.get('LayoutCount') ?? null,
  };
}

test('R2.7.22 original native Eistute Book Chromium import, patch, sample, heap and canvas stability',async({page})=>{
  test.setTimeout(360_000);
  test.skip(!existsSync(source),
    'Real same-run original accepted C++ artifact not available; CI MUST supply it.');
  const original=readFileSync(source);
  const manifest=JSON.parse(original.toString('utf8'));
  expect(manifest.schema).toBe(
    'apmesh.meshstudio.r2720.original_accepted_tri_scene.v1');
  expect(manifest.no_implicit_node_welding).toBe(true);
  const candidates=manifest.scenes as Array<{
    model:'eistute'|'book',native_tri_faces:number,
    accepted_native_step:number,source_ndjson_sha256:string,
    source_patch_face_counts:number[],native_source_patches:number,
  }>;
  expect(candidates.map(x=>x.model)).toEqual(['eistute','book']);
  expect(candidates.map(x=>x.native_tri_faces)).toEqual([1168,4256]);
  expect(candidates.map(x=>x.native_source_patches)).toEqual([4,28]);
  expect(candidates.map(x=>x.accepted_native_step)).toEqual([1,1]);
  await page.goto('/?nativeScene=1&nativePerf=1');
  const cdp=await page.context().newCDPSession(page);
  await cdp.send('Performance.enable');
  const memoryBefore=await browserMetricSnapshot(cdp);
  const start=await now(page);
  await page.getByTestId('r2720-import').setInputFiles({
    name:'ORIGINAL_ACCEPTED_NATIVE_TRI_from_same_run.json',
    mimeType:'application/json',buffer:original,
  });
  await expect(page.getByTestId('r2720-tri-count')).toHaveText('1168');
  const xyz=page.getByTestId('r2720-viewport-xyz');
  const uv=page.getByTestId('r2720-viewport-uv');
  await expect(xyz).toHaveAttribute('data-native-accepted-faces','1168');
  await expect(uv).toHaveAttribute('data-native-displayed-patch-slot','0');
  await paintAfterDOM(page);
  const importReadyMs=(await now(page))-start;
  const originalImportMeasurements=await page.getByTestId('r2720-panel')
    .evaluate(node => {
      const el=node as HTMLElement;
      return {
        file_read_ms:Number(el.dataset.nativePerfFileReadMs),
        contract_ms:Number(el.dataset.nativePerfContractMs),
        verified_real_seam_edges_ms:Number(el.dataset.nativePerfActualSeamCheckMs),
        pre_react_ms:Number(el.dataset.nativePerfPreReactMs),
        json_bytes:Number(el.dataset.nativePerfJsonBytes),
      };
    });
  expect(originalImportMeasurements.json_bytes).toBe(original.length);
  expect(originalImportMeasurements.contract_ms).toBeGreaterThanOrEqual(0);
  expect(originalImportMeasurements.verified_real_seam_edges_ms).toBeGreaterThanOrEqual(0);
  const memoryAfterImport=await browserMetricSnapshot(cdp);
  const report:{
    schema:string; source_kind:string; workflow_sha:string|null;
    hosted_runner_scope:string; original_scene_json_bytes:number;
    original_scene_json_sha256:string;
    source_browser_user_agent:string; measurement_method:string;
    real_original_sources:Record<string,unknown>;
    imported_original_cpu:typeof originalImportMeasurements;
    original_import_to_two_raf_ready_ms:number;
    memory_before_original_import:typeof memoryBefore;
    memory_after_original_import:typeof memoryBefore;
    memory_after_interactions:typeof memoryBefore|null;
    physical_windows_gpu_present_rss_vram_qualified:false;
    scientific_lod_qualified:false;
  }={
    schema:'apmesh.meshstudio.r2722.real_original_native_chromium_interactions.v1',
    source_kind:'SAME_RUN_COMPILED_ORIGINAL_ACCEPTED_NATIVE_TRI_SCENE',
    workflow_sha:process.env.GITHUB_SHA ?? null,
    hosted_runner_scope:'ubuntu-24.04 GitHub-hosted Chromium; hardware not qualified',
    original_scene_json_bytes:original.length,
    original_scene_json_sha256:createHash('sha256').update(original).digest('hex'),
    source_browser_user_agent:await page.evaluate(()=>navigator.userAgent),
    measurement_method:'Playwright input to 2 RAF readiness includes controller round trips; CDP JS heap is browser estimate, not RSS or VRAM; VTK synchronous render-call time is not GPU present.',
    real_original_sources:{},
    imported_original_cpu:originalImportMeasurements,
    original_import_to_two_raf_ready_ms:importReadyMs,
    memory_before_original_import:memoryBefore,
    memory_after_original_import:memoryAfterImport,
    memory_after_interactions:null,
    physical_windows_gpu_present_rss_vram_qualified:false,
    scientific_lod_qualified:false,
  };
  // An original model change is allowed to create a new VTK context;
  // changing patches WITHIN the same model must retain its exact canvas.
  for(const [index,scene] of candidates.entries()) {
    const modelStart=await now(page);
    await page.getByTestId('r2720-model').selectOption(String(index));
    await expect(page.getByTestId('r2720-tri-count')).toHaveText(
      String(scene.native_tri_faces));
    await expect(xyz).toHaveAttribute('data-original-source-model',scene.model);
    await expect(xyz).toHaveAttribute(
      'data-native-accepted-faces',String(scene.native_tri_faces));
    await paintAfterDOM(page);
    const initialRenderMs=(await now(page))-modelStart;
    await xyz.locator('canvas').first().evaluate(node=>
      node.setAttribute('data-r2722-preserved-canvas','real-original'));
    const patchCount=scene.native_source_patches;
    const patchSlots=[0,patchCount-1,Math.floor(patchCount/2),1,
      patchCount-1,0,Math.floor(patchCount/3),patchCount-1,0,1];
    const patchDurations:number[]=[];
    for(const patch of patchSlots) {
      const before=await now(page);
      await page.getByTestId('r2720-patch').selectOption(String(patch));
      await expect(uv).toHaveAttribute(
        'data-native-displayed-patch-slot',String(patch));
      await expect(xyz).toHaveAttribute(
        'data-native-accepted-faces',String(scene.native_tri_faces));
      await paintAfterDOM(page);
      patchDurations.push((await now(page))-before);
    }
    const expectedSeams=scene.model==='book'?336:40;
    await expect(xyz).toHaveAttribute(
      'data-native-seam-segments',String(expectedSeams));
    await expect(xyz.locator('canvas').first()).toHaveAttribute(
      'data-r2722-preserved-canvas','real-original');
    const sampleKeys=['End','Home','ArrowRight','End','Home','ArrowRight'];
    const maxSample=scene.model==='book'?12:10;
    const sampleIndices=[maxSample,0,1,maxSample,0,1];
    const sampleDurations:number[]=[];
    for(let i=0;i<sampleKeys.length;i++) {
      const before=await now(page);
      await page.getByTestId('r2720-sample').focus();
      await page.keyboard.press(sampleKeys[i]);
      await expect(xyz).toHaveAttribute(
        'data-native-selected-sample',String(sampleIndices[i]));
      await expect(uv).toHaveAttribute(
        'data-native-selected-sample',String(sampleIndices[i]));
      await paintAfterDOM(page);
      sampleDurations.push((await now(page))-before);
    }
    const timing=await Promise.all([xyz.evaluate(node=>{
      const el=node as HTMLElement;
      return {
        vtk_setup_cpu_ms:Number(el.dataset.nativePerfVtkSetupCpuMs),
        vtk_render_call_cpu_ms:Number(el.dataset.nativePerfVtkRenderCallCpuMs),
        vtk_seam_overlay_cpu_ms:Number(el.dataset.nativePerfSeamOverlayCpuMs),
        typed_cpu_buffer_bytes:Number(el.dataset.nativePerfVtkExplicitCpuTypedBytes),
      };
    }),uv.evaluate(node=>{
      const el=node as HTMLElement;
      return {
        vtk_setup_cpu_ms:Number(el.dataset.nativePerfVtkSetupCpuMs),
        vtk_render_call_cpu_ms:Number(el.dataset.nativePerfVtkRenderCallCpuMs),
        vtk_seam_overlay_cpu_ms:Number(el.dataset.nativePerfSeamOverlayCpuMs),
        typed_cpu_buffer_bytes:Number(el.dataset.nativePerfVtkExplicitCpuTypedBytes),
      };
    })]);
    expect(timing[0].typed_cpu_buffer_bytes).toBe(
      scene.native_tri_faces*56);
    expect(timing[1].typed_cpu_buffer_bytes).toBe(
      scene.source_patch_face_counts[1]*56);
    expect(timing[0].vtk_setup_cpu_ms).toBeGreaterThan(0);
    report.real_original_sources[scene.model]={
      original_native_accepted_step:scene.accepted_native_step,
      original_native_source_sha256:scene.source_ndjson_sha256,
      real_original_accepted_faces:scene.native_tri_faces,
      original_source_patches:patchCount,
      original_accepted_seam_edges:expectedSeams,
      model_select_to_two_raf_ready_ms:initialRenderMs,
      patches:stats(patchDurations),
      source_samples:stats(sampleDurations),
      final_xyz_vtk_cpu_calls:timing[0],
      final_local_uv_vtk_cpu_calls:timing[1],
      physical_gpu_present_time_measured:false,
    };
  }
  report.memory_after_interactions=await browserMetricSnapshot(cdp);
  mkdirSync(dirname(output),{recursive:true});
  writeFileSync(output,JSON.stringify(report,null,2)+'\n',{flag:'w'});
  console.log('R2722_REAL_ORIGINAL_CHROMIUM_PERFORMANCE='+JSON.stringify({
    sources:Object.fromEntries(Object.entries(report.real_original_sources)
      .map(([model,row])=>[model,{
        faces:(row as {real_original_accepted_faces:number}).real_original_accepted_faces,
        patches:(row as {patches:{median_ms:number,p95_ms:number}}).patches,
        source_samples:(row as {source_samples:{median_ms:number,p95_ms:number}}).source_samples,
      }])),
    js_heap_used_after:report.memory_after_interactions?.js_heap_used_bytes,
    physical_gpu_present_qualified:false,
  }));
});
