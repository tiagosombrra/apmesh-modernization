import { expect, test } from '@playwright/test';
import { createHash } from 'node:crypto';
import { existsSync, readFileSync, readdirSync } from 'node:fs';
import { join, resolve } from 'node:path';

/** These tests load actual C++ same-run original accepted source artifacts.
 * Missing artifacts skip local dev only; CI separately requires their presence.
 */
const root = resolve(process.cwd(), '../../../build');
const scenePath = join(root, 'r2720-native-accepted-scene.json');
const packageRoot = join(root, 'v52-native-publication-artifact');
const candidates = [
  join(packageRoot, 'v52-native-accepted-uv-publication'),
  join(packageRoot, 'build', 'v52-native-accepted-uv-publication'),
  packageRoot,
];
const packageDir = candidates.find(path =>
  existsSync(join(path, 'manifest.json'))) ?? candidates[0];

function ready() {
  return existsSync(scenePath) &&
    existsSync(join(packageDir, 'manifest.json')) &&
    existsSync(join(packageDir, 'eistute-accepted-step1-uv.svg')) &&
    existsSync(join(packageDir, 'book-accepted-step1-uv.svg'));
}

async function importScene(page: import('@playwright/test').Page) {
  await page.goto('/?nativeScene=1');
  await page.getByTestId('r2720-import').setInputFiles({
    name: 'R2720_ORIGINAL_NATIVE_ACCEPTED_FROM_SAME_CPP_RUN.json',
    mimeType: 'application/json',
    buffer: readFileSync(scenePath),
  });
  await expect(page.getByTestId('r2720-tri-count')).toHaveText('1168');
}

function filenames() {
  return ['manifest.json', 'eistute-accepted-step1-uv.svg',
    'book-accepted-step1-uv.svg'].map(name => join(packageDir, name));
}

test('V5.2 actual compiled C++ Eistute and Book original accepted patch UV vector figures load, preview and download', async ({page}) => {
  test.skip(!ready(), 'Real original native C++ same-run SVG inputs not available in local dev');
  test.setTimeout(180_000);
  const raw = readFileSync(scenePath);
  const original = JSON.parse(raw.toString('utf8'));
  const manifest = JSON.parse(readFileSync(filenames()[0], 'utf8'));
  expect(original.scenes.map((s:{model:string,accepted_native_step:number}) =>
    s.model + ':' + s.accepted_native_step)).toEqual(['eistute:1', 'book:1']);
  expect(manifest.source_scene_bundle_sha256).toBe(
    createHash('sha256').update(raw).digest('hex'));
  expect(manifest.figures.map((f:{original_native_tri_faces:number}) =>
    f.original_native_tri_faces)).toEqual([4256,1168]);

  await importScene(page);
  await page.getByTestId('v52-native-vector-import').setInputFiles(filenames());
  await expect(page.getByTestId('v52-native-vector-ready')).toBeVisible();
  await expect(page.getByTestId('v52-native-vector-error')).toHaveCount(0);
  const image = page.getByTestId('v52-native-vector-image');
  await expect.poll(async () => image.evaluate(img =>
    (img as HTMLImageElement).naturalWidth)).toBeGreaterThan(0);
  await expect(page.getByTestId('v52-native-vector-sha')).toHaveText(
    manifest.figures.find((f:{model:string})=>f.model==='eistute').svg_sha256);

  const [download] = await Promise.all([
    page.waitForEvent('download'),
    page.getByTestId('v52-native-vector-download').click(),
  ]);
  expect(download.suggestedFilename()).toBe('eistute-accepted-step1-uv.svg');

  await page.getByTestId('r2720-model').selectOption('1');
  await expect(page.getByTestId('r2720-tri-count')).toHaveText('4256');
  await expect(page.getByTestId('v52-native-vector-sha')).toHaveText(
    manifest.figures.find((f:{model:string})=>f.model==='book').svg_sha256);
  await expect.poll(async () => image.evaluate(img =>
    (img as HTMLImageElement).naturalWidth)).toBeGreaterThan(0);
  const book = await Promise.all([
    page.waitForEvent('download'),
    page.getByTestId('v52-native-vector-download').click(),
  ]);
  expect(book[0].suggestedFilename()).toBe('book-accepted-step1-uv.svg');
});

test('V5.2 original native C++ source figure refuses forged LOD, corrupted SVG and mismatched scene SHA', async ({ page }) => {
  test.skip(!ready(), 'Real native C++ source publication CI artifacts missing locally');
  test.setTimeout(180_000);
  await importScene(page);
  const files = filenames();
  const original = JSON.parse(readFileSync(files[0], 'utf8'));
  const forged = {...original, scientific_lod_qualified: true};
  await page.getByTestId('v52-native-vector-import').setInputFiles([
    {name:'manifest.json', mimeType:'application/json',
      buffer:Buffer.from(JSON.stringify(forged))},
    files[1], files[2],
  ]);
  await expect(page.getByTestId('v52-native-vector-error'))
    .toContainText('v52_manifest_not_bound_to_imported_original_native_scene');
  await expect(page.getByTestId('v52-native-vector-ready')).toHaveCount(0);

  const wrongSvg = Buffer.from(readFileSync(files[1]));
  const needle = Buffer.from('data-original-native-node-ids');
  const index = wrongSvg.indexOf(needle);
  expect(index).toBeGreaterThan(0);
  wrongSvg[index] = 0x78;
  await page.getByTestId('v52-native-vector-import').setInputFiles([
    files[0],
    {name:'eistute-accepted-step1-uv.svg', mimeType:'image/svg+xml',
      buffer:wrongSvg},
    files[2],
  ]);
  await expect(page.getByTestId('v52-native-vector-error'))
    .toContainText('v52_native_original_vector_bytes_changed');
  await expect(page.getByTestId('v52-native-vector-ready')).toHaveCount(0);

  const mismatched = {...original, source_scene_bundle_sha256:'0'.repeat(64)};
  await page.getByTestId('v52-native-vector-import').setInputFiles([
    {name:'manifest.json',mimeType:'application/json',
      buffer:Buffer.from(JSON.stringify(mismatched))},
    files[1], files[2],
  ]);
  await expect(page.getByTestId('v52-native-vector-error'))
    .toContainText('v52_manifest_not_bound_to_imported_original_native_scene');
  await expect(page.getByTestId('v52-native-vector-ready')).toHaveCount(0);
});
