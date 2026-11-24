# S40-F9 — Correção certificada do Jacobiano na ilha Bézier de quatro faces

**Checkpoint:** 18/11/2026. **Classificação:** candidato geométrico isolado validado por prova exata de regularidade e auditoria de superfícies analíticas reconstruídas; **não admitido** no atlas S3.Y do CAD industrial original. PR de pesquisa #225; não modificar a `main`.

## Ponto de partida: resultado negativo da F8

A ilha S40-F6 possui oito patches Bézier bicúbicos indexados, 104 controles, seis costuras internas e 20 lados abertos rastreados a `EDGE_CURVE` originais. Quatro faces do S40 são representadas como superfícies analíticas reconstruídas: `#1279`, `#1386`, `#3269` e `#3485`.

A auditoria S40-F8, que interpreta os números decimais impressos do BP como racionais exatos, encontrou Jacobiano negativo em cantos dos patches 0 e 3 e exatamente nulo em um canto do patch 1. A F8 bloqueou corretamente a admissão dessa ilha, apesar de seus testes amostrados terem sido positivos.

- **F6 original imutável:** SHA-256 `72b8756c948a7a7da19c9f2a9a7099673e81a30573f19e4820abf27ba720f0a7`.
- **CAD STEP original:** `original/i25o_s40.step`, revisão `8f00f02579037cc893042f2ee2c910b20e3fb1b0`, SHA-256 `b79eb5be1fde71b6a8d086fe14800a1ec62e3a3c4618910c81c64d23718abf3b`.
- **BP S3.Y previamente aceito:** 156 patches, 1.665 controles, 22/43 faces, SHA-256 `af50597db4b8d7b3bcb2fc381596fefc95ba6b6e00ed169576bec7a6b7873177`. Não foi recuperado nesta sessão.

## Correção realmente implementada

O algoritmo S40-F9 utiliza o BP F6 congelado e os dois manifestos privados de geometria fonte, sempre verificados por hash. Para cada um dos quatro arcos `EDGE_CURVE #1307`, `#1336`, `#1415` e `#1444`, desloca **somente os dois controles internos do cúbico** por um vetor radial de módulo `0,0001 mm` apontando para o centro do círculo original. Os vértices de origem de cada arco **não** mudam.

Em seguida, recalcula os quatro controles interiores de cada um dos quatro patches horizontais utilizando a interpolação Coons sobre as fronteiras indexadas já definidas. Os índices dos oito patches permanecem exatamente os mesmos; os patches verticais #4–#7 permanecem inalterados. A rotina visita 16 controles interiores, mas apenas 12 mudam de valor; no total, **20 controles globais apresentam alteração numérica** (oito controles de arco e 12 interiores).

Essa regularização quebra de modo controlado a tangência exata no vértice da curva aproximada, com uma pequena diferença para o contorno circular original; ela **não** demonstra preservação de continuidade geométrica com futuras faces cilíndricas. Portanto, essas interfaces deverão reutilizar os mesmos controles quando forem integradas. Não se faz welding por proximidade.

As oito interfaces com o futuro pai S3.Y são conservadas **numericamente, por índice e por identidade de aresta original**: `#1002`, `#1080`, `#1139`, `#1259`, `#1284`, `#1473`, `#1030`, `#1057`. Mantêm-se seis costuras internas de incidência dupla e orientação oposta e 20 lados abertos com identidade de aresta original. **Não se redistribuíram os cantos nem se modificou o F6 original.**

## Prova matemática e auditoria geométrica

Para cada patch `P(u,v)`, o certificado reconstrói exatamente o polinômio bivariado `J = n · (∂P/∂u × ∂P/∂v)` em Bernstein de grau (5,5) com `fractions.Fraction` aplicado aos controles decimais impressos no novo BP. A positividade estrita é provada pela convexidade dos coeficientes, com subdivisão racional de de Casteljau disponível quando necessária.

