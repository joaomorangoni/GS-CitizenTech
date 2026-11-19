# Evidências reais — MongoDB, Oracle e Data Modeler

Validação final Oracle: [relatório de aprovação](oracle_relatorio_final.md),
[saída real completa](oracle_validacao_final.txt) e
[comparação do design com o banco](oracle_comparacao_modelo_final.json).
Foram aprovadas 15 verificações, incluindo contagens totais, JOINs, restrições,
preservação integral dos registros e correspondência do design nativo.

Execução em 17/11/2026. Shell 2.14.1 e servidor 8.3.8.

Oracle 26ai Free 23.26.3.0.0 local configurado e validado. Salve para a FIAP:

- `oracle_execucao.txt`: criação, dados, JOINs e testes de PK/FK/CHECK aprovados.
- `oracle_reverificacao.txt`: consultas e testes repetidos sem recriar tabelas.
- `data_modeler_importacao.png`: captura real de sete instruções importadas, zero falhas.
- `data_modeler_diagrama.png`: captura real das quatro tabelas e três relacionamentos.
- `../../diagramas/citizentech.dmd` e toda a pasta `citizentech/`: design nativo.

Para reproduzir Oracle, siga `../oracle_local.md`; para reabrir o design,
siga `../data_modeler.md`. Os bancos Oracle/MongoDB continuam separados do SQLite.

| Arquivo | Conteúdo observado |
| --- | --- |
| mongosh_versao.txt | Saída de --version |
| mongodb_auditoria.txt | Ping, servidor, validator, índices, contagens, comparação da fixture e médias |
| mongodb_consultas.txt | Saída completa de 03_consultas.js |
| mongodb_validacao.txt | Rejeições 121 e 11000 e confirmação final |
| mongodb_reinsercao.txt | Cinco correspondências, zero alterações/inserções/exclusões |
| auditoria_mongodb.js | Script de auditoria somente leitura reproduzível |

Para a FIAP, salve capturas legíveis do terminal mostrando:

1. `mongosh --version` e ping local com `ok: 1`.
2. Os cinco documentos da origem `simulacao-v1`, IDs 1 a 5; mostre também os nulls.
3. As consultas de alertas e estatísticas por risco (saída de 03_consultas.js).
4. Os códigos de rejeição 121 e 11000 e a confirmação de aprovação do teste 04.
5. Índice único origem_api + leitura.id, validator strict/error e reinserção sem duplicatas.

Comandos PowerShell da raiz, em terminal novo:

```powershell
mongosh --version
mongosh 'mongodb://127.0.0.1:27017' --quiet --file DataScience/documentacao/evidencias/auditoria_mongodb.js
mongosh 'mongodb://127.0.0.1:27017' --quiet --file DataScience/mongodb/03_consultas.js
mongosh 'mongodb://127.0.0.1:27017' --quiet --file DataScience/mongodb/04_verificacao.js
```

Não reexecute 01_colecoes.js: a coleção já existe, e o script recusará recriá-la.
02_insercao.js pode ser repetido para a amostra e foi verificado como idempotente.
Os TXT foram gerados diretamente dos comandos. As evidências MongoDB são textuais;
as duas capturas de tela existentes são do Data Modeler.
As evidências Oracle e Data Modeler listadas acima também foram executadas e salvas.
