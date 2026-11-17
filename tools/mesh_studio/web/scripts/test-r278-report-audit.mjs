import assert from 'node:assert/strict';
import { test } from 'node:test';
import { auditR277Receipt } from './audit-r277-report.mjs';

/** In-memory fabricated fixture tests ONLY the auditor, never geometric speed. */
const FACE_IDS=[68,76,69];
const PICKERS=['EXPERIMENTAL_XYZ_BVH_MAIN','EXPERIMENTAL_XYZ_BVH_WORKER','VTK_CELL_PICKER'];

function stats(values){
  const sorted=[...values].sort((a,b)=>a-b);
  const p=n=>Math.round(sorted[Math.ceil(n*sorted.length)-1]*1000)/1000;
  return{n:sorted.length,p50_ms:p(.5),p95_ms:p(.95),
    min_ms:Math.round(sorted[0]*1000)/1000,
    max_ms:Math.round(sorted.at(-1)*1000)/1000};
}
function fixture(){
  const raw=[];
  const pixelTable=FACE_IDS.map((id,i)=>({id,x:100+i*80,y:80+i*35}));
  for(let round=0;round<8;round++){
    const order=[0,1,2].slice(round%3).concat([0,1,2].slice(0,round%3));
    if(round%2)order.reverse();
    const faces=round%2?[...FACE_IDS].reverse():FACE_IDS;
    for(const faceId of faces)for(const pickerIndex of order){
      const method=PICKERS[pickerIndex];
      const base=method==='EXPERIMENTAL_XYZ_BVH_WORKER'?20:
        method==='EXPERIMENTAL_XYZ_BVH_MAIN'?.2:.7;
      const time=base+round*.05;
      const point=pixelTable.find(p=>p.id===faceId);
      raw.push({round,faceId,method,pixelX:point.x,pixelY:point.y,
        eventToPickerMs:time,eventToTwoRafMs:time+31,pickerWallMs:time*.95,
        browserVisibility:'visible',inspectorId:'#'+faceId});
    }
  }
  return {
    schema:'apmesh.meshstudio.r277.operator_attested_headed_desktop.v1',
    classification:'PHYSICAL_DESKTOP_ATTESTED_NOT_GPU_PRESENT_OR_TOTAL_RAM_CERTIFIED',
    model:'p1',
    originalSourceSha:'cbf6cd6308ba54544d06c5d562c491eb7d43ddb216365e0e9d188fd3430295e0',
    sourceStatus:'CONTROLLED_PHYSICAL_GENERATION',
    cameraXYZ:{position:[0,0,3],focal_point:[0,0,0],view_up:[0,1,0],
      parallel_scale:1,parallel:false},
    cameraPreserved:true,
    cameraXYZBeforeByMethod:Array.from({length:3},()=>({
      position:[0,0,3],focal_point:[0,0,0],view_up:[0,1,0],
      parallel_scale:1,parallel:false,
    })),
    cameraXYZAfterByMethod:Array.from({length:3},()=>({
      position:[0,0,3],focal_point:[0,0,0],view_up:[0,1,0],
      parallel_scale:1,parallel:false,
    })),
    viewportCSS:{width:600,height:350},
    originalSourceFaceIds:[...FACE_IDS],originalFacePixels:pixelTable,
    exactOriginalIdMatches:raw.length,
    conditions:{quadVisible:false,rounds:8,warmupsPerFacePerMethod:2,pickerOrder:'ROTATED_REVERSED'},
    operatorAttestation:{value:'I_CONFIRM_PHYSICAL_WORKSTATION',
      declaredGpuModel:'fixture-model',declaredGpuDriver:'fixture-driver',declaredRefreshHz:60},
    browser:{
      webgl:{softwareSuspected:false,unmaskedRenderer:'TEST_FIXTURE_MOCK_GPU_NEVER_REAL'},
      scope:'BROWSER_REPORTED_GL_AND_JS_ESTIMATES_NOT_CERTIFIED_PHYSICAL_GPU_OR_RSS',
      totalProcessRssBytes:null,workerRssBytes:null,gpuVramBytes:null,
    },
    synchronousBuildMs:'1.2',
    qualification:{sourceIdsInTest:true,physicalMachineOperatorAttested:true,
      rendererNonSoftwareStringVerified:true,
      hardwareGpuPresentTimestampVerified:false,totalBrowserRssMeasured:false,
      workerRssMeasured:false,gpuVramMeasured:false,largeRealAcceptedPatchMeshTested:false},
    rawSamples:raw,distributions:PICKERS.map(method=>{
      const data=raw.filter(row=>row.method===method);
      return{method,eventToPicker:stats(data.map(x=>x.eventToPickerMs)),
        eventToSecondRaf:stats(data.map(x=>x.eventToTwoRafMs)),
        pickerWall:stats(data.map(x=>x.pickerWallMs))};
    }),
  };
}
const clone=x=>structuredClone(x);
const reject=(data,pattern)=>assert.throws(()=>auditR277Receipt(data),pattern);

