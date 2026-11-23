import { expect, test } from '@playwright/test';
import { createHash } from 'node:crypto';
import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { join, resolve, basename } from 'node:path';

/** Real original C++ sources are independently authenticated in Python before
 * the V5.8 launcher starts. Browser uploads alone cannot prove C++ provenance.
 */
const folder = resolve(process.env.APMESH_V59_CORPUS_DIR ??
  '../../../build/v59-native-reviewer');
const scenePath = join(folder, 'r2720-native-accepted-scene.json');
const vectors = join(folder, 'v52-native-accepted-uv-publication');
const manifestPath = join(vectors, 'manifest.json');
const sourceSvg = ['eistute','book'].map(name =>
  join(vectors, name + '-accepted-step1-uv.svg'));
const sha = {
  scene: 'eb72cb058fef2a7632e09f5a3572f39e32f4d9038780cce05337d1afd86f2816',
  manifest: '85e2df4d178bb277c15989d6893903be0e69e1fe37b162ca1dc675e0afe59aee',
  eistute: 'c3757577ddc6cc147a029303be4bbe60fa0a87e4063829257ef7f7d91764bd66',
  book: '8d639313d8ade37fd4a8b0347fe5787d5d2db15296f0d3e6c6844e6abb39b248',
};
type NativeFace = [number, number, number, number, number[][]];
type NativeScene = {
  model:'eistute'|'book', accepted_native_step:number,
  native_tri_faces:number, native_source_patches:number,
  source_ndjson_sha256:string, native_faces:NativeFace[],
};
type SourceBundle = {
  scenes:NativeScene[], scientific_lod_qualified:boolean,
  no_implicit_node_welding:boolean,
  identity:{ documents:Array<{model:string,qualified_shared_source_curves:
    Array<{sample_groups:Array<{members:Array<{patch_slot:number,native_node_id:number}>}>}>}> };
};
function digest(body:Buffer):string {
  return createHash('sha256').update(body).digest('hex');
}
function sourceReady():boolean {
  return [scenePath, manifestPath, ...sourceSvg].every(existsSync);
}
function pinned() {
  if (!sourceReady()) throw new Error('v59_original_native_cpp_artifact_required');
  const paths = [scenePath,manifestPath,...sourceSvg];
  const expected = [sha.scene,sha.manifest,sha.eistute,sha.book];
  paths.forEach((p,i) =>
    expect(digest(readFileSync(p)), 'original source bytes: '+basename(p)).toBe(expected[i]));
  const scene = JSON.parse(readFileSync(scenePath,'utf8')) as SourceBundle;
  const manifest = JSON.parse(readFileSync(manifestPath,'utf8'));
  expect(scene.no_implicit_node_welding).toBe(true);
  expect(scene.scientific_lod_qualified).toBe(false);
  expect(scene.scenes.map(x=>[x.model,x.accepted_native_step,
    x.native_tri_faces,x.native_source_patches])).toEqual([
      ['eistute',1,1168,4],['book',1,4256,28],
    ]);
  expect(manifest.source_scene_bundle_sha256).toBe(sha.scene);
  expect(manifest.scientific_lod_qualified).toBe(false);
  return {scene,manifest};
}
function uploadFile(file:string) {
  return {name:basename(file), mimeType:file.endsWith('.svg')?
    'image/svg+xml':'application/json',buffer:readFileSync(file)};
}
test.beforeEach(()=>{
  // Mandatory CI must fail, not skip, if an original-source file is absent.
  test.skip(!sourceReady() && process.env.APMESH_V59_REQUIRED !== '1',
    'Original source reviewer fixture not present in ordinary local browser tests');
});

