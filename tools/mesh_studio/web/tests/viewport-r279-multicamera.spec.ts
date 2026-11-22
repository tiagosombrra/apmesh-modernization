import { expect, test } from '@playwright/test';
import { mkdir, writeFile } from 'node:fs/promises';
import type { Page, Locator } from '@playwright/test';
import { MODELS, METHODS, GRID, measuredClick, camera } from './support/r277Protocol';
import type { Pixel } from './support/r277Protocol';

type Pose = {
  position:[number,number,number];focal_point:[number,number,number];
  view_up:[number,number,number];parallel_scale:number;parallel:boolean;
};

/** Rotate the existing source-locked camera about world Z without changing the mesh. */
function rotatePose(pose:Pose,angleDegrees:number):Pose {
  const a=angleDegrees*Math.PI/180,c=Math.cos(a),s=Math.sin(a);
  const d=pose.position.map((x,i)=>x-pose.focal_point[i]);
  return {...pose,position:[
    pose.focal_point[0]+c*d[0]-s*d[1],
    pose.focal_point[1]+s*d[0]+c*d[1],
    pose.focal_point[2]+d[2],
  ] as [number,number,number]};
}

async function installAndRestore(page:Page,sha:string,pose:Pose){
  await page.evaluate(({sha,pose})=>{
    const key='apmesh.meshstudio.camera.v1.'+sha;
    const current=localStorage.getItem(key);
    if(!current)throw new Error('R279_missing_source_camera_recipe');
    const recipe=JSON.parse(current) as {
      schema:string;source_sha256:string;camera_uv:unknown;camera_xyz:unknown;
    };
    if(recipe.schema!=='apmesh.meshstudio.web_camera.v1'||recipe.source_sha256!==sha)
      throw new Error('R279_camera_source_identity_mismatch');
    recipe.camera_xyz=pose;
    localStorage.setItem(key,JSON.stringify(recipe));
  },{sha,pose});
  await page.getByTestId('restore-cameras').click();
  await expect(page.getByTestId('camera-status')).toHaveText(
    'Enquadramentos restaurados com a origem verificada.');
}

async function methodAt(host:Locator,pixel:{x:number;y:number}){
  await host.evaluate(element=>{
    delete (element as HTMLElement).dataset.lastPickerMethod;
    delete (element as HTMLElement).dataset.lastPickerSourceId;
  });
  await host.click({position:pixel});
  await expect.poll(()=>host.getAttribute('data-last-picker-method'),{timeout:12000})
    .toMatch(/^(EXPERIMENTAL_XYZ_BVH_MAIN|VTK_CELL_PICKER)$/);
  return {
    method:await host.getAttribute('data-last-picker-method'),
    id:await host.getAttribute('data-last-picker-source-id'),
  };
}

