/* Hermetic binary and ASCII STL adversarial fixtures; no third-party data. */
'use strict';
const {test}=require('node:test');
const assert=require('node:assert/strict');
const crypto=require('node:crypto');
const zlib=require('node:zlib');
const fs=require('node:fs');
const os=require('node:os');
const path=require('node:path');
const m=require('./zip_stl_probe.js');
const cli=require('./thingi10k_zip_audit.cjs');

function tetra(){
 const points=[[0,0,0],[1,0,0],[0,1,0],[0,0,1]];
 const faces=[[0,1,2],[0,3,1],[0,2,3],[1,3,2]];
 const bytes=Buffer.alloc(84+faces.length*50);bytes.writeUInt32LE(faces.length,80);
 for(let i=0;i<faces.length;i++)for(let j=0;j<3;j++)for(let k=0;k<3;k++)bytes.writeFloatLE(points[faces[i][j]][k],84+i*50+12+12*j+4*k);
 return bytes;
}
function makeZip(data,name='293137.stl',compress=true){
 const value=compress?zlib.deflateRawSync(data):data,filename=Buffer.from(name,'ascii');
 const local=Buffer.alloc(30+filename.length),central=Buffer.alloc(46+filename.length),end=Buffer.alloc(22);
 local.writeUInt32LE(0x04034b50,0);local.writeUInt16LE(20,4);local.writeUInt16LE(compress?8:0,8);
 local.writeUInt32LE(m.crc32(data),14);local.writeUInt32LE(value.length,18);local.writeUInt32LE(data.length,22);local.writeUInt16LE(filename.length,26);filename.copy(local,30);
 central.writeUInt32LE(0x02014b50,0);central.writeUInt16LE(20,4);central.writeUInt16LE(20,6);central.writeUInt16LE(compress?8:0,10);
 central.writeUInt32LE(m.crc32(data),16);central.writeUInt32LE(value.length,20);central.writeUInt32LE(data.length,24);central.writeUInt16LE(filename.length,28);filename.copy(central,46);
 end.writeUInt32LE(0x06054b50,0);end.writeUInt16LE(1,8);end.writeUInt16LE(1,10);end.writeUInt32LE(central.length,12);end.writeUInt32LE(local.length+value.length,16);
 return Buffer.concat([local,value,central,end]);
}
function digests(zip,raw){return {zip:crypto.createHash('sha1').update(Buffer.from(`blob ${zip.length}\0`)).update(zip).digest('hex'),raw:crypto.createHash('sha256').update(raw).digest('hex')}}
const raw=tetra(),zip=makeZip(raw),hashes=digests(zip,raw);

