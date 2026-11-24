# S3.Z.1 — Verificação global de costuras indexadas no S40 original

**17/11/2026 — etapa de robustez topológica, sem admissão nativa nesta sessão.** Branch `research/benchmark-corpus-reverse-patches`, PR #225 em draft. Nenhuma mudança autorizada na `main`.

## Estado experimental preservado

A última admissão nativa amostral está documentada na S3.Y: **156 patches Bézier, 1.665 controles globais declarados, 264 costuras indexadas com dois lados, 96 lados abertos e 22 das 43 faces STEP originais representadas**. A face `#3044` foi admitida na S3.Y. As faces `#1827` e `#1907` permanecem bloqueadas por recorte nativo, respectivamente com 18 amostras `OUT` cada na candidata conjunta anteriormente testada. Não se trata de medições novas da S3.Z.1.

Fonte original requer SHA-256 `b79eb5be1fde71b6a8d086fe14800a1ec62e3a3c4618910c81c64d23718abf3b`; pai privado S3.W de 148 patches requer `c826487d8cee76f6649100c59e5ce84fa6cb43c9004f53c68e3e565e86cdb174`; filho aprovado S3.Y requer `af50597db4b8d7b3bcb2fc381596fefc95ba6b6e00ed169576bec7a6b7873177`.

## Implementação do portão topológico global

O protótipo de ensaios S3.Z foi reforçado com `audit_global_repair_scope`, executado para cada deslocamento candidato **antes** da auditoria geométrica. A função exige:

1. Prefixo exato dos 156 patches S3.Y e dos índices globais de controle anteriormente admitidos.
2. Alteração apenas dos 16 controles interiores compartilhados identificados pelas oito arestas circulares STEP originais; no deslocamento zero, nenhuma alteração anterior.
3. Análise exaustiva de dependências: **somente oito patches cilíndricos anteriores** podem ser modificados. Nenhum patch adjacente inesperado pode reutilizar controle móvel sem auditoria.
4. Preservação integral do furo original `#218` (patches 96–125) e da face já admitida `#3044` (patches 148–155).
5. Para todas as 12 arestas STEP das duas faces bloqueadas, incidência `1→2` no atlas de patches, pareando exatamente uma face antiga com uma nova, e orientação dos quatro controles **invertida** entre os dois lados. Igualdade de um conjunto não ordenado de índices não é suficiente.
6. Ausência de costura com mais de dois lados, controles degenerados, registro de arestas duplicado e reindexação anterior.
7. Cardinalidade esperada da candidata conjunta: **160 patches, 1.685 controles, 278 costuras indexadas com dois lados e 84 lados abertos**. São expectativas estruturais de uma **candidata não admitida**.

Os oito arcos originais são `#1523 #252 #1834 #1886` em `#1827` e `#1911 #1962 #326 #1593` em `#1907`. Os testes de deslocamento entre 0 e 0,0014 mm não alteram o orçamento fixo de erro geométrico de **0,001 mm**.

## Validação efetuada e lacuna

**28/28 testes herméticos aprovados, 0 falhas, 0 ignorados**, sendo 13 testes já presentes no protótipo S3.Z e 15 novos testes adversariais de incidência, orientação, aliasing, mutação indevida, furo, face `#3044` e cardinalidades. A compilação Python também passou. O código do piloto atualizado, os testes e o log estão no pacote reproduzível da etapa, cujo SHA-256 é `9e34dcb5a79ddc0f39f47a27115b5d88706ce1c07e6c9bb55d88bc69f7612df0`.

**Não foi possível montar o STEP original e o BP privado S3.W nesta sessão.** A tentativa de acesso ao arquivo público externo também falhou. Assim, nenhum ensaio S3.Z.1 foi executado sobre os `TopoDS_Face` originais, nenhuma das duas faces foi admitida, e não se alegam aproximações certificadas, geração TRI/QUAD pelo APMesh nem regressão C++ de produção. A auditoria é **topológica e sintética**, não um certificado geométrico do S40.

## Próxima decisão

Executar o protótipo com o original STEP autorizado e BP S3.W de SHA fixado; exigir equivalência de costuras, `IN/ON` de todos os pontos originais amostrados nos dois proprietários de cada aresta, limites radiais Bernstein das superfícies cilíndricas modificadas, distância às curvas nativas, orientação e não regressão do furo. Em caso de falha, preservar o atlas de **156 patches / 22 faces**, investigar subdivisão conforme de arcos e **não** relaxar tolerâncias após a observação. Manter PR #225 draft e `main` protegida.
