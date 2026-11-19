# Decisões e contrato inspecionado

Foram lidos `Backend/app.py`, `armazenamento.py`, `config.py`, `monitoramento.py`,
`validacoes.py`, `alertas.py` e `testes/test_backend.py`. Nenhum foi modificado.

O POST recebe `distancia_cm`, `temperatura_c`, `umidade_relativa`, `risco` e
`tempo_ms`; todos são obrigatórios, mas as três medições aceitam null.
O GET devolve `risco_esp32` no lugar do nome de entrada `risco`, além das análises.
Campos extras do POST são descartados. Não enviar um documento MongoDB ao POST.

| Campo na resposta | Tipo e significado |
| --- | --- |
| id | Inteiro positivo atribuído pelo PostgreSQL, único somente naquela base |
| distancia_cm | Número >= 0 ou null; distância ao alvo do ultrassom |
| temperatura_c | Número de -40 a 80 ou null |
| umidade_relativa | Número de 0 a 100 ou null; umidade do ar |
| risco_esp32 / risco_python | SEM_RISCO_DETECTADO, ATENCAO, RISCO_ALTO ou DADOS_INVALIDOS |
| tempo_ms | Inteiro de 0 a 4294967295; uptime com reinício/overflow, não timestamp |
| recebido_em | String ISO 8601 UTC atribuída pelo servidor |
| analise_distancia | SEM_LEITURA, CRITICA (<=10), CURTA (<=30) ou ACIMA_DO_LIMITE_DE_ATENCAO |
| ambiente | Objeto com temperatura_disponivel booleano e umidade_elevada booleano ou null |
| alerta | Mensagem em todos os riscos, inclusive SEM_RISCO_DETECTADO |
| risco_divergente | Booleano: risco_esp32 diferente de risco_python |
| sensores_sem_leitura | Lista dos nomes das medições null, não IDs de sensores físicos |

Distância ou umidade null gera DADOS_INVALIDOS. Caso contrário, distância <=10
e umidade >=80 gera RISCO_ALTO; distância <=30 ou umidade >=80 gera ATENCAO;
os demais casos geram SEM_RISCO_DETECTADO. Temperatura não determina risco.
Os indicadores são heurísticos: não representam previsão validada, altura de água
ou percentual de enchimento. Estatísticas contam leituras, não enchentes distintas.

## Oracle: cadastros e ocorrências selecionadas

PKs numéricas identificam cadastros locais. Todo dispositivo pertence a exatamente
um bueiro; todo sensor e alerta pertencem a um dispositivo. Cada pai aceita zero
ou vários filhos. Não há exclusão em cascata: preserva-se a rastreabilidade.
As relações no Mermaid são não identificadoras (linhas tracejadas), pois cada
entidade filha tem PK própria e suas FKs não integram essa PK. A cardinalidade
continua sendo exatamente um pai para zero ou muitos filhos.
Os índices de FK ajudam as consultas JOIN. O cadastro admite mais dispositivos
futuramente, mas a API atual não distingue suas origens.

| Tabela | Dados obrigatórios | Dados opcionais |
| --- | --- | --- |
| BUEIRO | bueiro_id NUMBER(10), PK manual | descricao VARCHAR2(200 CHAR), localizacao VARCHAR2(300 CHAR) |
| DISPOSITIVO | dispositivo_id NUMBER(10), PK manual; bueiro_id NUMBER(10), FK | descricao VARCHAR2(200 CHAR) |
| SENSOR | sensor_id NUMBER(10), PK manual; dispositivo_id NUMBER(10), FK; modelo VARCHAR2(30 CHAR) | Nenhum |
| ALERTA | alerta_id NUMBER identity; dispositivo_id NUMBER(10), FK; origem_api VARCHAR2(100 CHAR); leitura_api_id NUMBER(19); recebido_em TIMESTAMP(6) WITH TIME ZONE; risco_python VARCHAR2(20 CHAR); mensagem VARCHAR2(500 CHAR) | Nenhum |

