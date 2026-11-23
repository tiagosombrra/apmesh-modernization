# Doutorado — pauta de decisão S40-F31 para os professores Creto e Bento

**Situação do projeto (23/11/2026):** APMesh gerou a malha **TRI nativa** do Thingi10K #293137 (3.504 triângulos, etapa inicial aceita). A reconexão da malha e as versões **QUAD são externas**, produzidas com pós-processamento controlado. **Ainda não existe um gerador QUAD nativo** no motor atual nem uma comparação cientificamente admitida com um resultado original do QuadWild. O `main` segue preservado.

## O que podemos demonstrar

- Geometria Bézier derivada de STL: 876 patches, curvas compartilhadas corretas, execução C++ nativa e geração TRI com evidência de repetibilidade; porém **não equivale a CAD original**.
- Versão QUAD externa com 876 elementos: qualidade Jacobiana média melhorada de 0,5981 para 0,6730 ao deslocar somente centros internos de 189 triângulos originais; feições e bordas preservadas. O pior ângulo continua limitado pelo STL.
- Nova F31, **geometrias geradas sinteticamente**, sem terceiros: nove superfícies fechadas (gêneros 0/1), 472 triângulos originais e 1.416 QUAD derivados. Cinco modelos melhoram a média de Jacobiano e quatro permanecem iguais. Média simples por modelo: 0,7105 → 0,7669. **Não é validação em nove modelos reais nem prova de superioridade do QUAD nativo.**
- Inventário histórico: 23 modelos da literatura; apenas um avançou à execução TRI nativa, e **zero** pares QUAD de referência foram independentemente confirmados/autorizados.

## Decisões solicitadas

1. **Qual é a pergunta científica?** Preservação e discretização de superfícies Bézier com curvas compartilhadas e junções, ou criação de um remalhador QUAD competitivo para STL? O escopo atual não permite assumir ambas como uma contribuição já demonstrada.
2. **Devemos criar QUAD nativo agora?** Alternativa A: apenas tipo/exportação/validação de QUAD (sem gerador). Alternativa B: gerador experimental próprio em cada patch Bézier, com sincronização de curvas. Alternativa C: pipeline global de quadrangulação orientado por feições (projeto muito maior). Sugestão para debate: A → B, apenas se QUAD fizer parte da contribuição central.
3. **Qual será a validação:** modelos Bézier autorais e direitos de uso; qualidade do QUAD (Jacobiano escalado, ângulos e distorção), conectividade, arestas de feição, erro geométrico, autointerseções e tempo de execução; registrar falhas, não apenas sucessos.
4. **Como comparar com o QuadWild:** obter par exato STL + QUAD gerado pelos autores, verificar versão/parâmetros/densidade/escala, permissões e critérios. A entrada STL do QuadWild não é equivalente ao domínio Bézier reconstruído usado pelo APMesh.

**Encaminhamento proposto:** manter o PR #225 como *Draft*, aprovar por escrito uma opção de escopo e um protocolo de métricas antes de qualquer mudança no motor C++. Dar prioridade à aquisição de um CAD Bézier com junções e autorização de utilização, além do par QuadWild verificável.
