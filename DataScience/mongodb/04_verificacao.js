// Verificacao real opcional apos scripts 01 e 02. Nao usa mock.
async function executarVerificacao() {
const verificacao = db.getSiblingDB('citizentech');
const conferir = require('node:assert/strict');
conferir.equal(await verificacao.leituras.countDocuments({origem_api: 'simulacao-v1'}), 5);
conferir.equal(await verificacao.leituras.countDocuments({origem_api: 'simulacao-v1',
  'leitura.risco_python': {$in: ['ATENCAO', 'RISCO_ALTO', 'DADOS_INVALIDOS']}}), 3);
conferir.equal(await verificacao.leituras.countDocuments({origem_api: 'simulacao-v1', 'leitura.risco_divergente': true}), 1);
async function conferirRejeicao(documento, codigo) {
  let erroRecebido;
  try {
    await verificacao.leituras.insertOne(documento);
  } catch (erro) {
    erroRecebido = erro;
  }
  conferir.ok(erroRecebido, 'O servidor deveria rejeitar a insercao.');
  conferir.equal(erroRecebido.code, codigo);
  print('Insercao rejeitada corretamente; codigo ' + codigo);
}
const invalido = {origem_api: 'verificacao-temporaria', dispositivo_id: 1, leitura: {id: 1}};
await conferirRejeicao(invalido, 121);
const copia = await verificacao.leituras.findOne({origem_api: 'simulacao-v1', 'leitura.id': 1});
delete copia._id;
await conferirRejeicao(copia, 11000);
conferir.equal(await verificacao.leituras.countDocuments({origem_api: 'simulacao-v1'}), 5);
print('Amostra, rejeicao de contrato incompleto e unicidade verificadas no servidor.');
}
executarVerificacao();
