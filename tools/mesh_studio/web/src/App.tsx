import { useEffect, useMemo, useRef, useState } from 'react';
import { studyApi } from './api';
import { Viewer } from './Viewer';
import type { ViewerHandle } from './Viewer';
import { CAMERA_SCHEMA, parseCameraRecipe, storageKey } from './camera';
import type { FaceDetail, MeshGeometry, ModelEntry } from './contracts';
import './style.css';

const statuses: Record<string, string> = {
  CONTROLLED_PHYSICAL_GENERATION: 'P1 · Execução controlada',
  STAGED_UNACCEPTED: 'Candidata real · Não aceita',
};

export default function App() {
  const [catalog, setCatalog] = useState<ModelEntry[]>([]);
  const [modelId, setModelId] = useState('p1');
  const [xyz, setXyz] = useState<MeshGeometry | null>(null);
  const [uv, setUv] = useState<MeshGeometry | null>(null);
  const [detail, setDetail] = useState<FaceDetail | null>(null);
  const [selected, setSelected] = useState<number | null>(null);
  const [showTri, setShowTri] = useState(true);
  const [showQuad, setShowQuad] = useState(true);
  const [edges, setEdges] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [cameraStatus, setCameraStatus] = useState('');
  const xyzRef = useRef<ViewerHandle>(null);
  const uvRef = useRef<ViewerHandle>(null);
  const model = useMemo(() => catalog.find((item) => item.id === modelId), [catalog, modelId]);

  useEffect(() => {
    studyApi.catalog().then((data) => setCatalog(data.models))
      .catch((e: Error) => setError(e.message));
  }, []);
  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    setXyz(null); setUv(null); setSelected(null); setDetail(null); setCameraStatus('');
    Promise.all([studyApi.geometry(modelId, 'xyz'), studyApi.geometry(modelId, 'uv')])
      .then(([a, b]) => {
        if (cancelled) return;
        if (a.source_sha256 !== b.source_sha256 || a.cells.length !== b.cells.length) {
          throw new Error('As vistas não possuem a mesma origem científica.');
        }
        setXyz(a); setUv(b);
      })
      .catch((e: Error) => { if (!cancelled) setError(e.message); })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [modelId]);
  useEffect(() => {
    let cancelled = false;
    if (selected === null) { setDetail(null); return; }
    studyApi.face(modelId, selected)
      .then((value) => { if (!cancelled) setDetail(value); })
      .catch((e: Error) => { if (!cancelled) setError(e.message); });
    return () => { cancelled = true; };
  }, [modelId, selected]);
  const toggleLayer = (kind: 'triangle' | 'quad') => {
    const visible = kind === 'triangle' ? !showTri : !showQuad;
    if (kind === 'triangle') setShowTri(visible);
    else setShowQuad(visible);
    if (!visible && selected !== null && xyz) {
      const index = xyz.source_face_ids.indexOf(selected);
      if (index >= 0 && xyz.cell_types[index] === kind) setSelected(null);
    }
  };
  const saveCameras = () => {
    if (!model || !xyz || !uv) return;
    const camera_xyz = xyzRef.current?.snapshotCamera();
    const camera_uv = uvRef.current?.snapshotCamera();
    if (!camera_xyz || !camera_uv) { setCameraStatus('Vistas ainda não inicializadas.'); return; }
    const recipe = { schema: CAMERA_SCHEMA, source_sha256: xyz.source_sha256, camera_xyz, camera_uv };
    try {
      localStorage.setItem(storageKey(xyz.source_sha256), JSON.stringify(recipe));
      setCameraStatus('Enquadramentos salvos para este SHA-256.');
    } catch { setCameraStatus('Não foi possível salvar as câmeras no navegador.'); }
  };
  const restoreCameras = () => {
    if (!xyz || !uv) return;
    try {
      const raw = localStorage.getItem(storageKey(xyz.source_sha256));
      if (!raw) throw new Error('no_saved_camera');
      const recipe = parseCameraRecipe(raw, xyz.source_sha256);
      if (!xyzRef.current?.restoreCamera(recipe.camera_xyz) ||
          !uvRef.current?.restoreCamera(recipe.camera_uv)) throw new Error('camera_renderer_unavailable');
      setCameraStatus('Enquadramentos restaurados com a origem verificada.');
    } catch { setCameraStatus('Receita ausente, inválida ou de outra malha.'); }
  };
  const resetCameras = () => {
    xyzRef.current?.resetCamera();
    uvRef.current?.resetCamera();
    setCameraStatus('Enquadramentos redefinidos.');
  };
  return (
    <div className="shell">
      <header className="topbar">
        <div className="brand"><span className="brand-mark">M<span>∕</span></span>
          <div><strong>Mesh Studio</strong><small>APMESH · RESEARCH WORKSPACE</small></div></div>
        <div className="topbar-right"><span className="top-pill">Scientific Viewer</span><span className="version">R1 / PROTOTYPE</span></div>
      </header>
      <div className="workspace">
        <aside className="left-sidebar">
          <div className="sidebar-eyebrow">WORKSPACE / 01</div>
          <h2>Explorar malhas</h2>
          <p className="sidebar-lead">Modelos com proveniência verificada, sem alterar o gerador.</p>
          <label className="field-label" htmlFor="model-select">MALHA DE ORIGEM</label>
          <select id="model-select" data-testid="model-select" value={modelId} onChange={(e) => setModelId(e.target.value)}>
            {catalog.length ? catalog.map((m) => <option value={m.id} key={m.id}>{m.id.toUpperCase()} · {m.quads} QUAD / {m.triangles} TRI</option>)
              : <option value="p1">Carregando catálogo</option>}
          </select>
          <div className="section-break" />
          <div className="field-label">CAMADAS</div>
          <label className="layer-row"><input data-testid="toggle-quad" type="checkbox" checked={showQuad} onChange={() => toggleLayer('quad')}/><span className="layer-dot quad" />Quadriláteros <b>{model?.quads ?? '—'}</b></label>
          <label className="layer-row"><input data-testid="toggle-tri" type="checkbox" checked={showTri} onChange={() => toggleLayer('triangle')}/><span className="layer-dot tri" />Triângulos AFT <b>{model?.triangles ?? '—'}</b></label>
          <label className="layer-row"><input data-testid="toggle-edges" type="checkbox" checked={edges} onChange={() => setEdges(!edges)}/><span className="layer-dot edges" />Arestas <b>ON</b></label>
          <div className="section-break" />
          <div className="field-label">INTEGRIDADE</div>
          <div className="integrity"><span className="status-dot"/>OBJ com SHA-256 conferido</div>
          <p className="small-note">A associação de faces UV / XYZ preserva os IDs originais. Não é uma prova global de validade.</p>
          <div className="sidebar-bottom">Fonte APMesh · leitura local<br/>Sem soldagem implícita de patches.</div>
        </aside>
        <main className="main-content">
          <div className="main-header"><div><div className="eyebrow">RESEARCH / VISUALIZATION</div><h1>Geometria sob investigação</h1><p>Uma malha. Dois espaços. Identidade científica preservada.</p></div>
          <div className="main-status">{loading ? 'Carregando' : error ? 'Erro' : 'Dados verificados'}</div></div>
          <div className="camera-toolbar" aria-label="Controles de câmera">
            <button type="button" data-testid="save-cameras" disabled={!xyz || !uv} onClick={saveCameras}>Salvar vistas</button>
            <button type="button" data-testid="restore-cameras" disabled={!xyz || !uv} onClick={restoreCameras}>Restaurar vistas</button>
            <button type="button" data-testid="reset-cameras" disabled={!xyz || !uv} onClick={resetCameras}>Redefinir câmeras</button>
            <span role="status" data-testid="camera-status">{cameraStatus}</span>
          </div>
          {error && <div role="alert" className="error">{error}</div>}
          {loading && <div className="loading">Carregando geometria e verificando a origem...</div>}
          {xyz && uv && <div className="view-grid">
            <Viewer ref={xyzRef} key={`${modelId}-xyz`} space="xyz" modelId={modelId} geometry={xyz} showTri={showTri} showQuad={showQuad} edges={edges} selectedId={selected} onSelect={setSelected}/>
            <Viewer ref={uvRef} key={`${modelId}-uv`} space="uv" modelId={modelId} geometry={uv} showTri={showTri} showQuad={showQuad} edges={edges} selectedId={selected} onSelect={setSelected}/>
          </div>}
          <div className="model-foot"><div><small>ORIGEM</small><strong>{model ? statuses[model.source_status] : '—'}</strong></div>
          <div><small>ÉPOCAS ADAPTATIVAS ACEITAS</small><strong>0</strong></div>
          <div><small>IDENTIDADE SHA-256</small><code title={model?.sha256}>{model?.sha256.slice(0, 24) ?? '...'}</code></div></div>
          <div className="caution">Os resultados são de uma superfície Bézier controlada. Candidatas em estágio não são épocas adaptativas aceitas. All-quad e anisotropia não estão disponíveis.</div>
        </main>
        <aside className="right-sidebar"><div className="sidebar-eyebrow">INSPECTOR / 02</div><h2>Face selecionada</h2>
          {selected === null ? <div className="inspector-empty"><span className="empty-icon">⌖</span><strong>Selecione uma face</strong><p>Clique em qualquer elemento no espaço físico ou UV para inspecionar os dados originais.</p></div>
            : <div className="inspector"><div className="face-id">#{selected}</div><small>ORIGINAL SOURCE FACE ID</small>
              <div className="section-break"/><dl><dt>Tipo</dt><dd>{detail?.element_type.toUpperCase() ?? '...'}</dd>
              <dt>Grupo</dt><dd>{detail?.group ?? '...'}</dd><dt>Patch</dt><dd>{detail?.patch_id ?? 'Não certificado'}</dd>
              <dt>Área física discreta</dt><dd>{detail?.quality.physical_area.toFixed(6) ?? '...'}</dd>
              <dt>Mean ratio TRI</dt><dd>{detail?.quality.triangle_mean_ratio?.toFixed(5) ?? 'N/A'}</dd>
              <dt>Planar QUAD Jacobian</dt><dd>{detail?.quality.planar_quad_min_scaled_jacobian?.toFixed(5) ?? 'N/A'}</dd></dl>
              <p className="small-note">{detail?.quality.physical_orientation ?? 'Sem validação contínua de orientação'}</p>
              <button type="button" className="clear-btn" onClick={() => setSelected(null)}>Limpar seleção</button></div>}
          <div className="inspector-footer">Métricas calculadas pelo motor Python; não pelo navegador.</div>
        </aside>
      </div>
    </div>
  );
}
