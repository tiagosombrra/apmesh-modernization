import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readFileSync } from 'node:fs';
import { createRequire } from 'node:module';
import { test } from 'node:test';

// Compile the pure module with the same retained compiler used by other contracts.
const require = createRequire(import.meta.url);
const ts = require('@typescript/typescript6');
const moduleText = readFileSync(new URL('../src/bezierSource.ts', import.meta.url), 'utf8');
const compiled = ts.transpileModule(moduleText, {
  compilerOptions: { target: ts.ScriptTarget.ES2022, module: ts.ModuleKind.ESNext },
  reportDiagnostics: true,
});
assert.deepEqual((compiled.diagnostics ?? []).filter((entry) => entry.category === ts.DiagnosticCategory.Error), []);
const api = await import(`data:text/javascript;base64,${Buffer.from(compiled.outputText).toString('base64')}`);
const { parseBezierSource, evaluatePatch, evaluateCurve, localParameter,
  patchSideParameters, exportCurveCSV, MAX_BP_BYTES, MAX_BP_PATCHES, MAX_BP_CONTROLS } = api;
const fixtureBytes = readFileSync(new URL('../src/fixtures/four_sheet_curved.bp', import.meta.url));
const fixture = fixtureBytes.toString('utf8');
const fixtureSha = 'b1b6610b63f10dfe91e84fc8de85d8cbb8b9bdb50a7b0ecdbc95efd89b64fdd4';

function sourceText(controls, patches) {
  return `${controls.map((point) => `v ${point.join(' ')}`).join('\n')}\n${patches.map((patch) => `p ${patch.join(' ')}`).join('\n')}\n`;
}

function close(actual, expected, tolerance = 3e-12) {
  assert.equal(actual.length, expected.length);
  for (let i = 0; i < expected.length; i += 1) {
    assert.ok(Math.abs(actual[i] - expected[i]) <= tolerance,
      `${actual[i]} differs from ${expected[i]} at coordinate ${i}`);
  }
}

const flatControls = Array.from({ length: 16 }, (_, index) => [index % 4, Math.floor(index / 4), 0]);
const flatPatch = Array.from({ length: 16 }, (_, index) => index);
const flat = sourceText(flatControls, [flatPatch]);

test('the authored Four-Sheet fixture retains the original source bytes', () => {
  assert.equal(createHash('sha256').update(fixtureBytes).digest('hex'), fixtureSha);
  const source = parseBezierSource(fixture);
  assert.equal(source.topologyBasis, 'DECLARED_BP_CONTROL_IDS');
  assert.equal(source.controls.length, 52);
  assert.equal(source.patches.length, 4);
  assert.equal(source.curves.length, 13);
  assert.deepEqual(source.incidenceHistogram, { 1: 12, 4: 1 });
  const shared = source.curves.find((curve) => curve.patchCount === 4);
  assert.deepEqual(shared.controlIds, [0, 1, 2, 3]);
  assert.deepEqual(shared.incidences.map(({ patchId, side, reversed }) => ({ patchId, side, reversed })), [
    { patchId: 0, side: 3, reversed: false }, { patchId: 1, side: 3, reversed: true },
    { patchId: 2, side: 3, reversed: false }, { patchId: 3, side: 3, reversed: false },
  ]);
});

test('independent affine formula distinguishes u and v and checks all four corners', () => {
  const affine = (u, v) => [3 + 2 * u + 5 * v, -7 - u + 4 * v, 1 + 9 * u - 2 * v];
  const controls = Array.from({ length: 16 }, (_, index) => affine((index % 4) / 3, Math.floor(index / 4) / 3));
  const source = parseBezierSource(sourceText(controls, [flatPatch]));
  for (const u of [0, 0.1, 0.37, 0.83, 1]) {
    for (const v of [0, 0.21, 0.64, 1]) close(evaluatePatch(source, 0, u, v), affine(u, v));
  }
  close(evaluatePatch(source, 0, 1, 0), controls[3]);
  close(evaluatePatch(source, 0, 0, 1), controls[12]);
});

test('independent curved polynomial and sheet directions match the authored surface', () => {
  const source = parseBezierSource(fixture);
  const direction = [[0, 5], [-5, 0], [5, 0], [0, -5]];
  for (let patchId = 0; patchId < 4; patchId += 1) {
    for (const u of [0, 0.09, 0.4, 0.73, 1]) {
      for (const v of [0, 0.07, 0.29, 0.61, 0.89, 1]) {
        const t = patchId === 1 ? 1 - v : v;
        const expected = [0.4 * t * (1 - t) + u * direction[patchId][0],
          0.3 * t * (1 - t) * (2 * t - 1) + u * direction[patchId][1], -2.5 + 5 * t];
        close(evaluatePatch(source, patchId, u, v), expected);
      }
    }
  }
});

