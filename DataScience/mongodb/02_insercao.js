// Fixture derivada das funcoes reais do Backend, com datas sinteticas fixas.
const bancoInsercao = db.getSiblingDB('citizentech');
if (!bancoInsercao.getCollectionNames().includes('leituras')) throw new Error('Execute 01_colecoes.js primeiro.');
const documentos = JSON.parse(require('fs').readFileSync('DataScience/mongodb/leituras_simuladas.json', 'utf8'));
printjson(bancoInsercao.leituras.bulkWrite(documentos.map(d => ({updateOne: {
  filter: {origem_api: d.origem_api, 'leitura.id': d.leitura.id},
  update: {$set: d}, upsert: true
}}))));