`origem_api` é um identificador lógico definido pelo operador para uma instância
persistente de PostgreSQL, não uma URL nem uma credencial. É limitado a 100 caracteres
para também caber no Oracle. Troque-o ao recriar/restaurar a base com IDs que possam
colidir. A chave única `(origem_api, leitura_api_id)` impede duplicar uma ocorrência.
ALERTA guarda somente ATENCAO, RISCO_ALTO e DADOS_INVALIDOS, uma ocorrência por leitura;
`mensagem` vem de `leitura.alerta`. Falha de sensor é ocorrência operacional.

Decisões assumidas: bueiro 1, dispositivo 1, um HC-SR04 e um DHT22 são cadastros
fictícios da demonstração. O DHT22 é um sensor físico com duas grandezas, não duas
linhas de SENSOR. Não inventamos endereço, GPS, altura, nome obrigatório de bueiro,
número de série nem data de instalação. Descrição e localização aceitam ausência.
Os únicos novos campos obrigatórios são chaves e metadados do cadastro/importação,
explicitamente preenchidos fora da API. Não há associação de ALERTA a um único
SENSOR: a regra combina distância e umidade do dispositivo.

## MongoDB: histórico documental

Uma coleção `citizentech.leituras` contém o histórico completo. Não duplicamos os
mesmos registros em outra coleção de alertas: consultas filtram o risco. O documento
tem `_id` automático, `origem_api`, `dispositivo_id` e `leitura`, com os 14 campos
originais da resposta preservados dentro de `leitura`. A amostra JSON não contém
`_id`, pois o banco o atribui. O envelope evita apresentar metadados assumidos como
se fossem retornados pelo firmware/API. A referência `dispositivo_id` aponta ao
cadastro Oracle; `(origem_api, leitura.id)` aponta à ocorrência selecionada.

Validação `$jsonSchema` exige campos, tipos, faixas e enums; não reimplementa toda
a classificação entre campos. A suíte confere a fixture contra o Backend real.
Novos campos na API exigem revisar o validator, que rejeita campos desconhecidos.
`recebido_em` permanece string para fidelidade ao JSON; a consulta por intervalo
converte para Date e ignora conversões inválidas. Esse cálculo não aproveita o
índice da string. Para grande volume, considerar campo BSON Date derivado/indexado.
Não ordenar por `tempo_ms` nem presumir espaçamento regular entre amostras.

## Por que separar

Oracle concentra entidades com identidade estável e relacionamentos sujeitos a
PK/FK, unicidade e JOIN: bueiros, dispositivos, sensores e ocorrências selecionadas.
MongoDB guarda a sequência de documentos com análises aninhadas, arrays e falhas
null, preservando a forma da API e permitindo agregações do histórico. É uma escolha
didática de persistência poliglota, não uma impossibilidade técnica de usar apenas
um banco. PostgreSQL continua sendo a persistência operacional da aplicação.

Não existe FK nem transação distribuída entre Oracle e MongoDB. Confira o cadastro
antes de importar e reconcilie pelas chaves de origem/leitura. Uma importação pode
gravar em um destino e falhar no outro; use upsert/MERGE e confira contagens ao
reexecutar. Não há sincronização automática Oracle nesta entrega. O histórico
espelha as análises apresentadas no momento da exportação; o Backend recalcula
campos derivados no GET, portanto regras futuras podem mudar essa apresentação.

## Limite da exportação

O coletor pagina por offset de 1000 em 1000, conserva null, objetos, arrays e
strings e deduplica IDs. Pause a simulação/envios antes da cópia: novas inserções
durante a paginação podem deslocar páginas e impedir um snapshot consistente.
A API não fornece cursor/snapshot. Um erro HTTP aborta a coleta antes da escrita.
O script não registra URI/credenciais, mas erros do driver devem ser tratados como
informação local e revisados antes de publicar evidências.

Referências: [validação MongoDB](https://www.mongodb.com/docs/manual/core/schema-validation/specify-json-schema/)
e [execução de scripts mongosh](https://www.mongodb.com/docs/mongodb-shell/write-scripts/).