| Patch | Face STEP | Certificado de `J > 0` em todo `[0,1]²` | Menor coeficiente de Bernstein de `J` (mm²) |
|---:|---:|---|---:|
| 0 | #1279 | PASS | 0,001637564387 |
| 1 | #1279 | PASS | 0,020303301000 |
| 2 | #1386 | PASS | 775,487838048085 |
| 3 | #1386 | PASS | 0,001637564387 |
| 4 | #3269 | PASS | 129,441733370218 |
| 5 | #3269 | PASS | 624,999999999999 |
| 6 | #3485 | PASS | 129,441733370064 |
| 7 | #3485 | PASS | 624,999999998749 |

**Resultado: 8/8 patches com certificado contínuo de Jacobiano estritamente positivo para os controles decimais do BP F9.** A prova é do objeto Bézier definido por esses controles, não uma prova da conversão exata de uma superfície CAD STEP nem da validade de todas as costuras futuras.

Também foram executados ensaios com `TopoDS_Face` construídas a partir de entidades analíticas correlacionadas do STEP (não é a importação integral do STEP S40):

| Face | Amostras interiores IN | Contorno IN/ON | Contorno OUT | Erro relativo de área amostrada/integrada |
|---:|---:|---:|---:|---:|
| #1279 | 450/450 | 408/408 | 0 | 0,000158021% |
| #1386 | 450/450 | 408/408 | 0 | 0,000158021% |
| #3269 | 450/450 | 408/408 | 0 | ≈ 0 |
| #3485 | 450/450 | 408/408 | 0 | 0 |

Os quatro arcos tiveram distância geométrica **bidirecional amostrada** máxima de `0,0002701998 mm`, menor que o orçamento congelado de `0,001 mm`. Um certificado radial com Bernstein racional sobre os controles binários de ponto flutuante usados no suporte da curva limita continuamente seus raios a aproximadamente `[5,999316985; 6,000000000] mm` com raio nominal `6 mm`. O limite radial contínuo não equivale à certificação do Hausdorff contínuo bilateral contra o **trecho recortado do STEP**; a cobertura angular e os classificadores de trim continuam amostrados.

## Arquivo privado F9 e resultados de regressão

- **BP isolado F9 gerado:** SHA-256 `328ff1ca784b4a82d2bd566309c21d7263cc5134ae37e7b1f4554acd7fd26e38`.
- **Leitura independente:** 104 controles, 8 patches, 6 costuras indexadas, 20 lados abertos; 8 interfaces antigas sem alteração, 8 Jacobianos estritamente positivos por verificação independente do construtor.
- **S40-F5:** 33/33 testes PASS.
- **S40-F6:** 37/37 testes PASS.
- **S40-F7:** 33/33 testes PASS.
- **S40-F8:** 17/17 testes PASS (o F6 antigo continua corretamente bloqueado).
- **S40-F9:** 30/30 testes PASS, incluindo SHA adversarial, invariante de IDs, geometria reconstruída, entradas faltantes e proteção contra emitir BP por erro.
- **Total:** 150/150 testes PASS em cinco seleções, não equivalentes a 150 ensaios de malha C++ ou provas de cobertura CAD contínua.

## Integração futura — fluxo nativo preparado, não executado

O script `s40f9_native_join_gate.py` aceita apenas o STEP integral original verificado por SHA, o BP privado S3.Y congelado, o F6 imutável e o F9 reconstruído com exatamente o hash acima, com seus manifestos. Ele calcula a correspondência nativa única dos oito lados com o pai, executa a junção por **identidade dos controles fonte** usando os métodos já existentes em F7 e submete as quatro faces originais à classificação nativa, área, orientação e verificação bidirecional das arestas, antes de gravar um candidato.

Sem o S3.Y e sem o STEP integral no ambiente de execução, a tentativa retorna **código 3 e `BLOCKED_NO_NATIVE_ADMISSION`**, sem criar BP unido. Uma união que venha a passar só constitui candidato com auditoria nativa **amostrada**; ainda não comprova um limite contínuo de Hausdorff de todos os trims, geração APMesh TRI/QUAD, inclusão de todas as 43 faces ou exemplo industrial genuíno não-manifold.

**Estado da pesquisa após F9:** ilha isolada agora matematicamente regular em seus oito patches; **nenhuma face industrial nova admitida** ao S3.Y (continua 22/43 faces, 156 patches). A `main` permanece protegida; PR #225 deve continuar `draft`.
