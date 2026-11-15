/** Browser-only viewport benchmark; no source algorithm, acceptance or physics claim. */
import { createRoot } from 'react-dom/client';
import { useCallback, useEffect, useRef, useState } from 'react';
import { Viewer } from './Viewer';
import type { ViewerHandle } from './Viewer';
import type { PickObservation, ScriptedOrbitObservation } from './performanceProbe';
import { chromiumHeapEstimate } from './performanceProbe';
import type { MeshGeometry } from './contracts';
import './style.css';

const ALLOWED_CELLS = [1_000, 50_000, 500_000] as const;
const SYNTHETIC_SHA = '0'.repeat(64);

type SyntheticSample = {
  xyz: MeshGeometry;
  uv: MeshGeometry;
  generationMs: number;
};

function syntheticScene(cells: number): SyntheticSample {
  if (!ALLOWED_CELLS.includes(cells as typeof ALLOWED_CELLS[number])) {
    throw new Error('invalid_synthetic_cell_budget');
  }
  const width = Math.floor(Math.sqrt(cells));
  const height = Math.ceil(cells / width);
  const started = performance.now();
  const points: number[][] = [];
  const uvPoints: number[][] = [];
  const faces: number[][] = [];
  const ids: number[] = [];
  for (let row = 0; row <= height; row += 1) {
    const v = row / height;
    for (let col = 0; col <= width; col += 1) {
      const u = col / width;
      // Synthetic height is for rendering only; never feed this into scientific metrics.
      points.push([u, v, 0.08 * Math.sin(u * Math.PI * 2) * Math.cos(v * Math.PI * 2)]);
      uvPoints.push([u, v, 0]);
    }
  }
  for (let row = 0; row < height && faces.length < cells; row += 1) {
    for (let col = 0; col < width && faces.length < cells; col += 1) {
      const first = row * (width + 1) + col;
      faces.push([first, first + 1, first + width + 2, first + width + 1]);
      ids.push(faces.length - 1);
    }
  }
  const common = {
    schema: 'apmesh.meshstudio.web.v1',
    source_sha256: SYNTHETIC_SHA,
    source_patch_ownership: 'NOT_APMESH_SOURCE',
    cells: faces,
    source_face_ids: ids,
    cell_types: Array<'quad'>(faces.length).fill('quad'),
    triangles: 0,
    quads: faces.length,
    warning: 'SYNTHETIC BENCHMARK ONLY. Not an APMesh experiment, not adaptive epochs.',
  };
  return {
    xyz: { ...common, coordinate_space: 'xyz', points },
    uv: { ...common, coordinate_space: 'uv', points: uvPoints },
    generationMs: performance.now() - started,
  };
}

type Result = {
  cells: number;
  points: number;
  synthetic: true;
  generation_ms: number;
  xyz_first_render_ms: number | null;
  uv_first_render_ms: number | null;
  render_scope: string;
  js_heap_bytes: number | null;
  gpu_memory_bytes: null;
  frame_rate_fps: null;
  result: 'PRELIMINARY_BROWSER_RENDER_OBSERVATION';
  scripted_camera_orbit: {
    xyz: ScriptedOrbitObservation;
    uv: ScriptedOrbitObservation;
    heap_before_bytes: number | null;
    heap_after_bytes: number | null;
    heap_scope: 'CHROMIUM_PERFORMANCE_MEMORY_ESTIMATE_NOT_TOTAL_RAM_OR_VRAM';
  } | null;
  last_picker_call: PickObservation | null;
};

