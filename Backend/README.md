# Monitoramento de bueiros — backend Python

Solução acadêmica CitizenTech da Global Solution 2026.2 FIAP. Recebe medições de
um ESP32, recalcula indicadores de risco e mantém um histórico consultável.
Tecnologias: Python 3.10 ou superior, Flask, SQLite e unittest (biblioteca padrão).
Não requer Machine Learning nem ESP32 conectado para demonstrar o processamento.

## Estrutura e responsabilidades

| Arquivo | Responsabilidade |
| --- | --- |
| `app.py` | Fábrica da aplicação, endpoints e respostas HTTP |
| `config.py` | Constantes dos limites de classificação e validação |
| `validacoes.py` | Validação de tipos, campos e faixas |
| `monitoramento.py` | Análise de distância e ambiente, risco e comparação |
| `alertas.py` | Mensagens por classificação |
| `armazenamento.py` | Criação, gravação e consultas SQLite |
| `testes/test_backend.py` | Casos simulados de processamento e API |
| `requirements.txt` | Dependência Flask |
| `dados/leituras.sqlite3` | Banco local, criado automaticamente e ignorado pelo Git |

## Instalação no Windows / VS Code / PowerShell

Instale Python 3.10+ com o inicializador `py`. No VS Code abra a raiz
`GS-CitizenTech` e um terminal PowerShell. Execute todos os comandos desta página
a partir dessa raiz:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r Backend\requirements.txt
.\.venv\Scripts\python.exe -m Backend.app
```

Não é necessário ativar o ambiente ou alterar a política de execução do PowerShell.
O servidor estará em `http://127.0.0.1:5000`, sem debug. Encerre com `Ctrl+C`.
Se `py` não existir, use o caminho completo de uma instalação real de `python.exe`.
Neste computador, os atalhos `py`/`python` falharam, mas esta instalação funcionou:

```powershell
& "$env:LOCALAPPDATA\Python\pythoncore-3.14-64\python.exe" -m venv .venv
```

Depois continue com os comandos `.\.venv\Scripts\python.exe` acima.
O banco persiste entre reinicializações. Para mudar seu caminho, configure
`$env:BUEIRO_DATABASE = 'C:\caminho\leituras.sqlite3'` antes de iniciar.

## Endpoints

| Método e caminho | Resultado |
| --- | --- |
| `GET /health` | `200`, processo ativo, `{"status":"ok"}` |
| `POST /api/leituras` | `201`, leitura armazenada com análise e alerta |
| `GET /api/leituras?limite=100&offset=0` | `200`, lista `leituras`, mais recentes primeiro |
| `GET /api/status` | `200`, `ultima_leitura` e mensagem sobre sua atualidade |
| `GET /api/resumo` | `200`, totais por risco, médias e divergências |

O histórico aceita limite de 1 a 1000 e offset não negativo. Antes de qualquer
envio, histórico é vazio, status tem `ultima_leitura: null`, totais são zero e
médias são null. As médias ignoram valores null de cada sensor.
O estado representa a última leitura recebida, sem garantir que o dispositivo
continua conectado: confira `recebido_em`. `/health` verifica o processo; as
operações de banco reportam indisponibilidade separadamente.

## Contrato de entrada e validação

```json
{
  "distancia_cm": 15.0,
  "temperatura_c": 27.0,
  "umidade_relativa": 85.0,
  "risco": "ATENCAO",
  "tempo_ms": 5000
}
```

Todos os cinco campos são obrigatórios. Distância é não negativa, umidade vai
de 0 a 100 e temperatura de -40 a 80 °C (faixa operacional do DHT22).
Números devem ser finitos; strings numéricas e booleanos são rejeitados.
`tempo_ms` é um inteiro de 0 a 4294967295: uptime `millis()` do ESP32, que pode
reiniciar ou dar a volta. Nunca é convertido em data nem usado para ordenar registros.
O servidor atribui ID e data/hora UTC com fuso em `recebido_em`.
Campos adicionais são ignorados, não sobrescrevem os campos calculados.

