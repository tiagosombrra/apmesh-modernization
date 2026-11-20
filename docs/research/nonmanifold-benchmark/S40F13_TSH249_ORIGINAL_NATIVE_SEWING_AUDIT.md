# S40-F13 — Reprodução independente da junção tripla nativa no Tsh249

**Checkpoint:** 2026-11-19. **Escopo:** frente `Modelos` de `apmesh-modernization`, exclusivamente na branch de pesquisa da PR #225. **Estado:** `POST_SEWING_THREE_FACE_NATIVE_EDGE_CONFIRMED_NOT_ORIGINAL_SOURCE_POSITIVE`.

## Objetivo e origem verificável

Concluir o bloqueio experimental F12 para um candidato externo de *reconstrução de junção não-manifold* usando o arquivo STEP **original**, não um substituto redesenhado. A fonte é o corpus público [zellyn/dodgy-step-files](https://github.com/zellyn/dodgy-step-files) (licença MIT, copyright Zellyn Hunter), fixado em `2a27aed219fbf930218aac5f24b07c131411b3de`. Arquivo: `step-examples/12-3a-shells/Tsh249.stp`.

- **Git blob SHA-1:** `ce612e8959c3e8954e2c0e565e291ecbbe6cd5ff`.
- **SHA-256 dos bytes STEP:** `d966aa342fea76d6027890fa4fee89283e5bcb2cbcbb9552cc3240d6bbad380d`.
- O arquivo de origem tem 3 `ADVANCED_FACE` `#27/#55/#83`, pertencentes a 3 `OPEN_SHELL` distintos, com `EDGE_CURVE` originalmente diferentes `#10/#38/#66`. O censo estrutural F12 já mostrou **zero** aresta original com três faces. O marcador `NON_MANIFOLD_SURFACE_SHAPE_REPRESENTATION` não altera esse resultado.

O STEP original foi reconstruído localmente **byte a byte** a partir do conteúdo autenticado do GitHub; o hash Git do objeto e o SHA-256 foram comparados **antes da importação CAD**. **Os bytes do STEP não são distribuídos nesta PR**; o código aborta quando os hashes divergem.

## Experimento OCCT realmente executado

Ambiente: Python, `cadquery-ocp==7.9.3.1.1` (Open CASCADE 7.9.3), `cadquery==2.8.0`; importação por `STEPControl_Reader`, `TransferRoots() == 1`, `OneShape()`. Costura com `BRepBuilderAPI_Sewing(1e-7)`, adicionando cada face individualmente. Foram ensaiadas as opções `SetNonManifoldMode(False)` e `SetNonManifoldMode(True)`. Cada resultado passou `BRepCheck_Analyzer.IsValid()`.

A incidência foi verificada **independentemente** pela associação nativa `TopExp.MapShapesAndAncestors_s(EDGE,FACE)` e novamente pelos contadores nativos `NbFreeEdges`, `NbContigousEdges` e `NbMultipleEdges`. Os proprietários são **faces distintas por identidade `IsSame`**, não o número bruto de coedges. O mapeamento de faces de volta à fonte usa centróides únicos, áreas e os três vértices originais de cada triângulo; vértices introduzidos pela costura devem permanecer no contorno original. Essa reconciliação por invariantes geométricos **não é** uma prova formal e genérica do histórico `TShape` para STEP.

| Configuração | Faces | Shells | Arestas nativas únicas | Arestas 1-face | Arestas 2-faces | Arestas 3-faces | BRepCheck |
|---|---:|---:|---:|---:|---:|---:|---|
| STEP original importado | 3 | 3 | 9 | 9 | 0 | 0 | PASS |
| Sewing convencional | 3 | 1 | 12 | 9 | 3 | 0 | PASS |
| Sewing não-manifold | 3 | 1 | 11 | 8 | 2 | **1** | PASS |

A união não-manifold retorna três seções sobre o eixo X (em unidades coordenadas originais):

| Seção X | Faces STEP incidentes | Incidência nativa |
|---|---|---:|
| `[2,4]` | `#27`, `#55` | 2 |
| **`[4,6]`** | **`#27`, `#55`, `#83`** | **3** |
| `[6,8]` | `#55`, `#83` | 2 |

O `NbMultipleEdges()` do próprio OCCT retorna **1** no modo não-manifold e **0** no convencional. As áreas importadas e costuradas permanecem **9,0 unidades² por face, total 27,0**; centróides, três cantos originais de cada triângulo e localização dos novos vértices no contorno foram preservados dentro das tolerâncias auditadas. Não se afirma uma equivalência geométrica global contínua ou prova de Hausdorff.

### Classificação científica

**PASS de reconstrução nativa pós-sewing em fixture de diagnóstico público.** É uma evidência independente de que três fragmentos de borda originalmente diferentes podem ser reconciliados numa aresta nativa de grau 3 na versão ensaiada do kernel.

**NÃO É** um caso positivo de incidência 3+ na identidade de aresta original do STEP; **NÃO É** um modelo industrial genuíno não-manifold; **NÃO É** conversão para atlas bicúbico conformante; **NÃO É** malha gerada pelo APMesh. O S40 permanece com **156 patches e 22/43 faces originais**. O merge em `main` permanece bloqueado.

## Código, testes e reprodutibilidade

- `probes/tsh249_native_occt_sewing_gate.py`: reprodutor nativo fail-closed, fixação SHA, comparação dos dois modos, incidência independente, preservação de faces, auditoria BRep e emissão de recibo JSON.
- `probes/test_tsh249_native_occt_sewing_gate.py`: **13/13 testes PASS, 0 skips** no ambiente local com o STEP original pinado, abrangendo a execução real com o kernel, manipulação adversarial do arquivo, orientação das seções, incidência artificial incorreta, geometria inválida e comportamento do CLI sem sobrescrever recibos.
- `evidence/tsh249/s40f13_original_native_sewing_receipt.json`: relatório de execução efetiva em OCCT 7.9.3.1.1, sem o arquivo STEP de terceiros ou BP geométrico.

Reproduzir no repositório clonado, a partir de `docs/research/nonmanifold-benchmark/probes`:

```bash
export APMESH_TSH249_ORIGINAL_STEP=/private/verified/Tsh249.stp
python -m unittest -v test_tsh249_native_occt_sewing_gate
python tsh249_native_occt_sewing_gate.py \
  --original-step "$APMESH_TSH249_ORIGINAL_STEP" \
  --receipt /private/receipts/s40f13_tsh249_original_native.json
```

O caminho de saída não pode existir anteriormente. Para reproduzir exatamente o resultado, usar o mesmo kernel ou documentar mudança de versão/tolerância e reexecutar todas as validações. O teste real depende do arquivo local indicado; na ausência da variável, os dois testes que precisam do original serão explicitamente **SKIP**, nunca contados como PASS.

## Próximo marco proposto — F14

Auditar uma decomposição de cada face triangular costurada em patches quadrilaterais Bézier de fronteira conforme e com **identidade compartilhada exata** ao longo da seção tripla, retendo a rastreabilidade das entidades STEP originais distintas. Comprovar Jacobianos, costuras 3-incidentes, tolerâncias e malha APMesh TRI antes de qualquer admissão adicional. Manter separada a busca por caso industrial **original-source-positive** com 3+ faces incidentes à mesma entidade topológica antes de qualquer sewing.
