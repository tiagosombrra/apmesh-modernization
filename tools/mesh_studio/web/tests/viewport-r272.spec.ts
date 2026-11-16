import { expect, test } from '@playwright/test';
import { mkdir, writeFile } from 'node:fs/promises';

// Real source candidates provide geometry-picking fixtures, not independent accepted experiments.
test('R2.7.2 five real-source BVH worker profiles retain provenance and bounded telemetry', async ({ page }, info) => {
  test.setTimeout(120_000);
  await page.goto('/');
  const samples = await page.evaluate(async () => {
    const { studyApi } = await import('/src/api.ts');
    const { createXyzBvhWorker } = await import('/src/xyzBvhClient.ts');
    const catalog = await studyApi.catalog();
    const expectedIds = ['p1','band','west','north','both'];
    const getHeap = () => {
      const api = performance as Performance & { memory?: { usedJSHeapSize?: number } };
      const bytes = api.memory?.usedJSHeapSize;
      return typeof bytes === 'number' && Number.isFinite(bytes) ? bytes : null;
    };
    const rows = [];
    for (const modelId of expectedIds) {
      const original = catalog.models.find(m=>m.id === modelId);
      if (!original) throw new Error('missing_source_catalog_model:'+modelId);
      const source = await studyApi.geometry(modelId,'xyz');
      const mesh = source.packed!;
      const heapBefore = getHeap();
      const client = createXyzBvhWorker(source);
      if (!client) throw new Error('missing_bvh_for_real_source:'+modelId);
      try {
        if (!await client.ready) throw new Error('bvh_rejected_real_source:'+modelId);
        const profile = client.buildMeasurement();
        const coverage = client.coverage();
        const tests = [];
        const count = Math.min(12, source.triangles);
        const triangles = Array.from(mesh.arities, (arity,i)=>arity===3?i:-1).filter(i=>i>=0);
        for (let sample=0;sample<count;sample++) {
          const face = triangles[Math.floor(sample*triangles.length/count)];
          const at = mesh.offsets[face];
          const xyz = (k:number):[number,number,number] => {
            const id = mesh.polys[at+1+k]*3;
            return [mesh.vertices[id],mesh.vertices[id+1],mesh.vertices[id+2]];
          };
          const [a,b,c] = [xyz(0),xyz(1),xyz(2)];
          const center = a.map((v,i)=>(v+b[i]+c[i])/3);
          const e = b.map((v,i)=>v-a[i]), f = c.map((v,i)=>v-a[i]);
          const normal = [e[1]*f[2]-e[2]*f[1],e[2]*f[0]-e[0]*f[2],
            e[0]*f[1]-e[1]*f[0]];
          const norm = Math.hypot(...normal);
          if (!(norm>1e-12)) throw new Error('invalid_source_triangle:'+modelId);
          const near = center.map((v,i)=>v+normal[i]/norm*.001) as [number,number,number];
          const far = center.map((v,i)=>v-normal[i]/norm*.001) as [number,number,number];
          const measured = await client.pickWithMeasurement(near,far,true,false);
          const withQuads = await client.pickWithMeasurement(near,far,true,true);
          tests.push({
            expectedSourceFaceId:mesh.faceIds[face],
            selectedSourceFaceId:measured.outcome.kind==='hit' ? measured.outcome.sourceFaceId:null,
            outcome:measured.outcome.kind,
            testedFaces:measured.outcome.testedFaces,
            workerQueryWallMs:measured.workerQueryWallMs,
            roundTripWallMs:measured.roundTripWallMs,
            status:measured.status,
            quadVisibleOutcome:withQuads.outcome.kind,
          });
        }
        const after = getHeap();
        rows.push({
          modelId, sourceStatus:original.source_status,
          originalSha:source.source_sha256, expectedSha:original.sha256,
          originalTri:source.triangles, originalQuad:source.quads,
          coverage,build:profile,heapBeforeEstimate:heapBefore,heapAfterEstimate:after,
          heapScope:'CHROMIUM_PERFORMANCE_MEMORY_ESTIMATE_NOT_TOTAL_RAM_VRAM_OR_WORKER_RSS',
          tests,sourceBuffersAttached:mesh.vertices.byteLength>0,
        });
      } finally { client.dispose(); }
    }
    return rows;
  });
  expect(samples).toHaveLength(5);
  let evaluated = 0, correct = 0, invalid = 0;
  for (const row of samples) {
    expect(row.originalSha).toBe(row.expectedSha);
    expect(row.sourceStatus).toBe(row.modelId==='p1'
      ? 'CONTROLLED_PHYSICAL_GENERATION' : 'STAGED_UNACCEPTED');
    expect(row.coverage).toEqual({
      sourceFaces:row.originalTri+row.originalQuad,
      indexedFaces:row.originalTri,
      excludedQuadFaces:row.originalQuad,
    });
    expect(row.build).toMatchObject({
      scope:'COPIED_TYPED_INPUT_AND_WORKER_CPU_NOT_HEAP_RSS_VRAM',
    });
    for(const metric of [row.build!.preparationWallMs, row.build!.readyRoundTripMs,
      row.build!.workerBuildWallMs, row.build!.copiedInputBytes,row.build!.nodeCount]) {
      expect(Number.isFinite(metric) && metric>=0).toBe(true);
    }
    expect(row.sourceBuffersAttached).toBe(true);
    for(const pick of row.tests) {
      evaluated += 1;
      if(pick.status!=='completed'||pick.workerQueryWallMs===null||
        !Number.isFinite(pick.roundTripWallMs) ||
        pick.quadVisibleOutcome!=='ambiguous') invalid += 1;
      if (pick.expectedSourceFaceId===pick.selectedSourceFaceId) correct += 1;
    }
  }
  expect(invalid).toBe(0);
  expect(correct).toBe(evaluated);
  expect(evaluated).toBe(60);
  const receipt={
    schema:'apmesh.meshstudio.r272.real_source_worker_profiles.v1',
    classification:'FIVE_SOURCE_FILES_ONE_CONTROLLED_P1_FOUR_STAGED_UNACCEPTED_NOT_INDEPENDENT_EXPERIMENTS',
    exactSourceGeometry:true, samplesByModel:12, count:evaluated, correct,
    profileScope:'WORKER_CPU_BUILD_QUERY_AND_MESSAGE_ONLY_NOT_UI_PAINT',
    memoryScope:'COPIED_TYPED_INPUT_AND_JS_HEAP_ESTIMATE_NO_NATIVE_RSS_OR_VRAM',
    rows:samples,
    caveats:[
      'no_cross_model_scientific_quality_comparison',
      'no_gpu_time_or_browser_click_to_paint_measurement',
      'near_centroid_source_rays_not_full_viewport_pixel_A_B',
      'warped_quad_picking_always_falls_back_when_visible',
    ],
  };
  const json=JSON.stringify(receipt,null,2)+'\n';
  await mkdir('test-results',{recursive:true});
  await writeFile('test-results/r272-real-source-worker-profiles.json',json,'utf8');
  await info.attach('r272-real-source-worker-profiles.json',{
    body:Buffer.from(json),contentType:'application/json',
  });
  console.log('R272_REAL_SOURCE_PROFILES='+JSON.stringify({
    models:samples.map(r=>({id:r.modelId,tri:r.originalTri,quads:r.originalQuad,
      buildMs:r.build?.workerBuildWallMs,readyMs:r.build?.readyRoundTripMs,
      bytes:r.build?.copiedInputBytes,matched:r.tests.filter(t=>t.selectedSourceFaceId===t.expectedSourceFaceId).length})),
    correct,evaluated,
  }));
});
