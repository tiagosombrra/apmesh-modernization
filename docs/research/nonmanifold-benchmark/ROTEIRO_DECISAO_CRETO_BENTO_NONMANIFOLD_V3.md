# Reunião de direcionamento — APMesh não manifold (v3)

**Data do plano:** 23/11/2026. **Natureza:** proposta para deliberação, não decisão já tomada pelos orientadores.

## Resumo objetivo

O projeto desviou esforço para modelos CAD industriais manifold (S40/M5) e para exemplos STL/QUAD, sem completar o ciclo de malhamento de um **novo modelo não manifold**. Isso não invalida os experimentos, mas **eles não demonstram a hipótese principal**. O S40 é um bom controle geométrico: 156 patches em 22/43 faces, **zero aresta CAD original com >=3 faces incidentes**. Terminar o S40 não mudará sua topologia de origem.

## Evidências concretas já disponíveis

| Modelo | Resultado confirmado | Ainda não demonstrado |
|---|---|---|
| Four-Sheet Curved, autoral | 4 patches bicúbicos completos, uma curva espacial com 4 incidências, controle OCCT e superfície analítica | Execução TRI original APMesh aceita + auditoria de conformidade |
| Tsh249, fonte externa | STEP fonte hash-lock; três arestas separadas na origem, **uma tripla somente após sewing OCCT** | Atlas Bézier completo e TRI APMesh, caso original espontaneamente não manifold |
| T/Cross autorais | Junções/atlas parciais 5/10 patches e auditorias topológicas | Malha TRI nativa e diversificação robusta |
| S40 | 43 faces STEP manifold, 22 representadas/21 pendentes | Atlas completo e geração, mas **não serve como prova não manifold** |
| CAD externo original N3 | Nenhum confirmado | Fonte original + identidade de curva 3+ + direitos + patch atlas + TRI |

## Cinco decisões que precisam ser tomadas

1. A hipótese principal é explicitamente o malhamento em **curvas incidentes a 3+ folhas distintas**? Esta é a interpretação operacional proposta.
2. Aprovar a sequência **Four-Sheet Curved → Tsh249 pós-sewing → CAD original externo 3+** e o uso do S40 exclusivamente como controle manifold?
3. Qual CAD originalmente não manifold pode ser disponibilizado com identidade de junção na fonte e direitos verificáveis? Uma fonte com múltiplos sólidos apenas tocando-se não satisfaz automaticamente a condição.
4. Fixar exigência de **aceite TRI nativo** por modelo (não apenas geometria B-Rep/patches/CI), critérios de incidência, tolerâncias, falhas e repetibilidade.
5. O componente QUAD nativo é objetivo obrigatório do trabalho agora ou linha subsequente? Não tratar pós-processamento F29/F30 como malha QUAD gerada nativamente.

## Próxima evidência solicitada

**M1:** executar `four_sheet_curved.bp` no motor TRI original, registrar aceita/rejeita, checar 4 folhas incidindo sobre a curva central e repetir. Resultado negativo também deve ser documentado sem alterar a geometria para fazê-la parecer manifold. Depois **M2**: completar atlas para as três superfícies do Tsh249 costurado e executar TRI.

A pauta acompanha [plano operacional v3](PLAN_NONMANIFOLD_FIRST_V3.md) e [registro dos modelos](MODEL_ROSTER_NONMANIFOLD_V3.csv). O plano v2 e os relatórios de S40/F27–F31 permanecem históricos e não são apagados.
