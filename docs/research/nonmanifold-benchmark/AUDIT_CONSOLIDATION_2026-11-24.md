# Auditoria de consolidação — NON-MANIFOLD FIRST v3

**Data:** 24/11/2026. **Escopo:** frente de pesquisa do PR #225; não é auditoria integral do produto nem qualificação de modelo novo. Base congelada: `92b8af3b9e73072d1122d82ed956f75b608ea5c1`.

## Inventário e decisões

A árvore Git anterior, integral (não truncada), continha 359 arquivos na frente de pesquisa, dos quais 97 diretamente na raiz, 173 em `probes/` e 80 módulos Python de teste. Foram identificados planos/READMEs acumulativos redundantes, seis workflows de regressão sobrepostos e quatro READMEs antigos de pacotes S40. Foram mantidos os relatórios científicos, fixtures, galerias, recibos e verificadores históricos; as referências de planejamento tornaram-se aliases para o plano vigente. Os textos integrais anteriores e receitas retiradas permanecem no [snapshot Git congelado](https://github.com/tiagosombrra/apmesh-modernization/tree/92b8af3b9e73072d1122d82ed956f75b608ea5c1).

**Política:** arquivo histórico com resultado único, código científico ou configuração reproduzível não é lixo. Remover somente wrappers obsoletos e orquestrações redundantes. Não excluir dados científicos, alterar baselines ou apagar `main`/histórico. F25/F26/F27 compilação/replay especializado continuam como receitas manuais; os demais seis workflows redundantes são retirados da árvore ativa em favor de um comando local.

## Correções científicas e operacionais

- Origem, prioridade, classe, papel, incidência e estados de fonte/atlas/TRI dos 14 registros v3 são validados de forma fail-closed. A combinação de mudanças coordenadas não pode transformar S40 em positivo nem antecipar um TRI. O snapshot v3 é explícito; futuras transições precisam de evidência e revisão conjunta.
- G0–G7 têm uma definição única no plano. Corrigida a sequência circular de M3 (G0–G2 antes da construção; G3/G4 depois; G5/G6 após geração) e o número arbitrário de quatro folhas para N3. N2 `derived` não é prova de topologia original.
- Regressores anteriores: preservados. Um runner local separa módulos Python, Node, recibos F27/F29/F30/F31, verificação de capacidade original, build CMake e CTest, com saídas explícitas PASS/FAIL/BLOCKED. Ausência, zero testes ou skips não certificam cobertura.

## Evidência realmente executada

O acesso Git direto ao repositório falhou por DNS. Recuperaram-se 36 arquivos originais dos pacotes públicos F19B–F31/v3; todos os 36 hashes Git blob foram comparados com o snapshot remoto e coincidiram. Antes das correções: 471 testes em 14 módulos, 0 falhas, 0 skips. Após as correções: **510 testes em 15 módulos**, 0 falhas, 0 skips (32 testes do gate v3 e 25 do runner, incluídos no total). A bateria incluiu a compilação do verificador C++ independente F22, não o build completo do motor. Execução local Python 3.13.5; ambiente detectado: CadQuery 2.8.0, OCP 7.9.3.1, NumPy 2.3.5, SciPy 1.17.0, Shapely 2.1.2, Trimesh 4.11.1. O [recibo](evidence/consolidation/recovered_regression_receipt.json) registra contagens por módulo e hashes dos logs locais, sem geometria de terceiros.

| Gate | Resultado observado |
|---|---|
| 14 módulos históricos recuperados + 1 novo | PASS, 510 testes, 0 falhas/skips |
| Inventário integral de testes Python históricos (80 módulos) | BLOCKED; 66 históricos não recuperados |
| Node, replay integral dos recibos, capacidade original no checkout | BLOCKED; checkout ausente |
| CMake/CTest do motor no HEAD final | BLOCKED; checkout ausente |
| Replay de dados CAD/STL privados | NOT RUN; exige workspace autorizado |
| Novo modelo não manifold M1 | NOT RUN; não promovido |

O runner retornou código 2 (**BLOCKED**) intencionalmente. Não se certifica regressão integral a partir de 510 testes parciais. A prova de preservação dos arquivos protegidos é uma comparação da árvore Git, não um teste dinâmico do motor.

## Gate de liberação de M1

Executar o comando documentado no [plano vigente](PLAN_NONMANIFOLD_FIRST_V3.md) no checkout integral e limpo, obter o recibo de cobertura completa e resolver os bloqueios. Registrar separadamente casos privados não executados. A próxima execução científica é Four-Sheet Curved, não S40; a matriz v3 permanece sem novo TRI não manifold qualificado. Não alterar motor de produção ou promover `main`.
