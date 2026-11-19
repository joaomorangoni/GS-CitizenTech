# Oracle local isolado no Docker — Windows 11

Usamos a imagem oficial `container-registry.oracle.com/database/free:latest-lite`.
O Docker Desktop existente usa WSL 2. Nenhum Oracle foi instalado como serviço
Windows; MongoDB, Backend e Hardware permanecem independentes.

## Recursos do projeto

| Recurso | Valor |
| --- | --- |
| Container | citizentech-oracle |
| Volume persistente | citizentech-oracle-data |
| Host | 127.0.0.1 |
| Porta | 1521 (publicada somente no loopback) |
| Tipo de conexão | Basic / Service name |
| Service name | FREEPDB1 |
| Usuário de aplicação | CITIZENTECH |
| Tablespace / quota | CITIZENTECH_DATA / 100 MB |
| Privilégios concedidos | CREATE SESSION, CREATE TABLE, CREATE SEQUENCE |
| Limite de memória do container | 3 GB |

As senhas são aleatórias. A credencial da aplicação está criptografada com DPAPI
em `%LOCALAPPDATA%\GS-CitizenTech\oracle-local.clixml`, fora do repositório.
Somente a mesma conta Windows consegue descriptografá-la normalmente. Não publique
o arquivo, a senha ou saídas de `docker inspect` que incluam variáveis de ambiente.
A senha administrativa de inicialização não foi gravada em arquivos do projeto.
A administração local usa autenticação do usuário `oracle` dentro do container.

## Reabrir e executar

Inicie Docker Desktop. Da raiz do repositório:

```powershell
docker start citizentech-oracle
docker inspect --format '{{.State.Health.Status}}' citizentech-oracle
powershell -NoProfile -ExecutionPolicy Bypass -File DataScience/oracle/executar_local.ps1
```

Aguarde `healthy` antes de executar SQL. O executor consulta e testa a amostra;
o teste de restrições usa rollback. A saída vai para
`DataScience/documentacao/evidencias/oracle_reverificacao.txt`.
O uso de `-ExecutionPolicy Bypass` vale somente para esse processo, não modifica
a política persistente do Windows nem exige executar como administrador.

Na primeira configuração de um computador sem esses recursos:

```powershell
docker pull container-registry.oracle.com/database/free:latest-lite
powershell -NoProfile -ExecutionPolicy Bypass -File DataScience/oracle/configurar_local.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File DataScience/oracle/executar_local.ps1 -Criar
```

Não repita a configuração neste computador após a instalação: o script recusa
substituir container, volume ou credencial existente. `-Criar` recusa executar
DDL se já existirem objetos do projeto. Não use em schemas compartilhados.
Se houver falha parcial, diagnostique os objetos antes de tentar criar novamente.

## Conexão no Data Modeler / SQL Developer

Crie conexão Basic com os parâmetros da tabela acima. Não use SID `FREEPDB1`;
selecione **Service name**. Para copiar a senha local para a área de transferência
sem imprimi-la no terminal, execute em PowerShell sob sua conta Windows:

```powershell
$credencialLocal = Import-Clixml "$env:LOCALAPPDATA\GS-CitizenTech\oracle-local.clixml"
$credencialLocal.GetNetworkCredential().Password | Set-Clipboard
```

Cole no campo de senha do aplicativo. Não mostre esse campo nas evidências;
limpe a área de transferência após usar: `Set-Clipboard -Value ''`.
O Data Modeler importa o DDL sem conexão: veja `data_modeler.md`.

## Evidências e operação

Salve o resultado da execução SQL, as três consultas JOIN e as mensagens de
rejeição ORA-00001, ORA-02291 e ORA-02290. Salve também o design `.dmd` com sua
pasta associada e uma imagem legível do modelo relacional no Data Modeler.
Não trate a disponibilidade do processo gráfico como prova de importação.

Ao terminar a demonstração, libere memória sem excluir o banco:

```powershell
docker stop citizentech-oracle
```

O volume preserva as tabelas e dados entre paradas. Não execute `docker rm`,
`docker volume rm` ou comandos de limpeza para repetir a apresentação.
O download inicial depende da rede; a configuração precisa do banco `healthy`.

Fontes: [Oracle — execução local oficial](https://docs.oracle.com/en/database/oracle/agent-memory/26.6/guide/run-locally.html)
e [Docker — backend WSL 2](https://docs.docker.com/desktop/features/wsl/).
