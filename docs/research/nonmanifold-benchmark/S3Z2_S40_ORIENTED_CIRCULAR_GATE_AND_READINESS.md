# S3.Z.2 — Portão de orientação global, Coons e pré-requisitos nativos

**Data:** 17/11/2026. **Escopo:** auditoria topológica e testes herméticos. **Estado geométrico:** NÃO ADMITIDO. Não há malhador TRI/QUAD, regressão C++ ou certificação de Hausdorff nesta execução. Preservar PR #225 como draft e a branch `main` sem alterações.

## Fonte e atlas congelados

- Fonte industrial S40 original, `cgg-bern/hex-me-if-you-can`, revisão `8f00f02579037cc893042f2ee2c910b20e3fb1b0`, arquivo `original/i25o_s40.step`, SHA-256 **`b79eb5be1fde71b6a8d086fe14800a1ec62e3a3c4618910c81c64d23718abf3b`**.
- BP privado S3.W de 148 patches, SHA-256 **`c826487d8cee76f6649100c59e5ce84fa6cb43c9004f53c68e3e565e86cdb174`**.
- Último filho experimental S3.Y admitido sob ensaios amostrais: BP de **156 patches / 1.665 controles declarados / 264 costuras indexadas duplas / 96 lados abertos / 22 das 43 faces STEP**. SHA-256 **`af50597db4b8d7b3bcb2fc381596fefc95ba6b6e00ed169576bec7a6b7873177`**.
- Face `#3044` já admitida em S3.Y. As faces `#1827` e `#1907` permanecem **bloqueadas** desde S3.Y: 18 amostras de fronteira `OUT` por face na candidata conjunta anterior. Isso é evidência histórica, **não** medição nativa desta etapa.
- Proposta S3.Z de reparo compartilhado de oito arestas CIRCLE de origem STEP, preservando os IDs globais existentes. Candidata **não admitida** prevista: 160 patches / 1.685 controles / 278 costuras indexadas duplas / 84 lados abertos.

## Problema identificado no protótipo S3.Z.1

A comparação de sequências **brutas** dos quatro controles de duas bordas vizinhas não equivale à comparação da orientação efetiva do contorno. Para patches bicúbicos em grade 4×4, as arestas `bottom` e `right` seguem o contorno CCW, ao passo que `top` e `left` percorrem a grade na direção oposta à do contorno. Uma regra que exige sempre a inversão das sequências brutas pode tanto rejeitar uma costura orientada corretamente quanto aceitar uma inconsistência.

A correção substitui esse teste por **sequências orientadas segundo o perímetro do patch**, exigindo inversão exata da sequência orientada entre os dois lados da costura. O teste anterior S3.Z.1 foi revisado para refletir essa semântica; a regressão completa continua verde.

## Novo portão S3.Z.2

Os arquivos `s3zb_oriented_seam_and_coons_gate.py`, `s3zb_check_private_readiness.py` e seus testes complementam o protótipo `s3z_s40_circular_seam_gate.py`.

1. **Todas as bordas dos quatro novos patches** devem ter exatamente uma contraparte, sem lados novos abertos nem incidência maior que dois. Distinguir ligações `old-new` (**12**) das duas diagonais internas `new-new` (**2**). Validar o sentido CCW de ambas.
2. **Prefixo original indexado preservado:** os 156 patches S3.Y antigos conservam seus 16 IDs por patch. Nenhuma reindexação é permitida; as movimentações de controles anteriores permanecem sujeitas ao registro S3.Z.1.
3. **Reconstrução Coons independente:** quatro controles interiores por novo patch, **16 controles interiores** no total, devem coincidir com o Coons cúbico reconstruído a partir dos quatro lados com orientação correta. Rejeitar alias de controles antigos, coincidência com borda, reuso de um interior por outro patch, valor não finito e relaxamento da tolerância numérica de identidade.
4. **Cardinalidades fixas da candidata:** 160 patches, 1.685 controles globais declarados, 278 costuras duplas e 84 lados abertos. Esses números são exigências combinatórias, não prova de cobertura nativa.
5. **Portão de prontidão privado:** verificar os hashes exatos do STEP e BP S3.W, identidade do manifesto privado, existência do construtor S3.Y e dependências Python CAD. Falhar explicitamente sem qualquer alegação geométrica quando ausentes.
6. Executar **primeiro** o portão S3.Z.1, **depois** o S3.Z.2 e **somente depois** o escrutínio nativo já previsto: todos os dois lados de cada aresta STEP, desvios às curvas originais, suporte cilíndrico com Bernstein bicúbico, Jacobianos, recorte de cada face e não regressão do furo `#218`.

## Validação realizada nesta sessão

- Testes herméticos S3.Z + S3.Z.1: **28/28 PASS** com a regra CCW corrigida.
- Testes novos S3.Z.2: **27/27 PASS**, envolvendo também costuras `new-new`, Coons, aliasing de controles e ausência/alteração de pré-requisitos.
- **55/55 testes herméticos aprovados**, zero falhas ou ignorados, compilação Python sem erros.
- Execução real do verificador: **`BLOCKED_MISSING_OR_MISMATCHED_INPUT`**, código de saída 3. Os quatro arquivos necessários não estão montados: STEP original, BP S3.W, manifesto S3.W e `s3y_s40_curved_planar_rings.py`.
- Dependências locais `cadquery`, `OCP`, `numpy`, `scipy` e `shapely`: disponíveis.
- Nenhum ensaio nativo com `TopoDS_Face` foi executado; nenhum deslocamento experimental novo foi aprovado e **nenhuma face STEP foi admitida**.

## Execução reproduzível

```bash
python -m unittest -v \
  test_s3z_s40_circular_seam_gate \
  test_s3za_topology_scope \
  test_s3zb_oriented_seam_and_coons_gate \
  test_s3zb_private_readiness

python s3zb_check_private_readiness.py \
  --original-step /private/original/i25o_s40.step \
  --s3w-bp /private/s3w/s40_spline_shared_repair.partial.bp \
  --s3w-manifest /private/s3w/s40_spline_shared_repair_manifest.json \
  --s3y-builder /private/research/s3y_s40_curved_planar_rings.py \
  --output /private/research/s3z2/input_readiness.json

# Only after readiness == READY_FOR_ORIGINAL_NATIVE_TRIAL
python s3z_s40_circular_seam_gate.py \
  --original-step /private/original/i25o_s40.step \
  --s3w-bp /private/s3w/s40_spline_shared_repair.partial.bp \
  --s3w-manifest /private/s3w/s40_spline_shared_repair_manifest.json \
  --output /private/research/s3z2/native_trial_receipt.json
```

O protótipo `run_private_trials` continua retornando **recibos de tentativas**, mesmo se houver êxito de testes amostrais. A admissão de face é uma decisão científica separada e exige validação independente com o original, sem reajustar tolerâncias após observar falhas. Os arquivos STEP/BP de terceiros **não foram incluídos** neste pacote e não são publicados no GitHub.

### Próximo passo condicionado

Com os quatro arquivos originais autorizados acessíveis, executar as oito tentativas de deslocamento, salvar os recibos negativos ou preliminares e revisar os candidatos. Se nenhuma passar todos os portões, permanecer em **156 patches / 22 faces** e investigar subdivisão conforme dos arcos circulares. S40 permanece um controle *manifold*, não uma evidência industrial positiva com arestas de incidência 3+.