test('all four side coordinates and reversed incidences refer to their own patch boundary', () => {
  assert.deepEqual(patchSideParameters(0, 0.25), [0.25, 0]);
  assert.deepEqual(patchSideParameters(1, 0.25), [1, 0.25]);
  assert.deepEqual(patchSideParameters(2, 0.25), [0.25, 1]);
  assert.deepEqual(patchSideParameters(3, 0.25), [0, 0.25]);
  const source = parseBezierSource(fixture);
  for (const curve of source.curves) {
    for (const incidence of curve.incidences) {
      for (const t of [0, 0.13, 0.37, 0.8, 1]) {
        const [u, v] = patchSideParameters(incidence.side, localParameter(incidence, t));
        close(evaluatePatch(source, incidence.patchId, u, v), evaluateCurve(source, curve, t));
      }
    }
  }
  const shared = source.curves.find((curve) => curve.patchCount === 4);
  const wrongSameLocalParameter = evaluatePatch(source, 1, 0, 0.2);
  assert.ok(Math.abs(wrongSameLocalParameter[2] - evaluateCurve(source, shared, 0.2)[2]) > 2);
});

test('equal XYZ at different control IDs does not fabricate a shared source curve', () => {
  const original = parseBezierSource(fixture);
  const controls = [...original.controls, ...original.controls.slice(0, 4)];
  const patches = original.patches.map((patch) => [...patch]);
  patches[1] = patches[1].map((id) => id < 4 ? id + 52 : id);
  const duplicated = parseBezierSource(sourceText(controls, patches));
  assert.equal(duplicated.controls.length, 56);
  assert.equal(duplicated.curves.length, 14);
  assert.deepEqual(duplicated.incidenceHistogram, { 1: 13, 3: 1 });
  for (const t of [0, 0.2, 0.8, 1]) {
    close(evaluatePatch(original, 1, 0.2, t), evaluatePatch(duplicated, 1, 0.2, t));
  }
});

test('canonical orientation compares numeric tuples rather than decimal strings', () => {
  const patch = [...flatPatch];
  patch.splice(0, 4, 2, 10, 11, 13);
  const source = parseBezierSource(sourceText(flatControls, [patch]));
  assert.deepEqual(source.curves[0].controlIds, [2, 10, 11, 13]);
  assert.equal(source.curves[0].incidences[0].reversed, false);
});

test('repeated sides on one patch count one owner and palindromic direction is explicit', () => {
  const source = parseBezierSource(sourceText([[2, -3, 8]], [Array(16).fill(0)]));
  assert.equal(source.curves.length, 1);
  assert.equal(source.curves[0].incidences.length, 4);
  assert.equal(source.curves[0].patchCount, 1);
  assert.equal(source.curves[0].orientationAmbiguous, true);
  assert.ok(source.curves[0].incidences.every((incidence) => incidence.orientationAmbiguous));
  assert.deepEqual(source.incidenceHistogram, { 1: 1 });
  close(evaluatePatch(source, 0, 0.41, 0.73), [2, -3, 8]);
});

test('all 15 patch subsets retain declared ownership and P1 orientation', () => {
  const original = parseBezierSource(fixture);
  for (let mask = 1; mask < 16; mask += 1) {
    const selected = [0, 1, 2, 3].filter((id) => mask & (1 << id));
    const source = parseBezierSource(sourceText(original.controls, selected.map((id) => original.patches[id])));
    const central = source.curves.find((curve) => curve.controlIds.join(',') === '0,1,2,3');
    assert.equal(source.curves.length, 3 * selected.length + 1);
    assert.equal(central.patchCount, selected.length);
    assert.deepEqual(central.incidences.filter((incidence) => incidence.reversed).map((incidence) => selected[incidence.patchId]),
      selected.includes(1) ? [1] : []);
  }
});

test('BOM, CRLF, whitespace, comments and decimal scientific notation are accepted', () => {
  const source = parseBezierSource(`\uFEFF# file comment\r\n\t// another comment\r\n${flat.replace(/\n/g, '\r\n').replace('v 0 0 0', '  v +0.0 .0 -0e3 # inline comment')}`);
  assert.equal(source.patches.length, 1);
  assert.deepEqual(source.controls[0].map((value) => value + 0), [0, 0, 0]);
});

