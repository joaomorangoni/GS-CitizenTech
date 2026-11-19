// Auditoria somente leitura. Executar da raiz via mongosh --file.
const auditoria = db.getSiblingDB('citizentech');
printjson({ping: db.adminCommand({ping: 1}), versaoServidor: db.version()});
printjson({colecao: auditoria.getCollectionInfos({name: 'leituras'}), indices: auditoria.leituras.getIndexes()});
printjson({totalColecao: auditoria.leituras.countDocuments({}),
  totalSimulacao: auditoria.leituras.countDocuments({origem_api: 'simulacao-v1'}),
  documentosInvalidosPersistidos: auditoria.leituras.countDocuments({origem_api: 'verificacao-temporaria'})});
const esperados = JSON.parse(require('fs').readFileSync('DataScience/mongodb/leituras_simuladas.json', 'utf8'));
const conferirDocumento = require('node:assert/strict');
function jsonOrdenado(valor) {
  if (Array.isArray(valor)) return '[' + valor.map(jsonOrdenado).join(',') + ']';
  if (valor !== null && typeof valor === 'object') {
    return '{' + Object.keys(valor).sort().map(chave => JSON.stringify(chave) + ':' + jsonOrdenado(valor[chave])).join(',') + '}';
  }
  return JSON.stringify(valor);
}
for (const documento of esperados) {
  const atual = auditoria.leituras.findOne({origem_api: documento.origem_api, 'leitura.id': documento.leitura.id});
  delete atual._id;
  conferirDocumento.equal(jsonOrdenado(atual), jsonOrdenado(documento));
}
print('Os cinco documentos conferem integralmente com a fixture JSON.');
printjson(auditoria.leituras.aggregate([
  {$match: {origem_api: 'simulacao-v1'}},
  {$group: {_id: null, total: {$sum: 1}, distancia_media_cm: {$avg: '$leitura.distancia_cm'},
    temperatura_media_c: {$avg: '$leitura.temperatura_c'}, umidade_media: {$avg: '$leitura.umidade_relativa'},
    divergencias: {$sum: {$cond: ['$leitura.risco_divergente', 1, 0]}}}}
]).toArray());