Um sensor com falha deve enviar `null`, como já faz o firmware. A leitura é
armazenada com `201`, e `sensores_sem_leitura` identifica o problema. Distância
ou umidade null resultam em `DADOS_INVALIDOS`. Temperatura null é sinalizada,
mas preserva o risco calculado com distância e umidade, igual ao firmware.
Valores impossíveis, campos ausentes, risco desconhecido ou JSON malformado
retornam `400` e não são gravados. Conteúdo sem tipo JSON retorna `415`;
corpo maior que 16 KiB retorna `413`. Falhas SQLite retornam `503`, sem expor
detalhes internos ao cliente.

Exemplo de erro: `{"erro":"Dados recebidos inválidos.","campos":{"distancia_cm":"Informe um número ou null."}}`.

## Envio e consulta pelo PowerShell

Em outro terminal, com o servidor em execução:

```powershell
$dados = @{
  distancia_cm = 15.0
  temperatura_c = 27.0
  umidade_relativa = 85.0
  risco = 'ATENCAO'
  tempo_ms = 5000
}
$json = $dados | ConvertTo-Json
Invoke-RestMethod -Uri 'http://127.0.0.1:5000/api/leituras' -Method Post -ContentType 'application/json' -Body $json | ConvertTo-Json -Depth 5
Invoke-RestMethod 'http://127.0.0.1:5000/api/status' | ConvertTo-Json -Depth 5
Invoke-RestMethod 'http://127.0.0.1:5000/api/resumo' | ConvertTo-Json -Depth 5
Invoke-RestMethod 'http://127.0.0.1:5000/api/leituras?limite=10' | ConvertTo-Json -Depth 5
```

Também é possível abrir os endpoints GET no navegador. No Postman selecione
POST, URL `/api/leituras`, Body → raw → JSON e cole o exemplo.

Trecho esperado da resposta ao primeiro envio (ID e horário variam):

```json
{
  "id": 1,
  "distancia_cm": 15.0,
  "risco_esp32": "ATENCAO",
  "risco_python": "ATENCAO",
  "risco_divergente": false,
  "sensores_sem_leitura": [],
  "analise_distancia": "CURTA",
  "alerta": "Atenção: distância curta ou umidade elevada. Verifique as condições do bueiro."
}
```

A resposta completa também contém temperatura, umidade, uptime, ambiente e
`recebido_em`. O resumo após esse único envio terá `total_leituras: 1`,
`por_risco.ATENCAO: 1` e os demais riscos com zero.

## Regras e limites da interpretação

O servidor usa as mesmas regras verificadas em `Hardware/src/sistema_bueiro.ino`:

1. Distância ou umidade sem leitura: `DADOS_INVALIDOS`.
2. Distância ≤ 10 cm **e** umidade ≥ 80%: `RISCO_ALTO`.
3. Distância ≤ 30 cm **ou** umidade ≥ 80%: `ATENCAO`.
4. Demais casos: `SEM_RISCO_DETECTADO`.

Os limites ficam em `config.py`; mudanças exigem sincronizar o firmware para
evitar divergências esperadas. A comparação usa `risco_divergente`, e a contagem
fica em `riscos_divergentes`. Estatísticas usam a classificação Python.

Distância significa distância até o fundo/obstáculo; não foi confirmado que
o eco vem da superfície da água. Não calculamos percentual de enchimento.
Isso exigiria confirmar posição, direção e superfície medida e calibrar a
altura de referência. Umidade relativa é do ar, não mede água acumulada.
Temperatura é contextual e não participa da regra. São indicadores heurísticos,
sem validação como previsão de enchentes. Contagens são de leituras, não de
eventos distintos: um alerta persistente gera várias ocorrências a cada 5 segundos.
O protótipo representa um único bueiro; o payload atual não identifica dispositivos.

## Integração com ESP32 e Wokwi

O hardware foi preservado. `enviarParaServidor()` já envia JSON com o cabeçalho
correto aproximadamente a cada 5 segundos. `API_URL` está vazia; preencha-a
somente quando escolher um endereço acessível ao dispositivo.

### Wokwi com gateway privado

A documentação oficial descreve instalar e executar o Wokwi IoT Gateway local,
ativá-lo no editor web com F1 → **Enable Private Wokwi IoT Gateway** e confirmar
`Client connected` no gateway. Esse recurso exige plano compatível.
Com o gateway privado ativo, configure:

