# V5.11 — continuidade auditada da evidência C++ original

**Data:** 23/11/2026. **Classificação:** manutenção da evidência científica histórica, sem alteração do algoritmo nativo, sem novo epoch e sem distribuição.

## Defeito de continuidade identificado

A execução nativa original [GitHub Actions #45147268663](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/45147268663), SHA de código 7d41ab8ec55b34bf879f9efc2a547168e50143de, foi a fonte dos dez arquivos históricos C++ certificados pelo STUDIO.

Os artefatos tinham dois prazos distintos, verificados diretamente no GitHub Actions:

- Arquivos C++ brutos pós-commit, resumos, logs do gerador: **30/11/2026, 09:30 UTC** (sete dias).
- Cena nativa, manifesto e SVGs de Eistute e Book: **07/12/2026, 09:29 UTC** (14 dias).

As V5.9, V5.10 e V5.11 precisavam das duas partes. Por isso, o prazo de falha do CI era **30/11**, e não 07/12. O ZIP independente com os dez arquivos já estava arquivado no Drive pessoal do Doutorado com SHA originalmente conferido: a8564310bf28cb8ec26aaa5f71b67399a374433f06181d7f598f7070fd9d8523.

## Preservação sem promover nova execução científica

Na branch de manutenção, o workflow mesh-studio-v511-cpp-evidence-continuity.yml recupera ambos os arquivos do run original exato. O verificador v511_native_evidence_mirror.py exige as mesmas dez entradas com tamanho e SHA-256 fixos; reabre os registros pós-commit da execução C++, reconstrói as identidades das faces, patches, UV e SVGs e rejeita alteração de fonte.

[**CI de renovação #45189301366 — 2/2 PASS**](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/45189301366), código do espelho SHA **6765536f05dbf83453aa7f2c65b79b696b9447c5**:

- [Arquivo com os dez arquivos originais — artefato #14825221229](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/45189301366/artifacts/14825221229).
- [Cadeia de proveniência original e espelho — #14823419997](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/45189301366/artifacts/14823419997).
- [Nova auditoria independente após download — #14825735383](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/45189301366/artifacts/14825735383).

**Expiração dos três artefatos espelhados: 21/02/2027, 13:58 UTC**, segundo os metadados do GitHub. Essa retenção não é permanente. O Drive pessoal continua a cópia independente durável. Não publicar URL privado de Drive em PRs ou Issues.

## Substituição controlada no CI de produto

O workflow mesh-studio-v511-built-reviewer.yml passou a consumir o novo run de espelho #45189301366, e não o run de origem que expira em novembro. Ele recupera **separadamente** os dez arquivos e o recibo de proveniência; verifica sua cadeia contra o run original, o SHA original de código, o SHA do workflow de espelho e a tabela individual de SHA/tamanho. Em seguida, a checagem já existente de V5.9 **reabre outra vez** o C++ nativo e todos os SVGs para o teste Chromium.

[**CI da V5.11 após o corte #45189641930 — 3/3 PASS**](https://github.com/tiagosombrra/apmesh-modernization/actions/runs/45189641930), **commit exato 7d52e7f602e1f23595724c0a0f1dd5689fc69cc2**:

| Verificação | Ubuntu 24.04 | Windows Server 2022 |
| --- | --- | --- |
| Reabertura de evidência C++ original e proveniência do espelho | PASS | PASS |
| Testes Python e negativos de segurança | 36 PASS | 36 PASS |
| Browser Chromium, verdadeira cena Eistute/Book e SVG original | 4 PASS | 4 PASS |
| Desligamento das portas locais 8765/5173 | PASS | PASS |
| Terceiro job independente — sete arquivos estáticos idênticos entre SOs | PASS | PASS |

Manifesto compilado da interface **idêntico nos dois sistemas**: SHA256 **ad6c4627090a335c0ed7e3bf1bae0c0d062ed1e48249f120b10f3ba8ff8a85f5**.

## Próxima renovação e limites

Antes de **21/02/2027**, a continuidade do CI deverá ser renovada **a partir do espelho ainda válido**, com outra auditoria integral das dez entradas e dos dados nativos. O workflow preparado admite o tipo de upstream **mirror** e identificador do run fonte, mas a disponibilidade de workflow_dispatch depende da instalação/configuração no branch padrão do GitHub; **não declarar renovação automática**. Caso não esteja disponível, fazer novo PR de manutenção e regenerar um espelho somente após revalidar o upstream ainda não expirado. Não substituir fonte ausente por fixture sintética.

O espelhamento **não** recompila GeneratorAdaptive, não simula execução original, não altera o código científico e não confere aprovação R2.8. Os únicos global steps C++ aceitos em Eistute e Book continuam **[1]**. Nada foi mesclado a main, publicado, assinado ou liberado como distribuição.

**Permanecem abertos:** homologação **humana independente** em Windows e Linux físicos ([Issue #255](https://github.com/tiagosombrra/apmesh-modernization/issues/255)); licenciamento de distribuição ([#250](https://github.com/tiagosombrra/apmesh-modernization/issues/250)); aceite editorial dos orientadores ([#251](https://github.com/tiagosombrra/apmesh-modernization/issues/251)); geração e validação científica de epochs originais distintos com erro CAD e ancestrais para R2.8.
