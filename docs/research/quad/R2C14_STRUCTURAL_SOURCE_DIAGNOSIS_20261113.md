# R2c-14 — Diagnóstico estrutural dos candidatos TRI recusados pelo gerador original

**Data:** 2026-11-13. **Entrada auditável:** [GitHub Actions #43504972443](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43504972443), 4/4 jobs SUCCESS e [artefato original #14077445183](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43504972443/artifacts/14077445183), contendo `r2c14_generator_rejection_forensics.json`, seis logs de execução e os CSV originais de aceitação/curvas/patches. **Contexto:** [MILESTONE_STATUS.md](MILESTONE_STATUS.md).

## Medições originais, não conjecturas

| Original / perfil | Etapa rejeitada | Patches no estado estrutural do gerador | Elementos anteriores → candidatos | Resultado do critério global |
|---|---|---|---|---|
| Eistute / artigo | 2 | 4/4 `ok`, modo `micro_refinement` | 1.168 → 2.008 | Erro aumentou ~24,9%; rejeitado |
| Eistute / artigo | 3 | 4/4 `ok`, modo `micro_refinement` | 1.168 → 2.196 | Erro aumentou ~20,2%; rejeitado |
| Eistute / artigo | 4 | 4/4 `curve_transition_needs_retry`, modo `interior_quality_recovery` | 1.168 → 7.216 | Erro reduziu ~83,9%; crescimento 6,178× e coerência de transição insuficiente |
| Book / artigo | 2–3 | 28/28 `degenerate_needs_retry`, modo `normal` | 4.256 → 19.774 | Erro aumentou ~300,4%; malha 4,646× |
| Book / estável alternativo | 1 | 28/28 `ok`, modo `normal` | 112 → 896 | Rejeitado; nenhuma etapa aceita nesse perfil |
| Book / estável alternativo | 2–3 | 28/28 `ok`, modo `curve_spacing_follow` | 112 → 784 | Erro reduziu ~33,8%, mas malha 7× e overshoot global ≈6,863 |
| Book / estável alternativo | 4 | 28/28 `curve_transition_needs_retry`, modo `curve_transition_repaired` | 112 → 784 | Erro reduziu ~33,8%; rejeitado |

A classificação `degenerate_needs_retry` é uma **saída diagnóstica do gerador**, não demonstra por si só a existência de elementos geométricos degenerados na malha final. Os rótulos vêm do campo original `generation_status_structural` dos CSV de cada patch; os totais vêm de `elements_prev` e `elements_current`, sem extrapolação.

## Separação das causas e próximos controles de engenharia

**Eistute, passos 2–3:** A malha gerada é marcada como estruturalmente `ok`, mas o erro global piora. Não se pode concluir que o problema seja exclusivamente um contorno ou orçamento: medir a relação entre `micro_refinement`, redistribuição de elementos e erro de aproximação.

**Eistute, passo 4:** Todos os quatro patches sinalizam `curve_transition_needs_retry`; o indicador de transição sub-resolvida é **1,0**. Aumentar indiscriminadamente os pontos de curva não resolve a incoerência, apesar de `actual_curve_points >= target_curve_points` no CSV. A correção deve respeitar a sincronização de fonte entre patches e o orçamento global de elementos.

**Book, configuração original:** Todos os 28 patches sinalizam `degenerate_needs_retry` em duas tentativas idênticas, com os mesmos CSV de curva e patch, e sem modificação da última malha aceita. A prioridade é localizar a origem e semântica exatas dessa classificação no caminho nativo Quadtree/AFT. Não marcar como `ok` artificialmente nem promover a malha rejeitada.

**Book, configuração estável exploratória:** Há 28/28 patches estruturalmente `ok` nos passos 2–3, mas **784 elementos foram gerados para uma meta global registrada de aproximadamente 114,24**, ao mesmo tempo em que o orçamento local dos patches está registrado como 2.600. Esse desencontro de escalas precisa de auditoria do cálculo de `target_elements_step`, `local_patch_budget` e dos limites reais do refinamento, sem supor automaticamente que o orçamento local seja aplicado da maneira desejada.

## Validação e limites

Os arquivos originais de artigo, modelos `.bp`, código do gerador TRI, critérios de aceitação e pesos de qualidade permanecem inalterados. A verificação R2c-15 confronta os logs com desigualdades literais do código para distinguir violações demonstráveis dos booleanos não observados. Esses resultados de diagnóstico **não satisfazem M7**: nenhum modelo completou duas épocas originais aceitas em sequência. A autorização de soldagem de nós nas junções non-manifold continua separadamente pendente no M6.

**Próximo gate após R2c-15:** teste experimental limitado e opt-in do gerenciamento de crescimento/transition retry baseado nas métricas medidas, mantendo o modo TRI original como referência congelada e exigindo dois commits reais `AcceptedMeshScope::Commit` antes de qualquer afirmação de êxito.
