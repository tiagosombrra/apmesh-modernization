# S40-F2 — Correção de identidade de vértices e rejeição nativa no conversor do S40

**Data:** 18/11/2026. **Branch:** `research/benchmark-corpus-reverse-patches`. **PR:** #225 (*draft*). **Escopo:** correções efetivas no código do conversor das faces STEP originais `#1279` e `#1386`, sem alegar geração de malha APMesh TRI/QUAD ou aprovação CAD que não ocorreu.

## Situação anterior

O piloto S3.Y mantém **156 patches Bézier, 1.665 controles globais, 264 costuras indexadas de dois lados, 96 lados abertos e 22/43 faces originais representadas**. O BP S3.Y aprovado está congelado pelo SHA-256 `af50597db4b8d7b3bcb2fc381596fefc95ba6b6e00ed169576bec7a6b7873177` e **não está disponível neste ambiente**. O STEP original S40 foi novamente consultado na revisão imutável do upstream, SHA-256 informado e anteriormente verificado `b79eb5be1fde71b6a8d086fe14800a1ec62e3a3c4618910c81c64d23718abf3b`.

## Defeito 1 — ordem das arestas cria índices de vértice conflitantes

O construtor S40-F1 tratava as arestas na ordem do `EDGE_LOOP`, atribuindo imediatamente novos índices globais aos vértices encontrados nas arestas ainda não representadas. Quando o último segmento era uma **aresta herdada**, o índice anterior desse mesmo vértice STEP só era descoberto depois da alocação nova, disparando rejeição incorreta por conflito.

A estrutura original obtida diretamente do grafo STEP confirma que o caso não é hipotético:

- Face original **`#1279`**: arestas orientadas `#1139` (herdada), `#1284` (herdada), `#1307` (nova), `#1336` (nova), `#1365` (nova), `#1002` (herdada). O vértice original **`#1003`** é término da aresta nova `#1365` e início da aresta herdada `#1002`.
- Face original **`#1386`**: arestas orientadas `#1259` (herdada), `#1080` (herdada), `#1392` (nova), `#1415` (nova), `#1444` (nova), `#1473` (herdada). O vértice original **`#1445`** é término da aresta nova `#1444` e início da herdada `#1473`.

**Correção:** antes de criar qualquer segmento novo, recuperar todos os lados herdados identificados pelo grafo STEP, conferir os extremos físicos dos controles, ligar cada `VERTEX_POINT` ao índice global já existente e registrar os lados consumidos. Só então processar as seis arestas do contorno na orientação original e produzir controles novos. A pré-vinculação rejeita controles fora do intervalo, índices conflitantes mesmo se as coordenadas coincidirem, vértices fora de posição e segmentos não bicúbicos. Nenhum índice antigo é reatribuído.

## Defeito 2 — candidato nativo rejeitado retornava sucesso ao chamador

No S40-F1, uma execução que construísse um BP e recebesse `BLOCKED_NATIVE_TRIM` gravava `s40f1.NOT_ADMITTED.bp`, porém **saía com status zero**. Esse estado poderia ser interpretado como sucesso por CI, scripts e auditorias automatizadas.

**Correção:** o novo `require_native_pilot_pass` permite continuar apenas quando as evidências de ambas as faces `#1279/#1386` contêm classificação `PASS_BOUNDED_SAMPLED_NATIVE_TRIM`, zero amostras `OUT`, amostras internas e de borda efetivas, auditorias numéricas independentes de área, Jacobiano orientado positivo, sobreposição e ausência de novos furos, e contagens globais coerentes com cada face. O método rejeita alegações indevidas de prova de Hausdorff contínuo ou execução TRI/QUAD C++. Densidades vazias, excessivas e não inteiras são bloqueadas. Exceções nativas de `RuntimeError` e erros de índices também produzem recibo explícito de falha.

**Resultado de erro:** arquivo `s40f1_rejection.json` com estado `BLOCKED_NO_NEW_FACE_ADMISSION`, **exit code 3**, sem BP de sucesso. **Resultado limitado positivo:** apenas uma candidata `s40f1.BOUNDED_RESEARCH_CANDIDATE.bp`, ainda sujeita a auditoria independente e execução real do APMesh; nunca equivale a uma malha de produção validada.

## Evidências executadas nesta etapa

| Escopo de testes | Executados | Aprovados | Falhas |
| --- | ---: | ---: | ---: |
| S40-F1 pré-existente (primitivas CAD sintéticas) | 18 | 18 | 0 |
| S40-F2: vértices STEP e identidade global | 16 | 16 | 0 |
| S40-F2: recibo CAD, métricas e densidade | 30 | 30 | 0 |
| S40-F2: CLI, bloqueio/erro e saída sem BP | 5 | 5 | 0 |
| **Subtotal S40-F1/F2** | **69** | **69** | **0** |
| S3.Z.4 regressão hermética separada | 102 | 102 | 0 |
| **Total em dois processos de testes** | **171** | **171** | **0** |

Foram testadas também situações com original STEP ausente, rejeição explícita pela classificação CAD, exceção na importação nativa e erro de índice global, sem saída BP aprovada. Essas execuções são **testes herméticos/sintéticos de algoritmo e fluxo da CLI**, não a construção da malha S40 real.

## Bloqueios que permanecem

- O arquivo privado BP S3.Y selecionado e respectivo manifesto não estão montados. Não é possível verificar as costuras contra seus 156 patches nem construir/admitir as duas novas faces.
- A execução com o verdadeiro CAD S40, os testes nativos de superfície aparada, a repetição do conjunto de regressão contra todo o atlas e a homologação do gerador C++ APMesh TRI/QUAD **não foram executadas aqui**.
- A auditoria original STEP consultada no GitHub confirmou as arestas acima por seus IDs, sem introduzir geometria derivada no repositório público; a verificação de hash de 216.438 bytes do STEP original foi realizada anteriormente (S40-F0), não como novo cálculo na CLI CAD desta etapa.

**Decisão:** publicar a correção do S40-F1 como S40-F2 na branch de pesquisa, manter o PR #225 em rascunho, manter `main` inalterada e preservar o baseline **156 patches / 22 faces**. Próximo ensaio: disponibilizar o BP S3.Y/manifesto pelo pacote privado autorizado, executar o construtor corrigido contra STEP original e só então auditar/admitir `#1279` e `#1386`.

## Comandos de execução

No diretório `docs/research/nonmanifold-benchmark/probes` do repositório:

```bash
python -m unittest -q test_s40f1_canonical_circle_math test_s40f2_inherited_vertex_prebinding test_s40f2_native_admission_gate test_s40f2_cli_rejection

python s40f1_six_edge_planar_builder.py \
  --original-step /private/originals/i25o_s40.step \
  --selected-s3y-bp /private/s3y/s40_3044_selected.partial.bp \
  --selected-s3y-manifest /private/s3y/s40_3044_selected_manifest.json \
  --output /private/s40f2_native
```

Os nomes dos arquivos privados no exemplo não são provas de identidade: **os hashes e as invariantes internas devem coincidir**. Não publicar STEP de terceiros nem coordenadas de BP derivadas sem revisão de direitos.
