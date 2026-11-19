# S40-F8 — Certificação exata do Jacobiano da ilha Bézier S40-F6

**Data:** 18/11/2026. **Status:** portão matemático implementado, executado sobre o BP privado F6 congelado, com **resultado negativo para regularidade estrita em três patches**. Este resultado não é uma importação integral do STEP industrial e não altera a contagem admitida do S3.Y.

## Entradas, fidelidade e escopo

- Modelo industrial original: `cgg-bern/hex-me-if-you-can`, revisão `8f00f02579037cc893042f2ee2c910b20e3fb1b0`, `original/i25o_s40.step`, SHA-256 `b79eb5be1fde71b6a8d086fe14800a1ec62e3a3c4618910c81c64d23718abf3b`.
- BP isolado privado S40-F6 **efetivamente analisado**: SHA-256 `72b8756c948a7a7da19c9f2a9a7099673e81a30573f19e4820abf27ba720f0a7`, 8 patches, 104 controles globais, 6 costuras internas, quatro faces STEP identificadas `#1279`, `#1386`, `#3269`, `#3485`. O BP não foi alterado.
- Os controles textuais decimais do BP são interpretados como **números racionais exatos**. Assim, a prova é exata **para a superfície polinomial definida pelos bytes do BP**, não para a geometria CAD original considerada em números reais ideais ou em presença de incertezas de fabricação/importação.
- Normais originais adotadas na ilha: `#1279/#1386: (0,0,-1)`, `#3269: (1,0,0)`, `#3485: (-1,0,0)`. Referência: entidades das superfícies analíticas reconstruídas e grafo STEP original inspecionado no checkpoint S40-F6.

## Método de prova (não é um teste de amostragem)

Para cada patch bicúbico vetorial `P(u,v)`, o algoritmo calcula com frações exatas o polinômio `J(u,v) = n · (∂P/∂u × ∂P/∂v)` e o expressa na base de Bernstein tensorial de grau `(5,5)`. Multiplicações entre polinômios são realizadas com os coeficientes combinatórios racionais; nenhum arredondamento de ponto flutuante intervém na decisão do sinal.

Pela propriedade de combinação convexa dos polinômios de Bernstein, se os 36 coeficientes forem positivos, então `J(u,v)>0` em todo `[0,1]²`. Quando necessário, o implemento pode subdividir exatamente por de Casteljau em `u`/`v`; ele nunca transforma uma amostra positiva em certificado contínuo. Sinais em cantos também são conferidos independentemente, calculando as derivadas a partir dos quatro controles adjacentes.

## Resultado efetivo sobre o BP F6 congelado

| Patch F6 | Face STEP | Classificação estrita | Jacobiano mínimo exato em um canto (mm²) |
| ---: | ---: | --- | ---: |
| 0 | `#1279` | **Bloqueado: negativo no canto `u=1,v=1`** | `−4.761298864114155 × 10⁻¹¹` |
| 1 | `#1279` | **Bloqueado: zero no canto `u=1,v=1`** | `0` |
| 2 | `#1386` | CERTIFICADO estritamente positivo | `775.487838048085` |
| 3 | `#1386` | **Bloqueado: negativo no canto `u=0,v=1`** | `−4.761298864114146 × 10⁻¹¹` |
| 4 | `#3269` | CERTIFICADO estritamente positivo | `129.4417333702182` |
| 5 | `#3269` | CERTIFICADO estritamente positivo | `625.0` |
| 6 | `#3485` | CERTIFICADO estritamente positivo | `129.44173337006444` |
| 7 | `#3485` | CERTIFICADO estritamente positivo | `624.9999999987499` |

**Cinco patches possuem certificado contínuo de positividade estrita. Dois têm canto de sinal negativo e um tem Jacobiano exatamente nulo no canto.** Os dois cantos negativos implicam, por continuidade do polinômio, que o BP decimal-definido apresenta uma região orientada negativamente, ainda que extremamente pequena, no entorno do canto. Isso não foi captado pelas sondagens anteriores baseadas em amostragem.

O encontro reto–arco nos vértices STEP `#1285` e `#1337` (`#1279`) e `#1445` (`#1386`) é tangencial na geometria de origem, mas foi escolhido como canto de quadrilátero no particionamento. A regularidade estrita no domínio fechado pode ser incompatível com esse particionamento sem reparametrização ou alteração de controles. O erro numérico dos controles decimais explica plausivelmente os pequenos sinais negativos, mas **essa explicação não substitui uma demonstração matemática ou a correção do BP**.

**Limite geométrico contínuo adicional:** para os oito patches, os coeficientes exatos de Bernstein certificam `J(u,v) > −5 × 10⁻¹¹ mm²` em todo o quadrado paramétrico. A propriedade prova apenas o limite inferior quantitativo; **não prova positividade**. O orçamento de ajuste de curva `0,001 mm` refere-se a distância espacial, enquanto este limite está em `mm²`; não devem ser confundidos.

## Defeito de admissão encontrado e correção de controle

O fluxo F7 tinha auditoria de Jacobiano em pontos interiores, mas nenhuma prova contínua que incluísse o comportamento nos cantos. A S40-F8 adiciona `s40f8_exact_planar_jacobian.py` e chama `require_strict_orientation_certificate(child)` **antes de tentar promover o BP F6 para uma união S3.Y**. O gate rejeita explicitamente o BP congelado no estado atual com a identificação dos patches `0,1,3`; não modifica dados anteriores ou tenta consertar a orientação por tolerância numérica.

Esta é uma **decisão de admissão mais conservadora da pesquisa**. Para liberar a união, será necessário projetar um novo particionamento ou construir um controle de regularidade adequado a singularidades de canto, com justificativa e critérios explícitos. Não se reinterpreta o caso `J≈0` como aprovação automática.

## Testes executados nesta etapa

- S40-F8: **17/17 PASS**, incluindo quatro verificações sobre o BP privado congelado e casos adversariais com jacobiano negativo/nulo, multiplicação racional e subdivisão exata.
- S40-F7: **33/33 PASS** com fixtures sintéticas e ilha privada; o novo gate é exercitado nos testes F8, não na execução de união real S3.Y.
- S40-F6: **37/37 PASS** com dados privados da ilha.
- S40-F5: **33/33 PASS** com dados privados.
- Total: **120/120 testes PASS** em quatro seleções. Estes não são 120 verificações nativas no STEP integral nem testes do APMesh C++.

## Próxima operação científica

1. Construir uma proposta de **redistribuição das esquinas** nas faces `#1279/#1386` (evitar cantos paramétricos de fronteiras tangentes ou formalizar singularidade admissível de borda).
2. Preservar os controles e IDs dos oito lados herdados e os registros de arestas de origem. Criar um **novo BP candidato distinto**; não substituir o F6 congelado nem publicar coordenadas privadas.
3. Reexecutar os certificados de Jacobiano, os testes de fidelidade em curvas/áreas e a auditoria de trimmed face no STEP integral.
4. Recuperar o BP S3.Y privado e executar a descoberta/união real das oito interfaces apenas se o candidato passar os novos portões.

**Situação atual:** o S3.Y aceito continua em **156 patches e 22/43 faces originais**; a ilha F6 isolada tem oito patches e quatro faces reconstruídas, mas encontra **bloqueio de regularidade estrita**. Nenhuma nova face foi admitida e nenhum mesher APMesh TRI/QUAD foi executado.
