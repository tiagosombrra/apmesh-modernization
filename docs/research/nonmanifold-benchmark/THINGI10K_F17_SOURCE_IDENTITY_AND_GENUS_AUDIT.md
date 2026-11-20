# S40-F17 — Originais Thingi10K: 23 arquivos localizados, 7 STL auditados e diversidade topológica

**Data:** 2026-11-20. **Ramo:** `research/benchmark-corpus-reverse-patches`; PR #225 continua em **Draft**. Sem alterações em `main`, nos modelos históricos ou no atlas S40.

## Decisão e alcance

Preservamos integralmente os **23 IDs** da seleção bibliográfica anterior (12 QuadWild/Pietroni e 11 Badia/Martorell/Verdugo). **23/23** ZIPs individuais foram identificados em **árvores Git imutáveis** dos três repositórios do espelho público `larsbrubaker/Thingi10K-meshes-{1,2,3}`. Identificadores, tamanhos exatos e hashes **Git SHA-1 dos arquivos ZIP** estão congelados em [CSV](THINGI10K_F17_PINNED_SOURCES_23.csv) e [JSON](evidence/thingi10k/thingi10k_f17_source_archives_23_and_raw_audits_7.json).

Revisões fixadas dos espelhos:
- `meshes-1`: `2d6f82c6f7934f23b051daf2b19e918c62d30d7b`; árvore `273d0a4ef6191be5a55ae54be37a285e235bfc83`.
- `meshes-2`: `ab50a098405dc2dfcf882e87dab3811b5ea8ce92`; árvore `e618767837922a374b56c48a7be956425ec6f617`.
- `meshes-3`: `626090c1a0bca7e31fe6c1cb5aede8541b16a7b7`; árvore `d7006757ed730043b237ceedb1452c25342ee860`.

Os arquivos originais têm direitos individuais: localizar um Git blob **não equivale a autorizar redistribuição**, gerar derivados ou aprovar automaticamente o seu uso comparativo. Os STL/ZIP de terceiros **não** foram copiados para o commit.

## Quatro auditorias adicionais efetivamente executadas

O mesmo verificador [F16 de ZIP/CRC e STL](probes/zip_stl_probe.js) foi utilizado nos quatro novos arquivos, com ZIP integral obtido via conector público GitHub e conferência exata do tamanho e blob Git da fonte. Foram verificadas a estrutura ZIP/CRC32, a codificação STL (ASCII ou binária), SHA-256 do STL descompactado, identidade dos vértices por coordenadas exatas, incidências das arestas, link de cada vértice, componentes, duplicações, orientação e áreas nulas.

- **58012 — Canopy Test (QuadWild/Pietroni):** 18.340 triângulos, 9.090 vértices, 27.510 arestas de grau 2, uma componente, sem singularidade/degeneração/duplicação. ZIP Git blob `67f266dad4f41137d7036d45c1d82774a2feea15`, STL SHA-256 `2c7c322af76b46a307e67af451ebba9e6609e6932a2829f4c596853dbf122d4b`. **Aviso:** licença individual declarada NC, ainda não verificada com o autor.
- **47076 — Chichen Itza (Badia):** 1.532 triângulos, 768 vértices, 2.298 arestas de grau 2, uma componente, sem defeitos identificados. ZIP Git blob `b34073240e8a518b4bffd31eb5e0164a929abc79`, STL SHA-256 `a2c0046818b7355101790959c69e81384e6999053425de86bf148d9609a43449`.
- **550964 — Eiffel Tower Mini (Badia):** 6.156 triângulos, 3.072 vértices, 9.234 arestas de grau 2, uma componente, sem defeitos identificados. ZIP Git blob `b52eafe18db650480460b8fb22672da24658806a`, STL SHA-256 `e9a81766577f716956bd4380d0b11c124b8d3fffb094adc995c3bcc8694d8b05`.
- **96457 — Nighthawk (Badia):** 1.634 triângulos, 813 vértices, 2.451 arestas de grau 2, uma componente, sem defeitos identificados. ZIP Git blob `295257d3fb226cf89ff0d1510b432c24b659e97c`, STL SHA-256 `9766f6f670cd3cebd6908c42e8deab48e88231a9d30d2e583c7da61cd7666de0`.

Resultados anteriores **F16** preservados sem modificação: #293137 (292 faces, esfera topológica), #37881 (3.400 faces, gênero 1), #61394 (malha adversarial não-manifold com 61 arestas de incidência 3+/4+, 86 links singulares, faces degeneradas). Total agora: **7/23 entradas originais realmente analisadas**, incluindo **2/12 QuadWild** e **5/11 Badia**.

## Métrica topológica útil à pesquisa: característica de Euler e gênero

Para cada malha triangular com arestas exatamente bivalentes, links de vértices fechados e não singulares, **uma componente conexa**, ausência de degenerações/duplicações e orientabilidade consistente nas arestas, calcula-se a característica de Euler `χ = V − E + F` e o gênero orientável `g = (2 − χ)/2`. Se a malha viola esses requisitos, o gênero **não é informado**.

