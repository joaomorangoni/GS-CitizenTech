# CitizenTech — Cognitive Data Science, GS 2026.2

Entrega independente em `DataScience/`. Backend Flask, PostgreSQL e Hardware
preservados. Os modelos Oracle/MongoDB são destinos acadêmicos opcionais;
nenhum substitui a persistência atual. Dados de demonstração são fictícios.

Estado local validado em 17/11/2026: MongoDB com cinco documentos e testes
aprovados; Oracle em Docker com quatro tabelas, dados e testes aprovados;
Data Modeler com design nativo e capturas reais salvos. Para continuar usando
o banco Oracle já configurado, siga [oracle_local.md](documentacao/oracle_local.md).
Não reexecute criação/inserção Oracle sobre as mesmas tabelas.

## Arquivos

| Caminho relativo a DataScience | Finalidade |
| --- | --- |
| oracle/01_criacao.sql | Quatro tabelas Oracle, PK/FK, CHECKs, unicidade e índices |
| oracle/02_dados_simulados.sql | Um bueiro, ESP32, dois sensores e três ocorrências |
| oracle/03_consultas.sql | Inventário, rastreabilidade e totais com JOIN |
| oracle/04_verificacao.sql | Conferência de cadastros, FKs e rejeições de PK/FK/CHECK com rollback; validado no Oracle local |
| oracle/configurar_local.ps1 | Instalação inicial isolada em Docker, sem substituir recursos existentes |
| oracle/criar_usuario_local.ps1 | Tablespace e usuário exclusivos; credencial DPAPI fora do repositório |
| oracle/executar_local.ps1 | Execução inicial com -Criar, consultas e reverificação sem -Criar |
| oracle/validar_final.ps1 | Validação final sem DDL: contagens, JOINs, testes e snapshots reais |
| oracle/05_snapshot_validacao.sql | Exportação somente leitura dos registros e metadados para conferência |
| oracle/comparar_modelo_final.py | Comparação do design nativo com o banco e geração do relatório final |
| mongodb/01_colecoes.js | Coleção leituras com validator e índices |
| mongodb/02_insercao.js | Inserção idempotente com upsert |
| mongodb/leituras_simuladas.json | Cinco respostas completas em envelope de origem/dispositivo |
| mongodb/03_consultas.js | Histórico, alertas, estatísticas e intervalo UTC |
| mongodb/04_verificacao.js | Verificação opcional contra servidor real |
| diagramas/modelo_er.mmd | Diagrama ER Mermaid |
| diagramas/citizentech.dmd e citizentech/ | Design nativo gerado pelo Oracle Data Modeler |
| documentacao/evidencias/ | Saídas reais MongoDB/Oracle e capturas do Data Modeler |
| documentacao/modelagem.md | Contrato, dicionário, decisões e separação dos bancos |
| documentacao/data_modeler.md | Importação do DDL e reprodução visual |
| documentacao/integracao_oracle.md | Exemplo Python com MERGE parametrizado |
| documentacao/validacao.md | Resultados efetivamente executados e pendências |
| integracao.py | Coleta GET paginada para JSON/MongoDB |
| testes/test_datascience.py | Testes de contrato e integração opcional com PostgreSQL |
| requirements.txt | Dependência opcional PyMongo |
| __init__.py, testes/__init__.py | Pacotes Python |

## Instalação Python e testes (PowerShell)

