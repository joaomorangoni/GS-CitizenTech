> Registro historico: resultados com SQLite anteriores a migracao para PostgreSQL.
> Nao comprovam a integracao atual. O teste atual usa TEST_DATABASE_URL e schema
> isolado no PostgreSQL; consulte o README de DataScience para executar.

# Validação executada — 17/11/2026

## Atualização: Oracle local e Data Modeler executados

Docker Desktop iniciado com WSL 2; imagem oficial Oracle Free Lite, digest
`sha256:cf540c3fa190d7cffad08c491652ac07fc70314e510f6b87890449517d565e94`.
Servidor efetivo: Oracle AI Database 26ai Free, versão 23.26.3.0.0.
Container `citizentech-oracle` saudável, volume `citizentech-oracle-data`,
publicação somente `127.0.0.1:1521`. Teste TCP a partir do Windows retornou True.
O Docker existente tinha outro projeto; seus containers e volumes não foram
modificados por comandos de configuração do Oracle.

A imagem Lite não incluía USERS. A tentativa inicial de cadastro falhou com
ORA-00959 antes de criar o usuário; foi criado tablespace exclusivo
CITIZENTECH_DATA (20 MB iniciais, máximo 100 MB), sem recriar banco ou volume.
Usuário CITIZENTECH em FREEPDB1 com CREATE SESSION, CREATE TABLE, CREATE SEQUENCE
e quota 100 MB. Credencial aleatória protegida por DPAPI fora do repositório.

Os scripts 01, 02, 03 e 04 foram executados nessa ordem: quatro tabelas, três
índices explícitos, um bueiro, um dispositivo, dois sensores e três ocorrências.
JOIN de inventário retornou dois sensores; rastreabilidade retornou IDs de leitura
2, 3 e 4 da origem simulacao-v1; total do bueiro 1 retornou três ocorrências.
Verificação: três FKs habilitadas; PK duplicada ORA-00001, FK inválida ORA-02291
e CHECK inválido ORA-02290 rejeitados. Testes com rollback; nenhuma alteração
persistida pelos testes. Consultas e verificações foram repetidas sem recriar
tabelas, com sucesso. Saídas reais: oracle_execucao.txt e oracle_reverificacao.txt.

Data Modeler 24.3.1 com Java 17.0.13: importação gráfica do DDL, dialeto Oracle
21c, sete instruções importadas e zero falhas. Mesclagem ao modelo relacional,
quatro tabelas e três FKs; design nativo citizentech.dmd e pasta associada salvos.
Capturas reais do log e do diagrama em documentacao/evidencias. A integração Git
do aplicativo criou automaticamente um commit do design durante o salvamento;
esse commit foi desfeito, mantendo todos os arquivos e o histórico anterior.
Nenhum commit ou publicação foi mantido por esta configuração.

As pendências históricas Oracle/Data Modeler registradas abaixo estão superadas.
Continuam não executados: importação Python via python-oracledb, PyMongo, conexão
gráfica do Modeler ao banco e comunicação Wokwi/ESP32. A execução Oracle foi
realizada por SQL*Plus do container, autenticando como CITIZENTECH via listener.
Backend e Hardware permanecem sem modificações.

## Atualização: MongoDB executado com sucesso

Após a instalação autorizada do MongoDB Shell pelo winget (`MongoDB.Shell`),
mongosh 2.14.1 conectou a `mongodb://127.0.0.1:27017`, servidor 8.3.8,
com ping `{ok: 1}`. O executável ficou em
`%LOCALAPPDATA%\Programs\mongosh\mongosh.exe` e o instalador adicionou seu
diretório ao PATH do usuário. Reabra terminais existentes para carregar o PATH.
O MongoDB Server não foi reinstalado.

A inspeção prévia de `citizentech` retornou lista vazia de coleções. Foram
executados os quatro scripts em ordem. Criação, inserção e consultas passaram;
o teste inicial encontrou `assert.eq` incompatível com mongosh moderno.
`04_verificacao.js` foi adaptado para `node:assert/strict`, função assíncrona
e conferência dos códigos de erro. A execução final passou.

