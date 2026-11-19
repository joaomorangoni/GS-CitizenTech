# Exemplo opcional de importação de ocorrências Oracle

Não é necessário para o Backend funcionar. Depois de criar cadastros reais e
validar a exportação JSON, um consumidor pode usar `python-oracledb` para executar
o MERGE abaixo com binds, uma vez por documento cujo risco não seja
SEM_RISCO_DETECTADO. Instalação opcional: `python -m pip install oracledb`.
Configure conexão e senha em variáveis de ambiente ou secret manager; nunca no SQL.

```python
import os
import json
from datetime import datetime
import oracledb

with open('DataScience/exportacao.local.json', encoding='utf-8') as arquivo:
    documentos = json.load(arquivo)
sql = '''
MERGE INTO ALERTA a
USING (SELECT :origem origem, :leitura_id leitura_id FROM dual) s
ON (a.origem_api = s.origem AND a.leitura_api_id = s.leitura_id)
WHEN NOT MATCHED THEN INSERT
 (dispositivo_id, origem_api, leitura_api_id, recebido_em, risco_python, mensagem)
VALUES (:dispositivo_id, s.origem, s.leitura_id,
 TO_TIMESTAMP_TZ(:data_utc, 'YYYY-MM-DD"T"HH24:MI:SS.FF6TZH:TZM'), :risco, :mensagem)
'''
with oracledb.connect(user=os.environ['ORACLE_USER'],
                     password=os.environ['ORACLE_PASSWORD'],
                     dsn=os.environ['ORACLE_DSN']) as conexao:
    with conexao.cursor() as cursor:
        for doc in documentos:
            leitura = doc['leitura']
            if leitura['risco_python'] == 'SEM_RISCO_DETECTADO':
                continue
            data = datetime.fromisoformat(leitura['recebido_em'])
            cursor.execute(sql, origem=doc['origem_api'], leitura_id=leitura['id'],
                           dispositivo_id=doc['dispositivo_id'],
                           data_utc=data.isoformat(timespec='microseconds'),
                           risco=leitura['risco_python'], mensagem=leitura['alerta'])
    conexao.commit()
```

Exemplo para executar em consumidor separado; não foi executado contra Oracle.
MERGE evita duplicar chaves já importadas e mantém a primeira ocorrência registrada.
Não atualiza cadastros, não infere IDs, não oferece atomicidade com MongoDB.
Antes de importar, confira `origem_api` (até 100 caracteres), dispositivo cadastrado
e origem exclusiva daquela base PostgreSQL. Não use `simulacao-v1` para dados reais.