Execute da raiz do repositório completo `GS-CitizenTech`, com Python 3.10+ instalado.
Os testes de contrato e a API precisam do código existente em `Backend/`.
O ZIP desta disciplina contém somente DataScience; Oracle, MongoDB e a modelagem
podem ser reproduzidos separadamente. Para testar a integração Python, use o
repositório completo e os comandos abaixo:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r Backend\requirements.txt
.\.venv\Scripts\python.exe -m unittest discover -s DataScience\testes -v
```

Se `py` não funcionar, use o caminho de uma instalação real. Neste ambiente:

```powershell
& "$env:LOCALAPPDATA\Python\pythoncore-3.14-64\python.exe" -m venv .venv
```

Não é preciso ativar o venv. Três testes de contrato/coleta não exigem banco.
O teste da API usa PostgreSQL e só executa com `TEST_DATABASE_URL` definida;
sem essa variável, aparece como ignorado (skipped). PyMongo e Oracle não são
necessários para esses testes.

Para executar também a integração, use um banco PostgreSQL de testes acessível
e um usuário com permissão para criar schemas:

```powershell
$env:TEST_DATABASE_URL = 'postgresql://usuario:senha@localhost:5432/citizentech_testes'
.\.venv\Scripts\python.exe -m unittest discover -s DataScience\testes -v
```

O teste cria um schema exclusivo, configura `search_path` somente para ele e
remove esse schema ao terminar, inclusive se uma asserção falhar. Não utiliza
`DATABASE_URL` da aplicação. Se a conexão de testes estiver inválida, o teste
falha em vez de ser ignorado.

## Executar API e exportar

Terminal 1, na raiz, com PostgreSQL disponível e o banco já criado:

```powershell
$env:DATABASE_URL = 'postgresql://usuario:senha@localhost:5432/citizentech'
.\.venv\Scripts\python.exe -m Backend.app
```

Terminal 2, na raiz, com API na porta 5000:

```powershell
Invoke-RestMethod 'http://127.0.0.1:5000/health'
$dados = @{distancia_cm=10; temperatura_c=27; umidade_relativa=85; risco='RISCO_ALTO'; tempo_ms=5000}
Invoke-RestMethod 'http://127.0.0.1:5000/api/leituras' -Method Post -ContentType 'application/json' -Body ($dados | ConvertTo-Json) | ConvertTo-Json -Depth 8
Invoke-RestMethod 'http://127.0.0.1:5000/api/status' | ConvertTo-Json -Depth 8
Invoke-RestMethod 'http://127.0.0.1:5000/api/resumo' | ConvertTo-Json -Depth 8
.\.venv\Scripts\python.exe -m DataScience.integracao --origem postgres-demo-01 --dispositivo-id 1 --saida DataScience/exportacao.local.json
```

O POST é uma demonstração opcional e grava uma leitura na API atual; a exportação
usa somente GET. Pause envios do Wokwi/outros clientes durante a coleta completa.
Cadastre dispositivo 1 no Oracle antes de associar seus dados. O payload atual
não identifica dispositivo: só associe uma origem que represente o dispositivo
escolhido. Troque `--origem` se recriar a base PostgreSQL. A exportação também funciona
com API vazia e produz `[]`. Encerre o servidor com Ctrl+C.

## Oracle

Pré-requisitos: instância Oracle 19c+ acessível, schema acadêmico vazio, quota de
tablespace e permissão CREATE TABLE; SQL Developer para execução e Data Modeler
para diagrama. Pode usar Oracle Database Free local ou o Oracle fornecido pela
FIAP. Instale o cliente pelas distribuições oficiais e configure conexão com
host, porta e service name fornecidos pela instituição/instalação. Não presumimos
serviço, usuário ou senha da FIAP. DDL Oracle faz commits implícitos.

No SQL Developer, abra conexão ao schema de demonstração. Abra e execute com
**Run Script (F5)** cada arquivo, nesta ordem:

1. `DataScience/oracle/01_criacao.sql`
2. `DataScience/oracle/02_dados_simulados.sql`
3. `DataScience/oracle/03_consultas.sql`
4. `DataScience/oracle/04_verificacao.sql`

Execute criação e amostras uma vez por schema vazio; os scripts não apagam tabelas
existentes e não são migrações idempotentes. Salve os resultados: inventário deve
ter duas linhas; rastreabilidade, três; total do bueiro 1, três ocorrências.
Esses valores foram confirmados no Oracle local; os resultados reais estão em
`documentacao/evidencias/oracle_validacao_final.txt` e no relatório final ao lado.
Confira PK/FK/UNIQUE/CHECK no navegador do schema. Em transação de teste, tente
inserir SENSOR com dispositivo inexistente e confirme rejeição por FK; tente
repetir uma chave e confirme rejeição. Não publique credenciais nas evidências.

Para reproduzir diagrama e salvar design, siga [Data Modeler](documentacao/data_modeler.md).
O [exemplo Oracle](documentacao/integracao_oracle.md) importa ocorrências da
exportação com binds; não existe escrita automática Oracle no Backend.

## MongoDB

Instale MongoDB Community Server e MongoDB Shell (`mongosh`) pelos instaladores
oficiais. No Windows, escolha execução como serviço local no instalador do servidor
e confirme que o serviço MongoDB está iniciado. Adicione `mongosh` ao PATH ou use
seu caminho completo. Alvo dos scripts: MongoDB 7+ e mongosh 2+.
Alternativamente use um cluster Atlas e as permissões de conexão correspondentes.
As instruções abaixo assumem servidor local em `127.0.0.1:27017` sem autenticação,
acessível apenas localmente. Não exigem configurar um servidor aberto na rede.

Na raiz do repositório, execute:

```powershell
mongosh 'mongodb://127.0.0.1:27017' --file DataScience/mongodb/01_colecoes.js
mongosh 'mongodb://127.0.0.1:27017' --file DataScience/mongodb/02_insercao.js
mongosh 'mongodb://127.0.0.1:27017' --file DataScience/mongodb/03_consultas.js
mongosh 'mongodb://127.0.0.1:27017' --file DataScience/mongodb/04_verificacao.js
```

Criação exige coleção ainda inexistente. Se ela já existir, o script para sem
alterá-la: revise validator e índices em vez de apagar dados. Inserção pode ser
repetida e mantém cinco documentos de origem `simulacao-v1`. Esperados: dois sem
risco, um ATENCAO, um RISCO_ALTO, um DADOS_INVALIDOS; três alertas/falhas, uma
divergência; distância média global 31,25 cm, temperatura 27 °C e umidade 70%.
Consultas retornam médias por risco; null é excluído da média de cada grandeza.
`04_verificacao.js` confere contagens, unicidade e rejeição de documento incompleto.

Para importar o histórico real da API, após criar a coleção:

```powershell
.\.venv\Scripts\python.exe -m pip install -r DataScience\requirements.txt
$env:MONGODB_URI = 'mongodb://127.0.0.1:27017'
.\.venv\Scripts\python.exe -m DataScience.integracao --origem postgres-demo-01 --dispositivo-id 1 --mongo
Remove-Item Env:MONGODB_URI
```

Com autenticação, forneça URI pelo mecanismo de segredos da sua máquina; não
grave senha em arquivos ou no histórico do terminal. A importação usa upsert por
origem + id e pode ser repetida. As consultas fornecidas filtram `simulacao-v1`;
troque o valor da variável `origem` para consultar seus dados importados.

Fontes oficiais: [MongoDB Community](https://www.mongodb.com/docs/manual/installation/),
[mongosh](https://www.mongodb.com/docs/mongodb-shell/install/),
[Oracle Database Free](https://www.oracle.com/database/free/),
[SQL Developer](https://www.oracle.com/database/sqldeveloper/) e
[Data Modeler](https://www.oracle.com/database/sqldeveloper/technologies/sql-data-modeler/).

## Evidências disponíveis e complementos opcionais

Já estão salvos em `documentacao/evidencias/`: saídas reais Oracle e MongoDB,
relatório final Oracle, comparação do modelo com o banco e duas capturas reais
do Data Modeler. A entrega consolidada está descrita em
[checklist_entrega.md](documentacao/checklist_entrega.md).
O roteiro abaixo permite reproduzir ou complementar a demonstração. Capturas
de terminal e vídeo só precisam ser acrescentados se exigidos pela rubrica.

1. Terminal com as duas suítes e resultado completo, incluindo data e versões.
2. API: health, resposta POST e resumo; exportação JSON com campos e null visíveis.
3. Data Modeler: quatro tabelas, atributos, PKs, FKs e cardinalidades; salve o design.
4. Oracle: execução sem erro dos três SQL, resultados JOIN e validação das constraints.
5. MongoDB: validator/índices, cinco documentos, consultas e saída da verificação real.
6. Reexecute inserção MongoDB e confirme cinco documentos; repita importação de API
   e confira ausência de duplicatas por origem/id. Compare contagens filtradas pela
   mesma origem; a API pode conter mais dados que a amostra.

Não há capturas inventadas. Pendências e execução local estão em
[validacao.md](documentacao/validacao.md). Limitações e justificativa da arquitetura
estão em [modelagem.md](documentacao/modelagem.md).
