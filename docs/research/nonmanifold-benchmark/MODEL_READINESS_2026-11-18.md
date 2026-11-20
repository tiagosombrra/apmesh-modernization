# APMesh — Modelos selecionados e matriz de prontidão experimental

**Data da revisão:** 18/11/2026. **Escopo:** planejamento de pesquisa do doutorado; não constitui homologação científica ou aprovação dos orientadores. Base da revisão: `tiagosombrra/apmesh-modernization`, branch `research/benchmark-corpus-reverse-patches`, PR #225 (draft), documentação S1, S3.K, S3.Y, S3.Z.3 e `SCIENTIFIC_MODEL_SELECTION_V2.md`.

## Decisão do corpus: quatro modelos CAD reais, com papéis distintos

| Ordem | CAD original (MAMBO/HexMe) | Faces STEP originais | Arestas STEP originais | Verificação CAD nativa | Reconstrução Bézier de pesquisa | Geração TRI/QUAD do APMesh | Papel científico |
|---|---|---:|---:|---|---|---|---|
| 1 | **M5** — `i05o_m5.step` | 41 | 102 (mais seis arestas degeneradas na importação nativa) | Importado como sólido válido, incidências auditadas | **14 patches / 8 faces** no piloto de 4 setores; 18 patches em variante de 6 setores | **Não executada/qualificada** sobre o CAD completo | Variedade de superfícies: planos, cilindros, cones e toro |
| 2 | **S40** — `i25o_s40.step` | 43 | 117 | Importado como sólido válido, face/aresta/vértice auditados | **156 patches / 22 faces** no atlas S3.Y; 21 faces ainda pendentes | **Não executada/qualificada** sobre o CAD completo | Recortes B-spline, curvas compartilhadas e quadrangulações locais |
| 3 | **S27** — `i22o_s27.step` | 52 | 144 | Importado como sólido válido, incidências auditadas | **Sem atlas Bézier integrado qualificado**; triagem planar inicial, não conversão | **Não executada/qualificada** | Densidade de arestas/restrições e feições mecânicas |
| 4 | **M3** — `i03o_m3.step` | 60 | 169 | Importado como sólido válido, incidências auditadas | **Sem atlas Bézier integrado qualificado**; triagem planar inicial, não conversão | **Não executada/qualificada** | Maior quantidade de faces; predomínio de planos e cilindros |

**Não são modelos industriais non-manifold positivos:** os quatro originais têm no máximo duas faces distintas incidentes por aresta nativa/STEP. A investigação de uma fonte externa intencional com curva de incidência **≥3 folhas** continua bloqueadora para alegações de generalização topológica.

## Originais e proveniência congelada

