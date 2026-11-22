import { expect, test } from '@playwright/test';
import { mkdir, writeFile } from 'node:fs/promises';
import { MODELS, METHODS, GRID, measuredClick, camera, distribution } from './support/r277Protocol';
import type { Pixel } from './support/r277Protocol';

/**
 * CI exercises the same source-locked click helper used by physical desktop.
 * This headless/software-renderer preflight NEVER qualifies a physical GPU.
 */
for (const model of MODELS) {
  test('R2.7.8 shared headed-desktop protocol preflight on hosted Chromium '+model.id,
    async ({page,context},info)=>{
      test.setTimeout(130_000);
      const worker=await context.newPage(),native=await context.newPage();
      const pages=[page,worker,native];
      const hosts=pages.map(p=>p.getByTestId('viewport-xyz'));
      try {
        await Promise.all([
          page.goto('/?xyzPicker=sync'),
          worker.goto('/?xyzPicker=bvh'),
          native.goto('/'),
        ]);
        if(model.id!=='p1') {
          await Promise.all(pages.map(p=>
            p.getByTestId('model-select').selectOption(model.id)));
        }
        for(let i=0;i<pages.length;i++){
          await expect(hosts[i].locator('canvas').first()).toBeVisible();
          await expect(pages[i].locator('.model-foot code')).toHaveAttribute('title',model.sha);
        }
        await expect.poll(()=>hosts[0].getAttribute('data-main-bvh-ready'),{timeout:25000}).toBe('true');
        await expect.poll(()=>hosts[1].getAttribute('data-bvh-ready'),{timeout:25000}).toBe('true');
        for(const p of pages)await p.getByTestId('toggle-quad').uncheck();
        const boxes=await Promise.all(hosts.map(h=>h.boundingBox()));
        if(boxes.some(b=>!b))throw new Error('R278_missing_qualified_viewport');
        for(let i=1;i<boxes.length;i++) {
          expect(Math.abs(boxes[i]!.width-boxes[0]!.width)).toBeLessThan(.1);
          expect(Math.abs(boxes[i]!.height-boxes[0]!.height)).toBeLessThan(.1);
        }
        const before=await Promise.all(pages.map(p=>camera(p,model.sha)));
        expect(before[1]).toEqual(before[0]);
        expect(before[2]).toEqual(before[0]);

        const positions:Pixel[]=[];
        for(const fy of GRID) {
          for(const fx of GRID) {
            const x=boxes[0]!.width*fx,y=boxes[0]!.height*fy;
            await hosts[0].evaluate(el=>{delete (el as HTMLElement).dataset.lastPickerMethod;});
            await hosts[0].click({position:{x,y}});
            await expect.poll(()=>hosts[0].getAttribute('data-last-picker-method'),{timeout:10000})
              .toMatch(/^(EXPERIMENTAL_XYZ_BVH_MAIN|VTK_CELL_PICKER)$/);
            if(await hosts[0].getAttribute('data-last-picker-method')!=='EXPERIMENTAL_XYZ_BVH_MAIN')continue;
            const raw=await hosts[0].getAttribute('data-last-picker-source-id');
            if(!raw||!/^\d+$/.test(raw))throw new Error('R278_invalid_source_face');
            const id=Number(raw);
            if(!positions.some(p=>p.id===id))positions.push({x,y,id});
            if(positions.length===2)break;
          }
          if(positions.length===2)break;
        }
        expect(positions).toHaveLength(2);
        const evidence=[];
        for(const position of positions) {
          for(let k=0;k<pages.length;k++) {
            // The exact same shared helper runs on both qualified paths.
            await measuredClick(pages[k],hosts[k],position,METHODS[k]);
          }
        }
        for(let round=0;round<2;round++){
          const order=round===0?[0,1,2]:[2,1,0];
          const pixels=round===0?positions:[...positions].reverse();
          for(const position of pixels){
            for(const k of order) {
              const result=await measuredClick(pages[k],hosts[k],position,METHODS[k]);
              evidence.push({
                round,originalSourceFaceId:position.id,method:METHODS[k],
                eventToPickerMs:result.eventToPickerMs,
                eventToTwoRafMs:result.eventToTwoRafMs,
                pickerWallMs:result.pickerWallMs,
                observedOriginalFaceId:result.sourceId,
                inspector:result.inspector,
              });
            }
          }
        }
        expect(evidence).toHaveLength(12);
        const after=await Promise.all(pages.map(p=>camera(p,model.sha)));
        expect(after).toEqual(before);
        const methods=METHODS.map(method=>{
          const rows=evidence.filter(e=>e.method===method);
          expect(rows).toHaveLength(4);
          return {method,eventToPicker:distribution(rows.map(r=>r.eventToPickerMs)),
            eventToTwoRaf:distribution(rows.map(r=>r.eventToTwoRafMs))};
        });
        const receipt={
          schema:'apmesh.meshstudio.r278.shared_protocol_ci_dry_run.v1',
          classification:'HOSTED_CHROMIUM_SHARED_EVENT_HELPER_FUNCTIONAL_ONLY_NOT_DESKTOP_GPU',
          sourceModel:model.id,sourceSha256:model.sha,sourceStatus:model.sourceStatus,
          originalFaceIds:positions.map(p=>p.id),
          exactOriginalIdAgreement:evidence.length,
          sourceCameraMatchedBeforeAfter:true,
          quadVisible:false,warmupPerMethodPerFace:1,rounds:2,
          measuredObservations:evidence.length,
          methods,raw:evidence,
          qualification:{
            sharedProtocolCodeExecuted:true,
            originalSourceIdentityMatched:true,
            physicalGPUQualified:false,
            gpuPresentQualified:false,
            browserProcessRssQualified:false,
            gpuVramQualified:false,
            acceptedAdaptiveEpochQualified:false,
          },
          caveats:[
            'Hosted Chromium may be backed by SwiftShader software rendering',
            'Playwright browser clicks are not physical pointer input',
            'Two requestAnimationFrame callbacks do not measure presented GPU frames',
            'Reduced dry-run protocol is NOT the full headed 8-round physical study',
            'Staged Band remains unaccepted and P1 has only one controlled generation',
          ],
        };
        await mkdir('test-results',{recursive:true});
        const filename='r278-shared-protocol-ci-'+model.id+'.json';
        const json=JSON.stringify(receipt,null,2)+'\n';
        await writeFile('test-results/'+filename,json,'utf8');
        await info.attach(filename,{body:Buffer.from(json),contentType:'application/json'});
        console.log('R278_SHARED_PROTOCOL_CI='+JSON.stringify({
          model:model.id,originalSourceFaceIds:positions.map(p=>p.id),
          methodCounts:methods.map(m=>({method:m.method,count:m.eventToPicker.n})),
          sourceIdentityValid:true,physicalGPUQualified:false,
        }));
      }finally{
        await worker.close();
        await native.close();
      }
    });
}
