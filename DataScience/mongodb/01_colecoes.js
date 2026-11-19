// mongosh: executar da raiz do repositorio. Nao apaga colecoes existentes.
const banco = db.getSiblingDB('citizentech');
const numero = {bsonType: ['double', 'int', 'long', 'decimal', 'null']};
const riscos = ['SEM_RISCO_DETECTADO', 'ATENCAO', 'RISCO_ALTO', 'DADOS_INVALIDOS'];
const schema = {
  bsonType: 'object', required: ['origem_api', 'dispositivo_id', 'leitura'],
  additionalProperties: false,
  properties: {
    _id: {}, origem_api: {bsonType: 'string', minLength: 1},
    dispositivo_id: {bsonType: ['int', 'long', 'double'], minimum: 1, multipleOf: 1},
    leitura: {
      bsonType: 'object', additionalProperties: false,
      required: ['id', 'distancia_cm', 'temperatura_c', 'umidade_relativa', 'risco_esp32',
        'risco_python', 'tempo_ms', 'recebido_em', 'analise_distancia', 'ambiente',
        'alerta', 'risco_divergente', 'sensores_sem_leitura'],
      properties: {
        id: {bsonType: ['int', 'long', 'double'], minimum: 1, multipleOf: 1},
        distancia_cm: {...numero, minimum: 0},
        temperatura_c: {...numero, minimum: -40, maximum: 80},
        umidade_relativa: {...numero, minimum: 0, maximum: 100},
        risco_esp32: {enum: riscos}, risco_python: {enum: riscos},
        tempo_ms: {bsonType: ['int', 'long', 'double'], minimum: 0, maximum: 4294967295, multipleOf: 1},
        // String original UTC preservada; consultas temporais convertem para BSON Date.
        recebido_em: {bsonType: 'string', pattern: '^\\d{4}-\\d{2}-\\d{2}T.*\\+00:00$'},
        analise_distancia: {enum: ['SEM_LEITURA', 'CRITICA', 'CURTA', 'ACIMA_DO_LIMITE_DE_ATENCAO']},
        ambiente: {bsonType: 'object', additionalProperties: false,
          required: ['temperatura_disponivel', 'umidade_elevada'], properties: {
            temperatura_disponivel: {bsonType: 'bool'}, umidade_elevada: {bsonType: ['bool', 'null']}}},
        alerta: {bsonType: 'string'}, risco_divergente: {bsonType: 'bool'},
        sensores_sem_leitura: {bsonType: 'array', uniqueItems: true,
          items: {enum: ['distancia_cm', 'temperatura_c', 'umidade_relativa']}}
      }
    }
  }
};
if (!banco.getCollectionNames().includes('leituras')) {
  banco.createCollection('leituras', {validator: {$jsonSchema: schema}, validationLevel: 'strict', validationAction: 'error'});
} else {
  // Falha explicitamente: nao alterar validacao de uma colecao preexistente sem revisao.
  throw new Error('Colecao leituras ja existe; confira seu validator e indices antes de prosseguir.');
}
banco.leituras.createIndex({origem_api: 1, 'leitura.id': 1}, {unique: true});
banco.leituras.createIndex({dispositivo_id: 1, 'leitura.recebido_em': -1});
banco.leituras.createIndex({'leitura.risco_python': 1});
print('Colecao e indices criados.');
