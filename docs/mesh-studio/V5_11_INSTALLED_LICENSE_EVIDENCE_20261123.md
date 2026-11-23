# V5.11 — evidência de licenças efetivamente instaladas (Linux e Windows)

**Data:** 23/11/2026. **Escopo:** ambiente Python mínimo de revisão local e dependências npm efetivamente instaladas para construir a interface estática V5.11. **Não é aprovação jurídica de redistribuição, SBOM definitivo do bundle JavaScript ou liberação comercial.**

## Contexto da Issue #250

A V5.6 havia identificado **141 entradas npm** no lockfile e **79 registros Python** agregados de diferentes perfis. Isso não comprovava os arquivos reais de licenças dos pacotes instalados nem a composição efetivamente distribuída. O servidor estático da V5.11 utiliza um ambiente Python mínimo de **13 pacotes** instalados via hashes fixos, sem PyMuPDF, VTK, NumPy e outras dependências de processamento científico e publicação em PDF.

A exclusão de PyMuPDF do servidor mínimo **não elimina** a obrigação de analisar o ambiente científico mais amplo. O manifesto de pesquisa inclui PyMuPDF 1.26.7 e seu fornecedor oferece **AGPLv3 ou licença comercial**. Fontes oficiais: [PyMuPDF licensing](https://pymupdf.io/licensing), [PyMuPDF 1.26.7](https://pypi.org/project/pymupdf/1.26.7/).

## Evidências implementadas

- O auditador Python **v511_runtime_license_evidence.py** confronta as versões efetivamente instaladas no venv com o lock SHA-256 específico do SO, copia arquivos reais de licença, aviso e copyright, com seus tamanhos e SHA-256; distingue expressões declaradas de texto original disponível.
- O auditador npm confere todas as entradas do lock, SRI/URL do registro, versão e metadados dos pacotes instalados após npm ci com scripts desativados. Copia arquivos reais de LICENSE e NOTICE. Os aliases são aceitos somente quando o **próprio lockfile** declara o pacote de origem, como a entrada para TypeScript antigo.
- Um terceiro job independente, **v511_license_evidence_reaudit.py**, baixa as duas coleções da mesma revisão, exige os mesmos SHA/versões de origem e reabre cada arquivo de licença capturado, impedindo arquivos ausentes, adulterados, links simbólicos e diretórios inesperados. **Nenhum** desses processos supõe que todo pacote instalado faça parte do JavaScript distribuído.

**[GitHub Actions #45200149320 — 3/3 SUCCESS](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/45200149320).** Revisão de código/CI efetivamente testada: **c2d4ac7ad874ac2b1db597060ea746e7171b985b**.

| Resultado concreto | Ubuntu 24.04 | Windows Server 2022 |
| --- | ---: | ---: |
| Pacotes Python mínimos efetivamente instalados | 13 | 13 |
| Pacotes Python sem texto de licença localizado | 0 | 0 |
| Entradas npm do lockfile | 141 | 141 |
| Pacotes npm realmente instalados no host | 91 | 89 |
| Arquivos reais de licença/aviso reabertos, Python + npm | 107 | 106 |
| Pacotes npm instalados sem arquivo de licença na raiz | 3 | 2 |

**Exceções verificadas, sem inferir licença a partir de metadata:**
- Linux: node_modules/@rolldown/binding-linux-x64-gnu, node_modules/@rolldown/binding-linux-x64-musl e node_modules/seedrandom.
- Windows: node_modules/@rolldown/binding-win32-x64-msvc e node_modules/seedrandom.

Os pacotes opcionais nativos da ferramenta de build **não são presumidos integrantes do bundle JavaScript**. Seedrandom declara MIT em metadados, mas não teve texto original LICENSE recuperado na raiz do pacote instalado. A obtenção dos textos exatos e a análise de atribuição permanecem pendentes.

**Rechoir 0.6.2:** falta a declaração de licença na entrada do package-lock, mas o pacote instalado nos **dois** sistemas possui texto original LICENSE de **1.056 bytes**, com copyright Tyler Kellen e concessão MIT; SHA-256 **55d982a7adf646503ff21d0de490091d6d74a9f3447ba6959bf4fbd9ee7385ae**. Essa lacuna documental específica foi identificada e o texto foi preservado, sem alterar o lockfile ou inferir aprovação de distribuição.

**Dependências diretas do navegador:** os pacotes @kitware/vtk.js 38.0.9, react 19.3.1 e react-dom 19.3.1 foram encontrados em ambas as instalações com arquivos de licença presentes. Declarações de licença em seus pacotes: BSD-3-Clause para vtk.js; MIT para React e React DOM.

SHA-256 do package-lock npm: **12f5a67d1b56007022f5843cbad324c0df987df006b9eac6591247f16cf38a90**. Inventário dos **sete** arquivos realmente compilados da interface: **ad6c4627090a335c0ed7e3bf1bae0c0d062ed1e48249f120b10f3ba8ff8a85f5**.

### Artefatos verificáveis

- [Pacotes, textos de licença e recibo Linux — #14830093500](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/45200149320/artifacts/14830093500).
- [Pacotes, textos de licença e recibo Windows — #14830273271](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/45200149320/artifacts/14830273271).
- [Reabertura independente dos textos e hashes dos dois sistemas — #14831096503](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/45200149320/artifacts/14831096503).

Todos têm retenção limitada até **21/02/2027, aproximadamente 14:59 UTC**. Reabrir um arquivo de licença e confirmar seu SHA não equivale a interpretar suas cláusulas ou demonstrar que os avisos necessários foram embarcados com uma versão de software.

## Critérios não satisfeitos — distribuição bloqueada

1. **Composição efetiva do bundle:** identificar todas as contribuições transitivas que realmente entraram nos sete arquivos JS/CSS/HTML compilados e produzir o NOTICE de redistribuição aplicável. A árvore npm instalada não demonstra essa composição.
2. **Textos/obrigações remanescentes:** esclarecer os arquivos de licença dos bindings Rolldown dos dois SOs e seedrandom, bem como possíveis avisos de terceiros embutidos nas bibliotecas diretas.
3. **Ambiente Python científico completo:** auditar as instalações reais e possíveis ativos redistribuídos do perfil com PDF/VTK, incluindo a alternativa AGPL/comercial de PyMuPDF, antes de decidir pelo tipo de distribuição.
4. **Revisão humana:** interpretação jurídica e definição do artefato a ser distribuído continuam exigidas pela [Issue #250](https://github.com/tiagosombrra/apmesh-modernization/issues/250). A homologação física continua pendente na [Issue #255](https://github.com/tiagosombrra/apmesh-modernization/issues/255); o formato editorial requer aval dos orientadores na [Issue #251](https://github.com/tiagosombrra/apmesh-modernization/issues/251).

Não houve alteração do C++ original, de malhas, de figuras certificadas, de algoritmo QUAD/anisotrópico ou de política científica. O único global accepted native step de Eistute e Book continua **[1]**; R2.8 científica permanece **bloqueada**. Nenhum merge na main, tag, release ou distribuição foi autorizado.


## Complemento: composição comprovada do JavaScript compilado em V5.11

**23/11/2026.** O inventário anterior de 141 entradas npm não demonstrava quais bibliotecas eram realmente incluídas na saída de produção. A auditoria foi estendida na **mesma Draft PR #261**, sem alteração do aplicativo ou do C++ científico. O script tools/mesh_studio/web/scripts/audit-v511-bundle.mjs executa uma **segunda compilação diagnóstica isolada** com Vite 8/Rolldown, recupera os módulos de cada chunk (hook generateBundle) e a saída de licenças nativa do Vite (build.license). É obrigatório reproduzir **byte a byte os sete arquivos estáticos** e o SHA256 de inventário anterior: ad6c4627090a335c0ed7e3bf1bae0c0d062ed1e48249f120b10f3ba8ff8a85f5. Nenhum arquivo de diagnóstico é incorporado à distribuição estática ou exposto pelo servidor local.

O novo validador tools/mesh_studio/v511_bundle_license_reaudit.py, independente do primeiro processo, baixa o grafo e os inventários dos **dois sistemas** e verifica o lock npm original, o SRI das dependências, as versões, os módulos atribuídos aos arquivos compilados, o SHA dos sete ativos e a cópia real dos avisos de licenciamento. Módulos internos do compilador, como o shim **__vite-browser-external**, não são confundidos com bibliotecas npm. O resultado é técnico, não é uma opinião jurídica.

**[CI #45209742219 — 4/4 SUCCESS](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/45209742219)**, SHA exato da implementação testada **fb665764143da62b9a44516654ed1057858c2639**:

| Evidência | Ubuntu 24.04 | Windows 2022 |
| --- | ---: | ---: |
| Arquivos de interface reproduzidos com hash idêntico | 7 | 7 |
| Chunks JavaScript rastreados | 3 | 3 |
| Pacotes npm efetivamente vistos no grafo | 13 | 13 |
| Entradas de licença do Vite | 13 | 13 |
| Arquivos originais de LICENSE/NOTICE/README reabertos | 108 | 107 |
| Reabertura independente e auditoria entre SOs | PASS | PASS |

Os **13 pacotes identificados no JavaScript real** são: **@kitware/vtk.js, d3-array, d3-color, d3-format, d3-interpolate, d3-scale, fast-deep-equal, gl-matrix, react, react-dom, scheduler, seedrandom e spark-md5**. Essa relação foi produzida por Rolldown e verificada nos dois SOs; ela não equivale à totalidade do diretório node_modules e não presume que bindings opcionais nativos de build sejam embarcados no navegador.

**Seedrandom 3.0.5:** o Vite efetivamente incluiu essa dependência e declarou MIT, mas sua saída build.license omitiu o campo de **texto**. A versão npm instalada de origem tem seu aviso MIT completo **dentro de README.md**, e não em LICENSE na raiz. O coletor preservou **o README integral** do tarball com SRI fixado e o SHA da seção MIT de David Bau (2019); outro job reextraiu independentemente o mesmo texto e verificou seu SHA. Nenhum texto MIT genérico foi fabricado. A saída Vite permanece marcada como **metadados sem texto** para essa entrada; o texto original complementar está separado e possui proveniência npm verificável. Uma futura lista THIRD_PARTY_NOTICES não pode copiar cegamente o JSON Vite e omitir esse aviso.

Arquivos de evidência de última execução, com retenção verificada até **21/02/2027 aproximadamente 15:50 UTC**:

- [Grafo e licenças de build Linux #14836090442](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/45209742219/artifacts/14836090442)
- [Grafo e licenças de build Windows #14835613038](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/45209742219/artifacts/14835613038)
- [Verificação independente do bundle e avisos #14835278629](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/45209742219/artifacts/14835278629)
- [Fontes instaladas Linux #14833519977](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/45209742219/artifacts/14833519977)
- [Fontes instaladas Windows #14835223617](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/45209742219/artifacts/14835223617)
- [Verificação independente dos textos instalados #14833469944](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/45209742219/artifacts/14833469944)

**Bloqueios remanescentes:** não existe um NOTICE de distribuição juridicamente aprovado e incorporado a um artefato distributivo definido; licenças compostas como spark-md5 (WTFPL OR MIT) e obrigações de atribuição devem ser revisadas; o perfil científico Python mais amplo ainda contém PyMuPDF sob modelo AGPL/comercial e não foi admitido para distribuição. A Issue #250 **continua aberta**. Não há aprovação humana física (Issue #255), segunda etapa original C++ aceita ou qualificação R2.8. Nenhuma alteração da main, tag, release ou publicação ocorreu.
