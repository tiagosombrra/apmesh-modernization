# S40-F9 — execução reproduzível

Contém correção de regularidade dos oito patches isolados S40-F6 e prova exata de Jacobiano, com arquivos privados separados dos itens publicáveis no GitHub. É uma **ilha de pesquisa ainda não integrada** ao atlas S3.Y.

A partir do diretório `probes` do pacote privado, com `cadquery`, `OCP`, `numpy`, `scipy` e `shapely` instalados:

```bash
python s40f9_regularized_source_island.py \
  --f6-bp ../private/s40f6_four_face_source_island.PRIVATE.bp \
  --f6-manifest ../private/s40f6_source_island.PRIVATE.json \
  --f5-source-spec ../private/s40f5_source_spec.PRIVATE.json \
  --f6-source-spec ../private/s40f6_vertical_faces.PRIVATE.json \
  --output-dir ../reproduced

python s40f9_independent_certificate.py \
  --original-f6-bp ../private/s40f6_four_face_source_island.PRIVATE.bp \
  --candidate-f9-bp ../reproduced/s40f9_four_face_regularized.PRIVATE.bp \
  --original-f6-manifest ../private/s40f6_source_island.PRIVATE.json \
  --candidate-f9-manifest ../reproduced/s40f9_private_candidate_manifest.json \
  --output ../reproduced/independent_f9_jacobian.json
```

Para executar testes **incluindo** os casos privados, defina os caminhos:

```bash
export APMESH_S40F9_F6_BP=../private/s40f6_four_face_source_island.PRIVATE.bp
export APMESH_S40F9_F6_RECEIPT=../private/s40f6_source_island.PRIVATE.json
export APMESH_S40F9_F5_SPEC=../private/s40f5_source_spec.PRIVATE.json
export APMESH_S40F9_F6_SPEC=../private/s40f6_vertical_faces.PRIVATE.json
python -m unittest -q test_s40f9_regularized_island
```

A execução **nativa integral** deve ocorrer dentro do diretório de pesquisa `docs/research/nonmanifold-benchmark/probes` do repositório clonado, que já contém os módulos S3 de correlação STEP/OCCT. Use `python s40f9_native_join_gate.py --help` para informar o STEP original, o BP S3.Y, os manifestos e as especificações privadas. O comando **recusa entradas ausentes ou divergentes** sem produzir um atlas unido.

**Regras de divulgação:** não publicar as coordenadas derivadas do STEP, os BP privados nem os manifestos geométricos na branch GitHub até revisar os direitos de redistribuição. O pacote ZIP é uma entrega privada de pesquisa. A main não deve receber merge automático.
