# Plano de execução v3 — NON-MANIFOLD FIRST (APMesh / doutorado)

**Revisão:** 2026-11-23. **Estado:** PROPOSTO PARA REVISÃO CIENTÍFICA; plano operacional vigente no ramo `research/benchmark-corpus-reverse-patches`, PR #225 **Draft**. **Não** constitui homologação por Creto/Bento nem autorização para merge, alteração do motor de produção ou publicação de CAD de terceiros.

> **Regra de prioridade inegociável:** a contribuição central deve ser demonstrada em complexos de superfícies com **uma curva/aresta de identidade topológica explícita incidente a três ou mais folhas distintas**. Complexidade CAD, triangulações STL, qualidade QUAD ou a palavra `non-manifold` em um nome de arquivo **não** substituem essa prova. Modelos manifold são apenas controles, não evidência positiva.

## 1. Problema e hipótese de pesquisa

**Problema:** gerar malhas triangulares adaptativas conformes em patches paramétricos Bézier que compartilham curvas não manifold, preservando identidade e orientação de cada incidência, qualidade/consistência geométrica e reprodutibilidade do algoritmo original APMesh.

**Hipótese experimental a submeter aos orientadores:** em um complexo de superfícies com junções multi-incidentes explícitas, o APMesh gera TRI com amostragem compatível nas curvas compartilhadas, sem perda/fusão de folhas, lacunas de parametrização, duplicação de arestas topológicas, inversão local ou artefatos aceitos indevidamente. Não há alegação de que a hipótese já foi demonstrada em modelo externo original.

**Método QUAD:** opcional, em linha metodológica explicitamente separada e dependente de aprovação dos orientadores. `WRITE_MODE=q` gera qualidade, não QUAD. F29–F31 são pós-processamentos/controles, nunca geração QUAD nativa.

## 2. Definições e três níveis de evidência

- **Nível N1 — CONTROLE NÃO MANIFOLD AUTORAL:** CAD/patches criados para a pesquisa, com prova OCCT/source-topology de >=3 folhas na mesma curva. Valida mecanismos, **não** prova generalização a originais independentes.
- **Nível N2 — NÃO MANIFOLD DERIVADO DE FONTE EXTERNA:** fonte externa autenticada, mas junção não manifold surge de *sewing*, imprint, split ou outra operação explicitamente documentada; identificar separadamente arestas originais e reconstruídas. Não se pode alegar que a fonte original já possuía a junção.
- **Nível N3 — NÃO MANIFOLD ORIGINAL EXTERNO:** a identidade topológica da aresta incidente a >=3 superfícies já existe no arquivo CAD original, preservando a intenção do autor. Requer direitos de uso/proveniência, auditoria independente por B-Rep e correspondência de curvas/folhas. **Ainda nenhum caso N3 qualificado.**

Uma aresta geométrica com XYZ coincidente, uma ligação somente por vértice, um artefato de triângulos quebrados, auto-interseção ou duplicação de faces **não** prova N1/N2/N3. Um complexo não manifold pode ter bordas abertas intencionais: **não** exigir Euler de um sólido manifold nem fechamento global como condição universal.

## 3. Registro de modelos e prioridade científica

