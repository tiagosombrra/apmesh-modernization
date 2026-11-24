# S40-F4 — Cobertura bidirecional das curvas STEP e reconstrução privada determinística do atlas S3.Y

**Checkpoint:** 18/11/2026. **Status:** algoritmo/testes aprovados; **nenhuma nova face industrial admitida**. Branch de pesquisa `research/benchmark-corpus-reverse-patches`, PR #225 permanece `draft`. Não há alteração autorizada no gerador C++ ou na `main`.

## Estado científico congelado

O modelo industrial original `i25o_s40.step`, repositório `cgg-bern/hex-me-if-you-can`, revisão `8f00f02579037cc893042f2ee2c910b20e3fb1b0`, tem hash SHA-256 `b79eb5be1fde71b6a8d086fe14800a1ec62e3a3c4618910c81c64d23718abf3b`. O BP parcial S3.W de 148 patches exige SHA-256 `c826487d8cee76f6649100c59e5ce84fa6cb43c9004f53c68e3e565e86cdb174`. Seu filho S3.Y aprovado experimentalmente exige SHA-256 `af50597db4b8d7b3bcb2fc381596fefc95ba6b6e00ed169576bec7a6b7873177` e mantém **156 patches, 1.665 controles e 22 das 43 faces STEP** originais representadas. Não são equivalentes a um modelo integralmente convertido, tampouco a uma malha TRI/QUAD aceita.

## Problema: distância unilateral não garante cobertura da aresta fonte

A implementação S40-F3 corrigiu a comparação por parâmetros sincronizados da curva Bézier e da circunferência nativa, adotando a distância geométrica dos pontos Bézier até a aresta original recortada. Mas uma **subcurva** poderia satisfazer esse teste unilateral sem alcançar o restante da aresta STEP. Para admitir a geometria seria necessário avaliar ambas as direções.

A implementação S40-F4 introduz:

- `bezier_segment_distance(net, xyz)`: projeção numérica de um ponto original sobre um segmento Bézier cúbico delimitado, combinando busca inicial em grade e otimização local, com validação de controles, densidade e coordenadas finitas.
- `native_curve_to_bezier_chain_distance(curve, segments)`: amostragem paramétrica da **aresta STEP recortada**, incluindo ambos os extremos, e minimização da distância a **todos** os segmentos da cadeia. A cadeia é tratada como conjunto geométrico, independentemente da parametrização.
- `fit_circle_source_segments`: só admite uma subdivisão circular se **ambas as direções amostradas** respeitarem 75% do orçamento congelado de **0,001 mm**.
- `recover_inherited_source_chain`: acrescenta verificação inversa da cadeia indexada herdada, para rejeitar lacunas em arestas já representadas por patches anteriores. Não modifica os controles existentes.

A otimização escalar e a amostragem continuam **numéricas e discretas**. A recíproca não fornece um limite superior de Hausdorff contínuo, prova formal de recorte STEP, orientação global garantida ou certificado de malha. Nenhum desses resultados deve ser inferido dos testes unitários.

## Ensaios de origem: quatro arcos originais de raio 6 mm

A consulta às entidades fonte originais verificou os quatro `EDGE_CURVE` relevantes:

| ADVANCED_FACE | EDGE_CURVE | Centro XYZ (mm) | Normal | Ângulo (graus) | Raio |
|---|---|---|---|---:|---:|
| `#1279` | `#1307` | `(-22, -67.17767, -33.75)` | `(0,0,-1)` | 90–135 | 6 mm |
| `#1279` | `#1336` | `(-22, -67.17767, -33.75)` | `(0,0,-1)` | 135–180 | 6 mm |
| `#1386` | `#1415` | `(22, -67.17767, -33.75)` | `(0,0,-1)` | 0–45 | 6 mm |
| `#1386` | `#1444` | `(22, -67.17767, -33.75)` | `(0,0,-1)` | 45–90 | 6 mm |

As propriedades de centro, raio, eixo e vértices foram verificadas por leitura das entidades STEP reais. O teste local **reconstrói esses arcos como primitivas independentes OCP**, porém **não importa o STEP original completo nem o BP privado**. Cada arco foi representado por um único segmento cúbico. Entre os ensaios reconstruídos, a diferença amostrada nas duas direções foi aproximadamente `2,54 × 10⁻⁵ mm`, abaixo de `0,001 mm`.

