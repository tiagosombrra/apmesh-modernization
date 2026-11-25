import { useEffect, useMemo, useRef, useState } from 'react';
import { BezierSourceViewer, PATCH_COLORS } from './BezierSourceViewer';
import { evaluateCurve, exportCurveCSV, localParameter, MAX_BP_BYTES,
  parseBezierSource, patchSideParameters } from './bezierSource';
import type { BezierSource } from './bezierSource';
import exampleText from './fixtures/four_sheet_curved.bp?raw';

const EXAMPLE_SHA256 = 'b1b6610b63f10dfe91e84fc8de85d8cbb8b9bdb50a7b0ecdbc95efd89b64fdd4';
const EXAMPLE_URL = 'https://github.com/tiagosombrra/apmesh-modernization/blob/07ca312d01f960669b1dc09a2cb30b1aa9d03165/docs/research/nonmanifold-benchmark/fixtures/four_sheet_curved.bp';
const SIDE_NAMES = ['v = 0', 'u = 1', 'v = 1', 'u = 0'];

interface LoadedSource {
  model: BezierSource;
  name: string;
  sha256: string;
}

/** Local input inspection keeps declared control identity separate from native topology. */
export function BezierWorkspace({ active }: { active: boolean }) {
  const [loaded, setLoaded] = useState<LoadedSource | null>(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [curveId, setCurveId] = useState(0);
  const [patchId, setPatchId] = useState(0);
  const [side, setSide] = useState(0);
  const [parameter, setParameter] = useState(0.25);
  const [visible, setVisible] = useState<boolean[]>([]);
  const [sharedOnly, setSharedOnly] = useState(false);
  const requestRef = useRef(0);

  const loadBytes = async (bytes: ArrayBuffer, name: string, request: number, pinned = false) => {
    if (bytes.byteLength > MAX_BP_BYTES) throw new Error('The BP source exceeds the 2 MiB limit.');
    const text = new TextDecoder('utf-8', { fatal: true }).decode(bytes);
    const model = parseBezierSource(text);
    const digest = await crypto.subtle.digest('SHA-256', bytes);
    const sha256 = Array.from(new Uint8Array(digest), n => n.toString(16).padStart(2, '0')).join('');
    if (pinned && sha256 !== EXAMPLE_SHA256) throw new Error('The bundled example does not match its source reference.');
    if (request !== requestRef.current) return;
    const first = model.curves.reduce((best, value) => value.patchCount > best.patchCount ? value : best);
    setLoaded({ model, name, sha256 });
    setCurveId(first.id);
    setPatchId(first.incidences[0].patchId);
    setSide(first.incidences[0].side);
    setVisible(model.patches.map(() => true));
    setSharedOnly(first.patchCount > 1);
    setParameter(0.25);
  };

  const importSource = async (file?: File) => {
    const request = ++requestRef.current;
    setError(''); setLoaded(null); setLoading(true);
    try {
      if (file && file.size > MAX_BP_BYTES) throw new Error('The BP source exceeds the 2 MiB limit.');
      const bytes = file ? await file.arrayBuffer() : new TextEncoder().encode(exampleText).buffer;
      await loadBytes(bytes, file?.name ?? 'four_sheet_curved.bp', request, !file);
    } catch (reason) {
      if (request === requestRef.current) setError(reason instanceof Error ? reason.message : String(reason));
    } finally {
      if (request === requestRef.current) setLoading(false);
    }
  };

  useEffect(() => {
    void importSource();
    return () => { requestRef.current++; };
  }, []);

  const source = loaded?.model;
  const curve = source?.curves.find(item => item.id === curveId);
  const filtered = useMemo(() => source?.curves.filter(item => !sharedOnly || item.patchCount > 1) ?? [], [source, sharedOnly]);
  const incidence = curve?.incidences.find(item => item.patchId === patchId && item.side === side) ?? curve?.incidences[0];
  const localT = incidence ? localParameter(incidence, parameter) : 0;
  const uv = incidence ? patchSideParameters(incidence.side, localT) : [0, 0];
  let pointLabel = '';
  try {
    pointLabel = source && curve ? `C(t) = (${evaluateCurve(source, curve, parameter)
      .map(value => value.toPrecision(6)).join(', ')})` : '';
  } catch {
    // A numeric display limit must not destroy the source or its topology view.
    pointLabel = 'C(t) exceeds the finite numeric evaluation range. Normalized preview only.';
  }

  const selectCurve = (id: number) => {
    const next = source?.curves.find(item => item.id === id);
    if (!next) return;
    setCurveId(id);
    setPatchId(next.incidences[0].patchId);
    setSide(next.incidences[0].side);
  };
  const toggleShared = (checked: boolean) => {
    setSharedOnly(checked);
    if (checked && curve && curve.patchCount < 2) {
      const next = source?.curves.find(item => item.patchCount > 1);
      if (next) selectCurve(next.id);
    }
  };
  const exportCsv = () => {
    if (!loaded) return;
    const blob = new Blob([exportCurveCSV(loaded.model, loaded.sha256)], { type: 'text/csv;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = `bezier_source_${loaded.sha256.slice(0, 12)}_incidences.csv`;
    anchor.click();
    window.setTimeout(() => URL.revokeObjectURL(url), 0);
  };

  return <main className="bezier-workspace" aria-labelledby="bezier-title" data-testid="bezier-workspace">
    <div className="bezier-title-row"><div><div className="eyebrow">SOURCE GEOMETRY / BÉZIER</div>
      <h1 id="bezier-title">Explore the surface before the mesh</h1>
      <p>Inspect patches, shared control IDs and curve orientation in one workspace.</p></div>
      <span className="bezier-status">Source inspection</span></div>
    <div className="bezier-import-bar">
      <label className="bezier-file-button">Open .bp file
        <input type="file" accept=".bp,text/plain" data-testid="bezier-file" aria-label="Open Bézier BP source"
          onChange={event => { const file = event.target.files?.[0]; event.target.value = ''; if (file) void importSource(file); }} />
      </label>
      <button type="button" onClick={() => void importSource()} data-testid="bezier-load-example">Load Four-Sheet example</button>
      <span>Processed in this browser · up to 2 MiB / 128 patches</span>
      <button type="button" className="bezier-export" disabled={!loaded} onClick={exportCsv}
        data-testid="bezier-export">Export incidences CSV</button>
    </div>
    {loading && <div role="status" className="loading">Reading source and calculating its fingerprint…</div>}
    {error && <div className="error" role="alert" data-testid="bezier-error">Import rejected. {error}</div>}
    {loaded && source && curve && incidence && <>
      <div className="bezier-source-strip"><strong data-testid="bezier-filename">{loaded.name}</strong>
        <span data-testid="bezier-provenance">{loaded.sha256 === EXAMPLE_SHA256 ? 'Matches the Four-Sheet reference' : 'Local source · fingerprint calculated'}</span>
        <details><summary>Source identity</summary><code data-testid="bezier-sha256">{loaded.sha256}</code>
          {loaded.sha256 === EXAMPLE_SHA256 && <a href={EXAMPLE_URL} target="_blank" rel="noreferrer">View the pinned source</a>}
          <p>The fingerprint identifies these bytes. A local upload does not attest a native generator run.</p></details></div>
      <div className="bezier-metrics" aria-label="Source inventory">
        <div><span>CONTROL POINTS</span><strong data-testid="bezier-control-count">{source.controls.length}</strong></div>
        <div><span>PATCHES</span><strong data-testid="bezier-patch-count">{source.patches.length}</strong></div>
        <div><span>DECLARED CURVES</span><strong data-testid="bezier-curve-count">{source.curves.length}</strong></div>
        <div><span>MAX. DISTINCT PATCHES / CURVE</span><strong data-testid="bezier-max-incidence">{Math.max(...source.curves.map(item => item.patchCount))}</strong></div>
      </div>
      <div className="bezier-layout">
        <aside className="bezier-controls"><h2>Patch visibility</h2>
          <div className="bezier-patches">{source.patches.map((_patch, id) => <label key={id}>
            <input type="checkbox" checked={visible[id] ?? false} data-testid={`bezier-patch-${id}`}
              onChange={() => setVisible(values => values.map((value, index) => index === id ? !value : value))} />
            <span className="bezier-swatch" style={{ background: PATCH_COLORS[id % PATCH_COLORS.length] }} />
            Patch {id}</label>)}</div>
          <div className="section-break" />
          <h2>Declared curves</h2>
          <label className="bezier-shared-filter"><input type="checkbox" checked={sharedOnly}
            disabled={!source.curves.some(item => item.patchCount > 1)} onChange={event => toggleShared(event.target.checked)} /> Shared only</label>
          <label htmlFor="bezier-curve-select" className="sr-only">Selected declared curve</label>
          <select id="bezier-curve-select" data-testid="bezier-curve-select" value={curveId}
            onChange={event => selectCurve(Number(event.target.value))}>
            {filtered.map(item => <option value={item.id} key={item.id}>C{item.id} · {item.patchCount} {item.patchCount === 1 ? 'patch' : 'patches'}</option>)}
          </select>
          <p className="bezier-control-ids">Controls <code data-testid="bezier-curve-controls">{curve.controlIds.join(' → ')}</code></p>
          <p className="small-note">Curves share identity only when their four declared control IDs match, in either order. Equal XYZ coordinates stay distinct.</p>
        </aside>
        <div className="bezier-center"><BezierSourceViewer source={source} curve={curve} parameter={parameter}
          visible={visible} selectedPatch={patchId} active={active} />
          <div className="bezier-parameter"><label htmlFor="bezier-parameter">Canonical parameter <strong>t = <output data-testid="bezier-t">{parameter.toFixed(2)}</output></strong></label>
            <input id="bezier-parameter" data-testid="bezier-parameter" type="range" min="0" max="1" step="0.01"
              value={parameter} onChange={event => setParameter(Number(event.target.value))} />
            <div className="bezier-parameter-endpoints"><span>0 · control {curve.controlIds[0]}</span><span>1 · control {curve.controlIds[3]}</span></div>
            <div className="bezier-point" data-testid="bezier-point">{pointLabel}</div>
          </div>
        </div>
        <aside className="bezier-inspector"><h2>Curve C{curve.id}</h2>
          <p className="bezier-incidence-count"><strong>{curve.patchCount}</strong> distinct {curve.patchCount === 1 ? 'patch' : 'patches'} · {curve.incidences.length} sides</p>
          <div className="bezier-incidence-table"><table><thead><tr><th>Patch / side</th><th>Direction</th><th>Local t</th></tr></thead>
            <tbody>{curve.incidences.map(item => <tr key={`${item.patchId}-${item.side}`} data-selected={item.patchId === patchId && item.side === side}
              data-testid={`bezier-incidence-${item.patchId}-${item.side}`}>
              <td><button type="button" onClick={() => { setPatchId(item.patchId); setSide(item.side); }}>P{item.patchId} · {SIDE_NAMES[item.side]}</button></td>
              <td>{item.orientationAmbiguous ? 'Ambiguous' : item.reversed ? 'Reversed' : 'Forward'}</td>
              <td>{localParameter(item, parameter).toFixed(2)}</td>
            </tr>)}</tbody></table></div>
          <div className="bezier-uv-heading"><h3>Patch {incidence.patchId} · UV</h3><span data-testid="bezier-local-t">local t = {localT.toFixed(2)}</span></div>
          <svg className="bezier-uv" viewBox="0 0 220 210" role="img" aria-label={`Patch ${incidence.patchId} UV chart, ${SIDE_NAMES[incidence.side]}`}>
            <rect x="35" y="20" width="155" height="155" fill="#10222f" stroke="#436174" />
            {[0.25, 0.5, 0.75].map(value => <g key={value} stroke="#263f50"><line x1={35 + value * 155} y1="20" x2={35 + value * 155} y2="175" />
              <line x1="35" y1={175 - value * 155} x2="190" y2={175 - value * 155} /></g>)}
            {(() => { const a = patchSideParameters(incidence.side, 0); const b = patchSideParameters(incidence.side, 1);
              return <line x1={35 + a[0] * 155} y1={175 - a[1] * 155} x2={35 + b[0] * 155} y2={175 - b[1] * 155} stroke="#ffdb7a" strokeWidth="4" />; })()}
            <circle cx={35 + uv[0] * 155} cy={175 - uv[1] * 155} r="6" fill="#ff785e" />
            <text x="110" y="200">u →</text><text x="9" y="105">v ↑</text>
            <text x="27" y="190">0</text><text x="187" y="190">1</text><text x="20" y="25">1</text>
          </svg>
          <p className="small-note">{incidence.orientationAmbiguous ? 'The control sequence is palindromic; direction is ambiguous. The displayed parameter uses the forward convention.' : incidence.reversed ? 'This side runs against the canonical curve: local t = 1 − t.' : 'This side follows the canonical curve: local t = t.'}</p>
        </aside>
      </div>
      <div className="bezier-scope"><strong>What this view represents</strong><p>Sampled Bézier surfaces and topology declared by BP control IDs.
        Display triangles are only a rendering approximation. Native accepted meshes remain in <b>Original TRI</b>.
        The native loader may resolve geometry differently; this inventory does not assert its post-load topology.</p></div>
    </>}
  </main>;
}
