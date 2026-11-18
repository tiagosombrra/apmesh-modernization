# S40-F3 — Correção da métrica de ajuste de curvas circulares no piloto S40

**18/11/2026.** Escopo: alteração de algoritmo do conversor de pesquisa, ensaio com primitivas reais OCP e regressão hermética. **Não é admissão de nova face STEP, execução de TRI/QUAD do APMesh, nem prova contínua de Hausdorff.** Preservar a branch de pesquisa e o PR #225 como draft; não integrar à `main`.

## Defeito identificado

A rotina `fit_circle_source_segments` de `s40f1_six_edge_planar_builder.py` empregava a comparação

`||B(t) - C(a + (b-a)t)||`, com `t` de 0 a 1,

como se o parâmetro do polinômio Bézier cúbico correspondesse linearmente ao ângulo da circunferência nativa. **As duas parametrizações são diferentes:** curvas geometricamente próximas podem apresentar diferenças tangenciais elevadas em pontos de mesmo parâmetro. Essa métrica não mede, por si só, a distância da curva aproximada ao conjunto geométrico da aresta original, e pode forçar subdivisão artificial.

O ensaio com uma **aresta OCP verdadeira**, raio 6 mm e amplitude angular 45°, observou (129 amostras) aproximadamente:

| Comparação | Máximo observado |
| --- | ---: |
| Avaliação em parâmetros sincronizados | 0,005739118302 mm |
| Distância de pontos Bézier à aresta original recortada | 0,000025473041 mm |
| Número de segmentos por aresta com ajuste corrigido | **1** |

A inspeção do STEP original pinado `i25o_s40.step` (SHA-256 `b79eb5be1fde71b6a8d086fe14800a1ec62e3a3c4618910c81c64d23718abf3b`), no commit upstream `8f00f02579037cc893042f2ee2c910b20e3fb1b0`, encontrou **quatro arcos originais CIRCLE de raio 6 mm e amplitude aproximada de 45°**: original EDGE_CURVE `#1307`, `#1336` no `ADVANCED_FACE #1279`, e `#1415`, `#1444` no `ADVANCED_FACE #1386`. A inspeção usou entidades STEP de centro, normal e extremos, não um BP privado reconstruído. A cobertura nativa completa das duas faces permanece não executada nesta sessão.

## Correção

Em cada um dos 33 pontos amostrados por segmento, a rotina agora usa `curve_distance(curve, p, divisions=64)`: uma busca conservadora pela menor distância do ponto Bézier à **faixa paramétrica nativa recortada** da mesma aresta OCP, com avaliação de grade e minimização limitada. A validação admite o segmento somente se o erro **amostrado** ficar abaixo de 75% do orçamento pré-declarado de **0,001 mm**, mantendo margem para o restante das verificações.

A checagem de continuidade por identidade dos controles, limites de 64 segmentos por aresta, matching dos vértices STEP, costuras com dois lados, classificação `IN/ON` na face nativa, área/Jacobiano e rejeição por status incorreto permanecem inalteradas. Os controles extremos da curva continuam vinculados à aresta original. O perfil de subdivisão passa a obedecer à geometria real em vez de à velocidade paramétrica.

O avaliador geométrico é uma **verificação amostrada e numérica**. Embora a busca produza um ponto existente na aresta original, a amostragem discreta em `t` não dá um limite superior contínuo certificado para todo o segmento Bézier. Não autoriza alterar a tolerância, admitir faces em lote ou concluir equivalência exata ao CAD.

## Execuções realizadas

- **S40-F1/F2/F3: 79/79 testes, 0 falhas**, em um processo: 69 regressivos anteriores e dez novos testes OCP independentes.
- **S3.Z.4: 102/102 testes, 0 falhas**, em processo separado, sem STEP/BP industrial.
- Teste adversarial de aresta circular com mesmo suporte geométrico, mas **intervalo paramétrico diferente**, confirma que a busca rejeita um arco fora do recorte original. Teste com controle Bézier deslocado para fora do plano também falha como esperado.
- Arquivos privados exigidos para S40-F3 **não estão acessíveis neste ambiente**: BP S3.Y selecionado e manifesto. O STEP original foi consultado por conteúdo no GitHub, mas **não foi importado como `TopoDS_Shape` para esse ensaio**. Nenhum BP industrial novo foi emitido.

## Estado preservado e próximo gate

Último BP experimental admitido, **S3.Y**: **156 patches Bézier, 1.665 controles, 22/43 faces originais**, SHA-256 privado `af50597db4b8d7b3bcb2fc381596fefc95ba6b6e00ed169576bec7a6b7873177`. Nenhuma nova face foi admitida na S40-F3.

Para testar a nova métrica no modelo original: recuperar esse BP selecionado e seu manifesto, conferir o SHA exato do original STEP, executar a S40-F3 em `#1279/#1386`, exigir costuras indexadas, classificação nativa, erro de curva e cobertura amostral e repetir a auditoria independente do atlas inteiro. Se a entrada não existir, **falhar explicitamente** e não criar um candidato classificado como admitido.