| Modelo | Literatura | Triângulos | V | E | χ=V−E+F | Gênero condicional | Evidência |
|---:|---|---:|---:|---:|---:|---:|---|
| 293137 | Badia | 292 | 148 | 438 | 2 | 0 | STL original auditado |
| 37881 | Badia | 3400 | 1700 | 5100 | 0 | 1 | STL original auditado |
| 61394 | QuadWild | 6747 | 3367 | 10127 | -13 | não aplicável | STL original auditado |
| 58012 | QuadWild | 18340 | 9090 | 27510 | -80 | 41 | STL original auditado |
| 47076 | Badia | 1532 | 768 | 2298 | 2 | 0 | STL original auditado |
| 550964 | Badia | 6156 | 3072 | 9234 | -6 | 4 | STL original auditado |
| 96457 | Badia | 1634 | 813 | 2451 | -4 | 3 | STL original auditado |

**Principal achado:** o modelo bibliográfico **#58012 Canopy Test apresenta gênero 41 no complexo triangular reconstruído do STL original**. A evidência é combinatória, pois `9.090 − 27.510 + 18.340 = −80` e `(2 − (−80))/2 = 41`. Isso torna o modelo particularmente discriminante para verificar se a quadrangulação preserva a conectividade e as múltiplas alças. **Não** prova fidelidade geométrica contínua, correspondência com a topologia CAD original ou gênero da malha QuadWild produzida na literatura — ainda inacessível individualmente.

Não se pode reportar `g = (2 − χ)/2` para o adversarial **#61394**: `χ = −13` é apenas uma contagem bruta de faces/arestas/vértices em um complexo não-manifold e degenerado, **não uma superfície fechada, conexa e orientável**.

## Novo gate independente e testes

- `probes/thingi10k_f17_topology_gate.py`: validará os 23 IDs congelados, as três referências Git, todos os direitos ainda não homologados, hashes/tamanhos das sete análises, identidades de incidência `Σ grau(e) = 3F`, conservação das classes de links e congruência de Euler/gênero.
- `probes/test_thingi10k_f17_topology_gate.py`: **21/21 testes herméticos PASS**, incluindo mudanças maliciosas de arquivos, direitos, estados experimentais, termos de Euler e segmentos adversariais.
- O comando executou localmente sobre o **snapshot F17 real**: validou 23/23 originais identificados, 7/7 recibos de topologia e reproduziu os gêneros `0, 1, 0, 4, 41, não aplicável, 3`. Os números brutos dos modelos provêm do conector remoto F16/F17; a segunda etapa independente verifica apenas invariantes/combinatória sobre os recibos, e **não relê os 7 STL neste ambiente isolado**.

Comandos:

```bash
cd docs/research/nonmanifold-benchmark/probes
python -m unittest -v test_thingi10k_f17_topology_gate
python thingi10k_f17_topology_gate.py \
  --snapshot ../evidence/thingi10k/thingi10k_f17_source_archives_23_and_raw_audits_7.json \
  --output /private/new_f17_invariants.json
```

O `--output` deve ser arquivo novo; saída preexistente não é sobrescrita.

## Pendências científicas (não confundir a existência de arquivos com validação)

1. **Casos prioritários #67792 e #94884:** ZIPs de **1.084.193 e 1.198.819 bytes**, respectivamente, e seus Git blobs verificados; conteúdo integral não entregue pela conexão neste ambiente. Não há SHA-256 do STL, nem censo nativo independente para esses dois modelos. #58012 fornece agora um *outro* caso QuadWild com arquivo integral e topologia conhecida, mas licença declarada NC limita publicação e precisa de revisão.
2. **Saídas QUAD oficiais:** [quadmesh.cloud](https://www.quadmesh.cloud/) distribui o dataset `thingi10k-quad-dataset.zip`; [Hugging Face](https://huggingface.co/datasets/Thingi10K/Thingi10K/blob/main/Thingi10K_quadwild_npz.tar.gz) lista arquivo de 4,4 GB e SHA-256 remoto `79d213585fce31c61f661221266c967b26c5eb446e394d2022280f5a02399011`. Nenhum arquivo de saída QUAD para um dos 12 IDs foi aberto/auditado. O GitHub dos autores [nicopietroni/quadwild](https://github.com/nicopietroni/quadwild) menciona como saídas `quadrangulation_smooth.obj`, `quadrangulation.obj`, `rem.obj` e decomposição em patches; diferenças entre código público e artigo são expressamente advertidas. Não comparar medidas de fontes incompatíveis.
3. **Métricas comparáveis a congelar:** preservação de χ/gênero, incidência livre e 3+, número de componentes, #quad/#tri, distribuição de *scaled Jacobian*, irregularidade de valência, ortogonalidade/ângulo, comprimento e preservação de feições, erro geométrico bidirecional e custo separadamente da conversão. **Qualquer comparação deve usar a mesma entrada e resolução de saída**.
4. **Conversão STL→Bézier e malhamento APMesh reais:** não executados. Não apresentar a sequência `STL→BP→APMesh` como resultado. Seleção de F17 não altera `M5/S40/S27/M3`, modelos históricos `Book/Eistute/Decor Shelf`, Tsh249 nem a base S40 de 156 patches/22 faces.

**Admissões de novos modelos APMesh: zero. Comparações diretas com QuadWild: zero. Fonte STL auditada: 7/23. ZIPs encontrados e pinados: 23/23.**