Um adversário que representa apenas a metade inicial de um arco passa na direção Bézier→aresta, mas falha na nova direção aresta→Bézier. Outros testes rejeitam curva de centro diferente, controle alterado, amostragem inválida, dados não finitos e cadeia ausente.

## Destravamento do BP privado — replay de S3.W para S3.Y

A execução original depende do atlas S3.Y privado, ausente no runtime atual. A nova ferramenta `s40f4_private_s3y_replay.py` aceita o **ZIP privado anterior S3.W** sem exigir o BP S3.Y isolado:

1. Verifica o hash do STEP original e encontra no ZIP exatamente um BP S3.W e seu manifesto (sem extração insegura de caminhos, links ou entrada ambígua).
2. Confere SHA-256 do BP, cardinalidade `148/1619`, manifesto e preservação do furo `#218`.
3. Executa o **construtor público S3.Y** sobre a face `#3044`, com as densidades nativas declaradas anteriormente e sem relaxar limites.
4. Exige exatamente o hash do filho selecionado S3.Y (`af505...`), cardinalidade `156/1665`, recibo nativo `PASS` e zero `OUT`.
5. Somente após todas as verificações grava a saída na **pasta privada local**; erro ou divergência retorna `BLOCKED`, sem fabricar atlas admitido.

**Exemplo de execução privada, após disponibilizar os três arquivos locais:**

```bash
python s40f4_private_s3y_replay.py \
  --original-step /private/original/i25o_s40.step \
  --s3w-private-zip /private/bundles/APMesh_S3W_S40_Original_Spline_Repair_20261117.zip \
  --s3y-builder /repo/docs/research/nonmanifold-benchmark/probes/s3y_s40_curved_planar_rings.py \
  --private-output-dir /private/replay/s40_s3y_selected

# Continue only if the preceding replay returned the READY state.
python /repo/docs/research/nonmanifold-benchmark/probes/s40f1_six_edge_planar_builder.py \
  --original-step /private/original/i25o_s40.step \
  --selected-s3y-bp /private/replay/s40_s3y_selected/s40_selected_s3y.partial.bp \
  --selected-s3y-manifest /private/replay/s40_s3y_selected/s40_selected_s3y_manifest.json \
  --output /private/trials/s40f4_1279_1386
```

Esta ferramenta foi testada com *bytes sintéticos*, ZIPs de teste e um construtor simulado; não foi executada com o ZIP S3.W verdadeiro. O STEP original e os dados derivados **não devem ser publicados** no GitHub até a revisão dos direitos de distribuição.

## Auditoria executada nesta sessão

- **108/108 testes S40-F1/F2/F3/F4**, 0 falhas, executados em um processo (79 anteriores + 15 novos de cobertura bidirecional + 14 novos de replay privado).
- **102/102 regressões S3.Z.4**, 0 falhas, executadas em outro processo. **210/210 em dois processos**, não uma execução de toda a pesquisa nem um teste C++.
- Sintéticos adversariais verificaram falha por hash STEP/BP, manifesto adulterado, entrada ZIP ambígua, arquivo ausente, construtor externo reprovado, saída filho com SHA incorreto e erro nativo simulado.
- STEP original consultado em GitHub e quatro arcos identificados em suas entidades; a geometria local foi reconstruída em Open CASCADE a partir desses descritores, **não carregada como `TopoDS_Face` original**.
- **Nenhum STEP industrial BP+CAD executado nesta etapa**, nenhum novo BP original criado, nenhuma face original admitida, nenhuma malha TRI/QUAD gerada pelo APMesh.

## Decisão e próximo marco

Permanece a referência S3.Y: **156 patches, 22/43 faces originais**. O próximo avanço real depende de obter **o ZIP privado S3.W ou o BP S3.Y** e o STEP original para auditoria nativa. A nova ferramenta permite reproduzir deterministicamente o S3.Y a partir do ZIP antigo. Depois de verificar as novas faces `#1279` e `#1386` com seus respectivos vizinhos e a cobertura original, poderá ser proposto um candidato 24/43, ainda sujeito a controle de qualidade e geração efetiva de malhas.
