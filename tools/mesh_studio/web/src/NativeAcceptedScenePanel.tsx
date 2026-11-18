import { useMemo, useState } from 'react';
import { NativeAcceptedTriViewer } from './NativeAcceptedTriViewer';
import { parseNativeAcceptedScene } from './nativeAcceptedSceneContract';
import type { NativeSceneBundle } from './nativeAcceptedSceneContract';

export function NativeAcceptedScenePanel() {
  const [data, setData] = useState<NativeSceneBundle | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [sceneIndex, setSceneIndex] = useState(0);
  const [patchSlot, setPatchSlot] = useState(0);
  const [sampleOrdinal, setSampleOrdinal] = useState(0);
  const [faceIndex, setFaceIndex] = useState<number | null>(null);
  const scene = data?.scenes[sceneIndex];
  const identity = scene && data?.identity.documents.find(d =>
    d.model === scene.model &&
    d.accepted_native_step === scene.accepted_native_step &&
    d.source_ndjson_sha256 === scene.source_ndjson_sha256);
  const curve = identity?.qualified_shared_source_curves[0];
  const sample = curve?.sample_groups[sampleOrdinal];
  const member = sample?.members.find(m => m.patch_slot === patchSlot);
  const selected = faceIndex === null ? null : scene?.native_faces[faceIndex] ?? null;
  const linkedSourceSamples = useMemo(() => {
    if (!selected || !identity) return [];
    const ids = new Set(selected[4].map(node => node[0]));
    return identity.qualified_shared_source_curves.flatMap(c =>
      c.sample_groups.flatMap(group => group.members
        .filter(m => m.patch_slot === selected[0] && ids.has(m.native_node_id))
        .map(m => ({curve_slot:c.source_curve_slot, ordinal:group.ordinal,
          native_id:m.native_node_id, t:group.canonical_t}))));
  }, [identity, selected]);

  async function importNative(file: File | undefined) {
    setData(null); setError(null); setSceneIndex(0); setPatchSlot(0);
    setSampleOrdinal(0); setFaceIndex(null);
    if (!file) return;
    try {
      if (file.size < 10 || file.size > 9_000_000) {
        throw new Error('r2720_bounded_native_scene_file_required');
      }
      const result = parseNativeAcceptedScene(await file.text());
      setData(result);
      setPatchSlot(result.identity.documents[0]
        .qualified_shared_source_curves[0].patch_slots[0]);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : 'r2720_invalid_native_scene');
    }
  }

  function changePatch(slot: number) {
    setPatchSlot(slot);
    setFaceIndex(null);
  }

  function selectSourceSampleFace() {
    if (!scene || !member) return;
    const found = scene.native_faces.findIndex(face =>
      face[0] === patchSlot && face[4].some(node =>
        node[0] === member.native_node_id));
    if (found >= 0) setFaceIndex(found);
  }

  return <section className="native-identity-panel native-accepted-scene-panel"
    data-testid="r2720-panel" aria-label="R2.7.20 cena TRI nativa aceita">
    <div className="native-identity-heading">
      <div><div className="eyebrow">RESEARCH / R2.7.20 · OPT-IN</div>
        <h2>Malha TRI nativa aceita — Eistute e Book</h2>
        <p>Identidades reais de faces, nós e patches · visão independente de P1</p>
      </div>
      <span className="native-identity-tag">Fonte C++ · Somente leitura</span>
    </div>
    <p className="native-identity-caution">
      Estas são faces da etapa adaptativa TRI nativa genuinamente aceita,
      não o catálogo P1 ou uma candidata QUAD. As duas vistas abaixo usam
      os mesmos IDs de face, mas UV pertence apenas ao patch selecionado.
      O transporte Float32 é somente visual; a fonte JSON conserva os números originais.
    </p>
    <label className="native-identity-upload">
      Carregar JSON R2.7.20 gerado pelo CI com os registros nativos originais
      <input type="file" data-testid="r2720-import" accept=".json,application/json"
        onChange={e => {void importNative(e.currentTarget.files?.[0]);}}/>
    </label>
    <p className="small-note">O manifesto importado é validado estruturalmente
      contra os IDs e os SHA-256 declarados do inspetor R2.7.19. O navegador
      não verifica criptograficamente os NDJSON brutos sem seus arquivos originais.</p>
    {error && <div role="alert" className="native-identity-error"
      data-testid="r2720-error">Fonte recusada: {error}</div>}
    {!data && !error && <p className="small-note" data-testid="r2720-empty">
      Nenhuma malha nativa carregada. Exporte ou extraia o JSON do artefato
      R2.7.20 do GitHub Actions.</p>}
    {scene && identity && curve && <>
      <div className="native-identity-controls">
        <label>Modelo / etapa realmente aceita
          <select data-testid="r2720-model" value={sceneIndex} onChange={e => {
            const index = Number(e.currentTarget.value);
            setSceneIndex(index); setPatchSlot(0);
            setFaceIndex(null); setSampleOrdinal(0);
          }}>
            {data.scenes.map((s,i) => <option key={s.model+':'+s.accepted_native_step}
              value={i}>{s.model.toUpperCase()} · aceita {s.accepted_native_step}
              {' · '}{s.native_tri_faces} TRI</option>)}
          </select>
        </label>
        <label>Patch local para UV e identidade
          <select data-testid="r2720-patch" value={patchSlot} onChange={e =>
            changePatch(Number(e.currentTarget.value))}>
            {Array.from({length:scene.native_source_patches},(_,slot)=>
              <option key={slot} value={slot}>Patch {slot} ·
                {' '}{scene.source_patch_face_counts[slot]} TRI</option>)}
          </select>
        </label>
        <label>Amostra da curva de origem ({sampleOrdinal + 1}/{curve.sample_count})
          <input data-testid="r2720-sample" type="range" min="0"
            max={curve.sample_count-1} value={sampleOrdinal}
            onChange={e => setSampleOrdinal(Number(e.currentTarget.value))}/>
        </label>
      </div>
      <div className="native-identity-evidence">
        <div><small>TRI NATIVAS ACEITAS</small>
          <strong data-testid="r2720-tri-count">{scene.native_tri_faces}</strong></div>
        <div><small>PATCHES DE ORIGEM</small><strong>{scene.native_source_patches}</strong></div>
        <div><small>CURVA COMPARTILHADA</small><strong>Slot {curve.source_curve_slot}</strong></div>
        <div><small>ÉPOCA ADAPTATIVA REAL</small>
          <strong>{scene.accepted_native_step} · sem LOD</strong></div>
      </div>
      <div className="view-grid native-accepted-view-grid">
        <NativeAcceptedTriViewer scene={scene} space="xyz" patchSlot={patchSlot}
          selectedFaceIndex={faceIndex}
          onSelectFace={index => {
            setFaceIndex(index);
            if (index !== null) setPatchSlot(scene.native_faces[index][0]);
          }}/>
        <NativeAcceptedTriViewer scene={scene} space="uv" patchSlot={patchSlot}
          selectedFaceIndex={faceIndex} onSelectFace={setFaceIndex}/>
      </div>
      <div className="native-accepted-inspectors">
        <div className="native-identity-selection" data-testid="r2720-face-inspector">
          <h3>Face TRI nativa selecionada</h3>
          {selected ? <>
            <dl>
              <dt>Patch (slot)</dt><dd>{selected[0]}</dd>
              <dt>Patch nativo (ID)</dt><dd>{selected[1]}</dd>
              <dt>Elemento no patch (slot)</dt><dd>{selected[2]}</dd>
              <dt>Elemento nativo (ID)</dt>
              <dd data-testid="r2720-native-element-id">{selected[3]}</dd>
            </dl>
            <table className="native-accepted-corners" data-testid="r2720-corners">
              <thead><tr><th>Canto</th><th>ID nativo do nó</th><th>XYZ</th><th>UV local</th></tr></thead>
              <tbody>{selected[4].map((n,i)=><tr key={i}>
                <td>{i+1}</td><td>{n[0]}</td>
                <td>{n.slice(1,4).map(v => Number(v.toPrecision(7))).join(' / ')}</td>
                <td>{n.slice(4).map(v => Number(v.toPrecision(7))).join(' / ')}</td>
              </tr>)}</tbody>
            </table>
            <p className="small-note" data-testid="r2720-linked-samples">
              Amostras desta face na curva de origem:
              {' '}{linkedSourceSamples.length
                ? linkedSourceSamples.map(x => 'curva '+x.curve_slot+
                  ', amostra '+x.ordinal+', nó '+x.native_id).join('; ')
                : 'nenhuma correspondência amostrada observada nesta face'}
            </p>
          </> : <p className="small-note">Clique em uma face nativa XYZ/UV
            ou destaque uma amostra da curva. A identidade é o par
            (patch, slot do elemento), acompanhado de seu ID nativo.</p>}
        </div>
        <div className="native-identity-selection" data-testid="r2720-source-identity">
          <h3>Amostra original · patch {patchSlot}</h3>
          <dl>
            <dt>Curva nativa</dt><dd>slot {curve.source_curve_slot}</dd>
            <dt>Amostra</dt><dd>{sampleOrdinal}</dd>
            <dt>Parâmetro canônico t</dt>
            <dd>{sample?.canonical_t.toFixed(6) ?? '—'}</dd>
            <dt>ID do nó no patch</dt><dd data-testid="r2720-source-node-id">
              {member?.native_node_id ?? '—'}</dd>
            <dt>XYZ fonte original</dt>
            <dd>{member?.original_xyz.join(' / ') ?? '—'}</dd>
            <dt>Nó C++ pertencente à SubMesh</dt>
            <dd>{member?.accepted_corner_cpp_owner_observed === null
              ? 'Não observado nesta amostra'
              : member?.accepted_corner_cpp_owner_observed
                ? 'Sim, no canto aceito' : 'Não comprovado'}</dd>
            <dt>Identidade C++ entre patches</dt>
            <dd>{member?.accepted_corner_shared_cpp_pointer_with_earlier_patch === null
              ? 'Não observada'
              : member?.accepted_corner_shared_cpp_pointer_with_earlier_patch
                ? 'Mesmo ponteiro em patch anterior'
                : 'Ponteiro distinto dos patches anteriores'}</dd>
          </dl>
          <button type="button" className="clear-btn"
            data-testid="r2720-highlight-source-sample" onClick={selectSourceSampleFace}
            disabled={!member}>Destacar face incidente à amostra</button>
          <p className="small-note">A face destacada é uma incidência observada
            do nó na malha aceita, não uma nova face criada pela curva.</p>
        </div>
      </div>
      <p className="native-identity-sha">SHA-256 original das faces aceitas:
        <code data-testid="r2720-source-sha">{scene.source_ndjson_sha256}</code></p>
      <p className="native-identity-caution">Cantos usados no VTK são
        separados por face para visualização: isso não solda nem certifica
        conectividade topológica. Não há ancestralidade entre épocas,
        nem limite de erro contínuo ou LOD geométrico científico qualificado.</p>
    </>}
  </section>;
}
