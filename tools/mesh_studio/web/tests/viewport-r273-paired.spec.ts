import { expect, test } from '@playwright/test';
import { mkdir, writeFile } from 'node:fs/promises';
import type { Page } from '@playwright/test';

type Method = 'EXPERIMENTAL_XYZ_BVH_WORKER' | 'VTK_CELL_PICKER';
type Pixel = { x: number; y: number; faceId: number };
type Observation = {
  sourceFaceId: number;
  x: number;
  y: number;
  round: number;
  firstMethod: Method;
  bvhPickerCallMs: number;
  vtkPickerCallMs: number;
  deltaBvhMinusVtkMs: number;
};

const GRID = [.25, .30, .35, .40, .45, .50, .55, .60, .65, .70, .75];
const ROUNDS = 8;
const PIXELS = 3;
const WARMUP_PER_METHOD = 2;
const BINARY_SCOPE = 'PICKER_CALL_WALL_NOT_CLICK_TO_PAINT_OR_GPU_PRESENTATION';

const models = [
  {id:'p1',sha:'cbf6cd6308ba54544d06c5d562c491eb7d43ddb216365e0e9d188fd3430295e0',
    status:'CONTROLLED_PHYSICAL_GENERATION',tri:36,quad:42},
  {id:'band',sha:'76b0b4defecc5d534815fb9f41e1405653597a4a0bee6cc7b722ec2460d7afd6',
    status:'STAGED_UNACCEPTED',tri:44,quad:62},
] as const;

/** Nearest-rank percentile; retain every raw observation in the attached receipt. */
function percentile(values: number[], fraction: number): number {
  if (!values.length || !values.every(Number.isFinite) || fraction <= 0 || fraction > 1) {
    throw new Error('invalid_repeated_picker_distribution');
  }
  const sorted = [...values].sort((a,b)=>a-b);
  return Math.round(sorted[Math.max(0, Math.ceil(fraction * sorted.length)-1)] * 1000)/1000;
}

function distribution(values: number[]) {
  return {
    n: values.length,
    p50_ms: percentile(values,.5),
    p95_ms: percentile(values,.95),
    min_ms: Math.round(Math.min(...values)*1000)/1000,
    max_ms: Math.round(Math.max(...values)*1000)/1000,
  };
}

/** Read a saved camera independently from each viewport without changing its projection. */
async function cameraSnapshot(page: Page) {
  await page.getByTestId('save-cameras').click();
  return await page.evaluate(() => {
    const key=Object.keys(localStorage).find(k=>k.startsWith('apmesh.meshstudio.camera.v1.'));
    if (!key) throw new Error('camera_snapshot_key_missing');
    const stored=localStorage.getItem(key);
    if(!stored) throw new Error('camera_snapshot_missing');
    const parsed=JSON.parse(stored) as { source_sha256:string; camera_xyz:unknown };
    return {sha:parsed.source_sha256,camera:parsed.camera_xyz};
  });
}

/** Always clear diagnostics first so stale clicks cannot be mistaken for measurements. */
async function samplePick(page: Page, pixel: Pixel, method: Method) {
  const host=page.getByTestId('viewport-xyz');
  await host.evaluate(node => {
    delete (node as HTMLElement).dataset.lastPickerMethod;
    delete (node as HTMLElement).dataset.lastPickerSourceId;
    delete (node as HTMLElement).dataset.lastPickerWallMs;
  });
  await host.click({position:{x:pixel.x,y:pixel.y}});
  await expect.poll(()=>host.getAttribute('data-last-picker-method'),{timeout:10_000}).toBe(method);
  const idText=await host.getAttribute('data-last-picker-source-id');
  const durationText=await host.getAttribute('data-last-picker-wall-ms');
  if (!idText || !/^\d+$/.test(idText) || durationText === null) {
    throw new Error('picker_did_not_report_original_source_face');
  }
  const id=Number(idText),ms=Number(durationText);
  if (id !== pixel.faceId || !Number.isFinite(ms) || ms < 0) {
    throw new Error('picker_original_face_mismatch_or_invalid_time');
  }
  return ms;
}

