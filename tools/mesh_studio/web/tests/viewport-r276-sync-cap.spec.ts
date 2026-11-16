import { expect, test } from '@playwright/test';
import { mkdir, writeFile } from 'node:fs/promises';

/**
 * This synthetic stress case checks the explicit synchronous build cap.
 * It is not real generator data, scientific LOD, or proof of GPU performance.
 */
test('R2.7.6 bounded 2048-face synthetic cap profiles synchronous build and UI thread occupancy',
  async ({page},info)=>{
    test.setTimeout(100_000);
    await page.goto('/bench.html');
    const result=await page.evaluate(async ()=>{
      const {createBoundedXyzBvhMain,MAIN_BVH_MAX_FACES,MAIN_BVH_MAX_VERTICES,
        MAIN_BVH_MAX_INPUT_BYTES}=await import('/src/xyzBvhMain.ts');
      const {chromiumHeapEstimate}=await import('/src/performanceProbe.ts');
      const side=32, vertices=new Float32Array((side+1)*(side+1)*3);
      for(let row=0;row<=side;row++)for(let col=0;col<=side;col++){
        const k=(row*(side+1)+col)*3;
        vertices[k]=col/side;vertices[k+1]=row/side;vertices[k+2]=0;
      }
      const faces=side*side*2,polys=new Uint32Array(faces*4),
        offsets=new Uint32Array(faces+1),
        arities=new Uint8Array(faces),faceIds=new Uint32Array(faces);
      let face=0;
      for(let y=0;y<side;y++)for(let x=0;x<side;x++){
        const v=y*(side+1)+x;
        for(const tri of [[v,v+1,v+side+2],[v,v+side+2,v+side+1]]){
          const offset=face*4;
          polys.set([3,...tri],offset);offsets[face]=offset;
          arities[face]=3;faceIds[face]=face;face++;
        }
      }
      offsets[faces]=faces*4;
      const typedBytes=vertices.byteLength+polys.byteLength+offsets.byteLength+
        arities.byteLength+faceIds.byteLength;
      const mesh={
        schema:'apmesh.meshstudio.synthetic_build_cap.v1',
        source_sha256:'0'.repeat(64),
        source_patch_ownership:'NOT_APMESH_SOURCE',
        coordinate_space:'xyz' as const,
        points:[],cells:[],source_face_ids:[],cell_types:[],
        triangles:faces,quads:0,warning:'SYNTHETIC_STRESS_ONLY',
        packed:{vertices,polys,offsets,arities,faceIds},
      };
      const before=chromiumHeapEstimate();
      const observerSupported=typeof PerformanceObserver!=='undefined' &&
        (PerformanceObserver.supportedEntryTypes||[]).includes('longtask');
      const longTasks:number[]=[];
      let observer:PerformanceObserver|null=null;
      if(observerSupported){
        observer=new PerformanceObserver(list=>{
          for(const entry of list.getEntries())longTasks.push(entry.duration);
        });
        observer.observe({entryTypes:['longtask']});
      }
      const builds=[];
      try{
        for(let run=0;run<4;run++){
          await new Promise<void>(resolve=>requestAnimationFrame(()=>resolve()));
          const started=performance.now();
          const index=createBoundedXyzBvhMain(mesh);
          const measured=performance.now()-started;
          if(!index)throw new Error('R276_synthetic_within_cap_rejected');
          const near:[number,number,number]=[.305,.405,1];
          const far:[number,number,number]=[.305,.405,-1];
          const outcome=index.pick(near,far,true,false);
          if(outcome.kind!=='hit'&&outcome.kind!=='ambiguous')
            throw new Error('R276_synthetic_query_unexpected_miss');
          builds.push({wallMs:measured,profile:index.profile,
            indexQuery:outcome.kind,sourceFaceOrdinal:outcome.kind==='hit'?outcome.sourceFaceId:null});
        }
        await new Promise<void>(resolve=>requestAnimationFrame(()=>resolve()));
      }finally{observer?.disconnect();}
      const after=chromiumHeapEstimate();
      const originalBufferStillAttached=vertices.byteLength===(side+1)*(side+1)*12 &&
        faceIds.length===faces && polys.length===faces*4;
      return {faces,vertices:vertices.length/3,typedBytes,
        caps:{faces:MAIN_BVH_MAX_FACES,vertices:MAIN_BVH_MAX_VERTICES,bytes:MAIN_BVH_MAX_INPUT_BYTES},
        runs:builds,originalBufferStillAttached,
        browserJSHeapEstimateBefore:before,browserJSHeapEstimateAfter:after,
        longTaskSupport:observerSupported,longTasks,
      };
    });
    expect(result.faces).toBe(2048);
    expect(result.vertices).toBe(1089);
    expect(result.caps).toEqual({faces:2048,vertices:8192,bytes:1048576});
    expect(result.typedBytes).toBeGreaterThan(60_000);
    expect(result.originalBufferStillAttached).toBe(true);
    expect(result.runs).toHaveLength(4);
    for(const run of result.runs){
      expect(Number.isFinite(run.wallMs)&&run.wallMs>=0).toBe(true);
      expect(run.profile).toMatchObject({
        sourceFaces:2048,indexedFaces:2048,excludedQuads:0,
        scope:'MAIN_THREAD_PREPARE_AND_BUILD_NOT_GPU_RSS_OR_SCIENTIFIC_GEOMETRY',
      });
      expect(run.profile.copiedInputBytes).toBe(result.typedBytes);
    }
    const receipt={
      schema:'apmesh.meshstudio.r276.synthetic_cap_build_blocking_preflight.v1',
      classification:'DETERMINISTIC_SYNTHETIC_2048_TRI_BOUND_NOT_A_REAL_GENERATOR_STUDY',
      results:result,
      caveats:[
        'main_thread_synchronous_build_may_delay_user_input_beyond_raw_wall_time',
        'one_CI_browser_no_physical_GPU_or_repeated_multi_host_distribution',
        'longtask_observer_threshold_is_50ms_and_misses_shorter_blockages',
        'chromiumJSHeapEstimate_is_optional_not_worker_RSS_total_native_RAM_or_GPU_VRAM',
        'synthetic_flat_grid_cannot_qualify_real_nonmanifold_Bezier_patch_ownership',
        'do_not_increase_caps_based_on_this_synthetic_stress_case',
      ],
    };
    await mkdir('test-results',{recursive:true});
    const json=JSON.stringify(receipt,null,2)+'\n';
    await writeFile('test-results/r276-synthetic-2048-cap-build.json',json,'utf8');
    await info.attach('r276-synthetic-2048-cap-build.json',{
      body:Buffer.from(json),contentType:'application/json',
    });
    console.log('R276_SYNTHETIC_CAP_BUILD='+JSON.stringify({
      faces:result.faces,typedBytes:result.typedBytes,
      buildWallMs:result.runs.map(r=>r.wallMs),
      longTaskSupport:result.longTaskSupport,longTaskCount:result.longTasks.length,
      chromiumHeapBefore:result.browserJSHeapEstimateBefore,
      chromiumHeapAfter:result.browserJSHeapEstimateAfter,
      classification:'SYNTHETIC_CAP_ONLY_NOT_APMESH_REAL',
    }));
  });