test('malformed, non-finite, partial and unsupported records are rejected', () => {
  for (const text of ['', '// only a comment', 'v 0 0 0', flat.replace('v 0 0 0', 'v 0 0'),
    flat.replace('v 0 0 0', 'v 0 0 0 1'), flat.replace('v 0 0 0', 'v NaN 0 0'),
    flat.replace('v 0 0 0', 'v Infinity 0 0'), flat.replace('v 0 0 0', 'v 1e999 0 0'),
    flat.replace('v 0 0 0', 'v 0x10 0 0'), flat.replace('p 0', 'p -1'),
    flat.replace('p 0', 'p 0.5'), flat.replace('p 0', 'p 0e0'),
    flat.replace('p 0', 'p 16'), flat.replace('p 0', 'p 9007199254740992'),
    flat.replace(' 15\n', '\n'), `${flat}f 0 1 2\n`, `${flat}p 0 1\n`,
    `p ${flatPatch.join(' ')}\n${flat}`]) {
    assert.throws(() => parseBezierSource(text), /BP/);
  }
});

test('file, control and patch limits reject excess and accept their exact boundary', () => {
  const exactBytes = `//${'x'.repeat(MAX_BP_BYTES - Buffer.byteLength(flat) - 3)}\n${flat}`;
  assert.equal(Buffer.byteLength(exactBytes), MAX_BP_BYTES);
  assert.equal(parseBezierSource(exactBytes).patches.length, 1);
  assert.throws(() => parseBezierSource('// ' + 'x'.repeat(MAX_BP_BYTES)), /2 MiB/);
  assert.throws(() => parseBezierSource('// ' + 'é'.repeat(MAX_BP_BYTES / 2)), /2 MiB/);
  const controls = Array(MAX_BP_CONTROLS).fill('v 0 0 0\n').join('');
  const patch = `p ${flatPatch.join(' ')}\n`;
  assert.equal(parseBezierSource(controls + patch).controls.length, MAX_BP_CONTROLS);
  assert.throws(() => parseBezierSource(controls + 'v 0 0 0\n' + patch), /20000/);
  const vertices = flat.slice(0, flat.indexOf('p '));
  assert.equal(parseBezierSource(vertices + patch.repeat(MAX_BP_PATCHES)).patches.length, MAX_BP_PATCHES);
  assert.throws(() => parseBezierSource(vertices + patch.repeat(MAX_BP_PATCHES + 1)), /128/);
});

test('evaluators reject out-of-domain parameters and unknown identities', () => {
  const source = parseBezierSource(flat);
  for (const value of [NaN, Infinity, -0.01, 1.01]) {
    assert.throws(() => evaluatePatch(source, 0, value, 0.5), /parameters/);
    assert.throws(() => evaluatePatch(source, 0, 0.5, value), /parameters/);
    assert.throws(() => evaluateCurve(source, source.curves[0], value), /parameters/);
    assert.throws(() => patchSideParameters(0, value), /parameters/);
    assert.throws(() => localParameter(source.curves[0].incidences[0], value), /parameters/);
  }
  for (const patchId of [-1, 0.5, 1, NaN]) assert.throws(() => evaluatePatch(source, patchId, 0, 0), /patch index/);
  assert.throws(() => patchSideParameters(4, 0.5), /patch side/);
});

test('CSV includes the exact source identity and explicit source-only topology semantics', () => {
  const source = parseBezierSource(fixture);
  const csv = exportCurveCSV(source, fixtureSha);
  const rows = csv.trimEnd().split('\n');
  assert.equal(rows.length, 17);
  assert.equal(rows[0], 'source_sha256,topology_basis,curve_id,control_ids,patch_count,patch_id,side,reversed,orientation_ambiguous');
  assert.ok(rows.slice(1).every((row) => row.startsWith(`${fixtureSha},DECLARED_BP_CONTROL_IDS,`)));
  assert.equal(rows.filter((row) => row.includes(',0 1 2 3,4,')).length, 4);
  assert.ok(rows.some((row) => row.includes(',0 1 2 3,4,1,3,true,false')));
  assert.equal(exportCurveCSV(source, fixtureSha), csv);
  assert.throws(() => exportCurveCSV(source, 'unverified'), /SHA-256/);
});