Resultados reais: cinco documentos integralmente iguais à fixture (desconsiderando
somente `_id` automático), dois SEM_RISCO_DETECTADO, um ATENCAO, um RISCO_ALTO,
um DADOS_INVALIDOS; três alertas/falhas e uma divergência. Médias globais:
31,25 cm, 27 °C e 70%. A consulta temporal retornou os cinco registros.
Documento incompleto rejeitado com código 121 e duplicata com 11000;
nenhum documento inválido persistiu. Reinserção: matchedCount 5, modifiedCount 0,
upsertedCount 0, deletedCount 0. Nenhum dado foi excluído.

Saídas reais salvas em `documentacao/evidencias/`: versão, auditoria com validator
e índices, consultas completas, testes e reinserção. A auditoria adicional é
somente leitura e compara o conteúdo JSON sem depender de protótipos internos
do ambiente mongosh. Não são capturas de tela. Backend e Hardware preservados.
Oracle, Data Modeler, PyMongo e comunicação Wokwi continuam pendentes.

## Registro anterior à configuração do MongoDB

As limitações MongoDB abaixo descrevem o estado anterior e foram superadas pela
execução registrada acima; permanecem válidas as pendências de Oracle e hardware.

Ambiente: Windows, Python 3.14.7, Flask 3.1.3. Execução a partir da raiz
do repositório, usando o Python instalado em
`$env:LOCALAPPDATA/Python/pythoncore-3.14-64/python.exe`.

| Verificação efetivamente executada | Resultado |
| --- | --- |
| `python -m unittest discover -s Backend/testes -v` | 10 testes aprovados |
| `python -m unittest discover -s DataScience/testes -v` | 4 testes aprovados |
| `node --check` em cada um dos quatro arquivos mongodb/*.js | Sem erros de sintaxe |
| CLI `python -m DataScience.integracao` contra servidor Flask HTTP local temporário | Exportou 1 leitura para JSON temporário, preservou temperatura null e RISCO_ALTO |
| `git diff -- Backend Hardware` | Sem alterações |
| `git diff --check` | Sem erros |

O teste HTTP adicional iniciou servidor Werkzeug em porta local dinâmica,
com SQLite em TemporaryDirectory, enviou uma leitura usando o cliente Flask,
executou o coletor em subprocesso contra o servidor HTTP, abriu o JSON gerado e
verificou quantidade, null e risco. Servidor e arquivos temporários foram
encerrados/removidos ao fim. Não acessou nem alterou a base operacional.

Os quatro testes versionados validam a fixture contra processamento/validação
reais, exportação via cliente Flask com SQLite temporário, paginação acima de
1000 leituras e exigência de vínculo explícito. A suíte existente exercita as
fronteiras das regras e erros da API. Seu teste de indisponibilidade SQLite
gera intencionalmente traceback no log, mas passou ao verificar 503 e recuperação.

## Não executado

- Oracle: conexão, criação das tabelas, inserções, JOINs, constraints e MERGE.
  Não havia Oracle configurado nem `sqlplus` disponível no PATH.
- MongoDB: criação/validação da coleção, índices, upserts, agregações,
  PyMongo e `04_verificacao.js`. Não havia MongoDB configurado nem `mongosh`
  ou `mongod` disponível no PATH. Não foi instalado nem iniciado banco externo.
- Data Modeler: importação gráfica, geração de design nativo e exportação de imagem.
- Comunicação Wokwi/ESP32 e importação de dados físicos.

Verificação de sintaxe em Node não verifica as APIs do mongosh nem o validator
no servidor. Os SQL foram revisados como artefatos Oracle; SQLite não foi usado
como substituto para alegar validação Oracle. As contagens descritas no README
para bancos externos são expectativas da fixture, não resultados observados.

Não foram criadas capturas de tela nem logs fictícios de bancos externos.
Execute o roteiro do README para obter essas evidências após configurar os bancos.
O README da raiz já tinha alteração antes deste trabalho e foi preservado;
todos os arquivos adicionados nesta entrega ficam em DataScience.