| Prioridade | Modelo | Categoria | Evidência existente | Lacuna para demonstração APMesh |
|---|---|---|---|---|
| **P0-1** | **Four-Sheet Curved** (`fixtures/four_sheet_curved.bp`) | N1 autoral; não manifold por uma curva cúbica de 4 folhas | 4 patches bicúbicos / 52 controles; curva comum com 4 incidências; OCCT BRep/Sewing + geometria analítica auditados; arquivo `.bp` público | **Executar APMesh C++ TRI real**, verificar etapa aceita, 4 incidências, IDs, orientação, coordenadas/UV, reprodutibilidade e testes negativos |
| **P0-2** | **Tsh249** (`zellyn/dodgy-step-files`, `Tsh249.stp`) | N2 externo **derivado após sewing** | STEP original autenticado, três superfícies em shells separados; `EDGE_CURVE` originais distintos; OCCT com sewing não manifold tem uma aresta com 3 incidências | Construir atlas Bézier integrado para as três faces e junção costurada; validar equivalência/fidelidade; executar APMesh TRI. **Nunca rotular STEP original como N3** |
| **P1** | **Primeiro CAD de terceiros genuinamente não manifold na origem** | N3 externo original — **NÃO LOCALIZADO/QUALIFICADO** | Busca histórica e candidatos, mas zero positivos de origem confirmados | Descobrir fonte/arquivo exato + licença + SHA, provar `EDGE_CURVE`/`TopoDS_Edge` original 3+ via identidade, converter atlas completo, rodar TRI real |
| **P1** | T-Junction / Cross-Junction; Four-Sheet Planar | N1/N2 controles construídos | 5/10 patches em casos T/Cross; quatro folhas planares com curva comum; testes de B-Rep e BP de escopo limitado | Qualificar execução TRI nativa e casos de junção/reversão; não promover a corpus externo independente |
| **P2** | Novos casos autorais complexos (ramificações curvas, >=5 folhas, curvas múltiplas, trims) | N1 propostos | Nenhuma malha nativa nova admitida para essa família | Definir modelos paramétricos próprios completos somente **após P0**, com verificadores geométricos independentes |
| **P3** | **S40** | **MANIFOLD_CONTROL** industrial | STEP original auditado; **156 patches cobrindo 22/43 faces**; 21 pendentes; 264 costuras duplas e 96 lados abertos no atlas parcial | Continuar conversão 43/43 **apenas como controle de complexidade CAD**, nunca contar como caso não manifold positivo |
| **P3** | M5 / S27 / M3 | **MANIFOLD_CONTROL** industrial | M5 14 patches / 8 de 41 faces; S27/M3 sem atlas integral | Manter como controles posteriores; não disputar prioridade com P0/P1 |
| **P4** | Thingi10K #293137 | **MANIFOLD_CONTROL** STL derivado | 876 patches bilineares elevados a bicúbicos de 292 triângulos, TRI nativo F27; QUAD F29/F30 derivado | Somente regressão/qualidade e estudo de método, nunca evidência de CAD original N3 ou gerador QUAD nativo |
| **REGRESSÃO** | Book / Eistute / Decor Shelf | HISTÓRICO do artigo | Entradas `.bp` originais e métricas anteriores congeladas | Usar em testes de não regressão; não apresentar como modelo novo |

A tabela [MODEL_ROSTER_NONMANIFOLD_V3.csv](MODEL_ROSTER_NONMANIFOLD_V3.csv) é o registro operacional de **status por modelo**, incluindo o campo invariante `original_source_edge_incidence_ge3`. `yes` significa prova no **CAD original**; `derived` significa a transformação criou a junção; `authored` significa que a fonte foi criada para a pesquisa; `no` significa controle manifold; `unverified` significa evidência ausente.

## 4. Plano de entregas por portões, sem simular êxitos

### M0 — Auditoria inicial e congelamento (CONCLUÍDO EM ESCOPO DOCUMENTAL)

1. Salvar a taxonomia N1/N2/N3 e a lista dos controles manifold sem reclassificá-los.
2. Preservar F17–F31, S3.Y/S40F13 e os 23 IDs de literatura como registros históricos imutáveis.
3. Assegurar que o benchmark primário **exclui** `S40`, `M5`, `S27`, `M3`, `#293137`, e os modelos do artigo, sem apagar seus resultados.

**Saída:** este plano, matriz de modelos, critérios de aceitação e pauta dos orientadores. Não implica execução TRI nova.

### M1 — Primeiro modelo não manifold novo e completo com TRI nativo (PRÓXIMA EXECUÇÃO)

1. Entrada: arquivo autoral `four_sheet_curved.bp` existente, quatro patches, curva comum com quatro folhas, hash e orientação canônica fixados; configurações próprias isoladas daquelas do artigo.
2. Executar **CLI original compilada** sobre o `.bp` exato em diretório de saída novo, com limite explícito de recursos; registrar versões, hash binário e configuração.
3. Reconciliar por patch: `4 x 16` controles locais, quatro curvas por patch, incidência **4** da curva central, parâmetro reverso, amostras por folha, topologia das faces TRI e lado-livre intencional.
4. Exigir relatório de etapas `accepted/rejected` do motor, OBJ e incidências independentes, testes de conformidade nas amostras e no contorno, normal/área/qualidade; **não** confundir arquivo salvo de etapa rejeitada com etapa aceita.
5. Repetir em processo novo e comparar resultados/hash; registrar também falhas/timeout e controles negativos de curvas quase coincidentes e indexação adulterada.

**M1 PASS somente se** existir geração TRI **real e aceita** no APMesh sobre este modelo de 4 folhas, e um auditor independente comprovar que as quatro incidências permaneceram representadas. Se falhar, investigar defeito na geração; não substituir a entrada por S40/STL nem falsificar equivalência.

