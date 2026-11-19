"""Replica GET da API para JSON ou MongoDB; nao escreve no Backend/SQLite."""
import argparse
import json
import os
from pathlib import Path
from urllib.request import urlopen


def coletar(base_url, origem, dispositivo_id, obter=None):
    """Pagina por offset; execute com ingestao pausada para snapshot consistente."""
    if not origem.strip() or dispositivo_id <= 0:
        raise ValueError('Informe origem estavel e dispositivo_id positivo.')
    if obter is None:
        def obter(url):
            with urlopen(url, timeout=15) as resposta:
                return json.load(resposta)
    documentos = {}
    offset = 0
    while True:
        pagina = obter(f'{base_url.rstrip("/")}/api/leituras?limite=1000&offset={offset}')['leituras']
        for leitura in pagina:
            documentos[leitura['id']] = {
                'origem_api': origem, 'dispositivo_id': dispositivo_id, 'leitura': leitura}
        if len(pagina) < 1000:
            return list(documentos.values())
        offset += len(pagina)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--api', default='http://127.0.0.1:5000')
    parser.add_argument('--origem', required=True)
    parser.add_argument('--dispositivo-id', required=True, type=int)
    parser.add_argument('--saida', type=Path)
    parser.add_argument('--mongo', action='store_true')
    args = parser.parse_args()
    if args.mongo and not os.environ.get('MONGODB_URI'):
        parser.error('Defina MONGODB_URI no ambiente, sem gravar credenciais no repositorio.')
    if not args.saida and not args.mongo:
        parser.error('Selecione --saida e/ou --mongo.')
    docs = coletar(args.api, args.origem, args.dispositivo_id)
    if args.saida:
        args.saida.write_text(json.dumps(docs, ensure_ascii=False, indent=2), encoding='utf-8')
    if args.mongo:
        from pymongo import MongoClient, UpdateOne
        with MongoClient(os.environ['MONGODB_URI'], serverSelectionTimeoutMS=5000) as client:
            banco = client['citizentech']
            if 'leituras' not in banco.list_collection_names():
                raise RuntimeError('Execute mongodb/01_colecoes.js antes da importacao.')
            if docs:
                banco.leituras.bulk_write([
                    UpdateOne({'origem_api': d['origem_api'], 'leitura.id': d['leitura']['id']},
                              {'$set': d}, upsert=True) for d in docs])
    print(f'{len(docs)} leituras exportadas; nenhuma alteracao na API.')


if __name__ == '__main__':
    main()
