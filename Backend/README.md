# Monitoramento de bueiros — backend

API Flask e painel para acompanhar leituras de sensores. Os dados são guardados
no PostgreSQL; a tabela `leituras` é criada automaticamente na inicialização.
O banco deve estar disponível e o usuário precisa de permissão para criar a tabela.
O banco SQLite usado anteriormente não é migrado automaticamente.

## Configuração e execução

Defina `DATABASE_URL` com a URL de conexão PostgreSQL, fornecida pelo seu
provedor, por exemplo `postgresql://usuario:senha@servidor:5432/bueiros`.
Não compartilhe essa URL: ela contém credenciais. Se o provedor exigir TLS,
use os parâmetros de conexão indicados por ele, como `sslmode=verify-full` com
certificado de autoridade configurado.

Na raiz do repositório, com Python 3.10 ou superior:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r Backend\requirements.txt
$env:DATABASE_URL = 'postgresql://usuario:senha@localhost:5432/bueiros'
.\.venv\Scripts\python.exe -m Backend.app
```

Acesse o painel em `http://127.0.0.1:5000/`. Os horários são gravados em UTC
com fuso e exibidos no fuso do navegador. O painel mostra as 100 últimas leituras;
o endpoint de histórico permite paginação. A porta do servidor de desenvolvimento
é 5000 e `BUEIRO_HOST` controla sua interface de escuta.

## Docker e hospedagem

Na raiz do repositório, construa a imagem com:

```powershell
docker build -t citizentech-backend ./Backend
docker run --rm -p 5000:5000 -e DATABASE_URL citizentech-backend
```

Defina `DATABASE_URL` no ambiente antes de executar o contêiner. `localhost`
dentro do contêiner aponta para o próprio contêiner, não para o PostgreSQL no
computador; use um endereço acessível a partir dele. Na plataforma de hospedagem,
configure `Backend` como contexto de build e `DATABASE_URL` como segredo. A
variável `PORT`, se fornecida, define a porta do Gunicorn; o padrão é 5000.
O PostgreSQL precisa de armazenamento persistente e backup próprios.

## Endpoints

- `GET /`: painel de leituras.
- `GET /health`: verifica o processo, sem testar a conexão com o banco.
- `POST /api/leituras`: recebe e registra uma leitura.
- `GET /api/leituras?limite=100&offset=0`: histórico do mais recente ao mais antigo.
- `GET /api/status`: última leitura recebida.
- `GET /api/resumo`: contagens, médias e divergências entre os riscos.

Exemplo de envio JSON:

```json
{"distancia_cm": 15, "temperatura_c": 27, "umidade_relativa": 85, "risco": "ATENCAO", "tempo_ms": 5000}
```

A API recalcula o risco e registra o horário de recebimento. Sensores sem leitura
podem enviar `null`; valores inválidos são rejeitados. O risco é um indicador
heurístico, não uma previsão validada de enchentes. A API e o painel não possuem
autenticação: proteja o acesso antes de publicá-los.

## Testes

Os testes de API precisam de um PostgreSQL de teste cujo usuário possa criar e
remover schemas. Cada teste cria seu próprio schema e o remove ao terminar;
não use um banco de produção.

```powershell
$env:TEST_DATABASE_URL = 'postgresql://usuario:senha@localhost:5432/bueiros_teste'
.\.venv\Scripts\python.exe -m unittest discover -s Backend\testes -v
```

Sem `TEST_DATABASE_URL`, os testes que dependem do banco são ignorados.