test('standard SHA-256 vectors match independent Node crypto',()=>{for(const s of ['','abc','test'.repeat(300)])assert.equal(m.sha256Hex(new Uint8Array(Buffer.from(s))),crypto.createHash('sha256').update(s).digest('hex'));});
test('base64 decoder agrees with Buffer on padded, wrapped input',()=>assert.deepEqual(Buffer.from(m.decodeBase64('UEs=\n')),Buffer.from('PK')));
test('base64 decoder fails closed on invalid glyphs',()=>assert.throws(()=>m.decodeBase64('AA@='),/base64/));
test('stored ZIP and DEFLATE ZIP both decode exactly',()=>{for(const bool of [true,false])assert.deepEqual(Buffer.from(m.extractSingleZip(makeZip(raw,'293137.stl',bool)).bytes),raw)});
test('CRC mismatch rejects even plausible length',()=>{const damaged=Buffer.from(zip);damaged.writeUInt32LE(0,14);damaged.writeUInt32LE(0,zip.length-22-46-10+16);assert.throws(()=>m.extractSingleZip(damaged),/CRC/)});
test('multi-entry ZIP declaration is rejected',()=>{const damaged=Buffer.from(zip);damaged.writeUInt16LE(2,damaged.length-22+10);assert.throws(()=>m.extractSingleZip(damaged),/one non-spanned/)});
test('ZIP internal path cannot escape archive',()=>assert.throws(()=>m.extractSingleZip(makeZip(raw,'../../evil.stl')),/numeric STL/));
test('truncated or oversized ZIP is rejected',()=>{assert.throws(()=>m.extractSingleZip(zip.subarray(0,zip.length-5)));assert.throws(()=>m.extractSingleZip(zip,12),/size unsupported/)});
test('binary tetra has closed genus-zero manifold incidence and regular vertex links',()=>{const q=m.parseBinaryStl(raw),a=m.auditMeshVertices(q.triangle_coordinates,q.triangles);assert.deepEqual({triangles:a.source_triangles,vertices:a.source_unique_exact_vertices,edges:a.source_unique_exact_edges,faces2:a.two_face_edges,links:a.vertex_link_interior,singular:a.vertex_link_singular,components:a.vertex_connected_components},{triangles:4,vertices:4,edges:6,faces2:6,links:4,singular:0,components:1})});
test('ASCII open triangle has boundary link path',()=>{const text='solid t\n facet normal 0 0 1\n outer loop\n vertex 0 0 0\n vertex 1 0 0\n vertex 0 1 0\n endloop\n endfacet\nendsolid t\n';const q=m.parseAsciiStl(Buffer.from(text));assert.equal(q.source_triangles,1);assert.equal(q.boundary_edges,3);assert.equal(q.vertex_link_boundary,3);});
test('invalid ASCII facets reject instead of quietly skipping data',()=>assert.throws(()=>m.parseAsciiStl(Buffer.from('solid a\n facet normal 0 0 1\nendsolid a')),/malformed/));
test('genuine three triangle owners is not misclassified as two',()=>{const ps=[[0,0,0],[1,0,0],[0,1,0],[0,0,1],[0,-1,0]];const ff=[[0,1,2],[1,0,3],[0,1,4]];const q=m.auditMeshVertices(ps,ff);assert.equal(q.three_plus_edges,1);assert.equal(q.edge_incidence_histogram['3'],1);assert(q.vertex_link_singular>=2)});
test('exact-coordinate duplicated triangles remain visible',()=>{const ps=[[0,0,0],[1,0,0],[0,1,0]];const q=m.auditMeshVertices(ps,[[0,1,2],[0,1,2]]);assert.equal(q.raw_duplicate_triangles,1);assert.equal(q.edge_winding_conflicts,3)});
test('original ZIP and original STL digests both required',()=>{assert.throws(()=>cli.inspect(zip,293137,'0'.repeat(40),hashes.raw),/ZIP Git blob/);assert.throws(()=>cli.inspect(zip,293137,hashes.zip,'0'.repeat(64)),/STL SHA-256/);assert.throws(()=>cli.inspect(zip,0,hashes.zip,hashes.raw),/internal file ID/);});
test('valid pinned synthetic binary STL returns raw identity only, no admission',()=>{const q=cli.inspect(zip,293137,hashes.zip,hashes.raw);assert.equal(q.topology.source_triangles,4);assert.equal(q.disclaimers.apmesh_tri_quad_generated,false);assert.equal(q.source.raw_stl_sha256,hashes.raw)});
test('CLI creates receipt atomically and refuses overwrite',()=>{const dir=fs.mkdtempSync(path.join(os.tmpdir(),'thingi-audit-'));try{const input=path.join(dir,'293137.zip'),output=path.join(dir,'receipt.json');fs.writeFileSync(input,zip);const args=['--zip',input,'--file-id','293137','--expected-zip-sha1',hashes.zip,'--expected-stl-sha256',hashes.raw,'--output',output];assert.equal(cli.main(args),0);assert.equal(JSON.parse(fs.readFileSync(output)).source.raw_stl_sha256,hashes.raw);assert.throws(()=>cli.main(args),/EEXIST/)}finally{fs.rmSync(dir,{recursive:true,force:true})}});