test('V5.9 actual P1 XYZ/UV linked face, staged rejection, native Eistute/Book IDs and exact SVG downloads',
async ({page})=>{
  test.setTimeout(220_000);
  const {scene,manifest}=pinned();
  const external:string[]=[];
  page.on('request',r=>{
    const url=new URL(r.url());
    if(['http:','https:'].includes(url.protocol) &&
       !['127.0.0.1','localhost'].includes(url.hostname)) external.push(r.url());
  });
  await page.goto('/');
  await expect(page.locator('.main-status')).toHaveText('Dados verificados');
  const xyz=page.getByTestId('viewport-xyz');
  const uv=page.getByTestId('viewport-uv');
  await expect(xyz.locator('canvas').first()).toBeVisible();
  await expect(uv.locator('canvas').first()).toBeVisible();
  const bounds=await uv.boundingBox();
  if(!bounds)throw Error('v59_missing_P1_uv_viewport');
  await uv.click({position:{x:bounds.width/2,y:bounds.height/2}});
  const sourceFace=await page.locator('.face-id').innerText();
  expect(sourceFace).toMatch(/^#\d+$/);
  await expect(page.getByTestId('selected-xyz')).toHaveText('Face '+sourceFace);
  await expect(page.getByTestId('selected-uv')).toHaveText('Face '+sourceFace);
  const q=await page.request.get('/api/v1/models/p1/quality');
  expect(q.status()).toBe(200);
  const originalFigure=await page.request.get('/api/v1/models/p1/publication.svg');
  expect(originalFigure.status()).toBe(200);
  const figure=await originalFigure.body();
  // Retain actual P1 vector bytes for independent cross-platform diff evidence.
  mkdirSync('test-results',{recursive:true});
  writeFileSync('test-results/v59-p1-source-uv.svg',figure);
  expect(originalFigure.headers()['x-vector-figure-sha256']).toBe(digest(figure));
  // Canonical source figure bytes must be identical across Linux and Windows.
  expect(digest(figure)).toBe('c4b759169bc68d147c70f8ae5a2127783e33299fe7ed3d35dca51610709d6bfe');
  expect(figure.toString('utf8')).not.toContain('<image');
  await page.getByTestId('model-select').selectOption('band');
  await expect(page.locator('.main-status')).toHaveText('Dados verificados');
  const staged=await page.request.get('/api/v1/models/band/publication.svg');
  expect(staged.headers()['x-source-status']).toBe('STAGED_UNACCEPTED');
  expect(await staged.text()).toContain('NOT AN ACCEPTED ADAPTIVE EPOCH');

  await page.getByTestId('v5-toggle-native-tri').click();
  await expect(page.getByTestId('r2720-panel')).toBeVisible();
  await page.getByTestId('r2720-import').setInputFiles({
    name:'AUTHENTIC_FROM_PINNED_CPP_RUN.json',
    mimeType:'application/json',buffer:readFileSync(scenePath),
  });
  await expect(page.getByTestId('r2720-tri-count')).toHaveText('1168');
  await page.getByTestId('v52-native-vector-import').setInputFiles(
    [manifestPath,...sourceSvg]);
  await expect(page.getByTestId('v52-native-vector-ready')).toBeVisible();
  await expect(page.getByTestId('v52-native-vector-error')).toHaveCount(0);
  const nativeImage=page.getByTestId('v52-native-vector-image');
  await expect.poll(()=>nativeImage.evaluate(img=>
    (img as HTMLImageElement).naturalWidth)).toBeGreaterThan(0);
  const checked=[];
  for(const [index,patch] of [[0,3],[1,27]] as const){
    const n=scene.scenes[index];
    await page.getByTestId('r2720-model').selectOption(String(index));
    await expect(page.getByTestId('r2720-tri-count'))
      .toHaveText(String(n.native_tri_faces));
    await expect(page.getByTestId('r2720-viewport-xyz'))
      .toHaveAttribute('data-native-accepted-faces',String(n.native_tri_faces));
    await page.getByTestId('r2720-patch').selectOption(String(patch));
    await expect(page.getByTestId('r2720-viewport-uv'))
      .toHaveAttribute('data-native-displayed-patch-slot',String(patch));
    await page.getByTestId('r2720-sample').focus();
    await page.keyboard.press('Home');
    const owner=scene.identity.documents[index].qualified_shared_source_curves[0]
      .sample_groups[0].members.find(m=>m.patch_slot===patch);
    expect(owner).toBeDefined();
    await expect(page.getByTestId('r2720-source-node-id'))
      .toHaveText(String(owner!.native_node_id));
    await page.getByTestId('r2720-highlight-source-sample').click();
    const elementId=Number(await page.getByTestId('r2720-native-element-id').innerText());
    expect(n.native_faces.some(f=>f[0]===patch && f[3]===elementId)).toBe(true);
    await expect(page.getByTestId('r2720-corners').locator('tbody tr')).toHaveCount(3);
    await expect(page.getByTestId('r2720-source-sha')).toHaveText(n.source_ndjson_sha256);
    const entry=manifest.figures.find((f:{model:string})=>f.model===n.model);
    expect(entry).toBeTruthy();
    await expect(page.getByTestId('v52-native-vector-sha')).toHaveText(entry.svg_sha256);
    await expect.poll(()=>nativeImage.evaluate(img=>
      (img as HTMLImageElement).naturalWidth)).toBeGreaterThan(0);
    const [download]=await Promise.all([
      page.waitForEvent('download'),
      page.getByTestId('v52-native-vector-download').click(),
    ]);
    expect(download.suggestedFilename()).toBe(n.model+'-accepted-step1-uv.svg');
    expect(digest(readFileSync(await download.path()))).toBe(entry.svg_sha256);
    checked.push({model:n.model,source_patch:patch,original_tri_faces:n.native_tri_faces,
      original_element_id:elementId,original_native_node_id:owner!.native_node_id,
      source_sha256:n.source_ndjson_sha256,vector_sha256:entry.svg_sha256});
  }
  expect(external).toEqual([]);
  const result={
    schema:'apmesh.meshstudio.v59.actual_original_reviewer_browser.v1',
    native_cpp_source_run:45147268663,
    native_source_tested_sha:'7d41ab8ec55b34bf879f9efc2a547168e50143de',
    original_scene_sha256:sha.scene,p1_source_face:sourceFace,
    p1_source_svg_sha256:digest(figure),staged_not_accepted_epoch:true,
    native_models:checked,external_requests:0,
    original_cpp_recompiled_in_this_browser:false,
    physical_gpu_qualified:false,scientific_lod_qualified:false,
  };
  mkdirSync('test-results',{recursive:true});
  writeFileSync('test-results/v59-original-reviewer.json',
    JSON.stringify(result,null,2)+'\n');
  console.log('V59_REAL_CPP_REVIEWER='+JSON.stringify(result));
});

test('V5.9 rejects forged real C++ source JSON, fabricated LOD and altered source vector',
async ({page})=>{
  test.setTimeout(180_000);
  pinned();
  await page.goto('/?nativeScene=1');
  const forged=JSON.parse(readFileSync(scenePath,'utf8'));
  forged.scenes[0].source_ndjson_sha256='f'.repeat(64);
  await page.getByTestId('r2720-import').setInputFiles({
    name:'FORGED_SOURCE.json',mimeType:'application/json',
    buffer:Buffer.from(JSON.stringify(forged)),
  });
  await expect(page.getByTestId('r2720-error')).toContainText('source_hash');
  await page.getByTestId('r2720-import').setInputFiles({
    name:'ORIGINAL_SOURCE.json',mimeType:'application/json',
    buffer:readFileSync(scenePath),
  });
  await expect(page.getByTestId('r2720-tri-count')).toHaveText('1168');
  const manifest=JSON.parse(readFileSync(manifestPath,'utf8'));
  await page.getByTestId('v52-native-vector-import').setInputFiles([
    {name:'manifest.json',mimeType:'application/json',
      buffer:Buffer.from(JSON.stringify({...manifest,scientific_lod_qualified:true}))},
    uploadFile(sourceSvg[0]),uploadFile(sourceSvg[1]),
  ]);
  await expect(page.getByTestId('v52-native-vector-error'))
    .toContainText('v52_manifest_not_bound_to_imported_original_native_scene');
  await expect(page.getByTestId('v52-native-vector-ready')).toHaveCount(0);
  const book=Buffer.from(readFileSync(sourceSvg[1]));
  const pos=book.indexOf(Buffer.from('data-original-native-node-ids'));
  expect(pos).toBeGreaterThan(0);
  book[pos]=0x78;
  await page.getByTestId('v52-native-vector-import').setInputFiles([
    uploadFile(manifestPath),uploadFile(sourceSvg[0]),
    {name:'book-accepted-step1-uv.svg',mimeType:'image/svg+xml',buffer:book},
  ]);
  await expect(page.getByTestId('v52-native-vector-error'))
    .toContainText('v52_native_original_vector_bytes_changed');
  await expect(page.getByTestId('v52-native-vector-ready')).toHaveCount(0);
});