Todos os originais são do repositório público [`cgg-bern/hex-me-if-you-can`](https://github.com/cgg-bern/hex-me-if-you-can/tree/8f00f02579037cc893042f2ee2c910b20e3fb1b0/original), revisão `8f00f02579037cc893042f2ee2c910b20e3fb1b0`, como auditados na S1. Os STEP de terceiros **não foram incorporados ao repositório de pesquisa**; permissões específicas de redistribuição precisam ser revisadas.

| Modelo | SHA-256 do STEP original |
|---|---|
| M5 | `895f67c0669096b287077ac1bb56dad0e117cd96f78334d3129d783fd78b96cb` |
| S40 | `b79eb5be1fde71b6a8d086fe14800a1ec62e3a3c4618910c81c64d23718abf3b` |
| S27 | `b4a60c43cabd3c72bf61d54a23f36e6e539ad985015d2a7c377885b5d170f8c5` |
| M3 | `c42862fa6bc1e94a9bb70e43a7dc9901aa5281d7b58de6ee4699494088286008` |

**Galeria das geometrias originais** — [`mambo_originals_native_gallery.png`](https://github.com/tiagosombrra/apmesh-modernization/blob/research/benchmark-corpus-reverse-patches/docs/research/nonmanifold-benchmark/gallery/source_cad/mambo_originals_native_gallery.png). Imagens individuais: [`M5`](https://github.com/tiagosombrra/apmesh-modernization/blob/research/benchmark-corpus-reverse-patches/docs/research/nonmanifold-benchmark/gallery/source_cad/m5_source_cad.png), [`S40`](https://github.com/tiagosombrra/apmesh-modernization/blob/research/benchmark-corpus-reverse-patches/docs/research/nonmanifold-benchmark/gallery/source_cad/s40_source_cad.png), [`S27`](https://github.com/tiagosombrra/apmesh-modernization/blob/research/benchmark-corpus-reverse-patches/docs/research/nonmanifold-benchmark/gallery/source_cad/s27_source_cad.png), [`M3`](https://github.com/tiagosombrra/apmesh-modernization/blob/research/benchmark-corpus-reverse-patches/docs/research/nonmanifold-benchmark/gallery/source_cad/m3_source_cad.png). São renderizações do CAD original, não malhas produzidas pelo APMesh.

## Duas outras populações a preservar no experimento

**Modelos históricos do artigo:** Book, Eistute e Decor Shelf — baselines congelados para comparabilidade e regressão. Não tratar como novos benchmarks externos sem revalidar executáveis/entrada/saída. A alegação de resultado TRI novo não está sustentada pelo conjunto S3.

**Controles sintéticos de topologia:** três caixas, múltiplas folhas, T/Cross e casos com curvas compartilhadas — úteis para testes adversariais de incidência e orientação, mas não substituem exemplo externo genuíno de geometria não manifold.

**Exemplos suplementares ou negativos:** M1, S8 e Quarter Torus — pré-analisados; não devem ser descritos como holdouts inéditos. Nenhum dos quatro CAD MAMBO principais prova a existência de uma aresta com três folhas intencionais.

## Critério operacional de 'modelo pronto'

1. **CAD REAL AUDITADO:** STEP de origem com hash, importação OCCT, topologia e figuras da peça real disponíveis — **M5, S40, S27 e M3 atendem** neste escopo.
2. **ATLAS BÉZIER PARCIAL AUDITADO:** somente superfícies e arestas já admitidas em etapa experimental — **M5 e S40 atendem parcialmente**; 33/41 e 21/43 faces continuam faltando, respectivamente.
3. **ENTRADA COMPLETA PARA MALHAMENTO ORIGINAL:** atlas completo, fronteiras conformes, recortes sem buracos indevidos, erro geométrico cientificamente definido e todas as faces originais representadas — **nenhum dos quatro atende**.
4. **SAÍDA REAL DO APMesh VALIDADA:** executar C++ TRI/QUAD contra essa mesma entrada, confirmar aceite, incidência, qualidade e regressão, com logs e hashes — **não demonstrada para os quatro CAD completos**.
5. **POSITIVE NON-MANIFOLD EXTERNO:** fonte independente original com pelo menos uma aresta intencional incidente a três ou mais folhas — **nenhum selecionado/homologado**.

Não equiparar `testes de unidade aprovados` com `modelo CAD completo` ou `malha gerada`; não confundir topologia manifold complexa com topologia non-manifold.

## Continuação recomendada do plano — trilhas paralelas, com gates

- **P0 — Recuperar os dados originais privados antes de novas admissões S3.Z.4.** É necessário o STEP S40, o BP S3.W e seu manifesto, e o construtor S3.Y. O pacote S3.Z.3 documenta **83 testes herméticos** válidos, mas ainda **sem corrida nativa S40**; nenhuma face foi acrescentada por essa etapa. Preservar o atlas S3.Y de **156 patches/22 faces** como referência.
- **P1 — Integrar e qualificar um ciclo real APMesh TRI no conjunto de pesquisa**, quando houver uma entrada integral legitimamente admitida; priorizar reproduzir Book/Eistute/Decor Shelf com baselines congelados separadamente, em vez de apresentar o S40 incompleto como apto a malhar.
- **P1 — Buscar imediatamente um original non-manifold positivo** (≥3 folhas incidentes sobre uma aresta original), com fonte, orientação, objetivo geométrico e direitos claros. Uma montagem derivada de sólidos manifold deve ser rotulada como derivada, jamais original positivo.
- **P2 — Evoluir a representação do S40 e M5** com reconciliação e validação das curvas compartilhadas, evitando aumentar tolerâncias após observar falhas. Adicionar S27 e M3 em segundo momento para casos de generalização geométrica e comparabilidade pré-definida.
- **P3 — Congelar métricas e matrizes experimentais:** tipos de superfícies, proporção de faces admitidas, tolerância local e normalizada, curvas compartilhadas, qualidade TRI/QUAD, falhas de geração e reprodutibilidade. Não reivindicar melhoria comparativa sem mesmos domínios, restrições e ambiente.

**Síntese de decisão:** os quatro CAD estão prontos como referências de entrada e apresentações visuais; S40 e M5 têm BP parcial de pesquisa; **nenhum dos quatro está pronto como demonstração completa do malhador nem como non-manifold original positivo**. Manter PR #225 como draft e não fazer merge em `main`.
