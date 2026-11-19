import json
import os
import uuid
import unittest
from pathlib import Path

from Backend.monitoramento import apresentar_leitura, processar_leitura
from Backend.validacoes import validar_leitura
from DataScience.integracao import coletar


class TestDataScience(unittest.TestCase):
    def test_fixture_compativel_com_regras_reais(self):
        docs = json.loads((Path(__file__).parents[1] / 'mongodb/leituras_simuladas.json').read_text(encoding='utf-8'))
        riscos = set()
        for doc in docs:
            leitura = doc['leitura']
            entrada = {c: leitura[c] for c in ('distancia_cm', 'temperatura_c', 'umidade_relativa', 'tempo_ms')}
            entrada['risco'] = leitura['risco_esp32']
            registro = processar_leitura(validar_leitura(entrada))
            registro.update(id=leitura['id'], recebido_em=leitura['recebido_em'])
            self.assertEqual(apresentar_leitura(registro), leitura)
            riscos.add(leitura['risco_python'])
        self.assertEqual(len(riscos), 4)
        self.assertTrue(any(d['leitura']['risco_divergente'] for d in docs))
        self.assertTrue(any(d['leitura']['temperatura_c'] is None for d in docs))

    @unittest.skipUnless(os.environ.get('TEST_DATABASE_URL'),
                         'Configure TEST_DATABASE_URL para o teste PostgreSQL')
    def test_exportacao_contra_api_real_temporaria(self):
        import psycopg
        from psycopg import sql
        from psycopg.conninfo import make_conninfo
        from Backend.app import create_app

        base = os.environ['TEST_DATABASE_URL']
        esquema = 'datascience_teste_' + uuid.uuid4().hex
        with psycopg.connect(base, autocommit=True) as conexao:
            conexao.execute(sql.SQL('CREATE SCHEMA {}').format(sql.Identifier(esquema)))

        def limpar():
            with psycopg.connect(base, autocommit=True) as conexao:
                conexao.execute(sql.SQL('DROP SCHEMA {} CASCADE').format(sql.Identifier(esquema)))

        self.addCleanup(limpar)
        banco = make_conninfo(base, options=f'-csearch_path={esquema}')
        client = create_app({'TESTING': True, 'DATABASE': banco}).test_client()
        self.assertEqual(coletar('http://local', 'teste', 1, lambda url: client.get(url).json), [])
        resposta = client.post('/api/leituras', json=dict(distancia_cm=None, temperatura_c=27,
            umidade_relativa=80, risco='ATENCAO', tempo_ms=4294967295))
        self.assertEqual(resposta.status_code, 201)
        docs = coletar('http://local', 'teste', 1, lambda url: client.get(url).json)
        self.assertEqual(docs, [{'origem_api': 'teste', 'dispositivo_id': 1, 'leitura': resposta.json}])
        self.assertEqual(client.get('/api/resumo').json['total_leituras'], 1)

    def test_paginacao_mais_de_mil(self):
        urls = []
        def obter(url):
            urls.append(url)
            return {'leituras': [{'id': i} for i in range(1001, 1, -1)] if len(urls) == 1 else [{'id': 1}]}
        docs = coletar('http://local/', 'teste', 1, obter)
        self.assertEqual(len(docs), 1001)
        self.assertTrue(urls[1].endswith('offset=1000'))

    def test_vinculo_exige_configuracao_explicita(self):
        for origem, dispositivo in [('', 1), ('teste', 0)]:
            with self.assertRaises(ValueError):
                coletar('http://local', origem, dispositivo)
