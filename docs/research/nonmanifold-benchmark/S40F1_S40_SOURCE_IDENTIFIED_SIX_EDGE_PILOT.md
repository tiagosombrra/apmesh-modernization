# S40-F1 — Próximas faces planas do CAD industrial: #1279 e #1386

**Checkpoint:** 18/11/2026. **Estado:** conversor de pesquisa implementado e testado com primitivas analíticas sintéticas; **nenhuma nova face do S40 foi admitida**. O atlas S3.Y de **156 patches / 1.665 controles / 22 das 43 faces** permanece congelado como referência. PR #225 continua *draft*; sem alteração do núcleo C++.

## Proveniência e o verdadeiro próximo alvo

- STEP original: `cgg-bern/hex-me-if-you-can`, revisão `8f00f02579037cc893042f2ee2c910b20e3fb1b0`, `original/i25o_s40.step`, SHA-256 `b79eb5be1fde71b6a8d086fe14800a1ec62e3a3c4618910c81c64d23718abf3b` (original recuperado e verificado pela auditoria S40-F0).
- BP original S3.Y selecionado: `af50597db4b8d7b3bcb2fc381596fefc95ba6b6e00ed169576bec7a6b7873177` (156 patches, 1.665 controles, 264 costuras de dois lados, 96 lados abertos).
- `ADVANCED_FACE #1279`: `#1139` LINE conectado a `#1105`, `#1284` LINE conectado a `#3737`, `#1002` LINE conectado a `#912`; novos `#1307` CIRCLE conectado à futura `#3710`, `#1336` CIRCLE conectado à futura `#3683` e `#1365` LINE conectado à futura `#3485`.
- `ADVANCED_FACE #1386`: `#1259` LINE conectado a `#1230`, `#1080` LINE conectado a `#912`, `#1473` LINE conectado a `#3737`; novos `#1392` LINE conectado à futura `#3269`, `#1415` CIRCLE conectado à futura `#3319` e `#1444` CIRCLE conectado à futura `#3402`.
- Ambos os alvos têm um contorno externo de seis arestas STEP. **Um único patch bicúbico não pode ser presumido** e o número final de patches depende da subdivisão curva e da disponibilidade dos controles herdados.

## Artefato implementado

`s40f1_six_edge_planar_builder.py` é um conversor experimental com portões de rejeição explícitos:

1. Exige o SHA original do STEP e o BP S3.Y, uma referência de manifesto ao SHA selecionado, a contagem congelada de patches/controles e o censo de costuras (264/96); **não aumenta** a tolerância geométrica experimental de `0.001 mm`.
2. Reconstrói a correspondência STEP→Open CASCADE; para cada aresta original identificada como já representada, recupera a sequência de lados abertos por **correspondência à curva nativa e a seus vértices STEP**. Rejeita ambiguidade, correspondências duplicadas, lacunas e lados anteriormente fechados. Não cria solda por arredondamento espacial.
3. Para arestas originais ainda não representadas, cria novos controles canônicos para `LINE` e aproxima cada arco `CIRCLE` por segmentos cúbicos tangentes via `4r/3 · tan(Δθ/4)`, refinando automaticamente até que as amostras em **33 pontos por segmento** tenham erro posicional abaixo de `0.00075 mm`; o orçamento externo permanece `0.001 mm`. Preserva IDs dos vértices STEP. As arestas novas são registradas no recibo privado com suas **cadeias de IDs de controle** para que futuras faces adjacentes possam reutilizá-las sem fit independente.
4. Exige contorno fechado com número **par** de lados cúbicos. Se um número ímpar surgir, bloqueia com erro explicativo em vez de criar T-junction ou modificar silenciosamente o atlas anterior.
5. Particiona o contorno no plano nativo usando o particionador quadrangular S3.Y, compartilhando índices de controle nas diagonais internas, e preenche interiores por Coons cúbico.
6. Exige prefixo de 156 patches e 1.665 controles anteriores **bit a bit inalterado**, costuras orientadas em sentidos contrários, zero incidências acima de dois, vínculo um a um dos lados herdados e que todos os lados novos ainda abertos pertençam a uma aresta original registrada. Assim, não inventa fechamento completo de um CAD ainda parcial.
7. Reexecuta classificadores nativos de interior e fronteira da face, suporte planar e auditor independente S3.Y de área/Jacobiano orientado/união de patches, com relatório explícito de erro. Aproximação geométrica amostrada **não** é certificação contínua de equivalência do trim.
8. Diante de um erro de entrada, topologia, curva ou nativo, emite `s40f1_rejection.json` e falha com código de saída 3; não substitui o BP selecionado S3.Y.

**Pontos pendentes para homologação:** executar efetivamente contra o STEP e o BP privados verificados; testar se a geometria original dos dois alvos admite a partição sem nenhuma alteração não autorizada; comparar amostras nativas mais densas; retestar faces anteriormente admitidas e o furo `#218`; gerar TRI/QUAD no APMesh C++, cumprir critérios dos orientadores e localizar um modelo industrial originalmente 3+-incidente.

## Testes executados em 18/11/2026

- **S40-F1:** 18/18 testes herméticos aprovados, usando primitivas reais `BRepAdaptor_Curve` com curvas `gp_Circ` e `TopoDS_Edge` do OCP. Os testes verificam raios 1/25/80 mm, segmentação adaptativa, extremos, tangentes, distância à curva nativa, orientações de segmentos, recusa de curvas inválidas, recuperação de cadeias de segmentos indexados e ambiguidades.
- **S3.Z.4 anterior:** 102/102 testes regressivos herméticos reexecutados de forma independente, sem skips/fails. Total de **120 casos em duas seleções**, não uma alegação de regressão científica integral.
- **CAD industrial S40/F1:** `NOT_RUN`: STEP original recuperável pela origem, mas o BP privado S3.Y/manifesto não está montado nesta sessão. Não atribuir hashes, resultados de qualidade, patches gerados ou faces admitidas a esse ensaio inexistente.

## Como reproduzir quando os dados originais estiverem disponíveis

Inserir `s40f1_six_edge_planar_builder.py` na pasta `docs/research/nonmanifold-benchmark/probes` da branch de pesquisa, preservando a estrutura e módulos `s3c`, `s3r`, `s3s`, `s3t`, `s3y` e `audit_analytic_bp`.

```bash
python -m unittest -v test_s40f1_canonical_circle_math
python s40f1_six_edge_planar_builder.py \
  --original-step /private/originals/i25o_s40.step \
  --selected-s3y-bp /private/s3y/s40_3044_selected.partial.bp \
  --selected-s3y-manifest /private/s3y/s40_3044_selected_manifest.json \
  --output /private/s40f1_native
```

Os nomes dos arquivos do BP/manifesto no comando são **exemplos de disposição privada**; a identidade correta é definida pelos hashes internos obrigatórios, não pela grafia do nome do arquivo. Uma execução que falhe não autoriza introduzir patches na branch `main` nem anunciar 24/43 faces.
