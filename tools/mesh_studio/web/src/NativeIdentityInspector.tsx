import { useMemo, useState } from 'react';
import { parseNativeIdentityManifest } from './nativeIdentityContract';
import type { NativeIdentityManifest } from './nativeIdentityContract';

/**
 * Independent symbolic source-incidence panel. The existing P1 XYZ/UV scenes
 * are unrelated research inputs and must never be overlaid with native data.
 */
export function NativeIdentityInspector() {
  const [bundle, setBundle] = useState<NativeIdentityManifest | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [documentIndex, setDocumentIndex] = useState(0);
  const [curveIndex, setCurveIndex] = useState(0);
  const [sampleIndex, setSampleIndex] = useState(0);
  const [patchSlot, setPatchSlot] = useState(0);
  const doc = bundle?.documents[documentIndex];
  const curve = doc?.qualified_shared_source_curves[curveIndex];
  const sample = curve?.sample_groups[sampleIndex];
  const member = sample?.members.find((item) => item.patch_slot === patchSlot) ??
    sample?.members[0] ?? null;
  const diagram = useMemo(() => curve?.patch_slots.map((slot, index, list) => {
    const angle = -Math.PI / 2 + 2 * Math.PI * index / list.length;
    return {
      slot,
      x: 210 + 112 * Math.cos(angle),
      y: 144 + 112 * Math.sin(angle),
    };
  }) ?? [], [curve]);

  async function load(file: File | undefined) {
    setBundle(null);
    setError(null);
    setDocumentIndex(0);
    setCurveIndex(0);
    setSampleIndex(0);
    if (!file) return;
    try {
      if (file.size > 800_000 || file.size < 2) {
        throw new Error('native_inspector_file_size_limit');
      }
      const parsed = parseNativeIdentityManifest(await file.text());
      setBundle(parsed);
      setPatchSlot(parsed.documents[0].qualified_shared_source_curves[0].patch_slots[0]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'native_inspector_invalid_document');
    }
  }

  return (
    <section className="native-identity-panel" data-testid="r2719-inspector"
      aria-label="R2.7.19 inspetor experimental de curvas nativas">
      <div className="native-identity-heading">
        <div><div className="eyebrow">RESEARCH / R2.7.19 · OPT-IN</div>
          <h2>Identidades e interfaces não manifold</h2>
          <p>Um relacionamento entre amostras de origem e nós locais — sem soldagem.</p>
        </div>
        <span className="native-identity-tag">Somente leitura</span>
      </div>
      <p className="native-identity-caution">
        Painel independente. Eistute/Book nativos não são a geometria das vistas
        P1 ou das candidatas acima. Este painel não desenha patches CAD em XYZ
        nem associa faces aos viewports atuais.
      </p>
      <label className="native-identity-upload">
        Carregar manifesto JSON nativo derivado dos artefatos R2.7.19
        <input type="file" accept=".json,application/json"
          data-testid="r2719-import" onChange={(e) => {
            void load(e.currentTarget.files?.[0]);
          }} />
      </label>
      <p className="small-note">O importador verifica limites e consistência estrutural.
        O SHA-256 original é exibido, mas o navegador não autentica
        criptograficamente os NDJSON sem os arquivos brutos originais.</p>
      {error && <div role="alert" data-testid="r2719-error"
        className="native-identity-error">Manifesto recusado: {error}</div>}
      {!bundle && !error && <p data-testid="r2719-empty" className="small-note">
        Nenhuma evidência nativa carregada. Utilize o manifesto preservado como
        artefato da execução C++ do GitHub Actions.</p>}
      {bundle && doc && curve && sample && <>
        <div className="native-identity-controls">
          <label>Modelo e etapa nativa aceita
            <select data-testid="r2719-document" value={documentIndex}
              onChange={(e) => {
                const i = Number(e.currentTarget.value);
                setDocumentIndex(i); setCurveIndex(0); setSampleIndex(0);
                setPatchSlot(bundle.documents[i].qualified_shared_source_curves[0].patch_slots[0]);
              }}>
              {bundle.documents.map((d, i) =>
                <option key={d.model + d.accepted_native_step} value={i}>
                  {d.model.toUpperCase()} · etapa {d.accepted_native_step}
                </option>)}
            </select>
          </label>
          <label>Curva de origem
            <select data-testid="r2719-curve" value={curveIndex}
              onChange={(e) => {
                const i = Number(e.currentTarget.value);
                setCurveIndex(i); setSampleIndex(0);
                setPatchSlot(doc.qualified_shared_source_curves[i].patch_slots[0]);
              }}>
              {doc.qualified_shared_source_curves.map((c, i) =>
                <option key={c.source_curve_slot} value={i}>
                  Slot {c.source_curve_slot} · ID {c.native_curve_id}
                </option>)}
            </select>
          </label>
          <label>Amostra da curva ({sampleIndex + 1}/{curve.sample_count})
            <input type="range" data-testid="r2719-sample" min="0"
              max={curve.sample_count - 1} value={sampleIndex}
              onChange={(e) => setSampleIndex(Number(e.currentTarget.value))}/>
          </label>
        </div>
        <div className="native-identity-evidence">
          <div><small>PATCHES INCIDENTES</small><strong>{curve.patch_slots.length}</strong></div>
          <div><small>AMOSTRAS DE ORIGEM</small><strong>{curve.sample_count}</strong></div>
          <div><small>PARÂMETRO CANÔNICO</small><strong>
            {sample.canonical_t.toFixed(6)}</strong></div>
          <div><small>COMPARAÇÃO CPP ENTRE CANTOS</small><strong>
            {doc.accepted_corner_cpp_pointer_reuse_count} reutilizações observadas</strong></div>
        </div>
        <div className="native-identity-layout">
          <div className="native-identity-fan-wrap">
            <svg data-testid="r2719-source-fan" className="native-identity-fan"
              role="img" aria-label={'Diagrama simbólico de incidência de ' +
                curve.patch_slots.length + ' patches à curva de origem'}
              viewBox="0 0 420 290">
              {diagram.map((p) =>
                <line key={'line-' + p.slot} x1="210" y1="144"
                  x2={p.x} y2={p.y} stroke="#3c6579" strokeWidth="1.5"/>)}
              <circle cx="210" cy="144" r="26" fill="#1c6a7d" stroke="#79cada"/>
              <text x="210" y="140" textAnchor="middle" fill="#e8f5f9"
                fontSize="10">CURVA</text>
              <text x="210" y="154" textAnchor="middle" fill="#e8f5f9"
                fontSize="12">#{curve.source_curve_slot}</text>
              {diagram.map((p) => <g key={p.slot}>
                <circle cx={p.x} cy={p.y} r={p.slot === patchSlot ? 13 : 10}
                  fill={p.slot === patchSlot ? '#d2a65a' : '#254758'}
                  stroke={p.slot === patchSlot ? '#f1d7a6' : '#6f9dac'}/>
                <text x={p.x} y={p.y + 3} fontSize="9" textAnchor="middle"
                  fill="#eef5f7">{p.slot}</text>
              </g>)}
            </svg>
            <p className="small-note">Diagrama de incidência abstrato:
              distância e ângulo não são coordenadas físicas do modelo.</p>
            <div className="native-identity-patch-buttons"
              data-testid="r2719-patches">
              {curve.patch_slots.map((slot) => <button type="button"
                key={slot} data-testid={'r2719-patch-' + slot}
                aria-pressed={patchSlot === slot}
                onClick={() => setPatchSlot(slot)}>Patch {slot}</button>)}
            </div>
          </div>
          <div className="native-identity-selection" data-testid="r2719-member">
            <h3>Identidade local do patch {member?.patch_slot ?? '—'}</h3>
            <dl>
              <dt>ID nativo original</dt><dd>{member?.native_node_id ?? '—'}</dd>
              <dt>Slot da borda</dt><dd>{member?.edge_slot ?? '—'}</dd>
              <dt>Parâmetro local canônico</dt><dd>{member?.canonical_t.toFixed(6) ?? '—'}</dd>
              <dt>XYZ original</dt><dd>{member?.original_xyz.join(' / ') ?? '—'}</dd>
              <dt>Nó C++ local na malha aceita</dt><dd>
                {member?.accepted_corner_cpp_owner_observed === null
                  ? 'Não observado nesta amostra'
                  : member?.accepted_corner_cpp_owner_observed ? 'Observado' : 'Não confirmado'}
              </dd>
              <dt>Mesmo objeto C++ em outro patch</dt><dd>
                {member?.accepted_corner_shared_cpp_pointer_with_earlier_patch === null
                  ? 'Não observado'
                  : member?.accepted_corner_shared_cpp_pointer_with_earlier_patch
                    ? 'Sim, nos patches previamente observados' : 'Não, nos patches anteriores'}
              </dd>
              <dt>Relação dos IDs na curva</dt><dd>
                {sample.logical_id_relation === 'same_native_logical_id_in_all_source_patches'
                  ? 'Mesmo ID lógico em todos os patches'
                  : sample.logical_id_relation ===
                    'different_native_logical_id_in_every_source_patch'
                    ? 'IDs lógicos distintos em todos os patches'
                    : 'Reutilização parcial de IDs'}
              </dd>
            </dl>
          </div>
        </div>
        <div className="native-identity-members">
          <h3>Associação dos nós locais na amostra {sample.ordinal}</h3>
          <div className="native-identity-table-scroll">
            <table data-testid="r2719-members-table">
              <thead><tr><th>Patch</th><th>Borda</th><th>ID nativo</th><th>t</th>
                <th>C++ observado</th></tr></thead>
              <tbody>{sample.members.map((m) =>
                <tr key={m.patch_slot} data-selected={m.patch_slot === patchSlot}
                  onClick={() => setPatchSlot(m.patch_slot)}>
                  <td>{m.patch_slot}</td><td>{m.edge_slot}</td>
                  <td>{m.native_node_id}</td><td>{m.canonical_t.toFixed(6)}</td>
                  <td>{m.accepted_corner_cpp_owner_observed === null ? 'Não aferido' :
                    m.accepted_corner_cpp_owner_observed ? 'Sim' : 'Não'}</td>
                </tr>)}</tbody>
            </table>
          </div>
        </div>
        <p className="native-identity-sha">SHA-256 NDJSON original:
          <code data-testid="r2719-source-sha">{doc.source_ndjson_sha256}</code></p>
        <p className="native-identity-caution">Sem nós globais artificiais, sem
          soldagem e sem LOD científico. Etapa nativa aceita ≠ tentativa local
          do Adapter. A identidade C++ não persiste entre épocas por inferência.</p>
      </>}
    </section>
  );
}
