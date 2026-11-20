# S40-F7 — Reconciliação indexada de quatro faces com o atlas S3.Y

**Checkpoint:** 18/11/2026. **Classificação:** implementação de um portão de união estrutural e de auditoria nativa, com testes sintéticos e uso privado da ilha S40-F6. **Não houve admissão de novas faces no atlas S3.Y.**

## Proveniência congelada

- STEP original `cgg-bern/hex-me-if-you-can/original/i25o_s40.step`, revisão `8f00f02579037cc893042f2ee2c910b20e3fb1b0`, SHA-256 `b79eb5be1fde71b6a8d086fe14800a1ec62e3a3c4618910c81c64d23718abf3b`.
- Atlas S3.Y anteriormente admitido: **156 patches, 1.665 controles, 264 costuras indexadas bilaterais, 96 lados abertos, 22/43 faces originais**. SHA-256 do BP privado `af50597db4b8d7b3bcb2fc381596fefc95ba6b6e00ed169576bec7a6b7873177`.
- Ilha S40-F6: **8 patches, 104 controles, 6 costuras internas, 20 lados abertos**, representando isoladamente faces originais `#1279`, `#1386`, `#3269` e `#3485`. SHA-256 do BP privado `72b8756c948a7a7da19c9f2a9a7099673e81a30573f19e4820abf27ba720f0a7`.
- O STEP original e o BP S3.Y **não estavam montados** durante os testes locais desta etapa; o pacote F6 privado estava presente e teve seus bytes conferidos.

## Oito interfaces necessárias

A ilha F6 possui **oito lados externos** que representam arestas originais já utilizadas por uma face do S3.Y. Os demais 12 lados permanecem abertos até próximas conversões.

| EDGE_CURVE original | Face da ilha | Proprietária S3.Y | Chave indexada F6 |
| ---: | ---: | ---: | --- |
| `#1002` | `#1279` | `#912` | `old:1002` |
| `#1080` | `#1386` | `#912` | `old:1080` |
| `#1139` | `#1279` | `#1105` | `old:1139` |
| `#1259` | `#1386` | `#1230` | `old:1259` |
| `#1284` | `#1279` | `#3737` | `old:1284` |
| `#1473` | `#1386` | `#3737` | `old:1473` |
| `#1030` | `#3485` | `#912` | `new:1030:0` |
| `#1057` | `#3269` | `#912` | `new:1057:0` |

As oito interfaces usam **26 controles locais distintos** da ilha, em vez de 32, pois alguns vértices originais são comuns a mais de uma aresta. **Não deve haver soldagem por proximidade**: cada controle compartilhado deve apontar para o mesmo índice global do pai, por vínculo de identidade da aresta original e orientação oposta.

## União implementada (S40-F7)

O módulo `probes/s40f7_parent_lineage_rebase.py` fornece:

1. Pré-validação dos hashes binários congelados e das cardinalidades do pai e da ilha.
2. Análise independente do grafo de arestas do STEP, com **43 faces, 117 EDGE_CURVE e incidência máxima 2**; cada uma das oito arestas deve ter os proprietários originais da tabela e tipo geométrico `LINE`.
3. Descoberta automática das oito correspondências, caso não seja fornecido um manifesto: importação do STEP original pelo Open CASCADE, bijeção original–nativa independente (`s3s_full_original_face_census.full_correspondence`) e recuperação de **um único lado indexado aberto por aresta**, via `s40f1_six_edge_planar_builder.recover_inherited_source_chain`. Se houver mais de um segmento, ambiguidade, divergência de proprietário ou correspondência ausente, a operação é bloqueada.
4. Alternativamente, leitura de manifesto de linhagem explicitamente vinculado ao SHA do BP pai e aos **IDs de face proprietária** originais. O manifesto não se substitui ao teste nativo.
5. Verificação do sentido CCW das interfaces, dos 26 IDs compartilhados, da distância entre todos os controles correspondentes (limite de compatibilidade de **1e-8 mm** para a união por reindexação, distinto do orçamento geométrico de 0,001 mm), e da preservação **exata** dos 156 patches e 1.665 controles existentes.
6. Construção de um BP **CANDIDATO**, com os controles novos acrescentados após os controles do S3.Y, sem alterar a prefixação anterior.
7. **Portão nativo obrigatório antes de gravar o candidato**: verificação da proprietária de cada lado herdado dentro de sua face original, cobertura amostrada das quatro faces originais importadas, orientação dos Jacobianos, área, recorte `IN/ON`, geometria planar e distância **bidirecional amostrada** às arestas nativas originais. Ele não substitui certificação Hausdorff contínua, regressão C++ ou execução TRI/QUAD.

