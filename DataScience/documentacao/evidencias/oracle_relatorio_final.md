# Relatório final — Oracle SQL CitizenTech

Execução real: 2026-11-17 23:48:16 -03:00 (America/Sao_Paulo).

**Oracle pronto para a entrega da FIAP no escopo solicitado.**

Conexão existente: container citizentech-oracle, usuário CITIZENTECH, PDB FREEPDB1, Oracle AI Database 26ai Free 23.26.3.0.0. Credencial DPAPI lida fora do repositório; senha não registrada.

| Verificação | Resultado | Evidência |
| --- | --- | --- |
| COUNT(*) BUEIRO | PASSOU | esperado 1; observado 1 |
| COUNT(*) DISPOSITIVO | PASSOU | esperado 1; observado 1 |
| COUNT(*) SENSOR | PASSOU | esperado 2; observado 2 |
| COUNT(*) ALERTA | PASSOU | esperado 3; observado 3 |
| Preservacao integral dos registros | PASSOU | Comparacao JSON de todos os campos e registros, ordenados por PK, antes/depois dos testes. |
| Execucao SQL completa | PASSOU | Finalizacao SQL sem erros inesperados; rejeicoes esperadas constam como testes aprovados. |
| Tres consultas JOIN originais | PASSOU | Inventario: 2 linhas; rastreabilidade: 3 linhas (leituras 2, 3 e 4); contagem do bueiro: 3 ocorrencias. |
| Teste ORA-00001 | PASSOU | Rejeicao esperada confirmada pelo script 04_verificacao.sql. |
| Teste ORA-02291 | PASSOU | Rejeicao esperada confirmada pelo script 04_verificacao.sql. |
| Teste ORA-02290 | PASSOU | Rejeicao esperada confirmada pelo script 04_verificacao.sql. |
| Modeler: tabelas | PASSOU | 4 tabelas no design nativo e no banco. |
| Modeler: colunas e tipos | PASSOU | 16 colunas: nomes, ordem, tipos, precisao/escala, VARCHAR2 CHAR, nulabilidade e identity. |
| Modeler: PK, UNIQUE e FK | PASSOU | 4 PKs, 1 UNIQUE composta e 3 FKs: nomes, colunas ordenadas, tabelas referenciadas e NO ACTION. |
| Modeler: CHECKs | PASSOU | 3 CHECKs nomeados com regras equivalentes e habilitados no banco. |
| Modeler: identity | PASSOU | ALERTA.ALERTA_ID GENERATED ALWAYS AS IDENTITY. |

Falhas observadas: 0.

As contagens totais são 1 BUEIRO, 1 DISPOSITIVO, 2 SENSOR e 3 ALERTA. Os snapshots completos antes/depois demonstram a preservação dos registros. Não foram executados os scripts de criação 01 ou inserção 02. O script 04 usa tentativas rejeitadas e rollback. Backend e Hardware não foram alterados.

## Arquivos para entregar

- [Saída real completa](oracle_validacao_final.txt): COUNT(*), JOINs, testes e metadados antes/depois.
- [Comparação detalhada](oracle_comparacao_modelo_final.json): banco versus XML nativo e hashes dos SQL testados.
- [Design nativo](../../diagramas/citizentech.dmd) junto com toda a pasta `../../diagramas/citizentech/`.
- [Captura do diagrama](data_modeler_diagrama.png) e [log de importação](data_modeler_importacao.png), capturados na etapa anterior.

## Pendências e limites

Nenhuma pendência técnica encontrada para os oito itens desta validação, se todos estiverem aprovados na tabela. Ainda cabe conferir o enunciado/rubrica oficial da FIAP e anexar os arquivos exigidos; a aprovação acadêmica não é determinada por estes testes. A conexão gráfica do Modeler ao banco e importadores Python não fazem parte desta validação. O design usa dialeto Oracle 21c; a comparação confirmou sua estrutura no servidor 26ai local. A comparação usa o modelo relacional nativo, não interpretação dos pixels da captura. O modelo lógico do design permanece vazio e só precisa ser desenvolvido se a rubrica exigir.

## Reproduzir sem recriar tabelas

Da raiz do repositório, com Docker e o container ativos:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File DataScience/oracle/validar_final.ps1
py -3 DataScience/oracle/comparar_modelo_final.py
```
