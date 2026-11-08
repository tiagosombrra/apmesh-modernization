# Plano de pesquisa e implementação QUAD — APMesh

**Estado:** M0 technical baseline inventory **complete with documented exceptions; exact checkpoint delivery gate required**; no QUAD algorithm implementation in the production pipeline. **Criado em:** 2026-11-08. **Revisão científica prevista:** 2026-11-11 com Joaquim Bento e Creto Vidal.
**Branch:** `quad-templates`; **baseline imutável de origem:** `f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94` (PR #183).  
**Auditoria:** [BASELINE_AUDIT.md](BASELINE_AUDIT.md). **Fonte histórica:** Bento et al., *Combinação das Técnicas de Quadtree e Delaunay para Geração Automática de Malhas de Elementos Finitos*, SIBGRAPI 1993, Figura 7 e seção sobre contorno.

## Continuity and mandatory research handoff

**Canonical current state:** [STATE.md](STATE.md) — read this before interpreting any milestone in this roadmap.  
**Conversation/agent workflow:** [CONTINUATION_PROTOCOL.md](CONTINUATION_PROTOCOL.md) — mandatory at each substantial QUAD session.  
**Append-only activity:** [SESSION_LOG.md](SESSION_LOG.md).  
**Current M0 gate evidence:** [M0_EVIDENCE.md](M0_EVIDENCE.md).

**2026-11-08-03 measured update:** M0 remains OPEN. A preserved local MSVC C++17
build and Eistute/Book captures have verified log/binary identities and offline
comparison evidence: 9 states, 45 exact scientific artifacts and 123 positive
boundaries. GCC/Linux, full research-branch CTest/Python and applicable memory
qualification remain pending. The Windows doctor/profile failure is retained;
see the [review receipt](evidence/M0_MSVC_REVIEW_20261108.json).

**2026-11-08-04 measured update:** [PR #184](https://github.com/tiagosombrra/apmesh-modernization/pull/184)
integrates bounded GNU validation portability into the research branch at
`a29711bea1e38f6a1ea49dde443f0ae58ebadfa7`. Exact head/merge Linux regression passes
75 CTest / 527 Python (all original 526 plus one new control). Strict Linux article
comparison passes 9 states / 45 exact artifacts / 123 positive boundaries; preserved
MSVC evidence remains separate. M0-G6 applicable memory disposition and M0-G7
semantic caller inventory remain pending, so M0 stays OPEN and M1 is not admitted.
See the [GNU qualification receipt](evidence/M0_GNU_QUALIFICATION_20261108.json).

At session end, write a verified GitHub checkpoint: update the canonical state,
append the session log and record executed/unexecuted gates. Update this roadmap
only for an actual milestone transition, changed approved scope or adjusted gate.
New ChatGPT/Codex sessions must resume from these files and current remote commits,
not from assumed recall of earlier conversations. The protocol is not an automatic
scheduler: a connected actor must perform the write. If tools are unavailable,
report that the checkpoint could not be persisted.

## 1. Decisão arquitetural

Implementar QUAD como caminho científico **opt-in**, isolado da modernização atual (Stage 3). Preservar o algoritmo TRI, oráculos de Eistute/Book, contratos de memória e o comportamento de configuração `template_mode` (y/n). O mecanismo de seleção de espécie TRI/QUAD é **ortogonal** à seleção de aplicação de templates.

A infraestrutura existente permite reutilizar:

- `Quadtree::refineAccordingToNeighbors()`;
- `Quadtree::makeTemplateBasedMesh()` e criação/compartilhamento de arestas e vértices externos;
- classificação T1–T6 em `QuadtreeCell::makeTemplateBasedMesh()` baseada em quatro listas de vizinhos;
- infraestrutura de parametrização UV das superfícies e amostras canônicas de curvas compartilhadas.

**Não reutilizar como se fossem genéricos:** `Face` (3 vértices), `TriangleAdaptive` (3 nós), leitura de malha anterior no `Adapter` (casteada para TRI), adjacência da curvatura e métricas/OBJ do `GeneratorAdaptive`.

**Atenção:** o artigo de 1993 pode produzir malhas *quad-dominant* ao combinar triângulos do contorno; ele não garante *all-quad* para todos os domínios. A escolha de alvo deve ser deliberada, com os casos não satisfeitos explicitados.

## 2. Organização e fluxo Git

- Branch científica permanente: `quad-templates`.
- A modernização continua em `main`, **sem** implementação QUAD experimental.
- Para cada marco: `quad/m01-pattern-oracle`, `quad/m02-uv-topology`, etc.; abrir PR com **base `quad-templates`**, revisão de escopo, testes e evidência. Não abrir PR para `main` por padrão.
- Dois worktrees locais, com diretórios separados. Exemplo:

```bash
git fetch origin
git worktree add ../apmesh-quad quad-templates
git worktree list
```

- Antes de absorver uma correção da `main`, congelar evidências por SHA, medir o diff, reexecutar o gate TRI e os novos gates QUAD. Não usar merge/rebase automático indiscriminado.
- Manter registros de oráculos em `docs/research/quad/evidence` e testes em `tests/quad`, sem editar as evidências fechadas da linha de modernização.

## 3. Anatomia do código a alterar, em ordem

| Ordem | Módulo | Estado atual | Mudança deliberada |
|---|---|---|---|
| 1 | `quadtree_cell.cpp` | T1–T6 triangulares e seleção por vizinhança; células `inBoundary()` ignoradas | Expor classificação `LeafPattern` com orientações; **não** mudar os métodos TRI |
| 2 | Novo `research/quad` e `tests/quad` | Inexistentes | Tipos UV/IDs, padrões poligonais do artigo, conversão polígono→QUAD e validador |
| 3 | `quadtree.cpp` | Compartilha vértices/arestas externos; gera `Face` | Acesso controlado aos dados de folhas e emissão QUAD em malha UV própria |
| 4 | `advancing_front.cpp` | AFT preenche região restante com TRI; `fillMesh` e `improveMesh` triangulares | Estratégia explícita para *boundary gap*, quad-dominant/all-quad; integração não invasiva |
| 5 | `element_adaptive.h` e nova `quadrilateral_adaptive.h/.cpp` | Contrato base incompleto para 4 nós/UV | 4 nós, UVs, área/normal/qualidade, observadores e falhas transacionais |
| 6 | `adapter.cpp` | TRI→`Face` na leitura e `Face`→TRI na saída | Caminho QUAD fisicamente tipado, preservando modo TRI; modos mistos suportados quando habilitados |
| 7 | `curvature/adjacent.cpp` + `curvature_discrete.cpp` | Acesso triangular e adjacência angular | Estratégia validada para valência e ângulos de QUAD; comparar oráculo analítico/discreto |
| 8 | `generator_adaptive.cpp` | Qualidade, erro, exportação, estatísticas e repetição triangulares | Oráculos e relatórios específicos TRI/QUAD; rollback e reentrada para múltiplas iterações |
| 9 | `cmake/Quality.cmake` | Registro dos gates de regressão existentes | Adicionar gates QUAD com rótulo `research-quad`, separados dos gates históricos |

Não editar arquivos de `main` a partir do worktree QUAD. Um novo `src/*.cpp` entra automaticamente no `ap_mesh_engine` por `GLOB_RECURSE`; manter o protótipo inicial em `research/quad` para não modificar a compilação da aplicação até a decisão M3.

## 4. Marcos com entregáveis e critérios objetivos

| Marco | Nome | Entregável verificável | Critério de saída |
|---|---|---|---|
| **M0** | Baseline e oráculos | Relatório completo de compilação GCC/MSVC, 75 CTest e 526 controles Python como referência a verificar, Eistute/Book, hashes e corpus | **Não avançar** sem baseline local reproduzido e documentação das exceções |
| **M1** | Reconstrução histórica T1–T6 | Inventário da Figura 7, polígonos padrões, rotações/reflexões e exemplos unitários | Os seis casos e orientações previstas conferem com o artigo; sem topologia inventada |
| **M2** | Topologia QUAD UV | `UvVertex`, `UvQuad`, registro de arestas/pontos médios e validador independente | Cobertura, área positiva, orientação, contagem de incidências, ausência de T-junctions; fuzz/negativos |
| **M3** | Emissor de templates de quadtree | Seletor TRI/QUAD opt-in, emissor QUAD para folhas internas e validação T1–T6 | Resultados TRI *byte-equal* no modo padrão; QUAD interior conforme em casos 2:1 |
| **M4** | QUAD físico | `QuadrilateralAdaptive`, UV→XYZ, normal/área válidas, exportação QUAD em prova isolada | Teste plano e curvo; 4 nós/UV; falhas de alocação e destruição sem observadores pendentes |
| **M5** | Tratamento de contorno | Política escolhida: combinar TRI na borda (*quad-dominant*) ou preencher com QUAD (*all-quad*) | Malha de patch completo, sem vazios, sobreposição, inversão nem divergência de IDs |
| **M6** | Conformidade multipatch | Compartilhamento canônico de curvas, sincronização e orientação invertida | 2 patches e 3 incidentes, 1:1 de pontos físicos e arestas, sem subdivisão local divergente |
| **M7** | Adaptação reiterada | Entrada QUAD como histórico, métrica de tamanho e erro, retry/rollback, relatórios | Pelo menos 2 iterações sucessivas; rejeição não publica malha; gates TRI protegidos |
| **M8** | Modelos e ablação | Conjunto de modelos controlados e CAD; TRI/quad-dominant/all-quad; custo/qualidade/erro | Protocolo reproduzível com seeds, hashes, gráficos e limites declarados |
| **M9** | Anisotropia (opcional para primeiro paper) | Campo métrico e propostas de templates orientados; testes de alinhamento e razão de aspecto | Efeito anisotrópico demonstrado no espaço físico; resultados comparados isotrópico/anisotrópico |

**Marcos M0–M3** são o primeiro lote viável de implementação com risco controlado. **M4–M7** dependem de engenharia de ciclo de vida e de uma decisão topológica explícita para a região de fronteira. **M8–M9** são investigação científica, não compromisso de performance antes de medir.

## 5. Portas técnicas de aprovação

### G0 — Baseline intacto

1. Build serial Linux GCC C++17 e Windows MSVC C++17; registrar compilers/options.
2. CTest completo e os controles Python realmente executados no commit da linha QUAD; guardar stdout/stderr, SHA, tempo, ambiente e fixture. Os números 75/526 são **evidência documental prévia**, não resultados desta criação de branch.
3. Eistute e Book: comparar saídas científicas aceitas pela linha de modernização, incluindo IDs, contagem, qualidade e limites — não trocar tolerâncias para passar.
4. ASan/LSan e CRT/checked-MSVC nos casos relevantes; não inferir segurança MPI/OpenMP.

### G1 — Template historical oracle

- Para T1–T6, publicar lista ordenada de vértices UV, polígonos, orientação, incidências esperadas e topologia final.
- A equivalência triangulada observada no código é **de classe de vizinhança**; diferentes diagonais, centro otimizado e contagem atual não são evidência de identidade literal com a publicação de 1993.
- A subdivisão centro/pontos médios só é aceita se cada polígono tiver centro válido, sem elemento côncavo/invertido; o registro de midpoint deve identificar a mesma **aresta canônica** em células adjacentes.

### G2 — Integridade UV

- Verificações sobre orientação CCW, área, degenerescência, interseção, incidência 1/2 em bordas/interior e não existência de *hanging nodes*.
- Metamórficos: rotações 90/180/270°, reflexão quando aplicável, escalonamento uniforme, permutação de IDs sem mudar topologia.
- Fuzz com níveis quadtree e padrões de vizinhança permitidos; entradas adversariais e falha explícita, sem sucesso vazio.

### G3 — Integridade física e de memória

- Elementos físicos em `SubMesh` devem possuir `unique_ptr<ElementAdaptive>`, nós proprietários e observadores cuja vida é estritamente menor que a dos nós.
- Testar 4 nós iguais/degenerados, reordenação, rejeição no construtor, falhas de adoção/clonagem, destruição e realocação.
- Normal/área em superfícies parametrizadas potencialmente não planares deve ter definição explícita e independente de eventual triangulação auxiliar.
- Normal/erro geométrico devem referir-se ao domínio físico, não somente à qualidade UV.

### G4 — Fronteiras e adaptação

- AFT atual é triangular. Não declarar “all-quad” quando a transição preserva TRI.
- Em curva física compartilhada, uma inserção canônica deve chegar a todas as superfícies incidentes, com orientação e IDs consistentes.
- Para atualização adaptativa, QUAD precisa de regra própria para tamanho local/curvatura e histórico; dupla iteração é obrigatória.
- Falhas ou reprovações devem preservar o estado anteriormente aceito.

## 6. Testes prioritários e fixtures

| Fixture | Problema isolado | Requisito |
|---|---|---|
| `quad_t1_uniform` | célula sem vizinhos subdivididos | quatro elementos QUAD esperados se padrão central do artigo for escolhido |
| `quad_t2_one_side` | uma lateral dividida | continuidade da lateral com a célula adjacente |
| `quad_t3_opposites` | duas laterais opostas | ausência de malha não conforme |
| `quad_t4_adjacent` | duas laterais adjacentes | orientação após rotação |
| `quad_t5_three_sides` | três laterais | midpoint com único ID |
| `quad_t6_four_sides` | quatro laterais | incidência correta para os oito segmentos |
| `quad_uv_grid_2to1` | folhas de níveis diferentes | cobertura + ausência de T-junctions |
| `quad_parametric_plane` | mapeamento UV→XYZ | área/normal/qualidade correspondentes ao plano |
| `quad_parametric_curved` | superfície curvada | comparação com referência geométrica independente |
| `quad_two_patches_reverse` | curva compartilhada invertida | mesma segmentação física |
| `quad_three_patches_incident` | junção não manifold | incidência em todos os patches, sem divergência |
| `quad_reuse_reject_retry` | segunda adaptação e falha | último resultado aceito intacto |

## 7. Experimentos para o paper

- **E0:** TRI atual — baseline original.
- **E1:** QUAD no interior por templates + transição mista quando necessária.
- **E2:** malha *all-quad*, somente se implementada e qualificada.
- **E3:** QUAD anisotrópico, somente após validação do tensor de métrica e do refinamento orientado.
- Variáveis controladas: modelos, número de patches, curvas compartilhadas, tolerâncias de erro, orçamento, threads, semente, plataforma e compilador.
- Medidas: falhas, conformidade, valência/singularidades, ângulos, *scaled Jacobian*, forma física, área, razão de aspecto, erro de aproximação de posição/normais, tempo, memória e elementos. Comparações TRI/QUAD exigem equivalência de erro, não igualdade ingênua de contagens.
- Modelos iniciais: patch plano; superfície cilíndrica/selada; dois patches com inversão de orientação; três patches não manifold; Eistute/Book **somente se a entrada/representação e os oráculos forem compatíveis**.
- Publicação: distinguir **reprodução de templates 1993**, **adaptação de engenharia para superfícies** e **eventual novidade de sincronização multipatch/anisotropia**; revisar estado da arte para testar novidade.

## 8. Critérios de parada

Bloquear avanço do marco em caso de: regressão não explicada do modo TRI; topologia com fendas/interseções/IDs divergentes; atribuição de ownership ambígua; falta de oráculo independente; falha de rollback; entrada multithread não qualificada; ou declaração de qualidade/anistropia não sustentada pelas medidas.

Nunca flexibilizar critérios científicos ou prolongar limites de tempo silenciosamente para concluir um marco.

## 9. Perguntas que precisam de decisão na reunião de 11/11

1. O primeiro paper deve perseguir **quad-dominant** ou **all-quad**? Quais triângulos residuais são aceitáveis?
2. Os seis templates QUAD de 1993 devem ser reproduzidos literalmente primeiro ou podemos reformular a subdivisão de polígonos quando houver centros com qualidade inferior?
3. Qual restrição é prioritária: conformidade em curvas 2-patch, casos não manifold (>2), ou erro geométrico?
4. O algoritmo de borda de 1993 (Delaunay + merge) é suficiente para a primeira validação, ou devemos buscar um preenchimento QUAD nativo?
5. É aceitável adiar anisotropia para o segundo estágio do artigo, mantendo modelos novos e métricas amplas já na primeira submissão?
6. Quais modelos/CAD e métricas os professores consideram indispensáveis como comparação externa?

## 10. Primeira execução prática (somente após G0)

- Criar `tests/quad/` e `research/quad/` no ramo de trabalho M1, sem alterar `src`.
- Implementar primeiro uma representação de padrões que não depende de `Face` ou `TriangleAdaptive`.
- Criar oráculos das seis classes de vizinhança, suas rotações e reflexões, com saídas visualizáveis SVG/OBJ 2D.
- Testar conectividade, midpoint e cobertura antes de tentar integrar `QuadtreeCell`.
- Revisar o PR contra a branch `quad-templates`, entregar evidência e somente então iniciar M2/M3.

**Registro de honestidade:** este documento é um plano com auditoria de código e evidências históricas. Não afirma execução dos 75 CTest /526 Python, compilação nativa nem implementação QUAD, que continuam pendentes.

## 2026-11-08-05 measured milestone transition

M0-G6 applicable memory and G7 frozen serial contract inventories are complete
in their declared scopes. Reuse source-bound Node22; reject stale UV/Linux
dependencies and refresh current UV21 plus the unchanged separate UBSan/LSan
32-production/five-terminal matrix per profile. Preserve actual negatives,
accepted/rejected traces, scientific comparisons and all earlier failures.
The [memory receipt](evidence/M0_MEMORY_APPLICABILITY_20261108.json),
[serial register](M0_SERIAL_TRI_CONSUMERS.md) and dated [closure audit](M0_EVIDENCE.md)
record exact limits. The current regression count is 75 CTest /527 Python,
retaining all original 526 plus one engineering regression. Before publishing
this checkpoint, require the complete regression on its committed revision;
missing/failing evidence blocks admission. Main and Stage 3 remain unchanged.

The next work item is M1 primary-source reconstruction: independently verify
the ordered T1-T6 polygon vertices, orientations, incidences and symmetries from
Figure 7. No connectivity may be invented from the existing triangular emitter.
This admission does not approve a new geometry/curvature formula or settle
quad-dominant versus all-quad. Unresolved topology/scientific choices require
adviser alignment before executable fixtures/emission. No QUAD code exists yet.
