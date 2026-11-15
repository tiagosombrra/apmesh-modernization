# APMesh Mesh Studio — R2.2: diagnóstico de navegação, picking e heap

**Data:** 15/11/2026. **Branch:** `feature/mesh-studio-fixture-first-20261114`.
**Commit de implementação testado:** `1f323d87e5b6dbcc7f2cfdec29d718c8b03044f2`.
**CI original:** [#43746603645](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/43746603645) — **3/3 jobs aprovados**.

## O que foi implementado

- Um instrumento de órbita controlada em cada uma das duas vistas vtk.js (XYZ/UV), com 24 movimentos programados, `requestAnimationFrame`, chamada efetiva ao renderizador e restauração da câmera original.
- Medições de duração total, rendimento médio de quadros programados, intervalos de quadro p50/p95/máximo. Esta contagem **não é** a quantidade de quadros efetivamente apresentados pela GPU.
- Medição da chamada síncrona original do `vtkCellPicker` e do ID de face retornado, sem adulterar a correspondência XYZ/UV.
- Leitura da estimativa `performance.memory` (quando existir) e de métricas de heap via Chrome DevTools Protocol (CDP). São estimativas de heap JavaScript, **não** RAM total do processo nem VRAM.
- Teste Playwright para 50.000 QUAD sintéticos, com recibo JSON original publicado como artefato do CI; teste 500.000 QUAD opcional com limite de 300 s, **não executado** na suíte padrão.
- Testes gráficos serializados (um worker) para evitar concorrência entre benchmarks WebGL que tornaria as medidas menos comparáveis.
- O motor científico Python permanece intocado; todas as métricas e a malha sintética do teste são descritas explicitamente como diagnósticos de renderização, **não** experimentos APMesh.

## Regressão comprovada

| Ambiente | Resultado | Observação |
|---|---|---|
| Python/VTK Linux | 209 testes, 0 falhas, 4 ignorados | Xvfb/Mesa no runner |
| Python Windows | 209 testes, 0 falhas, 10 ignorados | GPU física Windows não homologada |
| Chromium | 10 testes aprovados e 1 ignorado | 500.000 QUAD é opt-in |
| Build React/TypeScript | Aprovado | Inclui `Bench.tsx`, `Viewer.tsx` e instrumentos TS novos |

## Valores originais, uma execução de 50.000 QUAD sintéticos

| Métrica | Resultado |
|---|---:|
| Frames programados, XYZ/UV | 24 / 24 |
| Órbita XYZ: rendimento programado | **14,78 quadros/s** |
| Órbita UV: rendimento programado | **16,82 quadros/s** |
| Intervalo p50, XYZ | 69,5 ms |
| Intervalo p95, XYZ | 73,9 ms |
| Intervalo p50, UV | 51,6 ms |
| Intervalo p95, UV | 76,4 ms |
| `vtkCellPicker.pick`, UV | **197,4 ms**, face sintética #25087 |
| Heap JS Chromium/CDP, antes | 31.438.388 bytes |
| Heap JS Chromium/CDP, depois | 34.407.872 bytes |
| Diferença observada entre dois instantes | 2.969.484 bytes |

Fonte primária: `r22-50k-scripted-interaction.json` com SHA-256 `2a6b6696b28e7865c9b51dd7542ce8390918b2c1afbc0ebea268a34355595131`, preservado no artefato original do GitHub Actions. O browser original foi HeadlessChrome 141 no Linux hospedado. Em outra máquina ou execução os números podem variar substancialmente. Não foram construídos intervalos de confiança nem calculadas médias entre execuções independentes.

## Conclusões técnicas e próximos gates R2.3

1. A operação de seleção (197,4 ms em uma ocorrência no runner) merece análise, mas **não demonstra** latência típica no Windows do pesquisador. Evitar prometer seleção instantânea antes de novos testes com várias faces e percentis.
2. Há redundância material no caminho dos dados: criação de arrays JS aninhados, conversão por `.flat()` e indexação de faces. Próximo experimento: **buffers tipados `Float32Array`/`Uint32Array` e mapeamento original de IDs**, com prova exata de equivalência de faces e origem antes de comparar desempenho.
3. Medir 500.000 elementos no navegador com ativação explícita de estresse, verificar tempo, abandono, limite de memória e possibilidade de LOD. **O CI normal não qualifica esse caso**.
4. Repetir o mesmo teste várias vezes na **mesma estação Windows/GPU**, registrando versões de Chromium, driver, resolução e CPU/GPU. Métricas WebGL no runner não substituem testes locais de hardware.
5. Em caso de LOD, a UI deve revelar a resolução utilizada e preservar a identificação dos elementos originais; não alterar silenciosamente métricas científicas nem soldar patches por proximidade.
6. Permanecem abertos modelos reais grandes, incidência multipatch não-manifold, eventos efetivos do gerador, all-QUAD real, anisotropia real, instalador e compositor científico.

## Reprodução local

No repositório atualizado, a partir da raiz, use o inicializador Windows já fornecido:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/mesh_studio/web/scripts/start-windows.ps1
```

No navegador: `http://127.0.0.1:5173/bench.html`. Selecione 50.000 QUAD, verifique as duas vistas e use o botão **Medir órbita XYZ + UV**. Clique depois no centro da vista UV para gerar uma amostra de picking. O recibo aparece no final da página. A opção de 500.000 células exige cautela devido à memória e ao tempo potencialmente altos.

Para executar o teste opt-in localmente, com as dependências do frontend instaladas:

```bash
cd tools/mesh_studio/web
APMESH_R22_500K=1 npm run test:e2e -- viewport-interaction-r22.spec.ts
```

No PowerShell:

```powershell
$env:APMESH_R22_500K='1'
npm run test:e2e -- viewport-interaction-r22.spec.ts
```

A saída pode ser falha ou indisponível dependendo da GPU/WebView. Não trate a aprovação desse teste como prova de 500.000 elementos de um modelo científico real.