### M2 — Primeiro caso externo DERIVADO com junção tripla (EM ABERTO)

1. Reproduzir o STEP original `Tsh249.stp` com licença/digest fixos e a operação OCCT de sewing documentada; diferenciar as três arestas de origem da **única aresta tripla resultante**.
2. Converter todas as faces costuradas para patches de quatro lados, segmentando curvas comuns e preservando etiquetas de faces de origem em um sidecar. Não inferir topologia por coordenadas.
3. Validar no original e no derivado: incidência 3; orientações, medidas, curvatura/área, limites de erro, não degenerescência e múltiplas folhas.
4. Rodar CLI APMesh TRI original; gerar e auditar seus arquivos, topologia e resultados, inclusive regressão após falha.

**M2 PASS:** conversão/execução completa de um **modelo derivado de original externo**, com provenance explícita. **M2 não atende M3.**

### M3 — Primeiro não manifold externo ORIGINAL (BLOQUEADOR CIENTÍFICO)

1. Buscar arquivos CAD **com superfícies/complexos intencionalmente multi-incidentes na origem**, não apenas sólidos fechados que se tocam. Solicitar exemplos CAD autorais de não manifold aos orientadores e autores de trabalhos relacionados; investigar explicitamente o grafo de `EDGE_CURVE`/faces antes de investir na conversão.
2. Congelar arquivo, hash, commit/revisão, unidades, licença e autorização de estudo; observar que permissão de leitura não significa redistribuição no GitHub.
3. Verificador independente deve demonstrar **>=3 superfícies distintas incidindo sobre a mesma aresta do CAD original**, com semântica orientada e sem confundir números de coedges, clones e identidade por proximidade.
4. Somente após aprovação G0–G4, produzir atlas Bézier completo, sem buracos indevidos, com costuras indexadas conforme parametrização; executar APMesh TRI realmente e auditar as quatro folhas/ramificações de cada junção relevante.

**M3 PASS:** caso N3 original externo de fato encontrado e convertido/executado. Sem isso, a publicação não pode reivindicar generalização sobre fontes industriais originalmente não manifold.

### M4 — Diversidade, análise comparativa e extensão geométrica (CONDICIONAL)

Depois de M1 e, para alegações externas, M3: ampliar número/tipo de junções (3, 4, >=5 incidências), número de curvas, superfícies curvas e recortadas, escalas, orientação mista, anisotropia e falhas adversariais. Congelar corpus de validação e holdout **antes** dos ajustes. Comparar somente sobre as mesmas entradas e condições, diferenciando métricas TRI, geometria e incidência. Estudos QUAD nativos exigem aprovação e implementação independentes.

### M5 — S40 apenas em trilha de controle (NÃO BLOQUEIA M1–M3)

Conservar atlas S3.Y **156 patches / 22 de 43 faces**, sem sobrescrever o candidato. A próxima tentativa documentada é a face planar `#859` ou reavaliar `#1827/#1907` com CAD original e checagem de curva/trim, mas o avanço 43/43 **não** conta como fechamento do problema não manifold. Congelar orçamento de execução para que S40 não consuma a janela principal destinada a M1–M3.

## 5. Critérios de aceite obrigatórios por modelo (Definition of Done)

| Código | Critério / oráculo | Obrigatório para N1 | N2 | N3 |
|---|---|---|---|---|
| G0 | **JUNÇÃO NÃO MANIFOLD DE ORIGEM CLARA**: curva/aresta única, >=3 folhas distintas por identidade topológica; nível original/autoral/derivado corretamente rotulado | Sim | Sim, após derivação | **Sim, já no arquivo original** |
| G1 | Direitos, autoria, fonte, SHA-256, sem distribuição indevida | Sim | Sim | Sim |
| G2 | Grafo independente de superfícies/arestas, orientação por folha, curvas coincidentes distintas não fundidas | Sim | Sim | Sim |
| G3 | Todas as folhas/contornos pertinentes convertidos para patches Bézier, indexação das curvas compartilhadas e sidecar de origem | Sim | Sim | Sim |
| G4 | Jacobiano regular/positivo conforme orientação local, limites geométricos amostrados/rigor quando possível, domínio, recortes, áreas, feições e unidades | Sim | Sim | Sim |
| G5 | **Execução real C++ APMesh TRI**, saída da etapa aceita, topologia/qualidade/identidade da junção examinadas independentemente | Sim | Sim | Sim |
| G6 | Dois processos independentes, hashes/logs, falhas/adversariais, dependências fixadas e regressão | Sim | Sim | Sim |
| G7 | Comparação externa com entrada idêntica, densidade/feições/métricas compatíveis e referência admitida | Não para piloto | Não para piloto | Só para alegações comparativas |