**Cardinalidades previstas condicionais, não medidas sobre o pai real:**

| Métrica | S3.Y aceito | Acréscimo líquido da ilha F6 | Candidato S40-F7 se todos os portões passarem |
| --- | ---: | ---: | ---: |
| Faces originais representadas | 22 | +4 | **26/43** |
| Patches Bézier | 156 | +8 | **164** |
| Controles globais | 1.665 | +78 (104 − 26 compartilhados) | **1.743** |
| Costuras bilaterais | 264 | +14 (6 internas + 8 S3.Y) | **278** |
| Lados abertos | 96 | +4 (20 na ilha − 16 lados emparelhados) | **100** |

Esses números são um **contrato topológico**; não comprovam que o S3.Y existente usa as mesmas oito curvas cúbicas. Se o pai representar alguma dessas arestas com segmentação diferente, orientação inválida ou parametrização cúbica incompatível, o portão falhará sem modificar o BP aceito. Uma refatoração de parâmetros ou subdivisão conjunta precisará ser estudada separadamente.

## Testes e limites atuais

- **S40-F7: 33/33 PASS**, incluindo testes sintéticos de ligação, orientação e rejeição, e testes da ilha privada F6 com BP byte-pinned. Não foi utilizado o BP S3.Y real.
- **Regressão S40-F6: 37/37 PASS** com especificações privadas F5/F6.
- **Regressão S40-F5: 33/33 PASS** com especificação privada F5.
- **103/103 PASS no total, em três processos separados**. Isso não é uma execução completa do APMesh C++.
- Quando a ilha F6 privada não está presente, os quatro testes privados dessa classe são explicitamente pulados; não podem ser contados como sucesso do original.
- O preflight com STEP e pai ausentes retorna **código de saída 3**, registra `BLOCKED_NO_NATIVE_ADMISSION` e não cria um BP candidato.
- O portão de auditoria original nativa foi implementado, mas **NÃO EXECUTADO** neste checkpoint por ausência do STEP integral montado e do BP S3.Y privado.

## Reprodução privada (a partir do checkout da branch de pesquisa)

```bash
cd docs/research/nonmanifold-benchmark/probes
python -m unittest -v test_s40f7_parent_lineage_rebase

python s40f7_parent_lineage_rebase.py \
  --original-step /private/original/i25o_s40.step \
  --s3y-bp /private/s3y/s40_selected_156_patches.bp \
  --island-f6-bp /private/s40f6/s40f6_four_face_source_island.PRIVATE.bp \
  --island-f6-receipt /private/s40f6/s40f6_source_island.PRIVATE.json \
  --output-dir /private/s40f7
```

O parâmetro `--parent-source-lineage` é **opcional**: sem ele, a descoberta utiliza as faces e as arestas originais. No modo opcional explícito, o manifesto deve ter o esquema `apmesh-s40f7-original-s40-parent-edge-lineage-v1`, os hashes corretos e as oito associações `patch`/`side`/`original_parent_face_id`.

**Resultado esperado apenas se os arquivos e os portões existirem e passarem:** `s40f7_s40_source_joined.CANDIDATE.bp` e `s40f7_structural_join_receipt.json`. Os nomes são deliberadamente `CANDIDATE`: os testes amostrados e a correspondência original não homologam automaticamente geração TRI/QUAD ou uso em produção.

## Decisão

**S40-F7 (código e portão de reconciliação): IMPLEMENTADO E TESTADO.**

**S40-F7 (importação do original e união com S3.Y): BLOQUEADO — DADOS PRIVADOS INDISPONÍVEIS.**

**Atlas de pesquisa efetivamente aceito permanece em 156 patches e 22/43 faces.** Não mover o PR #225 para merge, não alterar `main` ou publicar controles derivados de terceiros antes da revisão de direitos.