```cpp
const char* API_URL = "http://host.wokwi.internal:5000/api/leituras";
```

Execute o backend no mesmo computador. O hostname especial dá acesso ao host;
`localhost` dentro do ESP32 não representa seu computador.

### Wokwi com gateway público

O gateway público padrão acessa a internet, mas não sua rede local. Use um
backend publicado em endereço público ou um túnel para a porta local 5000.
O endereço completo deverá terminar em `/api/leituras`.
O firmware atual usa `HTTPClient.begin(API_URL)` sem configuração explícita de
cliente TLS/certificado; não presuma que trocar a URL para HTTPS será suficiente.
Para manter o firmware intacto, use o gateway privado com HTTP local acima.
Uma demonstração via endereço HTTP público/túnel que aceite HTTP sem redirecionar
para HTTPS deve usar apenas dados sintéticos. Para HTTPS, será necessário adaptar
o transporte do firmware com cliente seguro e validação do certificado do servidor.
Essa adaptação não foi aplicada por não ser necessária à execução local.

Fonte: [Rede Wi-Fi e gateways ESP32 — documentação Wokwi](https://docs.wokwi.com/guides/esp32-wifi).
O gateway público monitora tráfego; não envie dados sensíveis.

Para ESP32 físico na mesma rede, configure o Wi-Fi apropriado e
`http://IP-DO-PC:5000/api/leituras`. Antes de iniciar o backend, defina
`$env:BUEIRO_HOST = '0.0.0.0'`, identifique o IPv4 com `ipconfig` e permita
a porta 5000 somente na rede privada necessária no firewall.

O servidor Flask incluído é de desenvolvimento, sem autenticação. Não o exponha
permanentemente à internet. Em uma publicação real, use servidor apropriado,
TLS, autenticação e restrições de acesso. Encerre túneis após a demonstração,
não grave credenciais no repositório e não desative a validação de certificados.

## Testes e demonstração ao professor

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s Backend\testes -v
```

Os testes usam banco temporário por caso e dados simulados: não alteram o banco
da aplicação e não exigem hardware. Verificam riscos e fronteiras, dados inválidos,
falhas de sensores, contrato JSON, persistência após recriar a aplicação, histórico,
paginação, status, resumo, divergências, alertas e indisponibilidade SQLite.

Validação realizada nesta entrega: 10 testes aprovados com Python 3.14.7 e Flask
disponível no ambiente. O teste de falha SQLite gera intencionalmente um log de
erro e verifica a resposta 503 e a recuperação no próximo envio. A comunicação
real ESP32/Wokwi não foi executada; depende de servidor acessível e configuração
de `API_URL` descrita acima.

Roteiro de apresentação:

1. Execute os testes e mostre o resultado.
2. Inicie o servidor e abra `/health`.
3. Use o exemplo PowerShell mudando distância/umidade/risco: `50/50/SEM_RISCO_DETECTADO`,
   `15/85/ATENCAO` e `10/85/RISCO_ALTO`.
4. Envie distância `$null` e risco `DADOS_INVALIDOS`: mostre o registro da falha.
5. Envie distância `-1`: mostre o erro 400 e que o total não aumentou.
6. Abra `/api/status`, `/api/resumo` e `/api/leituras` no navegador.
7. Opcionalmente conecte o Wokwi, ajuste os sensores e mostre `HTTP: 201` no serial.

## Atendimento a Computational Thinking with Python

| Requisito | Evidência |
| --- | --- |
| Aplicação funcional Python | API Flask executável com cinco endpoints |
| Listas e dicionários | Histórico, sensores com falha, JSON e contagens por risco |
| Funções | Validação, classificação, análise ambiental, alertas e persistência |
| Modularização | Responsabilidades divididas nos arquivos da tabela inicial |
| Receber e processar hardware | POST compatível com o JSON e os nulls do ESP32 |
| Resultados úteis | Última leitura, alerta, divergência, estatísticas e histórico |
| Casos de teste | Suíte unittest reproduzível sem ESP32 |