**Não são critérios universais:** malha global watertight, Euler=2 ou genus0. Um complexo não manifold de superfícies abertas pode ser matematicamente correto com arestas livres intencionais; validar **links locais por folha** e contagem específica de incidências.

Estados permitidos: `SOURCE_AUTHENTICATED` → `TOPOLOGY_CONFIRMED` → `PATCH_ATLAS_COMPLETE` → `NATIVE_TRI_ACCEPTED` → `REPRODUCED`; ou `BLOCKED`, `REJECTED`, `NOT_RUN`, com evidência. **Nunca** pular um estado pelo número de testes unitários ou por resultado TRI/QUAD de outro modelo.

## 6. Regras de trabalho, prioridades e regressão

- Nenhuma alteração em `main`, release/tag, modelos terceiros no Git, baselines científicos congelados ou C++ do gerador sem aceite explícito de escopo e regressão.
- Não normalizar modelo adversarial removendo sua junção; toda correção deve preservar contagem de folhas/curvas.
- Seleção **fail-closed**: quando G0 falhar, o modelo vai para controle/negativo, nunca para corpus não manifold positivo.
- Registrar negativos e bloqueios. Sucesso da biblioteca de testes não significa uma malha real aceita.
- Modelo com superfície aberta não pode ser forçado a adquirir volume/manifoldness só para satisfazer verificadores STL usuais.
- Resultados privados de terceiros permanecem fora de GitHub/CI e de ZIP público; publicar no máximo código autoral, verificadores e recibos numéricos sem coordenadas completas.
- Não alterar documentos legados (S3, F17–F31) para retroativamente fazê-los parecer não manifold; as mudanças são aditivas e rastreáveis.

## 7. Decisões objetivas para professores Creto e Bento

1. Confirmar **não manifold por aresta/curva com >=3 folhas** como núcleo científico; discriminar junções por vértice e contatos por proximidade.
2. Aprovar N1 Four-Sheet Curved como primeiro teste TRI nativo e N2 Tsh249 como segunda etapa; exigir N3 originalmente não manifold para alegação externa?
3. Indicar ou fornecer **CAD originalmente não manifold** com 3+ folhas e direitos de uso; decidir o número mínimo de modelos/variação topológica para a tese/artigo.
4. Fixar limiares de regularidade, tolerâncias físicas/normalizadas, orçamento de malhamento e significado de conformidade em curva multi-incidente.
5. Definir se QUAD nativo integra a contribuição principal ou fica para pesquisa posterior, sem contaminar o teste TRI não manifold.

**Próximo ato verificável:** executar M1 sobre o `.bp` autoral existente, publicar somente evidência agregada e determinar `NATIVE_TRI_ACCEPTED` ou `BLOCKED`, sem desviá-lo para conversão de S40 antes do resultado.

## 8. Rastreabilidade histórica (não converter em êxitos novos)

- [Four-Sheet Curved geométrico/topológico](R3_CURVED_BICUBIC_PILOT.md) e [fixture](fixtures/four_sheet_curved.bp): N1 válido em escopo geométrico/OCCT, `NATIVE_TRI_ACCEPTED=NOT_RUN` no registro anterior.
- [Tsh249 costura original auditada](S40F13_TSH249_ORIGINAL_NATIVE_SEWING_AUDIT.md): N2 após sewing, `original_source_edge_incidence_ge3=no`, sem atlas completo/TRI nativos.
- [S40 lacunas](S3Z4_S40_NATIVE_TRIAL_AND_21_FACE_REGISTER.md): manifold controle 22/43, `NATIVE_TRI_ACCEPTED=NOT_RUN` para S40 integral.
- [F31 QUAD RFC](THINGI10K_F31_NATIVE_QUAD_RESEARCH_DECISION.md): modelos fechados sintéticos de qualidade QUAD não são evidência de junções não manifold originais.
- [Protocolo histórico](MODEL_ADMISSION_PROTOCOL.md), [decisões](RISK_AND_DECISION_REGISTER.md), [estratégia v2 substituída](SCIENTIFIC_MODEL_SELECTION_V2.md). Registros de resultados passados permanecem preservados.
