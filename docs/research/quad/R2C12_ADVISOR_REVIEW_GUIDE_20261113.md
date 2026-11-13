# R2c-12 — Parecer científico necessário para conectividade non-manifold QUAD/AFT

**Estado:** guia de deliberação, **não é homologação**. **Data:** 2026-11-13. **Revisores pretendidos:** professores Creto Vidal e Joaquim Bento. Nenhuma manifestação, assinatura, autorização ou concordância é presumida.

## Evidências disponíveis

- [R2c-11 CI original](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43497162260): 4/4 jobs aprovados, teste original nativo, equivalência TRI congelada e auditoria física independente, somente em patches desconectados.
- [OBJ, atlas CSV e relatório R2c-11](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43497162260/artifacts/14073665054): evidência temporária, sujeito à retenção do GitHub Actions.
- [R2c-1 — pacote científico de ordenação radial sem autorização](https://github.com/tiagosombrra/apmesh-modernization/blob/quad/integration-r2b2-exterior-aft-20261112/docs/research/quad/R2C1_SOURCE_BOUND_SHEET_REVIEW_20261113.md): arquivo de referência na PR experimental; assinatura/decisão independente ainda não realizada.
- [Evidência qualificada R2c-11](evidence/R2C11_ORIGINAL_SOURCE_SEAM_ATLAS_20261113.json) e [R2c-12](evidence/R2C12_MODEL_BOUND_ADVISOR_HANDOFF_20261113.json).
- [Plano geral M0–M9](MILESTONE_STATUS.md). O código de produção TRI e os arquivos de entrada não foram alterados.

| Modelo original | SHA-256 do arquivo original | Patches | Curvas originais | Valência da curva compartilhada |
|---|---|---:|---:|---:|
| Eistute (`eistute2.fixed.bp`) | `fdce4714524b88f536ec9f8eddc467e54e638dc6e765784ab68edc9a366a0a3f` | 4 | 13 | 4 |
| Book (`book_v7a.bp`) | `3c4255cbd2f46bd2dce5f0e86b8e7ee9ac0c58df949d4563dd821deedcd8412d` | 28 | 85 | 28 |

**Medição física:** 4/4 Eistute e 28/28 Book foram gerados separadamente em elementos QUAD+AFT (512 QUAD e 1456 TRI em conjunto) e exportados como OBJ **desconectados**. A correspondência das amostras paramétricas originais com vértices OBJ foi medida; isso não estabelece pares de halfedges nem propriedade compartilhada de nós.

## Uma diferença que requer decisão explícita

O pacote de ordenação radial R2c-0/R2c-1 deriva do gerador original e registra **10 intervalos na curva central de Eistute e 12 em Book**. O atlas físico R2c-11 deriva de **uma operação independente de adaptação em dois passes** e pode produzir outras subdivisões (observadas separadamente no pacote R2c-12). Geometria original e incidência de superfícies podem coincidir apesar de os pontos, parâmetros e IDs de discretizações de *épocas distintas* não coincidirem.

Consequentemente, um argumento de conformidade global precisa distinguir:

1. **Identidade da curva geométrica original:** índice canônico no registro `Geometry`, SHA do modelo e lados incidentes.
2. **Identidade das amostras de uma mesma época:** parâmetro, ID e XYZ sob a transação de adaptação que as produziu.
3. **Continuidade de superfícies e propriedade física dos nós:** hipótese topológica que depende de semântica de sheet, orientação, normais e ciclo de vida dos objetos.

O identificador legado `CurveAdaptiveParametric::GetId()` apareceu repetido entre curvas diferentes e **não é chave global adequada** para distinguir as curvas originais. Não unir vértices só porque esse ID, o XYZ ou o parâmetro coincidem.

## Perguntas para deliberação de Creto/Bento

1. A curva central representa uma **junção ramificada non-manifold**, um conjunto de **sheets independentes**, uma ou mais **continuações par-a-par**, ou uma combinação? Justificar com a geometria/modelo/semântica do benchmark.
2. Para cada modelo, quais são **todos os pares ou grupos permitidos** de incidências (patch, lado) e suas orientações? A ordem angular radial é somente dado geométrico e não autoriza `halfedge.twin`.
3. Qual a relação esperada das normais físicas e das orientações de fronteira? Devemos reorientar patches ou representar uma orientação não orientável/ramificação legítima?
4. Quais nós físicos devem permanecer **independentes** e quais poderiam ter um proprietário global compartilhado? Descrever também rollback, desalocação e relações de observação dos `SubMesh`.
5. Se dois experimentos adaptativos tiverem subdivisões diferentes na curva original, a conformidade exige **reexecução da adaptação numa única época comum**, **propagação de inserções de pontos** ou outra política demonstrável? Em quais intervalos ela vale?
6. Qual regra histórica do artigo de 1993 deve ser reproduzida literalmente, e quais adaptações de engenharia para malha em superfícies podem ser declaradas modificações?
7. Qual protocolo de validação física (interseções entre superfícies, T-junctions, topologia de links, qualidade geométrica, SANITIZERS, segunda época adaptativa) deve preceder a publicação de um modelo global?

## Estado das opções — sem classificação antecipada

- **Charts independentes:** já é a única interpretação materializada em OBJ no R2c-10/11; válida como conjunto experimental, não como conectividade global comprovada.
- **Conexão por pares de sheets:** é uma possibilidade a revisar, não inferível a partir de valência ou coincidência espacial.
- **Ramificação de três ou mais superfícies:** a definição de incidência por aresta depende de semântica/representação compatível, incluindo elementos não manifold; não confundir com estrutura halfedge exclusivamente manifold.
- **Conexão variável ao longo da curva:** o atual esquema de revisão estrutural cobre intervalos originais inteiros; qualquer mudança local requer nova representação e auditoria por intervalo.

## Critério para liberar a implementação seguinte

A decisão deve estar vinculada ao **SHA-256 do modelo**, ao **índice da curva original**, à listagem completa de incidências (patch,lado), às regras de orientação e ao escopo de adaptação, com revisão científica identificável. A aprovação de uma alternativa deve ser armazenada separadamente do pacote de evidências, sem editar o histórico ou gerar assinaturas fictícias.

**Até esse aceite:** sem soldagem de nós físicos, sem associação automática de `halfedge.twin`, sem promoção do modo `quad_uv` ou declaração de malha global non-manifold correta.

**Execução paralela independente permitida:** prosseguir com o gate M7 de `GeneratorAdaptive::AdaptCurve`/`AdaptDomain` e rollback em duas épocas aceitas, sem alterar produção e sem depender da decisão de sheets.
