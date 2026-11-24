#!/usr/bin/env node
/* Deterministic, fail-closed local audit for an authorized Thingi10K STL ZIP.
 * This gate checks mesh incidence, not author permissions or QUAD quality.
 */
'use strict';
const fs=require('node:fs');
const crypto=require('node:crypto');
const {extractSingleZip,parseBinaryStl,parseAsciiStl,auditMeshVertices,sha256Hex}=require('./zip_stl_probe.js');

function inspect(zipBytes,modelId,expectedZipSha1,expectedStlSha256){
  if(!/^\d+$/.test(String(modelId)))throw Error('Invalid file ID');
  if(!/^[a-f0-9]{40}$/.test(String(expectedZipSha1))||!/^[a-f0-9]{64}$/.test(String(expectedStlSha256)))throw Error('Expected immutable digests are mandatory');
  const header=Buffer.from(`blob ${zipBytes.length}\0`);
  const zipSha=crypto.createHash('sha1').update(header).update(zipBytes).digest('hex');
  if(zipSha!==expectedZipSha1)throw Error('ZIP Git blob SHA-1 mismatch');
  const zip=extractSingleZip(new Uint8Array(zipBytes),50_000_000);
  if(zip.name!==`${modelId}.stl`)throw Error('ZIP internal file ID mismatch');
  const raw=zip.bytes,hash=sha256Hex(raw);
  if(hash!==expectedStlSha256)throw Error('Original STL SHA-256 mismatch');
  const dv=raw.length>=84 ? new DataView(raw.buffer,raw.byteOffset,raw.byteLength) : null;
  const isBinary=dv!==null&&84+dv.getUint32(80,true)*50===raw.length;
  const q=isBinary?parseBinaryStl(raw):parseAsciiStl(raw);
  const counts=isBinary?auditMeshVertices(q.triangle_coordinates,q.triangles):q;
  const {triangle_coordinates,triangles,...safeCounts}=counts;
  return {
    schema:'apmesh-thingi10k-raw-stl-topology-v1',
    classification:'RAW_STL_INCIDENT_FACE_GRAPH_ONLY_PENDING_AUTHOR_RIGHTS_AND_APMESH',
    source:{file_id:Number(modelId),zip_git_blob_sha1:zipSha,raw_stl_sha256:hash,raw_stl_bytes:raw.length,zip_bytes:zipBytes.length,zip_crc32:zip.crc32,stl_encoding:isBinary?'binary':'ASCII'},
    topology:safeCounts,
    disclaimers:{original_author_license_independently_verified:false,reference_quad_output_pair_verified:false,apmesh_bezier_conversion_executed:false,apmesh_tri_quad_generated:false,stl_coordinate_reconstruction_is_original_index_identity:false,source_cad_nonmanifold_intent_proven:false}
  };
}
function parseArgs(argv){
 const options={};for(let i=0;i<argv.length;i+=2){if(i+1>=argv.length||!argv[i].startsWith('--'))throw Error('Expected --option VALUE pairs');if(argv[i] in options)throw Error('Duplicate CLI option');options[argv[i]]=argv[i+1];}
 for(const x of ['--zip','--file-id','--expected-zip-sha1','--expected-stl-sha256','--output'])if(!options[x])throw Error('Missing required '+x);
 if(Object.keys(options).length!==5)throw Error('Unknown option');return options;
}
function main(argv){
 const a=parseArgs(argv);const bytes=fs.readFileSync(a['--zip']);
 const result=inspect(bytes,a['--file-id'],a['--expected-zip-sha1'],a['--expected-stl-sha256']);
 const payload=JSON.stringify(result,null,2)+'\n';
 fs.writeFileSync(a['--output'],payload,{flag:'wx'});
 console.log(JSON.stringify({file_id:result.source.file_id,source_triangles:result.topology.source_triangles,three_plus_edges:result.topology.three_plus_edges,vertex_link_singular:result.topology.vertex_link_singular},null,2));
 return 0;
}
if(require.main===module){try{process.exitCode=main(process.argv.slice(2));}catch(e){console.error(String(e));process.exitCode=2}}
module.exports={inspect,parseArgs,main};
