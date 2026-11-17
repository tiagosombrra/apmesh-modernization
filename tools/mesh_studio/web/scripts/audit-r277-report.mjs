/**
 * Audit internal consistency of operator-produced R2.7.7 reports.
 * Never infer physical hardware authenticity, presented frames, RSS, or VRAM.
 */
import { createHash } from 'node:crypto';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const MODELS={
  p1:{sha:'cbf6cd6308ba54544d06c5d562c491eb7d43ddb216365e0e9d188fd3430295e0',
    sourceStatus:'CONTROLLED_PHYSICAL_GENERATION'},
  band:{sha:'76b0b4defecc5d534815fb9f41e1405653597a4a0bee6cc7b722ec2460d7afd6',
    sourceStatus:'STAGED_UNACCEPTED'},
};
const METHODS=['EXPERIMENTAL_XYZ_BVH_MAIN','EXPERIMENTAL_XYZ_BVH_WORKER','VTK_CELL_PICKER'];
const CHECKS=['hardwareGpuPresentTimestampVerified','totalBrowserRssMeasured',
  'workerRssMeasured','gpuVramMeasured','largeRealAcceptedPatchMeshTested'];

function check(condition,reason){
  if(!condition)throw new Error('R278_AUDIT_REJECTED: '+reason);
}
function finiteNonnegative(x){return typeof x==='number'&&Number.isFinite(x)&&x>=0;}
function distribution(xs){
  check(xs.length>0&&xs.every(finiteNonnegative),'invalid_measured_samples');
  const a=[...xs].sort((x,y)=>x-y),p=f=>Math.round(a[Math.ceil(a.length*f)-1]*1000)/1000;
  return {n:a.length,p50_ms:p(.5),p95_ms:p(.95),
    min_ms:Math.round(a[0]*1000)/1000,max_ms:Math.round(a.at(-1)*1000)/1000};
}
function cameraValid(pose){
  const vec=v=>Array.isArray(v)&&v.length===3&&v.every(
    x=>typeof x==='number'&&Number.isFinite(x));
  if(!pose||!vec(pose.position)||!vec(pose.focal_point)||!vec(pose.view_up)||
     !(typeof pose.parallel_scale==='number'&&pose.parallel_scale>0&&
       Number.isFinite(pose.parallel_scale))||typeof pose.parallel!=='boolean')return false;
  const delta=pose.position.map((v,i)=>v-pose.focal_point[i]);
  const cross=[delta[1]*pose.view_up[2]-delta[2]*pose.view_up[1],
    delta[2]*pose.view_up[0]-delta[0]*pose.view_up[2],
    delta[0]*pose.view_up[1]-delta[1]*pose.view_up[0]];
  return Math.hypot(...delta)>1e-12&&Math.hypot(...cross)>1e-12;
}
function checkDistribution(reported,observed,name){
  check(reported&&typeof reported==='object','missing_distribution_'+name);
  const derived=distribution(observed);
  for(const k of Object.keys(derived)){
    check(reported[k]===derived[k],'distribution_mismatch_'+name+'_'+k);
  }
}

