# Auditoria de viabilidade — linha científica QUAD

Data da análise: 2026-11-08. Status: **auditoria estática do repositório concluída; execução local de testes pendente**.
Branch: `research/quad-templates-bento1993`. Baseline de origem: `f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94` (merge PR #183).

## Decisão e limites

**Viável para iniciar uma pesquisa isolada de geração QUAD a partir do código atual.** O repositório contém quadtree, balanceamento, seis classificações de vizinhança e algoritmos de triangulação por templates. **Não está pronto para aceitar QUAD como novo tipo de elemento ao longo de todo o pipeline sem trabalho adicional.** O objetivo imediato não é integrar a `main`.

A base documental é o artigo de Joaquim Bento Cavalcante Neto e colaboradores, *Combinação das Técnicas de Quadtree e Delaunay para Geração Automática de Malhas de Elementos Finitos* (SIBGRAPI, 1993), especialmente Figura 7 e a discussão da região de transição. Os seis padrões triangulares do código correspondem às mesmas seis **classes de vizinhança**; as conectividades internas atuais não devem ser tratadas como cópias literais de todas as triangulações históricas. Os templates QUAD serão reconstituídos e testados contra a figura original, não deduzidos das diagonais atuais.

## Estado do projeto-base (evidência declarada, não reexecutada nesta análise)

- `main` em `f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94`: PR #183 integrado, tratamento de falhas de cópia de estado dos nós.
- Linha de modernização: Etapa 3 em pacotes F1–F7 e auditoria F8; há obrigações abertas de cópia, observadores, falhas e rollback. Não alegar segurança de memória integral.
- Evidências documentadas no repositório apontam 75 CTest / 526 controles Python na qualificação recente. **Não foram executados nesta análise.**
- Nenhum pull request aberto na consulta de 2026-11-08.
- A branch QUAD nasce neste SHA, sem alterações em `main`.

## Inventário código → responsabilidade → risco QUAD

| Caminho e referência | Constatação no SHA de origem | Ação proposta | Risco |
|---|---|---|---|
| [`src/crab_mesh/aft/quadtree_cell.cpp#L342-L928`](../../../../src/crab_mesh/aft/quadtree_cell.cpp) | `makeMeshType1..6` constroem triângulos e aplicam escolhas geométricas de qualidade | Reusar a **classificação** e construir um emissor QUAD independente; preservar os seis métodos TRI | Médio |
| [`src/crab_mesh/aft/quadtree_cell.cpp#L1766-L1900`](../../../../src/crab_mesh/aft/quadtree_cell.cpp) | `makeTemplateBasedMesh()` exclui folhas em `inBoundary()` e escolhe T1–T6 pela vizinhança | Extração controlada de `LeafPattern` e confrontação topológica | Alto |
| [`src/crab_mesh/aft/quadtree.cpp#L460-L479`](../../../../src/crab_mesh/aft/quadtree.cpp) | Ordena vizinhos, cria vértices/arestas externos, delega templates à raiz | Reutilizar exclusivamente após provar identidade de bordas e responsabilidade de ownership | Alto |
| [`src/crab_mesh/aft/advancing_front.cpp#L1498-L1588`](../../../../src/crab_mesh/aft/advancing_front.cpp) | Quadtree → templates opcionais → AFT geométrico/topológico → `fillMesh` → `improveMesh`; preenchimento é triangular | Novo caminho experimental QUAD para interior; escolha explícita de política na faixa de transição | Alto |
| [`include/crab_mesh/aft/face.h#L14-L50`](../../../../include/crab_mesh/aft/face.h) | `Face` possui `Vertex* v[3]`; algoritmos de área/qualidade usam três vértices | **Não adicionar vértice 4 em `Face`**; nova topologia UV QUAD tipada | Alto |
| [`src/adapter/adapter.cpp#L1353-L1470`](../../../../src/adapter/adapter.cpp) | Converte histórico `TriangleAdaptive` em `Face` UV; saída vira somente triângulos físicos em dois caminhos do Adapter | Adicionar entrada/saída por espécie de elemento, posteriormente, sem alterar TRI padrão | Muito alto |
| [`include/data/mesh/sub_mesh.h#L30-L66`](../../../../include/data/mesh/sub_mesh.h) | Armazena `unique_ptr<ElementAdaptive>` e nós proprietários | Reutilizar container após verificar contratos de destruição, adoção e observadores | Médio |
| [`include/data/element_adaptive.h#L8-L25`](../../../../include/data/element_adaptive.h) | Classe polimórfica para área, normal, nó e ângulo; não expõe cardinalidade/UV genérico | Introduzir acesso polimórfico somente quando existir exigência validada em testes | Alto |
| [`include/data/triangle_adaptive.h#L10-L65`](../../../../include/data/triangle_adaptive.h) | 3 nós, parâmetros UV por vértice, registro de observadores nos nós | Nova `QuadrilateralAdaptive` separada, com quatro parâmetros e rollback seguro | Alto |
| [`src/curvature/adjacent.cpp#L5-L14`](../../../../src/curvature/adjacent.cpp) | Uma rota usa `static_cast<const TriangleAdaptive&>` ao obter posições de vértices | Acesso tipado genérico, ordem de adjacência auditada antes de uso QUAD | Muito alto |
| [`src/curvature/curvature_discrete.cpp`](../../../../src/curvature/curvature_discrete.cpp) | Curvatura discreta soma áreas/ângulos e depende da ordem de adjacência | Confirmar validade em polígonos não triangulares; não apenas reinterpretar somas | Alto |
| [`src/generator/generator_adaptive.cpp#L7430-L7450`](../../../../src/generator/generator_adaptive.cpp) | OBJ escreve somente 3 índices por elemento, com cast direto | Exportador separado QUAD/misto; não alterar exportação TRI sem gates | Médio |
| [`src/generator/generator_adaptive.cpp#L7760-L7815`](../../../../src/generator/generator_adaptive.cpp) | Métricas, histogramas, contagem de arestas e qualidade usam `TriangleAdaptive` | Métricas segregadas por topologia, referenciais UV e XYZ; auditoria de TODOS os consumidores | Muito alto |
| [`src/adapter/adapter.cpp#L1719-L1730`](../../../../src/adapter/adapter.cpp) | `SetTemplateMode` configurado por `serial_flow->template_mode` e controla templates triangulares | Não reutilizar valor `y/n` para espécie de elemento; adicionar modo ortogonal *opt-in* | Médio |
| [`CMakeLists.txt#L29-L42`](../../../../CMakeLists.txt) | `GLOB_RECURSE src/*.cpp` alimenta `ap_mesh_engine` | Prototipar fora de `src/`, em `research/quad`, para não ativar código automaticamente | Médio |
| [`cmake/Quality.cmake`](../../../../cmake/Quality.cmake) | Muitos controles existentes de vida útil, UV, preservação e regressão | Testes QUAD independentes, seguidos dos gates TRI não regressivos | Alto |

Os links relativos acima são referências internas ao repositório; a evidência fixada é o commit `f6050ec1b12b508b9d8d761db1fa9a95ab1e3d94`.

## Inventário de riscos de produção (não ignorar)

1. **Região de fronteira:** templates atuais são omitidos em células que tocam o contorno. Uma malha QUAD de interior isolada não produz uma superfície completa.
2. **Conformidade intercelular:** novos pontos médios de uma aresta devem usar identidade única/compartilhada, inclusive transições 2:1.
3. **Contorno multipatch:** subdividir uma amostra física de curva compartilhada exige publicação canônica simultânea para todas as incidências; nunca inserir um ponto apenas no contorno local UV e declarar conformidade.
4. **Triângulo assumido implicitamente:** Adapter, Generator, exportação, adjacência e curvatura não se tornam QUAD-safe pelo simples uso de `ElementAdaptive`.
5. **Área/curvatura em XYZ:** quadriláteros sobre superfície paramétrica podem ser não coplanares; área, normal, qualidade e erro precisam de definição geométrica explícita.
6. **Ownership e rollback:** Etapa 3 não está encerrada; novas estruturas devem usar propriedade explícita e testar falhas de alocação, observadores e descarte de candidatos.
7. **Ciclo adaptativo:** sem política validada para utilizar uma malha QUAD anterior como fonte de tamanhos/curvaturas, somente a primeira geração pode ser qualificada.
8. **Validação científica:** byte-a-byte dos resultados TRI é obrigatório apenas para o modo padrão; QUAD exige oráculos próprios, não comparações numéricas ingênuas de contagem de elementos.

## Gates de viabilidade antes da primeira alteração de algoritmo

- Q0-A: em worktree isolado, reproduzir build C++17 GCC e MSVC, CTest integral, roteiros científicos Eistute e Book no SHA fixo, documentando configuração, executáveis e hashes (a consulta GitHub não substitui a execução).
- Q0-B: mapear exaustivamente os casts e loops triangulares alcançáveis na rota serial e registrar as rotas não qualificadas (OpenMP/MPI explicitamente fora do escopo inicial).
- Q0-C: digitalizar e testar por conectividade os seis templates QUAD exatamente como prescritos na Figura 7, inclusive rotações e espelhamentos; a imagem não deve ser usada como argumento de equivalência sem oráculo.
- Q0-D: aprovar definição científica de saída inicial: `quad-dominant` com triângulos remanescentes ou `all-quad` com resolução de paridade/singularidades. Implementar ambas sem decisão explícita amplia escopo sem evidência.

## Avaliação

**Aprovado para protótipo isolado e branch específica.** **Não aprovado para merge de QUAD na `main`**, nem para declarar comportamento adaptativo completo. A transição para modo físico QUAD depende dos gates de malha UV e memória; a integração em múltiplos patches depende de curva canônica, orientação e incidência.

Responsabilidade de entrega: cada milestone requer artefato executável, oráculo independente, dados de regressão, diff circunscrito, evidência no commit candidato e registro de decisões científicas.
