# Mesh Studio R2.1 — Medição de renderização no navegador

Data: 15/11/2026. Alterações isoladas à interface React/vtk.js e aos testes Playwright. Não modificar os algoritmos C/C++ do APMesh, as malhas científicas nem o protocolo de aceitação de épocas.

## Implementado

O modo de diagnóstico local `http://127.0.0.1:5173/bench.html` gera malhas QUAD **sintéticas** de 1 mil, 50 mil ou 500 mil elementos, em duas vistas XYZ/UV, e exercita o mesmo componente vtk.js utilizado pelo aplicativo. Não recebe nem produz resultados científicos do APMesh e não atribui patches ou curvas reais aos dados artificiais.

O componente Viewer registra um evento opcional ao completar a primeira chamada de renderização vtk.js. As medições incluem o tempo total desde o início da geração no navegador até o retorno dessa chamada, separadamente para XYZ e UV, além da duração de criação da malha e uso de heap JS quando o navegador o permite. Não são FPS, tempos de GPU, VRAM, latência consistente de picking, energia, erro geométrico ou performance do gerador.

O ensaio de 50 mil elementos faz parte dos testes Chromium do CI, inclusive com controle de filtros. O cenário de 500 mil fica inicialmente disponível para execução **manual e exploratória**; não é declarado aprovado sem evidência do ambiente e sua configuração. O limite binário de 32 MiB e a origem dos modelos reais permanecem inalterados.

## Gates de execução e evidências

- Testes existentes de seleção sincronizada, câmera persistida, schema de transporte e origem SHA-256 continuam obrigatórios.
- `tests/viewport-scale.spec.ts` verifica 1 mil e 50 mil elementos no Chromium, retorno das duas renderizações, presença dos canvases, controle QUAD/arestas e rótulos sintéticos.
- O CI só será qualificado após verificar `npm run build` e todos os testes E2E no **commit exato**. A existência dos arquivos TS/HTML não representa aprovação.
- O custo de geração em JS, as cópias em arrays aninhados e a ausência de LOD ainda exigem revisão. Metas de FPS, seleção, uso de VRAM e 500 mil células em máquina Windows não estão encerradas.

## Uso local

```bash
# A partir da raiz do repositório, iniciar serviço Python no terminal 1
python -m uvicorn tools.mesh_studio.web_api:app --host 127.0.0.1 --port 8765

# Terminal 2
cd tools/mesh_studio/web
npm install
npm run dev
```

Acesse `/bench.html` no endereço do frontend. Para Windows/UCRT64, prefira o script existente `tools/mesh_studio/web/scripts/start-windows.ps1`, que usa Python 3.13 nativo no ambiente virtual e não o interpretador MSYS2.

## Próxima etapa

Após os testes Chromium, medir latência de seleção, tempo de rotação, frames produzidos sob interação e memória do processo navegador com os datasets 1k/50k/500k, além de avaliar streaming/LOD ou decimação controlada **sem alterar os dados científicos**. Somente então estabelecer metas quantitativas e critérios de produto.
