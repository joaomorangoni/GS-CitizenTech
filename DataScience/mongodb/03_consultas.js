const bancoConsultas = db.getSiblingDB('citizentech');
const origem = 'simulacao-v1';
// Historico na ordem da API; uptime nao e data.
print('Historico');
printjson(bancoConsultas.leituras.find({origem_api: origem}).sort({'leitura.id': -1}).limit(20).toArray());
// A API tem mensagem alerta em TODOS os riscos. Selecionar pela classificacao.
print('Alertas e falhas');
printjson(bancoConsultas.leituras.find({origem_api: origem, 'leitura.risco_python':
  {$in: ['ATENCAO', 'RISCO_ALTO', 'DADOS_INVALIDOS']}}).toArray());
print('Estatisticas por risco; medias ignoram null');
printjson(bancoConsultas.leituras.aggregate([
  {$match: {origem_api: origem}},
  {$group: {_id: '$leitura.risco_python', total: {$sum: 1},
    distancia_media_cm: {$avg: '$leitura.distancia_cm'},
    temperatura_media_c: {$avg: '$leitura.temperatura_c'},
    umidade_media: {$avg: '$leitura.umidade_relativa'},
    divergencias: {$sum: {$cond: ['$leitura.risco_divergente', 1, 0]}}}},
  {$sort: {_id: 1}}
]).toArray());
print('Historico por intervalo UTC');
printjson(bancoConsultas.leituras.aggregate([
  {$match: {origem_api: origem}},
  {$set: {data_consulta: {$convert: {input: '$leitura.recebido_em', to: 'date', onError: null, onNull: null}}}},
  {$match: {data_consulta: {$gte: ISODate('2026-11-17T12:00:00Z'), $lt: ISODate('2026-11-17T12:01:00Z')}}},
  {$sort: {data_consulta: 1, 'leitura.id': 1}}
]).toArray());
