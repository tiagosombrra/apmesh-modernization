# R2c-17 — Protocolo de causa-raiz do fallback nativo Adapter/Quadtree

**Data:** 2026-11-13. **Estado:** plano para o próximo experimento, ainda não executado. **Objetivo M7:** compreender por que o gerador original rejeita o segundo estado adaptativo, preservando a política de aceitação TRI.

## Problema comprovado

A auditoria [R2c-14](evidence/R2C14_ORIGINAL_GENERATOR_REJECTION_FORENSICS_20261113.json) com os CSV nativos mostrou Eistute passo 4 com 4/4 patches em `curve_transition_needs_retry`, embora o erro global caia cerca de 83,9%; Book original passos 2–3 com 28/28 em `degenerate_needs_retry` e erro global aproximadamente 300% maior. Os dados vieram do [CI #43504972443](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43504972443), cujo artefato guarda os arquivos originais de adaptação por patch e curva.

**A semântica de `degenerate_needs_retry` precisa ser preservada:** conforme o método `PatchNeedsFallback` no [código nativo do Adapter](https://github.com/tiagosombrra/apmesh-modernization/blob/quad/integration-r2b2-exterior-aft-20261112/src/adapter/adapter.cpp), o rótulo pode ser acionado por número insuficiente de elementos, qualidade pós-AFT, proporção de elementos ruins, sub-resolução em relação ao objetivo `h`, incompatibilidade entre curvas e interior, falta de banda de transição ou notas de templates Quadtree. Não prova, isoladamente, faces de área nula. O rótulo `curve_transition_needs_retry` destaca sub-resolução de transições ou deficiência curva/interior, e pode também ser atribuído por overshoot local com sensibilidade de transição.

## Nova evidência necessária, preservando a aplicação de produção

O `Adapter` já escreve nativamente `<OUTPUT_PREFIX>_domain_adaptation.csv` com **patch, step, retry, local_regen_attempt, generation_status, degeneracy_score, degenerate_post_aft_count, degenerate_post_smoothing_count, template_low_score_count, template_score_min, transition_floor, transition_underresolved, interior_transition_imbalance, curve_domain_balance, generated_faces, quality_post_aft_min, poor_ratio_post_aft e regiões do AFT**. Os artefatos do R2c-14 guardavam CSV de aceitação/patch/curva, mas não esse log granular por tentativa local.

A próxima mudança deve incluir o arquivo de domínio no artefato de pesquisa e introduzir um verificador independente que:

1. Confira SHA-256 do modelo original e origem da configuração, sem alterar `main`, `Adapter`, `GeneratorAdaptive` ou entradas `.bp`.
2. Una `step,retry,patch_id,local_regen_attempt` com os registros de status do R2c-14, sem inferir identidade de tentativas pelo ID legado da curva.
3. Diferencie quantitativamente fallback por **qualidade/degeneração**, **template Quadtree**, **curva/interior** e **transição insuficiente**, e conte as tentativas de regeneração para cada patch.
4. Compare o status do patch escolhido com todas as tentativas locais (inclusive candidatos não selecionados), sem chamar um candidato rejeitado de aceito.
5. Preserve o modo histórico `research_debug` de Book e o `adaptive_stable` de Eistute; não aplicar automaticamente critérios do modo estável aos dois.
6. Só considerar M7 atendido se o log original comprovar duas etapas `AcceptedMeshScope::Commit` distintas, cobertura completa dos patches, curvas de origem íntegras, rollback e paridade científica TRI.

## Hipóteses para testar, não conclusões

- **Book (modo original):** verificar se os 28 rótulos `degenerate_needs_retry` compartilham a mesma causa em qualidade pós-AFT, scores Quadtree ou número mínimo de elementos; medir possíveis faces degeneradas reais em vez de supô-las.
- **Eistute (passo 4):** medir qual transição do AFT está sub-resolvida e por que o crescimento de malha 6,18× não resolve a coerência. Revisar controle `h`, orçamento e banda de transição sem alterar critérios de aceitação.
- **Book (perfil estável de pesquisa):** confrontar orçamento global registrado de aproximadamente 114 elementos com 784 efetivos, observando que o orçamento local por patch registrado como 2.600 não corresponde necessariamente à restrição global desejada.

**Gate seguinte:** relatório original por tentativa local e patch com as causas específicas, acompanhado de controles negativos. Depois, propor **uma** modificação opt-in limitada ao gerador experimental, com regressão TRI congelada e sem autorizar soldagem non-manifold.

**Limitação científica permanente:** M6 continua bloqueado para malha global por falta de decisão aprovada sobre os sheets e a propriedade dos nós físicos nas curvas de valência 4 e 28. O desenvolvimento isolado de M7 não deve ocultar essa restrição.
