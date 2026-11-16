/* Pure TypeScript contract regression, independent of WebGL and browser state. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const ts = require('typescript');
const path = require('node:path');
const root = path.join(__dirname, '..', 'src');
require.extensions['.ts'] = (mod, filename) => {
  const input = fs.readFileSync(filename, 'utf8');
  const js = ts.transpileModule(input, { fileName: filename, reportDiagnostics: true,
    compilerOptions: { target: ts.ScriptTarget.ES2022, module: ts.ModuleKind.CommonJS } });
  const errors = (js.diagnostics ?? []).filter(x => x.category === ts.DiagnosticCategory.Error);
  assert.equal(errors.length, 0, filename + ': ' + errors.map(x => ts.flattenDiagnosticMessageText(x.messageText, '\n')));
  mod._compile(js.outputText, filename);
};
const { syntheticPackedScene } = require(path.join(root,'syntheticPacked.ts'));
const { syntheticGridFacePartition, verifyFacePartition } = require(path.join(root,'sourceLodLineage.ts'));
const { buildSyntheticXyzRayPicker } = require(path.join(root,'xyzSyntheticRayPicker.ts'));
const start = performance.now();
const mesh = syntheticPackedScene(500000).xyz;
const partition = syntheticGridFacePartition(mesh, 8);
assert.equal(partition.source_face_count, 500000);
assert.ok(partition.aggregate_count > 6000 && partition.aggregate_count < 8500);
assert.equal(partition.offsets.at(-1),500000);
assert.equal(partition.covers_every_original_face_exactly_once,true);
assert.equal(partition.aggregate_geometry_defined,false);
assert.equal(partition.is_geometric_lod,false);
assert.equal(partition.metric_comparable,false);
assert.equal(new Set(partition.original_face_ids).size,500000);
assert.doesNotThrow(() => verifyFacePartition(mesh.packed.faceIds,partition.offsets,partition.original_face_ids));
const foreign=partition.original_face_ids.slice();foreign[7]=599999;
assert.throws(() => verifyFacePartition(mesh.packed.faceIds,partition.offsets,foreign),/foreign_original_face_id/);
const duplicated=partition.original_face_ids.slice();duplicated[7]=duplicated[6];
assert.throws(() => verifyFacePartition(mesh.packed.faceIds,partition.offsets,duplicated),/duplicate_aggregate_ownership/);
const wrongSource={...mesh,source_sha256:'1'.repeat(64)};
assert.throws(()=>syntheticGridFacePartition(wrongSource),/unqualified_synthetic_grid_partition/);
const lookupStart=performance.now();
const picker=buildSyntheticXyzRayPicker(mesh);
assert.ok(picker);
const indexMs=performance.now()-lookupStart;
const w=Math.floor(Math.sqrt(500000)),h=Math.ceil(500000/w);
for(const [x,y] of [[0,0],[w-2,0],[99,250],[w-2,h-2],[200,400]]){
  const u=(x+.37)/w, v=(y+.43)/h;
  const hit=picker.pick([u,v,2],[u,v,-2],true);
  assert.deepEqual(hit,{kind:'hit',sourceFaceId:y*w+x,testedFaces:1});
}
const edge=picker.pick([100/w,250/h,2],[100/w,250/h,-2],true);
assert.equal(edge.kind,'ambiguous');
assert.equal(picker.pick([.5,.5,2],[.5,.5,-2],false).kind,'miss');
assert.equal(picker.pick([NaN,.5,2],[.5,.5,-2],true).kind,'ambiguous');
assert.equal(buildSyntheticXyzRayPicker(wrongSource),null);
const corrupt={...mesh,packed:{...mesh.packed,faceIds:mesh.packed.faceIds.slice()}};
corrupt.packed.faceIds[47]=25;
assert.equal(buildSyntheticXyzRayPicker(corrupt),null);
console.log(JSON.stringify({schema:'apmesh.meshstudio.r26.local_unit.v1',
  cells:500000,mapped:partition.original_face_ids.length,aggregates:partition.aggregate_count,
  xyz_index_build_ms:Number(indexMs.toFixed(2)),unit_contracts:'PASS',
  caveat:'synthetic_xyz_ray_and_partition_only_not_general_real_mesh_or_lod'}));
console.log('R26_UNIT_PASS');