test('R278 report auditor accepts internally consistent in-memory TEST FIXTURE (no hardware claim)',()=>{
  const verdict=auditR277Receipt(fixture());
  assert.equal(verdict.sampleCount,72);
  assert.equal(verdict.model,'p1');
  assert.equal(verdict.gpuPresentedFrameQualified,false);
  assert.equal(verdict.gpuVramQualified,false);
  assert.match(verdict.status,/NOT_PHYSICAL_HARDWARE_CERTIFICATION/);
});
test('R278 refuses incomplete and repeated samples',()=>{
  const missing=fixture();missing.rawSamples.pop();
  reject(missing,/expected_72_raw_samples/);
  const duplicate=fixture();duplicate.rawSamples[1]=clone(duplicate.rawSamples[0]);
  reject(duplicate,/duplicate_source_face_round_picker/);
});
test('R278 refuses mismatched source and camera lineage',()=>{
  const forged=fixture();forged.originalSourceSha='0'.repeat(64);
  reject(forged,/original_sha_mismatch/);
  const camera=fixture();camera.cameraXYZ.position=[0,0,0];
  reject(camera,/missing_or_invalid_camera_provenance/);
  const legacy=fixture();legacy.model='eistute';
  reject(legacy,/model_not_in_qualified_catalog/);
  const status=fixture();status.sourceStatus='STAGED_UNACCEPTED';
  reject(status,/source_status_mismatch/);
});
test('R278 refuses unsupported GPU, RAM, and software-renderer assertions',()=>{
  const gpu=fixture();gpu.qualification.hardwareGpuPresentTimestampVerified=true;
  reject(gpu,/unsupported_claim_hardwareGpuPresentTimestampVerified/);
  const rss=fixture();rss.browser.totalProcessRssBytes=1234;
  reject(rss,/unmeasured_memory_claim_totalProcessRssBytes/);
  const software=fixture();software.browser.webgl.softwareSuspected=true;
  reject(software,/unverified_renderer/);
});
test('R278 rejects altered percentiles and inconsistent picker/RAF evidence',()=>{
  const summary=fixture();summary.distributions[0].eventToPicker.p50_ms=123;
  reject(summary,/distribution_mismatch_/);
  const raf=fixture();raf.rawSamples[0].eventToTwoRafMs=-1;
  reject(raf,/invalid_callback_or_two_raf_timing/);
  const inspector=fixture();inspector.rawSamples[0].inspectorId='#999';
  reject(inspector,/inspector_original_id_mismatch/);
});

test('R2.7.9 rejects reordered samples despite all 72 identities being present',()=>{
  const changed=fixture();
  [changed.rawSamples[0],changed.rawSamples[1]]=[changed.rawSamples[1],changed.rawSamples[0]];
  reject(changed,/raw_measurement_protocol_order_mismatch/);
});
test('R2.7.9 rejects different pixels for same original face and unsupported viewport',()=>{
  const pixels=fixture();pixels.rawSamples[0].pixelX+=1;
  reject(pixels,/methods_not_picking_identical_original_pixel/);
  const negative=fixture();negative.originalFacePixels[1].x=negative.viewportCSS.width+2;
  reject(negative,/source_face_pixel_mismatch/);
});
test('R2.7.9 rejects inconsistent stored XYZ camera among methods or after collection',()=>{
  const after=fixture();after.cameraXYZAfterByMethod[1].position=[0,0,4];
  reject(after,/camera_changed_or_methods_disagree/);
  const before=fixture();before.cameraXYZBeforeByMethod.pop();
  reject(before,/missing_per_method_camera_snapshots/);
});
