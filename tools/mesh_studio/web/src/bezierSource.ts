/** Read-only inspection of control identities declared by an indexed BP source. */
export type Point3 = [number, number, number];
export type PatchSide = 0 | 1 | 2 | 3;

export interface BezierIncidence {
  patchId: number;
  side: PatchSide;
  reversed: boolean;
  orientationAmbiguous: boolean;
}

export interface BezierCurve {
  id: number;
  controlIds: number[];
  incidences: BezierIncidence[];
  patchCount: number;
  orientationAmbiguous: boolean;
}

export interface BezierSource {
  controls: Point3[];
  patches: number[][];
  curves: BezierCurve[];
  incidenceHistogram: Record<number, number>;
  topologyBasis: 'DECLARED_BP_CONTROL_IDS';
}

export const MAX_BP_BYTES = 2 * 1024 * 1024;
export const MAX_BP_PATCHES = 128;
export const MAX_BP_CONTROLS = 20000;

// The native reader uses p00, p10, p20, p30, p01, ...: u varies fastest.
const SIDE_INDICES = [
  [0, 1, 2, 3], [3, 7, 11, 15], [12, 13, 14, 15], [0, 4, 8, 12],
] as const;
const DECIMAL = /^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?$/;
const INDEX = /^\d+$/;

function inputError(line: number, message: string): never {
  throw new Error(`BP line ${line}: ${message}`);
}

/**
 * Parse the bounded indexed, non-rational bicubic BP profile.
 * Coordinates never determine control or curve identity. This intentionally
 * does not reproduce the native loader's coordinate-interning policy.
 */