function BrowserBenchmark() {
  const [count, setCount] = useState(1_000);
  const [sample, setSample] = useState<SyntheticSample | null>(null);
  const [selected, setSelected] = useState<number | null>(null);
  const [showQuads, setShowQuads] = useState(true);
  const [edges, setEdges] = useState(false);
  const [nativePicker, setNativePicker] = useState(false);
  const [xyzDuration, setXyzDuration] = useState<number | null>(null);
  const [uvDuration, setUvDuration] = useState<number | null>(null);
  const [status, setStatus] = useState('Sem medição');
  const startTime = useRef(0);
  const xyzViewer = useRef<ViewerHandle>(null);
  const uvViewer = useRef<ViewerHandle>(null);
  const runEpoch = useRef(0);
  const [motion, setMotion] = useState<Result['scripted_camera_orbit']>(null);
  const [lastPick, setLastPick] = useState<PickObservation | null>(null);
  const [motionStatus, setMotionStatus] = useState('Não medido');
  const [runningMotion, setRunningMotion] = useState(false);

  const measureOrbit = async () => {
    if (!sample || runningMotion || !xyzViewer.current || !uvViewer.current ||
        xyzDuration === null || uvDuration === null) return;
    const epoch = ++runEpoch.current;
    setRunningMotion(true);
    setMotion(null);
    setMotionStatus('Executando órbita controlada em ambas as vistas...');
    const heapBefore = chromiumHeapEstimate();
    try {
      // Run sequentially to avoid contending two WebGL scenes for the same frame budget.
      const xyz = await xyzViewer.current.probeOrbit(24);
      if (!xyz || epoch !== runEpoch.current) return;
      const uv = await uvViewer.current.probeOrbit(24);
      if (!uv || epoch !== runEpoch.current) return;
      setMotion({ xyz, uv, heap_before_bytes: heapBefore,
        heap_after_bytes: chromiumHeapEstimate(),
        heap_scope: 'CHROMIUM_PERFORMANCE_MEMORY_ESTIMATE_NOT_TOTAL_RAM_OR_VRAM' });
      setMotionStatus('Medição concluída (órbita sintética, não FPS de apresentação GPU).');
    } catch (error) {
      if (epoch === runEpoch.current) setMotionStatus(`Erro na medição: ${String(error)}`);
    } finally {
      if (epoch === runEpoch.current) setRunningMotion(false);
    }
  };
  const onXyz = useCallback(() => {
    if (startTime.current && xyzDuration === null) {
      setXyzDuration(performance.now() - startTime.current);
    }
  }, [xyzDuration]);
  const onUv = useCallback(() => {
    if (startTime.current && uvDuration === null) {
      setUvDuration(performance.now() - startTime.current);
    }
  }, [uvDuration]);
  useEffect(() => {
    let stopped = false;
    const timer = setTimeout(() => {
      if (stopped) return;
      setStatus(`Construindo ${count.toLocaleString('pt-BR')} QUAD sintéticos...`);
      // Yield before expensive synthetic scene generation so status can paint.
      requestAnimationFrame(() => {
        if (stopped) return;
        try {
          setSample(null);
          setXyzDuration(null);
          setUvDuration(null);
          setSelected(null);
          setMotion(null);
          setLastPick(null);
          setMotionStatus('Não medido');
          setShowQuads(true);
          startTime.current = performance.now();
          const next = syntheticScene(count);
          setSample(next);
          setStatus('Processando geometria na GPU...');
        } catch (error) {
          setStatus(`Falha de benchmark: ${String(error)}`);
        }
      });
    }, 10);
    return () => { stopped = true; clearTimeout(timer); };
  }, [count]);
  const measurement: Result | null = sample ? {
    cells: sample.xyz.quads,
    points: sample.xyz.points.length,
    synthetic: true,
    generation_ms: Math.round(sample.generationMs * 1000) / 1000,
    xyz_first_render_ms: xyzDuration === null ? null : Math.round(xyzDuration * 1000) / 1000,
    uv_first_render_ms: uvDuration === null ? null : Math.round(uvDuration * 1000) / 1000,
    render_scope: 'SYNTHETIC_CLIENT_GENERATION_TO_FIRST_VTK_RENDER_NOT_FPS',
    js_heap_bytes: (() => {
      const p = performance as Performance & { memory?: { usedJSHeapSize: number } };
      return Number.isFinite(p.memory?.usedJSHeapSize) ? p.memory!.usedJSHeapSize : null;
    })(),
    gpu_memory_bytes: null,
    frame_rate_fps: null,
    result: 'PRELIMINARY_BROWSER_RENDER_OBSERVATION',
    scripted_camera_orbit: motion,
    last_picker_call: lastPick,
  } : null;
  const complete = xyzDuration !== null && uvDuration !== null;
  return (
    <main style={{ padding: 24, maxWidth: 1400, margin: 'auto', fontFamily: 'system-ui' }}>
      <p style={{ color: '#89bacc', fontSize: 12, letterSpacing: 1.5 }}>APMESH MESH STUDIO / R2 / BENCHMARK</p>
      <h1 style={{ fontSize: 26 }}>Capacidade de visualização no navegador</h1>
      <p style={{ maxWidth: 840, lineHeight: 1.6, color: '#c4d2dc' }}>
        Ensaio sintético de visualização, separado dos experimentos científicos. Não mede qualidade do gerador,
        desempenho do APMesh C++, VRAM, FPS sustentado ou erro geométrico real.
      </p>
      <label htmlFor="cells" style={{ marginRight: 12 }}>Células QUAD sintéticas</label>
      <select id="cells" data-testid="benchmark-cells" value={count}
        onChange={(event) => {
          // Invalidate the old measurement synchronously before requesting the new scene.
          runEpoch.current += 1;
          setSample(null);
          setXyzDuration(null);
          setUvDuration(null);
          setSelected(null);
          setMotion(null);
          setLastPick(null);
          setMotionStatus('Não medido');
          setRunningMotion(false);
          setStatus('Preparando um novo ensaio sintético...');
          setCount(Number(event.target.value));
        }} style={{ maxWidth: 190 }}>
        {ALLOWED_CELLS.map((value) => <option key={value} value={value}>{value.toLocaleString('pt-BR')}</option>)}
      </select>
      <label style={{ marginLeft: 20 }}><input type="checkbox" checked={showQuads}
        data-testid="benchmark-quad-filter" onChange={(event) => setShowQuads(event.target.checked)} /> Mostrar QUAD</label>
      <label style={{ marginLeft: 15 }}><input type="checkbox" checked={edges}
        data-testid="benchmark-edge-filter" onChange={(event) => setEdges(event.target.checked)} /> Arestas</label>
      <label style={{ marginLeft: 15 }}><input type="checkbox" checked={nativePicker}
        data-testid="benchmark-native-picker" onChange={(event) => setNativePicker(event.target.checked)} /> vtkCellPicker de controle (A/B)</label>
      <div style={{ display: 'flex', alignItems: 'center', flexWrap: 'wrap', gap: 16, marginTop: 16 }}>
        <button type="button" data-testid="benchmark-run-motion" disabled={!complete || runningMotion}
          onClick={() => { void measureOrbit(); }} style={{ padding: '9px 14px', cursor: 'pointer' }}>
          {runningMotion ? 'Medindo órbita...' : 'Medir órbita XYZ + UV (24 quadros por vista)'}
        </button>
        <span role="status" data-testid="benchmark-motion-status">{motionStatus}</span>
      </div>
      <p style={{ maxWidth: 850, fontSize: 12, color: '#9cbbcc' }}>
        A órbita registra intervalos requestAnimationFrame → chamada de renderização VTK, não FPS apresentado pela GPU.
        O picking registra apenas a chamada síncrona vtkCellPicker. A memória JavaScript é uma estimativa do Chromium;
        VRAM, memória nativa e FPS de interação humana permanecem desconhecidos.
      </p>
      <p data-testid="benchmark-status" role="status" style={{ color: complete ? '#91dfbf' : '#f6cb8a' }}>
        {complete ? 'As duas cenas foram renderizadas; dados sintéticos.' : status}
      </p>
      {sample && <div className="view-grid" style={{ marginTop: 16 }}>
        <Viewer ref={xyzViewer} key={`r2-xyz-${count}`} space="xyz" modelId={`SYNTHETIC_${count}`}
          geometry={sample.xyz} showTri={false} showQuad={showQuads} edges={edges}
          selectedId={selected} onSelect={setSelected} onRendered={onXyz} onPickMeasured={setLastPick}
          pickingMode={nativePicker ? 'native' : 'auto'} />
        <Viewer ref={uvViewer} key={`r2-uv-${count}`} space="uv" modelId={`SYNTHETIC_${count}`}
          geometry={sample.uv} showTri={false} showQuad={showQuads} edges={edges}
          selectedId={selected} onSelect={setSelected} onRendered={onUv} onPickMeasured={setLastPick}
          pickingMode={nativePicker ? 'native' : 'auto'} />
      </div>}
      <p data-testid="benchmark-linked-selection">Face sintética selecionada: {selected ?? 'nenhuma'}</p>
      <pre data-testid="benchmark-receipt" style={{ marginTop: 20, whiteSpace: 'pre-wrap', fontSize: 12,
        background: '#172a3b', padding: 14, borderRadius: 8 }}>
        {JSON.stringify(measurement, null, 2)}
      </pre>
    </main>
  );
}

const root = document.getElementById('benchmark-root');
if (!root) throw new Error('missing_benchmark_root');
createRoot(root).render(<BrowserBenchmark />);
