/* R2.7 CPU-only BVH contracts: source IDs, geometry rejection and bounded traversal. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const ts = require('@typescript/typescript6');
require.extensions['.ts'] = (mod, filename) => {
  const js=ts.transpileModule(fs.readFileSync(filename,'utf8'), {
    fileName:filename,reportDiagnostics:true,
    compilerOptions:{target:ts.ScriptTarget.ES2022,module:ts.ModuleKind.CommonJS}});
  assert.equal((js.diagnostics??[]).filter(x=>x.category===ts.DiagnosticCategory.Error).length,0);
  mod._compile(js.outputText,filename);
};
const {buildXyzBvh,prepareBvhPayload,BVH_MAX_FACES} =
  require(path.join(__dirname,'..','src','xyzBvh.ts'));

function fixture(vertices,faces,ids,space='xyz') {
  const polys=[],offsets=[0],arities=[];
  for(const face of faces) { arities.push(face.length);polys.push(face.length,...face);offsets.push(polys.length); }
  return {coordinate_space:space,points:[],cells:[],source_face_ids:[],cell_types:[],
    triangles:faces.filter(x=>x.length===3).length,quads:faces.filter(x=>x.length===4).length,
    packed:{vertices:new Float32Array(vertices.flat()),faceIds:new Uint32Array(ids),
      polys:new Uint32Array(polys),offsets:new Uint32Array(offsets),arities:new Uint8Array(arities)}};
}
const square=fixture([[0,0,0],[1,0,0],[1,1,0],[0,1,0]],[[0,1,2,3]],[903]);
const payload=prepareBvhPayload(square);
assert.ok(payload);
assert.notStrictEqual(payload.vertices,square.packed.vertices);
const quad=buildXyzBvh(payload);
assert.ok(quad);
assert.deepEqual(quad.pick([.36,.42,2],[.36,.42,-2],true,true),
  {kind:'hit',sourceFaceId:903,testedFaces:1});
assert.equal(quad.pick([0,.42,2],[0,.42,-2],true,true).kind,'ambiguous');
assert.equal(quad.pick([1.5,.42,2],[1.5,.42,-2],true,true).kind,'miss');
assert.equal(quad.pick([.36,.42,2],[.36,.42,-2],true,false).kind,'miss');
assert.equal(quad.pick([NaN,.42,2],[.36,.42,-2],true,true).kind,'ambiguous');
const overlap=fixture([[0,0,0],[1,0,0],[1,1,0],[0,1,0],
                       [0,0,0],[1,0,0],[1,1,0],[0,1,0]],
  [[0,1,2,3],[4,5,6,7]],[9,77]);
assert.equal(buildXyzBvh(prepareBvhPayload(overlap)).pick([.26,.41,2],[.26,.41,-2],true,true).kind,
  'ambiguous');
const warped=fixture([[0,0,0],[1,0,0],[1,1,.6],[0,1,0]],[[0,1,2,3]],[9]);
assert.equal(buildXyzBvh(prepareBvhPayload(warped)),null);
const bowtie=fixture([[0,0,0],[1,1,0],[0,1,0],[1,0,0]],[[0,1,2,3]],[9]);
assert.equal(buildXyzBvh(prepareBvhPayload(bowtie)),null);
const duplicate=fixture([[0,0,0],[1,0,0],[1,1,0],[0,1,0]],
  [[0,1,2],[0,2,3]],[10,10]);
assert.equal(buildXyzBvh(prepareBvhPayload(duplicate)),null);
// A mixed real-like source may index flat TRI only; warped QUAD visibility is never ignored.
const mixedCurved=fixture([
  [0,0,0],[1,0,0],[1,1,.6],[0,1,0],
  [2,0,0],[3,0,0],[2,1,0]
],[[0,1,2,3],[4,5,6]],[90,91]);
const mixedPayload=prepareBvhPayload(mixedCurved);
assert.equal(buildXyzBvh(mixedPayload),null);
const partial=buildXyzBvh(mixedPayload,{allowUnindexedWarpedQuads:true});
assert.ok(partial);
assert.equal(partial.faceCount,2);
assert.equal(partial.indexedFaceCount,1);
assert.equal(partial.excludedQuadCount,1);
assert.deepEqual(partial.pick([2.2,.2,2],[2.2,.2,-2],true,false),
  {kind:'hit',sourceFaceId:91,testedFaces:1});
assert.deepEqual(partial.pick([2.2,.2,2],[2.2,.2,-2],true,true),
  {kind:'ambiguous',testedFaces:0});
assert.equal(buildXyzBvh(prepareBvhPayload(warped),
  {allowUnindexedWarpedQuads:true}),null);
// Invalid crossing connectivity must still reject the entire source in partial mode.
const invalidMixed=fixture([
  [0,0,0],[1,1,0],[0,1,0],[1,0,0],
  [2,0,0],[3,0,0],[2,1,0]
],[[0,1,2,3],[4,5,6]],[95,96]);
assert.equal(buildXyzBvh(prepareBvhPayload(invalidMixed),
  {allowUnindexedWarpedQuads:true}),null);
const triangle=fixture([[0,0,0],[1,0,0],[0,1,0]],[[0,1,2]],[31]);
assert.deepEqual(buildXyzBvh(prepareBvhPayload(triangle)).pick([.25,.3,2],[.25,.3,-2],true,true),
  {kind:'hit',sourceFaceId:31,testedFaces:1});
assert.equal(prepareBvhPayload({...square,coordinate_space:'uv'}),null);
const nx=11,ny=9,vertices=[],faces=[],ids=[];
for(let y=0;y<=ny;y++) for(let x=0;x<=nx;x++) vertices.push([x/nx,y/ny,Math.sin(x/20)*.01]);
for(let y=0;y<ny;y++) for(let x=0;x<nx;x++) {
  const a=y*(nx+1)+x;
  faces.push([a,a+1,a+nx+2],[a,a+nx+2,a+nx+1]);
  ids.push(500+ids.length,500+ids.length+1);
}
const grid=buildXyzBvh(prepareBvhPayload(fixture(vertices,faces,ids)));
assert.ok(grid);
const picked=grid.pick([.217,.183,2],[.217,.183,-2],true,true);
assert.equal(picked.kind,'hit');
assert.ok(picked.testedFaces<faces.length);
assert.ok(grid.nodeCount>1);
// Reject non-finite source coordinates without changing the original geometry.
const invalidVertex=fixture([[0,0,0],[1,0,0],[0,Infinity,0]],[[0,1,2]],[401]);
assert.equal(buildXyzBvh(prepareBvhPayload(invalidVertex)),null);
const invalidVertexNan=fixture([[0,0,0],[1,0,0],[0,NaN,0]],[[0,1,2]],[402]);
assert.equal(buildXyzBvh(prepareBvhPayload(invalidVertexNan)),null);
// Occlusion must select the nearest physical face, regardless of source ID order.
const occlusion=fixture([
  [0,0,0],[1,0,0],[0,1,0],
  [0,0,1],[1,0,1],[0,1,1]
],[[0,1,2],[3,4,5]],[900,17]);
const occlusionIndex=buildXyzBvh(prepareBvhPayload(occlusion));
assert.ok(occlusionIndex);
assert.deepEqual(occlusionIndex.pick([.2,.3,2],[.2,.3,-1],true,true),
  {kind:'hit',sourceFaceId:17,testedFaces:2});
assert.deepEqual(occlusionIndex.pick([.2,.3,-1],[.2,.3,2],true,true),
  {kind:'hit',sourceFaceId:900,testedFaces:2});
assert.equal(occlusionIndex.pick([.2,.3,2],[.2,.3,-1],false,true).kind,'miss');
console.log(JSON.stringify({schema:'apmesh.meshstudio.r27.bvh_core.v1',
  qualified_faces_cap:BVH_MAX_FACES,grid_nodes:grid.nodeCount,candidates:picked.testedFaces,
  source_ids_preserved:true,overlap_and_invalid_fallback:true,
  validated:'CPU_CONTRACTS_ONLY_NOT_REAL_MODEL_BROWSER_OR_LOD'}));
console.log('R27_BVH_UNIT_PASS');