/** Validate structure, source provenance and repeated measurements, not hardware authenticity. */
export function auditR277Receipt(record){
  check(record&&typeof record==='object','missing_report');
  check(record.schema==='apmesh.meshstudio.r277.operator_attested_headed_desktop.v1','schema');
  check(record.classification==='PHYSICAL_DESKTOP_ATTESTED_NOT_GPU_PRESENT_OR_TOTAL_RAM_CERTIFIED',
    'scope');
  const model=MODELS[record.model];
  check(Boolean(model),'model_not_in_qualified_catalog');
  check(record.originalSourceSha===model.sha,'original_sha_mismatch');
  check(record.sourceStatus===model.sourceStatus,'source_status_mismatch');
  check(record.conditions?.quadVisible===false,'curved_quad_must_be_hidden');
  check(record.conditions.rounds===8&&record.conditions.warmupsPerFacePerMethod===2,
    'protocol_counts_mismatch');
  check(record.conditions.pickerOrder==='ROTATED_REVERSED','picker_order_mismatch');
  check(Array.isArray(record.originalSourceFaceIds)&&record.originalSourceFaceIds.length===3,
    'three_original_source_faces_required');
  const faces=record.originalSourceFaceIds;
  check(faces.every(x=>Number.isSafeInteger(x)&&x>=0)&&new Set(faces).size===3,
    'duplicate_or_invalid_original_source_face');
  check(cameraValid(record.cameraXYZ)&&record.cameraPreserved===true,
    'missing_or_invalid_camera_provenance');
  const before=record.cameraXYZBeforeByMethod,after=record.cameraXYZAfterByMethod;
  check(Array.isArray(before)&&before.length===3&&
    Array.isArray(after)&&after.length===3&&
    before.every(cameraValid)&&after.every(cameraValid),
    'missing_per_method_camera_snapshots');
  // Stored camera equality is internal provenance, not an independent viewport/GPU oracle.
  const cameraReference=JSON.stringify(record.cameraXYZ);
  check(before.every(p=>JSON.stringify(p)===cameraReference)&&
    after.every(p=>JSON.stringify(p)===cameraReference),
    'camera_changed_or_methods_disagree');
  const bounds=record.viewportCSS;
  check(bounds&&typeof bounds.width==='number'&&
    typeof bounds.height==='number'&&Number.isFinite(bounds.width)&&
    Number.isFinite(bounds.height)&&bounds.width>0&&bounds.height>0,
    'invalid_viewport_geometry');
  const pixelTable=record.originalFacePixels;
  check(Array.isArray(pixelTable)&&pixelTable.length===3,
    'missing_source_face_pixels');
  for(let i=0;i<faces.length;i++){
    const p=pixelTable[i];
    check(p&&p.id===faces[i]&&finiteNonnegative(p.x)&&
      finiteNonnegative(p.y)&&p.x<bounds.width&&p.y<bounds.height,
      'source_face_pixel_mismatch');
  }
  check(record.operatorAttestation?.value==='I_CONFIRM_PHYSICAL_WORKSTATION','attestation');
  check(typeof record.operatorAttestation.declaredGpuModel==='string'&&
    record.operatorAttestation.declaredGpuModel.trim().length>2,'gpu_model_not_declared');
  check(typeof record.operatorAttestation.declaredGpuDriver==='string'&&
    record.operatorAttestation.declaredGpuDriver.trim().length>1,'driver_not_declared');
  const hz=record.operatorAttestation.declaredRefreshHz;
  check(typeof hz==='number'&&hz>=30&&hz<=500&&Number.isFinite(hz),
    'refresh_rate_invalid');
  check(record.browser?.webgl?.softwareSuspected===false&&
    typeof record.browser.webgl.unmaskedRenderer==='string'&&
    record.browser.webgl.unmaskedRenderer.trim().length>4,'unverified_renderer');
  check(record.browser.scope==='BROWSER_REPORTED_GL_AND_JS_ESTIMATES_NOT_CERTIFIED_PHYSICAL_GPU_OR_RSS',
    'browser_scope_mismatch');
  check(record.qualification?.sourceIdsInTest===true&&
    record.qualification.physicalMachineOperatorAttested===true&&
    record.qualification.rendererNonSoftwareStringVerified===true,'test_scope_flags');
  for(const key of CHECKS)check(record.qualification[key]===false,'unsupported_claim_'+key);
  for(const key of ['totalProcessRssBytes','workerRssBytes','gpuVramBytes']){
    check(record.browser[key]===null,'unmeasured_memory_claim_'+key);
  }
  check(finiteNonnegative(Number(record.synchronousBuildMs))&&
    record.synchronousBuildMs!==null,'synchronous_build_missing');
  const raw=record.rawSamples;
  check(Array.isArray(raw)&&raw.length===72,'expected_72_raw_samples');
  check(record.exactOriginalIdMatches===raw.length,'source_id_agreement_claim_mismatch');
  const encountered=new Set();
  for(const s of raw){
    check(Number.isSafeInteger(s.round)&&s.round>=0&&s.round<8,'round_out_of_range');
    check(faces.includes(s.faceId),'face_outside_fixed_source_id_set');
    check(METHODS.includes(s.method),'picker_outside_three_methods');
    check(s.inspectorId==='#'+s.faceId,'inspector_original_id_mismatch');
    check(s.browserVisibility==='visible','sample_not_visible');
    check(finiteNonnegative(s.eventToPickerMs)&&finiteNonnegative(s.eventToTwoRafMs)&&
      finiteNonnegative(s.pickerWallMs)&&s.eventToTwoRafMs>=s.eventToPickerMs,
      'invalid_callback_or_two_raf_timing');
    const identity=[s.round,s.faceId,s.method].join('/');
    check(!encountered.has(identity),'duplicate_source_face_round_picker');
    encountered.add(identity);
  }
  check(encountered.size===8*3*3,'missing_one_or_more_source_round_methods');
  // Identity alone does not establish the declared rotated/reversed paired protocol.
  // Reconstruct its exact method and face order and reject permuted traces.
  const expectedSequence=[];
  for(let round=0;round<8;round++){
    const methods=[0,1,2].slice(round%3).concat([0,1,2].slice(0,round%3));
    if(round%2)methods.reverse();
    const faceOrder=round%2?[...faces].reverse():faces;
    for(const faceId of faceOrder)for(const methodIndex of methods){
      expectedSequence.push({round,faceId,method:METHODS[methodIndex]});
    }
  }
  for(let index=0;index<raw.length;index++){
    const sample=raw[index],expected=expectedSequence[index];
    check(sample.round===expected.round&&sample.faceId===expected.faceId&&
      sample.method===expected.method,'raw_measurement_protocol_order_mismatch');
    const p=pixelTable[faces.indexOf(sample.faceId)];
    check(sample.pixelX===p.x&&sample.pixelY===p.y,
      'methods_not_picking_identical_original_pixel');
  }
  check(Array.isArray(record.distributions)&&record.distributions.length===3,
    'missing_three_distributions');
  for(const method of METHODS){
    const saved=record.distributions.filter(x=>x.method===method);
    check(saved.length===1,'missing_or_duplicate_method_distribution');
    const subset=raw.filter(x=>x.method===method);
    checkDistribution(saved[0].eventToPicker,subset.map(x=>x.eventToPickerMs),
      method+'_eventToPicker');
    checkDistribution(saved[0].eventToSecondRaf,subset.map(x=>x.eventToTwoRafMs),
      method+'_eventToSecondRaf');
    checkDistribution(saved[0].pickerWall,subset.map(x=>x.pickerWallMs),
      method+'_pickerWall');
  }
  return{
    status:'R278_REPORT_INTERNAL_CONSISTENCY_PASS_NOT_PHYSICAL_HARDWARE_CERTIFICATION',
    model:record.model,sourceSha256:record.originalSourceSha,
    originalSourceFaceIds:[...faces],sampleCount:raw.length,
    scopedPhysicalMachineOperatorAttestation:true,
    gpuPresentedFrameQualified:false,browserRssQualified:false,workerRssQualified:false,
    gpuVramQualified:false,
  };
}

/** CLI performs read-only audit; it does not rewrite or upload the private device report. */
const direct=process.argv[1]&&resolve(process.argv[1])===fileURLToPath(import.meta.url);
if(direct){
  try{
    const files=process.argv.slice(2);
    check(files.length===1||files.length===2,'provide_one_or_two_report_json_paths');
    const summary=[];
    const models=new Set();
    for(const file of files){
      const raw=readFileSync(file);
      check(raw.length<=8*1024*1024,'report_too_large');
      const receipt=JSON.parse(raw.toString('utf8'));
      const result=auditR277Receipt(receipt);
      check(!models.has(result.model),'duplicate_model_report');
      models.add(result.model);
      summary.push({...result,reportSha256:createHash('sha256').update(raw).digest('hex')});
    }
    process.stdout.write(JSON.stringify({
      schema:'apmesh.meshstudio.r278.local_receipt_audit.v1',
      scope:'REPORT_ONLY_NOT_PHYSICAL_GPU_MEMORY_OR_SOURCE_ACCEPTANCE',
      auditedReports:summary,
    },null,2)+'\n');
  }catch(error){
    process.stderr.write(String(error)+'\n');
    process.exitCode=2;
  }
}