for (const model of models) {
  test('R2.7.3 paired, warmed BVH/VTK distributions on '+model.id+' real TRI-only viewport', async ({ page, context }, info) => {
    test.setTimeout(210_000);
    // Two identical Chromium viewports preserve independently warmed selector instances.
    const vtkPage=await context.newPage();
    try {
      await page.goto('/?xyzPicker=bvh');
      await vtkPage.goto('/');
      if(model.id!=='p1') {
        await page.getByTestId('model-select').selectOption(model.id);
        await vtkPage.getByTestId('model-select').selectOption(model.id);
      }
      const bvh=page.getByTestId('viewport-xyz');
      const vtk=vtkPage.getByTestId('viewport-xyz');
      await expect(bvh.locator('canvas').first()).toBeVisible();
      await expect(vtk.locator('canvas').first()).toBeVisible();
      await expect(page.locator('.model-foot code')).toHaveAttribute('title',model.sha);
      await expect(vtkPage.locator('.model-foot code')).toHaveAttribute('title',model.sha);
      await expect.poll(()=>bvh.getAttribute('data-bvh-ready'),{timeout:25_000}).toBe('true');
      expect(await bvh.getAttribute('data-bvh-indexed-faces')).toBe(String(model.tri));
      expect(await bvh.getAttribute('data-bvh-excluded-quads')).toBe(String(model.quad));

      await page.getByTestId('toggle-quad').uncheck();
      await vtkPage.getByTestId('toggle-quad').uncheck();
      const bvhBounds=await bvh.boundingBox(),vtkBounds=await vtk.boundingBox();
      if(!bvhBounds||!vtkBounds)throw new Error('missing_real_viewport_bounds');
      expect(Math.abs(bvhBounds.width-vtkBounds.width)).toBeLessThan(.1);
      expect(Math.abs(bvhBounds.height-vtkBounds.height)).toBeLessThan(.1);

      const camerasBefore=[await cameraSnapshot(page),await cameraSnapshot(vtkPage)];
      expect(camerasBefore[0].sha).toBe(model.sha);
      expect(camerasBefore[1]).toEqual(camerasBefore[0]);

      // Use a fixed candidate grid and retain only distinct, interior TRI BVH hits.
      const candidates:Pixel[]=[];
      let candidateCount=0;
      for(const fy of GRID) {
        for(const fx of GRID) {
          const point={x:bvhBounds.width*fx,y:bvhBounds.height*fy};
          await bvh.evaluate(node => {
            delete (node as HTMLElement).dataset.lastPickerMethod;
            delete (node as HTMLElement).dataset.lastPickerSourceId;
          });
          await bvh.click({position:point});
          candidateCount++;
          await expect.poll(()=>bvh.getAttribute('data-last-picker-method'),{timeout:10_000})
            .toMatch(/^(EXPERIMENTAL_XYZ_BVH_WORKER|VTK_CELL_PICKER)$/);
          if(await bvh.getAttribute('data-last-picker-method')!=='EXPERIMENTAL_XYZ_BVH_WORKER')continue;
          const source=await bvh.getAttribute('data-last-picker-source-id');
          if(!source||!/^\d+$/.test(source))throw new Error('missing_BVH_source_id');
          const faceId=Number(source);
          if(candidates.some(p=>p.faceId===faceId))continue;
          candidates.push({...point,faceId});
          if(candidates.length===PIXELS)break;
        }
        if(candidates.length===PIXELS)break;
      }
      expect(candidates, 'Require three distinct real source TRI faces').toHaveLength(PIXELS);

      // Validate each selected original ID with the native VTK picker before warmup.
      for(const candidate of candidates) {
        await samplePick(vtkPage,candidate,'VTK_CELL_PICKER');
      }

      // Warm both implementations without counting startup, page navigation or discovery.
      for(const candidate of candidates) {
        for(let i=0;i<WARMUP_PER_METHOD;i++){
          await samplePick(page,candidate,'EXPERIMENTAL_XYZ_BVH_WORKER');
          await samplePick(vtkPage,candidate,'VTK_CELL_PICKER');
        }
      }

      const pairs:Observation[]=[];
      for(let round=0;round<ROUNDS;round++){
        // AB/BA alternating order reduces bias from monotonic host warmup.
        const workerFirst=round%2===0;
        // A deterministic reversal also changes the pixel order without changing geometry.
        const ordered=round%2===0 ? [...candidates] : [...candidates].reverse();
        for(const candidate of ordered) {
          let bvhMs:number, vtkMs:number;
          if(workerFirst) {
            bvhMs=await samplePick(page,candidate,'EXPERIMENTAL_XYZ_BVH_WORKER');
            vtkMs=await samplePick(vtkPage,candidate,'VTK_CELL_PICKER');
          } else {
            vtkMs=await samplePick(vtkPage,candidate,'VTK_CELL_PICKER');
            bvhMs=await samplePick(page,candidate,'EXPERIMENTAL_XYZ_BVH_WORKER');
          }
          pairs.push({
            sourceFaceId:candidate.faceId,x:candidate.x,y:candidate.y,
            round,firstMethod:workerFirst?'EXPERIMENTAL_XYZ_BVH_WORKER':'VTK_CELL_PICKER',
            bvhPickerCallMs:bvhMs,vtkPickerCallMs:vtkMs,
            deltaBvhMinusVtkMs:bvhMs-vtkMs,
          });
        }
      }

      expect(pairs).toHaveLength(ROUNDS*PIXELS);
      const camerasAfter=[await cameraSnapshot(page),await cameraSnapshot(vtkPage)];
      expect(camerasAfter).toEqual(camerasBefore);
      const workerMs=pairs.map(p=>p.bvhPickerCallMs), nativeMs=pairs.map(p=>p.vtkPickerCallMs);
      const deltaMs=pairs.map(p=>p.deltaBvhMinusVtkMs);
      const receipt={
        schema:'apmesh.meshstudio.r273.paired_real_viewport_picking.v1',
        classification:'CONTROLLED_REAL_SOURCE_TRI_ONLY_VIEWER_DIAGNOSTIC_NOT_SCIENTIFIC_OR_GPU_BENCHMARK',
        model:model.id,source_sha256:model.sha,source_status:model.status,
        sampled_original_face_ids:candidates.map(c=>c.faceId),
        source_tri:model.tri,excluded_warped_quads:model.quad,quad_visible:false,
        candidate_pixels_scanned:candidateCount, warmup_calls_per_method:PIXELS*WARMUP_PER_METHOD,
        rounds:ROUNDS,pairs:pairs.length,paired_order:'AB_BA_ALTERNATING_WITH_PIXEL_REVERSAL',
        measurement_scope:BINARY_SCOPE,
        bvh_picker_call:distribution(workerMs),
        native_vtk_picker_call:distribution(nativeMs),
        paired_bvh_minus_vtk_call:distribution(deltaMs),
        observed_p50_bvh_faster:percentile(deltaMs,.5)<0,
        identical_cameras_before_after:true,
        exact_source_face_ids_matched:pairs.length,
        samples:pairs,
        memory:'NOT_MEASURED_TOTAL_RSS_WORKER_RSS_OR_VRAM',
        gpu:'NOT_MEASURED_PRESENTATION_FPS',
        caveats:[
          'two_headless_browser_pages_with_separate_renderer_and_worker_instances',
          'fixed_nonboundary_pixels_selected_by_successful_worker_hit',
          'not_blinded_random_sample_and_not_multihost_confidence_intervals',
          'picker_call_wall_time_not_end_to_end_pointer_to_visible_paint',
          'no_index_build_cost_inside_warmed_pick_distributions',
          'warped_quads_excluded_and_native_selector_required_when_visible',
          'one_controlled_P1_or_one_staged_unaccepted_candidate_only',
        ],
      };
      await mkdir('test-results',{recursive:true});
      const json=JSON.stringify(receipt,null,2)+'\n';
      const filename='r273-paired-'+model.id+'-real-tri-only.json';
      await writeFile('test-results/'+filename,json,'utf8');
      await info.attach(filename,{body:Buffer.from(json),contentType:'application/json'});
      console.log('R273_PAIRED_REAL='+JSON.stringify({
        model:model.id,pairs:pairs.length,
        bvh:receipt.bvh_picker_call,native:receipt.native_vtk_picker_call,
        paired_delta:receipt.paired_bvh_minus_vtk_call,
        original_face_ids:receipt.sampled_original_face_ids,
        observed_p50_bvh_faster:receipt.observed_p50_bvh_faster,
      }));
    } finally {
      await vtkPage.close();
    }
  });
}