export function parseBezierSource(text: string): BezierSource {
  // A string-length screen avoids allocating another copy of clearly huge input.
  if (text.length > MAX_BP_BYTES || new TextEncoder().encode(text).byteLength > MAX_BP_BYTES) {
    throw new Error('BP input exceeds the 2 MiB inspection limit.');
  }
  const controls: Point3[] = [];
  const patches: number[][] = [];
  const lines = text.replace(/^\uFEFF/, '').split(/\r?\n/);
  for (let lineIndex = 0; lineIndex < lines.length; lineIndex += 1) {
    const line = lines[lineIndex].split(/\/\/|#/, 1)[0].trim();
    if (!line) continue;
    const [tag, ...fields] = line.split(/\s+/);
    const lineNumber = lineIndex + 1;
    if (tag === 'v') {
      if (fields.length !== 3) inputError(lineNumber, 'a vertex requires exactly three coordinates.');
      if (controls.length >= MAX_BP_CONTROLS) {
        inputError(lineNumber, `more than ${MAX_BP_CONTROLS} control points are not supported.`);
      }
      const values = fields.map((value) => DECIMAL.test(value) ? Number(value) : NaN);
      if (!values.every(Number.isFinite)) inputError(lineNumber, 'coordinates must be finite decimal numbers.');
      controls.push(values as Point3);
    } else if (tag === 'p') {
      if (fields.length !== 16) inputError(lineNumber, 'a bicubic patch requires exactly 16 control indices.');
      if (patches.length >= MAX_BP_PATCHES) {
        inputError(lineNumber, `more than ${MAX_BP_PATCHES} patches are not supported.`);
      }
      const indices = fields.map((value) => INDEX.test(value) ? Number(value) : NaN);
      if (!indices.every((value) => Number.isSafeInteger(value) && value >= 0 && value < controls.length)) {
        inputError(lineNumber, 'indices must be zero-based integers referencing preceding control points.');
      }
      patches.push(indices);
    } else {
      inputError(lineNumber, `unsupported record "${tag.slice(0, 40)}"; expected v or p.`);
    }
  }
  if (!controls.length || !patches.length) throw new Error('BP input must contain control points and at least one bicubic patch.');

  const curves: BezierCurve[] = [];
  const groups = new Map<string, BezierCurve>();
  patches.forEach((patch, patchId) => {
    SIDE_INDICES.forEach((sideIndices, side) => {
      const localIds = sideIndices.map((index) => patch[index]);
      const reverseIds = [...localIds].reverse();
      let comparison = 0;
      for (let index = 0; index < 4 && comparison === 0; index += 1) {
        comparison = localIds[index] - reverseIds[index];
      }
      // Compare integer tuples, not their decimal string representations.
      const reversed = comparison > 0;
      const controlIds = reversed ? reverseIds : localIds;
      const orientationAmbiguous = comparison === 0;
      const key = controlIds.join(',');
      let curve = groups.get(key);
      if (!curve) {
        curve = { id: curves.length, controlIds, incidences: [], patchCount: 0, orientationAmbiguous };
        groups.set(key, curve);
        curves.push(curve);
      }
      curve.incidences.push({ patchId, side: side as PatchSide, reversed, orientationAmbiguous });
    });
  });
  const incidenceHistogram: Record<number, number> = {};
  for (const curve of curves) {
    // Two sides on one patch are two uses, but still only one owning patch.
    curve.patchCount = new Set(curve.incidences.map((incidence) => incidence.patchId)).size;
    incidenceHistogram[curve.patchCount] = (incidenceHistogram[curve.patchCount] ?? 0) + 1;
  }
  return { controls, patches, curves, incidenceHistogram, topologyBasis: 'DECLARED_BP_CONTROL_IDS' };
}

function parameter(value: number): number {
  if (!Number.isFinite(value) || value < 0 || value > 1) {
    throw new Error('Bezier parameters must be finite numbers in [0, 1].');
  }
  return value;
}

function bernstein(value: number): [number, number, number, number] {
  const t = parameter(value);
  const s = 1 - t;
  return [s * s * s, 3 * t * s * s, 3 * t * t * s, t * t * t];
}

function finiteResult(point: Point3): Point3 {
  if (!point.every(Number.isFinite)) throw new Error('Bezier evaluation exceeded the finite numeric range.');
  return point;
}

/** Evaluate a bicubic source patch; no sample is a generated mesh vertex. */
export function evaluatePatch(source: BezierSource, patchId: number, u: number, v: number): Point3 {
  if (!Number.isInteger(patchId) || patchId < 0 || patchId >= source.patches.length) {
    throw new Error('Unknown BP patch index.');
  }
  const bu = bernstein(u);
  const bv = bernstein(v);
  const patch = source.patches[patchId];
  const result: Point3 = [0, 0, 0];
  for (let j = 0; j < 4; j += 1) {
    for (let i = 0; i < 4; i += 1) {
      const point = source.controls[patch[4 * j + i]];
      const weight = bu[i] * bv[j];
      for (let coordinate = 0; coordinate < 3; coordinate += 1) {
        result[coordinate] += weight * point[coordinate];
      }
    }
  }
  return finiteResult(result);
}

/** Evaluate the numerically canonical control sequence of one source curve. */
export function evaluateCurve(source: BezierSource, curve: BezierCurve, t: number): Point3 {
  const weights = bernstein(t);
  const result: Point3 = [0, 0, 0];
  if (curve.controlIds.length !== 4) throw new Error('A BP boundary curve requires four control indices.');
  for (let index = 0; index < 4; index += 1) {
    const point = source.controls[curve.controlIds[index]];
    if (!point) throw new Error('Unknown BP curve control index.');
    for (let coordinate = 0; coordinate < 3; coordinate += 1) {
      result[coordinate] += weights[index] * point[coordinate];
    }
  }
  return finiteResult(result);
}

export function localParameter(incidence: BezierIncidence, t: number): number {
  const value = parameter(t);
  // A palindromic control sequence has no distinguishable direction by IDs.
  return incidence.reversed ? 1 - value : value;
}

export function patchSideParameters(side: PatchSide, t: number): [number, number] {
  const value = parameter(t);
  switch (side) {
    case 0: return [value, 0];
    case 1: return [1, value];
    case 2: return [value, 1];
    case 3: return [0, value];
    default: throw new Error('Unknown BP patch side.');
  }
}

/** Export declared source incidence, without making a native-mesh claim. */
export function exportCurveCSV(source: BezierSource, sha256: string): string {
  if (!/^[a-f0-9]{64}$/i.test(sha256)) throw new Error('A complete source SHA-256 is required for export.');
  const rows = ['source_sha256,topology_basis,curve_id,control_ids,patch_count,patch_id,side,reversed,orientation_ambiguous'];
  for (const curve of source.curves) {
    for (const incidence of curve.incidences) {
      rows.push([sha256.toLowerCase(), source.topologyBasis, curve.id,
        curve.controlIds.join(' '), curve.patchCount, incidence.patchId,
        incidence.side, incidence.reversed, incidence.orientationAmbiguous].join(','));
    }
  }
  return `${rows.join('\n')}\n`;
}
