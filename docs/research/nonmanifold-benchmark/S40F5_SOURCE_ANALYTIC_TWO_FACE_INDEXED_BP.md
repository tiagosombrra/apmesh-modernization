# S40-F5 — Dois rostos CAD originais reconstruídos como BP indexado isolado

**Data:** 18/11/2026. **Classificação:** ensaio de pesquisa reproduzível sobre geometria analítica derivada de entidades STEP; **não** importação nativa da peça STEP integral, **não** integração ao atlas S3.Y e **não** malhamento do APMesh.

## Fonte e integridade

O arquivo upstream de referência é `cgg-bern/hex-me-if-you-can`, revisão `8f00f02579037cc893042f2ee2c910b20e3fb1b0`, `original/i25o_s40.step`, SHA-256 registrado e verificado no checkpoint anterior: `b79eb5be1fde71b6a8d086fe14800a1ec62e3a3c4618910c81c64d23718abf3b`. As entidades das faces `ADVANCED_FACE #1279` e `#1386`, seus 12 `EDGE_CURVE`, vértices e suportes planos foram recuperadas da revisão fixada por conector GitHub e transcritas para uma **especificação privada de 3.020 bytes**, SHA-256 `81c50cee156de79a10883643fa75da52b1c07a528ad0f06ad256156cf1fd9e7a`. O módulo público rejeita especificação privada com hash diferente.

A especificação privada contém os centros dos quatro círculos e as coordenadas de seus vértices, **não o STEP completo**. Este trabalho reconstrói novas faces OCP com seis arestas: quatro retas e dois arcos de 45 graus, raio 6 mm, por face. Portanto as medições abaixo dizem respeito a um **substituto analítico reconstruído das entidades**, e não devem ser citadas como medição do `TopoDS_Face` importado diretamente do STEP original.

## Construção efetiva

- `#1279`: 2 patches Bézier bicúbicos, 6 lados originais (3 herdáveis, 3 ainda pendentes).
- `#1386`: 2 patches Bézier bicúbicos, 6 lados originais (3 herdáveis, 3 ainda pendentes).
- Os quatro arcos STEP (`#1307`, `#1336`, `#1415`, `#1444`) usam um segmento cúbico cada. O controle tangencial é **encurtado em 0,0007 mm** em relação à parametrização circular cúbica padrão, para deixar a curva do lado interno do recorte planar analítico. Esse encurtamento **não altera o orçamento de erro de 0,001 mm**.
- O BP isolado gerado efetivamente possui **4 patches / 56 controles globais / 2 costuras internas de dois lados com índices idênticos em ordem oposta / 12 bordas abertas rastreadas aos IDs originais**.
- O arquivo `s40f5_1279_1386_ISOLATED_PRIVATE.bp` é utilizável como entrada sintática `.bp` para auditorias de patches, mas **não é a peça S40 completa e não substitui o atlas S3.Y**.
- Os seis lados classificados como herdáveis do S3.Y ainda não estão unidos aos controles antigos, pois o BP de 156 patches não está disponível. Nenhuma operação de união geométrica por proximidade é feita.

## Medições realizadas sobre o substituto OCP

| Critério | Fonte `#1279` | Fonte `#1386` |
| --- | ---: | ---: |
| Patches e suportes planos reconstruídos | 2 | 2 |
| Área nativa do substituto OCP (mm²) | 836,5134606232842 | 836,5134606239776 |
| Área Bézier integrada por Gauss (mm²) | 836,5125803895312 | 836,5125803902243 |
| Diferença relativa de área | 0,00010522649% | 0,00010522649% |
| Amostras interiores `IN` | 450/450 | 450/450 |
| Amostras de contorno `IN/ON` | 408/408 | 408/408 |
| Amostras de contorno `OUT` | 0 | 0 |
| Máxima distância bilateral amostrada das arestas curvas (mm) | 0,000200909 | 0,000200909 |
| Curvas com certificado radial racional, para controles float | 2/2 | 2/2 |

A avaliação racional em base Bernstein da distância radial quadrática dos **quatro segmentos cúbicos definidos pelos controles IEEE-754** certificou, em cada caso, raio dentro de `[5,999; 6,0000001] mm` na totalidade do parâmetro cúbico. O limite inferior bruto dos coeficientes, quando convertido em raio, foi aproximadamente `5,99939750355 mm`; isso é mais conservador que o desvio real amostrado e ainda respeita o orçamento fixo de 0,001 mm.

**Limites epistemológicos:** não existe aqui prova de equivalência das faces STEP originais, erro Hausdorff contínuo entre superfícies, conformidade com os controles do atlas pai, junta com as faces cilíndricas vizinhas nem resultado do malhador TRI/QUAD de produção. Os testes finitos de trim, Jacobiano e área são evidência limitada; o certificado racional cobre apenas a distância ao círculo ideal para a curva cúbica float-definida.

## Execução e testes

No ambiente de pesquisa (Python 3.13, CadQuery 2.8, OCP 7.9), o ensaio local executou **33/33 testes**, sem falhas ou skips: 20 sobre a especificação privada e o BP gerado, 13 testes matemáticos independentes dos dados privados. Os testes incluem auditoria independente da gramática BP, censo indexado das 2 costuras, todas as 12 identidades de arestas STEP, quatro trajetórias circulares, duas direções de distância, rejeição de especificação modificada, orientação e casos adversariais para curvas que saem do lado correto do recorte. O BP foi escrito antes de gerar o pacote de entrega, e seu hash está no recibo JSON.

Para reproduzir a parte privada:

```bash
python -m unittest -v test_s40f5_original_source_analytic_pilot test_s40f5_bounded_analytic_math
python s40f5_original_source_analytic_pilot.py \
  --source-spec s40f5_source_spec.PRIVATE.json \
  --isolated-bp s40f5_1279_1386_ISOLATED_PRIVATE.bp \
  --output source_analytic_receipt.json
```

Sem `s40f5_source_spec.PRIVATE.json`, os testes geométricos dependentes do CAD declaram SKIP, jamais PASS. O código, os testes matemáticos e a documentação podem ser publicados sem revelar coordenadas ou controles originais; a especificação derivada e o BP ficam apenas no pacote de usuário.

## Próxima etapa condicionada

**S40-F6:** recuperar `s40_spline_shared_repair.partial.bp` + manifesto do pacote S3.W ou o BP privado S3.Y (SHA-256 `af50597db4b8d7b3bcb2fc381596fefc95ba6b6e00ed169576bec7a6b7873177`); executar correspondência exata de seis lados herdados contra IDs de controle antigos; reconverter e auditar as duas faces **no original STEP importado** com `BRepClass_FaceClassifier`; verificar suporte, inversão, área e conformidade com as faces vizinhas; só então avaliar a promoção da referência `22/43` para `24/43`. Nenhuma modificação foi feita ao `main` nem ao C++ de produção.
