# Pesquisa APMesh — NON-MANIFOLD FIRST

**Entrada única da frente de pesquisa.** O objetivo principal é malhamento de complexos de superfícies com curva topológica compartilhada por três ou mais folhas distintas. S40 e outros CAD manifold permanecem controles; relatórios anteriores não são novas admissões.

| Necessidade | Fonte oficial |
|---|---|
| Hipótese, critérios G0–G7, sequência M0–M5, riscos e procedimento de regressão | [Plano vigente v3](PLAN_NONMANIFOLD_FIRST_V3.md) |
| Status e bloqueador por modelo | [Matriz v3](MODEL_ROSTER_NONMANIFOLD_V3.csv) |
| Decisões com orientadores | [Pauta científica v3](ROTEIRO_DECISAO_CRETO_BENTO_NONMANIFOLD_V3.md) |
| Regressão consolidada e cobertura | [Auditoria de 24/11/2026](AUDIT_CONSOLIDATION_2026-11-24.md) / [recibo](evidence/consolidation/recovered_regression_receipt.json) |

## Executar a regressão

A partir da raiz de um checkout Git integral e limpo:

```bash
python docs/research/nonmanifold-benchmark/probes/run_research_regression.py --output ../apmesh-regression-001
```

A opção `--scope recovered` é exclusivamente diagnóstica e não libera a regressão completa. O procedimento, dependências e interpretação das saídas estão no plano, seção 6.1. Não rodar workflows hospedados automaticamente.

## Evidências e histórico

- N1: [Four-Sheet Curved](R3_CURVED_BICUBIC_PILOT.md), [entrada BP autoral](fixtures/four_sheet_curved.bp).
- N2: [Tsh249, costura não manifold derivada](S40F13_TSH249_ORIGINAL_NATIVE_SEWING_AUDIT.md).
- Controles CAD manifold: [S40 parcial](S3Z4_S40_NATIVE_TRIAL_AND_21_FACE_REGISTER.md), [inventário CAD histórico](MODEL_READINESS_2026-11-18.md).
- Controles STL/QUAD: [TRI F27](THINGI10K_F27_ORIGINAL_NATIVE_TRI_EXECUTION_AND_TOPOLOGY.md), [reconexão F28](THINGI10K_F28_SOURCE_AWARE_SEAM_STITCH_AND_CREASE_AUDIT.md), [recuperação QUAD F29](THINGI10K_F29_NATIVE_QUAD_CAPABILITY_AND_DERIVED_PATCH_RECOVERY.md), [otimização F30](THINGI10K_F30_FEATURE_LOCKED_QUAD_QUALITY_PARETO_EXPERIMENT.md), [RFC F31](THINGI10K_F31_NATIVE_QUAD_RESEARCH_DECISION.md).
- `evidence/`, `fixtures/`, `gallery/` e `probes/`: registros científicos e reprodutibilidade; não são uma segunda fila de tarefas.
- [Snapshot imutável anterior à consolidação](https://github.com/tiagosombrra/apmesh-modernization/tree/92b8af3b9e73072d1122d82ed956f75b608ea5c1/docs/research/nonmanifold-benchmark): todos os antigos planos, relatórios e README de pacotes. [Receitas CI históricas](https://github.com/tiagosombrra/apmesh-modernization/tree/92b8af3b9e73072d1122d82ed956f75b608ea5c1/.github/workflows).

Nenhum experimento M1 é iniciado nesta auditoria. O próximo ato é completar M0 e então qualificar o Four-Sheet Curved.