for(const model of MODELS){
  test('R2.7.9 source-locked three-camera TRI picking and warped QUAD fallback '+model.id,
    async({page,context},info)=>{
      test.setTimeout(210_000);
      const worker=await context.newPage(),native=await context.newPage();
      const pages=[page,worker,native];
      const hosts=pages.map(p=>p.getByTestId('viewport-xyz'));
      const readings=[];
      try{
        await Promise.all([
          page.goto('/?xyzPicker=sync'),worker.goto('/?xyzPicker=bvh'),native.goto('/'),
        ]);
        if(model.id!=='p1')
          await Promise.all(pages.map(p=>p.getByTestId('model-select').selectOption(model.id)));
        for(let i=0;i<3;i++){
          await expect(hosts[i].locator('canvas').first()).toBeVisible();
          await expect(pages[i].locator('.model-foot code')).toHaveAttribute('title',model.sha);
        }
        await expect.poll(()=>hosts[0].getAttribute('data-main-bvh-ready'),{timeout:25000}).toBe('true');
        await expect.poll(()=>hosts[1].getAttribute('data-bvh-ready'),{timeout:25000}).toBe('true');
        for(const p of pages)await p.getByTestId('toggle-quad').uncheck();
        const boxes=await Promise.all(hosts.map(h=>h.boundingBox()));
        if(boxes.some(b=>!b))throw new Error('R279_missing_real_mesh_viewport');
        for(let i=1;i<3;i++){
          expect(Math.abs(boxes[i]!.width-boxes[0]!.width)).toBeLessThan(.1);
          expect(Math.abs(boxes[i]!.height-boxes[0]!.height)).toBeLessThan(.1);
        }
        const original=await Promise.all(pages.map(p=>camera(p,model.sha))) as Pose[];
        expect(original[1]).toEqual(original[0]);
        expect(original[2]).toEqual(original[0]);
        const rotations=[{label:'original',degrees:0},
          {label:'left_18_degrees',degrees:18},
          {label:'right_18_degrees',degrees:-18}];
        for(const rotation of rotations){
          const desired=rotatePose(original[0],rotation.degrees);
          // All pages intentionally share origin storage; update before each restore.
          for(const p of pages)await installAndRestore(p,model.sha,desired);
          const poses=await Promise.all(pages.map(p=>camera(p,model.sha))) as Pose[];
          expect(poses[0]).toEqual(desired);
          expect(poses[1]).toEqual(desired);
          expect(poses[2]).toEqual(desired);
          const pixels:Pixel[]=[];
          let attempted=0;
          for(const fy of GRID){
            for(const fx of GRID){
              const pixel={x:boxes[0]!.width*fx,y:boxes[0]!.height*fy};
              const current=await methodAt(hosts[0],pixel);
              attempted+=1;
              if(current.method!=='EXPERIMENTAL_XYZ_BVH_MAIN'||!current.id||
                !/^\d+$/.test(current.id))continue;
              const id=Number(current.id);
              if(!pixels.some(p=>p.id===id))pixels.push({...pixel,id});
              if(pixels.length===2)break;
            }
            if(pixels.length===2)break;
          }
          expect(pixels,'need two distinct real interior native TRI faces for this camera')
            .toHaveLength(2);
          const observations=[];
          for(const pixel of pixels){
            for(let k=0;k<3;k++){
              const sample=await measuredClick(pages[k],hosts[k],pixel,METHODS[k]);
              observations.push({id:pixel.id,method:METHODS[k],
                pixel:{x:pixel.x,y:pixel.y},
                sourceId:sample.sourceId,
                callbackMs:sample.eventToPickerMs,twoRafMs:sample.eventToTwoRafMs});
            }
          }
          expect(observations).toHaveLength(6);
          // QUAD layers contain nonplanar original elements; the bounded BVH
          // never uses a partial index with these potentially occluding faces.
          await page.getByTestId('toggle-quad').check();
          await worker.getByTestId('toggle-quad').check();
          const fallback=[];
          for(let k=0;k<2;k++){
            const x=await methodAt(hosts[k],{x:pixels[0].x,y:pixels[0].y});
            expect(x.method).toBe('VTK_CELL_PICKER');
            fallback.push({variant:METHODS[k],method:x.method,sourceFaceId:x.id});
          }
          await page.getByTestId('toggle-quad').uncheck();
          await worker.getByTestId('toggle-quad').uncheck();
          for(let k=0;k<2;k++)await measuredClick(
            pages[k],hosts[k],pixels[0],METHODS[k]);
          const after=await Promise.all(pages.map(p=>camera(p,model.sha))) as Pose[];
          expect(after).toEqual(poses);
          readings.push({camera:rotation.label,rotationDegrees:rotation.degrees,
            pose:desired,distinctSourceFaceIds:pixels.map(x=>x.id),
            searchedScreenPixels:attempted,exactOriginalIdMatches:observations.length,
            observations,curvedVisibleQuadForcedNative:fallback});
        }
        expect(readings).toHaveLength(3);
        const receipt={
          schema:'apmesh.meshstudio.r279.multicamera_source_ids.v1',
          sourceSha256:model.sha,sourceStatus:model.sourceStatus,
          classification:'HOSTED_CHROMIUM_REAL_SOURCE_TRI_ONLY_MULTICAMERA_NOT_SURFACE_OR_GPU_ORACLE',
          cameraRotationsDegrees:rotations.map(x=>x.degrees),
          distinctOriginalSourceFacesPerCamera:2,
          exactMethodFaceComparisons:readings.reduce((x,r)=>x+r.exactOriginalIdMatches,0),
          allCameraSnapshotsPreserved:true,
          allCurvedQuadFallbacksNative:true,
          observations:readings,
          qualification:{
            sourceFaceIdentityForSelectedPixels:true,
            testedOnlyOriginalAftTriangles:true,
            continuousBezierSurfaceIntersectionsQualified:false,
            acceptedAdaptiveEpochsBeyondP1:false,
            physicalGPUQualified:false,presentedGPUFramesMeasured:false,
            memoryVRAMQualified:false,scientificLODQualified:false,
          },
          limitations:[
            'two_positive_TRI_hits_per_camera_not_exhaustive_hit_or_miss_coverage',
            'VTK_display_polygon_raster_picking_is_a_behavioral_reference_not_Bezier_surface_truth',
            'only_three_related_camera_angles_and_the_same_hosted_Chromium_environment',
            'warped_source_QUAD_visibility_forces_native_fallback_without_picking_quad_by_BVH',
            'BAND_is_staged_unaccepted_and_not_a_second_accepted_adaptive_epoch',
            'two_RAF_callbacks_are_not_GPU_frame_present_timestamps',
          ],
        };
        await mkdir('test-results',{recursive:true});
        const filename='r279-multicamera-'+model.id+'.json',json=JSON.stringify(receipt,null,2)+'\n';
        await writeFile('test-results/'+filename,json,'utf8');
        await info.attach(filename,{body:Buffer.from(json),contentType:'application/json'});
        console.log('R279_MULTICAMERA='+JSON.stringify({
          source:model.id,sha:model.sha,angles:rotations.map(x=>x.degrees),
          faces:readings.map(x=>x.distinctSourceFaceIds),matched:receipt.exactMethodFaceComparisons,
          visibleWarpedQuadNativeFallback:true,physicalGPUQualified:false,
        }));
      }finally{
        await worker.close();
        await native.close();
      }
    });
}
