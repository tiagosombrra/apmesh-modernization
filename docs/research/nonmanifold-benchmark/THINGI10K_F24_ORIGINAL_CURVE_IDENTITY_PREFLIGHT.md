# S40-F24 — Identidade de curvas compartilhadas do Bunny #293137: pré-auditoria independente

**Data:** 2026-11-23. **Ramo:** `research/benchmark-corpus-reverse-patches` (PR #225, Draft). **Classificação:** auditoria de entrada/semântica baseada em código original e no `.bp` real; **não é execução do `Geometry` C++**. `main` e modelos anteriores não foram modificados.

## O que foi efetivamente conferido

O `.bp` privado gerado na F22 a partir do STL original #293137 (Bunny LowPoly) foi reaberto, com verificação obrigatória do SHA-256 `6049d4e46cfd73e104c2b63ef34d3a8089c4f59d1f940bee8c1ec66a8f0bafb0` e dos exatos 538.482 bytes. A gramática da entrada já passou pela validação C++ de produção (F23: 32/32 testes e 3/3 execuções, apenas `ValidateBezierPatchInput`). Esta etapa confere independentemente as regras de **identidade das curvas** implementadas no código C++ atualmente versionado:

- `Geometry::VerifyCurveGeometry`, `src/data/geometry.cpp` (Git blob `411cff31f274f260eabf1d4e43e09e46c3c5a6a9`): procura cada curva existente em ordem, com os quatro controles diretos ou invertidos.
- `PointAdaptive::operator==`, `src/data/point_adaptive.cpp` (blob `92c77580d6778ee793c154d1f4f3dbe7e58ee34f`): comparação **por coordenada**, com `|delta| <= EPSYLON` global; não usa igualdade exata de identificadores.
- `PatchReader::ReaderFilePatches`, `src/input_output/patch_reader.cpp` (blob `a00fa0c712ae31380e08e557be4d199abf5d40ea`): usa interning de pontos com tolerância fixa `1e-7`, independentemente do parâmetro de meshing.
- `src/application/runtime_state.cpp` (blob `d21ceb3397c7825bb50534be072261908c9b0e49`) e `runtime_config.cpp` (blob `21438cd2f2921508832cdd833ed8eca067fb3bfd`): `EPSYLON` padrão `1e-7`, configurável em tempo de execução.

Os Git blobs referem-se à leitura conectada do repositório, não a um binário de produção reexecutado nesta F24. O ambiente não conseguiu clonar o checkout completo (`github.com` sem resolução DNS); o limite de observação nativa da F23 permanece.

## Resultado no `.bp` real

| Invariante ou métrica | Resultado |
|---|---:|
| Registros `v` de controle | 7.886 |
| Registros `p` bicúbicos | 876 |
| Usos orientados de lados de patch | 3.504 |
| Curvas de fronteira geometricamente distintas (4 controles, direta ou inversa) | **1.752** |
| Incidências por curva | **2 em 1.752/1.752** |
| Pares compartilhados com orientação de contorno incorreta | **0** |
| Pares de controles *distintos* confundíveis por EPS `1e-7` a `1e-1` | **0** |
| Pares de curvas *distintas* confundíveis por EPS `1e-7` a `1e-1` | **0** |
| Consultas de `VerifyCurveGeometry` previstas (quatro por patch) | 3.504 |
| Entradas de curvas examinadas sob a busca linear original e correspondência inequívoca | **3.069.504** |
| Comparações de IDs no `FindControlPoint` inferidas dos índices de controle da entrada original | **51.714.078** |

Os dois últimos números são **contagens determinísticas derivadas do fluxo do código e da ordem dos registros**, não medições de tempo, memória, número de alocações ou performance do mesher original. A busca linear de curvas pressupõe ausência de falsas correspondências por tolerância. Esta premissa foi examinada diretamente para `1e-7`, `1e-5`, `1e-3`, `1e-2` e `1e-1` neste modelo.

**Decisão:** o modelo #293137 é **apto apenas para prosseguir à prova de construção das curvas C++**, dentro desses limites de pré-auditoria. A continuidade C0 está verificada para a representação matemática serializada; a continuidade C1 não está garantida. Um EPS maior, outros modelos, efeitos de ponto flutuante/estado mutável ou um `Geometry` modificado requerem nova qualificação. Em particular, este controle não autoriza um novo modelo original CAD; a representação continua sendo a subdivisão plana do STL de terceiros.

## Reprodutibilidade e negativos

Arquivos da etapa:

- `probes/thingi10k_f24_curve_identity_preflight.py` — parser de BP indexado, inspeção de pares de curvas, checagens de orientação e rastreamento das buscas sequenciais do código original.
- `probes/test_thingi10k_f24_curve_identity_preflight.py` — **24/24 testes herméticos positivos e negativos**, incluindo curvas quase coincidentes, inversão de orientação, limites de EPS, índices inválidos, não finitos, alteração de identidade e rejeição de domínio aberto.
- `evidence/thingi10k/thingi10k_f24_293137_curve_identity_preflight.json` — recibo de contagens e status, sem coordenadas, STL original, ZIP original ou derivado privado `.bp`.

Da pasta `docs/research/nonmanifold-benchmark/probes`:

```bash
python -m unittest -v test_thingi10k_f24_curve_identity_preflight
python thingi10k_f24_curve_identity_preflight.py \
  --private-bp /private/293137_piecewise_linear_candidate.bp \
  --output /private/f24_new_receipt.json
```

O CLI não sobrescreve recibos anteriores; recusa `.bp` de tamanho/hash divergente e não toca no código C++ ou no corpus de modelos do repositório.

## Bloqueios para a F25

1. Executar, num checkout completo e ambiente controlado, o **`PatchReader::ReaderFilePatches` de produção**, não apenas o validador de cabeçalho.
2. Inspecionar `Geometry::GetNumberPatches()`, `GetNumberCurves()`, ponteiros compartilhados, direção de controles, curvas de incidência 2 e memória, observando eventual gargalo da busca linear sem alterar a regra de identidade antes de medi-la.
3. Tentar gerar a primeira malha TRI real de APMesh com aceite e exportação verificáveis, sob orçamento de tempo/memória explícito; só então analisar QUAD suportado e métricas de qualidade.
4. Revisar direitos por asset antes de distribuir STL, `BP` derivado e artefatos de malha, e não tratar esta entrada Badia como comparação de saída QuadWild.

**Admissão científica de modelo novo: zero. Geração TRI/QUAD de APMesh com esse modelo: zero. PR permanece Draft.**
