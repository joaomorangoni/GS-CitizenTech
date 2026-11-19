"""Compara evidencias SQL reais ao design nativo; nao acessa nem altera bancos."""
import hashlib
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET


def main():
    raiz = Path(__file__).resolve().parents[2]
    evidencias = raiz / 'DataScience/documentacao/evidencias'
    texto = (evidencias / 'oracle_validacao_final.txt').read_text(encoding='utf-8-sig')
    dados = {'ANTES': {}, 'DEPOIS': {}}
    metadata = {chave: [] for chave in ('COLUNA', 'CHAVE', 'CHECK', 'IDENTITY')}
    for linha in texto.splitlines():
        if linha.startswith('DADOS|'):
            _, fase, tabela, documento = linha.split('|', 3)
            dados[fase][tabela] = json.loads(documento)
        else:
            tipo, _, documento = linha.partition('|')
            if tipo in metadata:
                item = json.loads(documento)
                if item not in metadata[tipo]:
                    metadata[tipo].append(item)

    resultados = []
    def conferir(nome, condicao, detalhe):
        resultados.append({'verificacao': nome, 'passou': bool(condicao), 'detalhe': detalhe})

    esperados = {'BUEIRO': 1, 'DISPOSITIVO': 1, 'SENSOR': 2, 'ALERTA': 3}
    for tabela, total in esperados.items():
        observado = len(dados['ANTES'].get(tabela, []))
        conferir(f'COUNT(*) {tabela}', tabela in dados['ANTES'] and observado == total,
                 f'esperado {total}; observado {observado}')
    conferir('Preservacao integral dos registros',
             set(dados['ANTES']) == set(esperados) and dados['ANTES'] == dados['DEPOIS'],
             'Comparacao JSON de todos os campos e registros, ordenados por PK, antes/depois dos testes.')
    conferir('Execucao SQL completa', 'VALIDACAO SQL CONCLUIDA' in texto
             and not re.search(r'(?m)^\s*(?:ORA-\d+|SP2-\d+|ERROR at line)', texto),
             'Finalizacao SQL sem erros inesperados; rejeicoes esperadas constam como testes aprovados.')
    trecho_joins = texto.split('INICIO JOINs 03_consultas.sql')[-1].split('FIM JOINs 03_consultas.sql')[0]
    conferir('Tres consultas JOIN originais', all(marca in trecho_joins for marca in
             ('2 rows selected.', '3 rows selected.', '1 row selected.')),
             'Inventario: 2 linhas; rastreabilidade: 3 linhas (leituras 2, 3 e 4); contagem do bueiro: 3 ocorrencias.')
    for codigo in ('ORA-00001', 'ORA-02291', 'ORA-02290'):
        conferir(f'Teste {codigo}', codigo in texto, 'Rejeicao esperada confirmada pelo script 04_verificacao.sql.')

    modelo = raiz / 'DataScience/diagramas/citizentech'
    ET.parse(raiz / 'DataScience/diagramas/citizentech.dmd')
    tabelas = [ET.parse(p).getroot() for p in modelo.glob('rel/*/table/seg_*/*.xml')]
    por_id = {t.attrib['id']: t for t in tabelas}
    dominios = {d.attrib['id']: d for p in modelo.glob('domains/*.xml')
                for d in ET.parse(p).getroot().findall('./domains/Domain')}
    colunas_modelo, chaves_modelo, checks_modelo, identity_modelo = [], [], [], []
    for tabela in tabelas:
        nome = tabela.attrib['name'].upper()
        colunas = tabela.findall('./columns/Column')
        ids = {c.attrib['id']: c.attrib['name'].upper() for c in colunas}
        for posicao, coluna in enumerate(colunas, 1):
            dominio = dominios[coluna.findtext('domain')]
            logico = dominio.findtext('logicalDatatype')
            precisao, escala, tamanho, semantica = None, None, 0, None
            if logico == 'LOGDT019':
                tipo = 'NUMBER'
                if dominio.findtext('dataTypePrecision'):
                    precisao = int(dominio.findtext('dataTypePrecision'))
                    escala = int(dominio.findtext('dataTypeScale', '0'))
            elif logico == 'LOGDT024':
                tipo = 'VARCHAR2'
                tamanho = int(dominio.findtext('dataTypeSize').split()[0])
                semantica = 'C' if 'CHAR' in dominio.findtext('dataTypeSize') else 'B'
            elif logico == 'LOGDT046':
                escala = int(dominio.findtext('dataTypePrecision'))
                tipo = f'TIMESTAMP({escala}) WITH TIME ZONE'
            else:
                raise ValueError(f'Tipo do Modeler nao suportado na comparacao: {logico}')
            identidade = coluna.findtext('identityColumn') == 'true'
            colunas_modelo.append(dict(tabela=nome, coluna=coluna.attrib['name'].upper(),
                posicao=posicao, tipo=tipo, precisao=precisao, escala=escala, tamanho=tamanho,
                semantica=semantica, nulo='Y' if coluna.findtext('nullsAllowed') == 'true' else 'N',
                identity='YES' if identidade else 'NO'))
            if identidade:
                identity_modelo.append(dict(tabela=nome, coluna=coluna.attrib['name'].upper(),
                    geracao='ALWAYS' if coluna.findtext('autoIncrementGenerateAlways') == 'true' else 'BY DEFAULT'))
        for indice in tabela.findall('./indexes/ind_PK_UK'):
            estado = indice.findtext('indexState')
            if estado not in ('Primary Constraint', 'Unique Constraint'):
                continue
            for posicao, uso in enumerate(indice.findall('./indexColumnUsage/colUsage'), 1):
                chaves_modelo.append(dict(tabela=nome, nome=indice.attrib['name'].upper(),
                    tipo='P' if estado == 'Primary Constraint' else 'U', coluna=ids[uso.attrib['columnID']],
                    posicao=posicao, pai=None, coluna_pai=None, exclusao=None, estado='ENABLED'))
        for check in tabela.findall('./tableCheckConstraints/tableCheckConstraint'):
            checks_modelo.append(dict(tabela=nome, nome=check.attrib['name'].upper(),
                                     regra=check.findtext('rule'), estado='ENABLED'))
    for arquivo in modelo.glob('rel/*/foreignkey/seg_*/*.xml'):
        fk = ET.parse(arquivo).getroot()
        filha = por_id[fk.attrib['containerWithKeyObject']]
        pai = por_id[fk.findtext('referredTableID')]
        ids = {c.attrib['id']: c.attrib['name'].upper() for c in filha.findall('./columns/Column')}
        indice = next(i for i in filha.findall('./indexes/ind_PK_UK') if i.attrib['id'] == fk.attrib['localFKIndex'])
        referencias = [c.strip().upper() for c in fk.findtext('refColNames').split(',')]
        for posicao, uso in enumerate(indice.findall('./indexColumnUsage/colUsage'), 1):
            chaves_modelo.append(dict(tabela=filha.attrib['name'].upper(), nome=fk.attrib['name'].upper(),
                tipo='R', coluna=ids[uso.attrib['columnID']], posicao=posicao, pai=pai.attrib['name'].upper(),
                coluna_pai=referencias[posicao-1], exclusao=fk.findtext('deleteRule'), estado='ENABLED'))

    def normalizados(lista):
        return sorted(json.dumps(item, ensure_ascii=False, sort_keys=True) for item in lista)
    def normalizar_checks(lista):
        return [dict(item, regra=re.sub(r'\s+', '', item['regra']).upper()) for item in lista]
    conferir('Modeler: tabelas', {t.attrib['name'].upper() for t in tabelas} == set(esperados), '4 tabelas no design nativo e no banco.')
    conferir('Modeler: colunas e tipos', normalizados(colunas_modelo) == normalizados(metadata['COLUNA']),
             '16 colunas: nomes, ordem, tipos, precisao/escala, VARCHAR2 CHAR, nulabilidade e identity.')
    conferir('Modeler: PK, UNIQUE e FK', normalizados(chaves_modelo) == normalizados(metadata['CHAVE']),
             '4 PKs, 1 UNIQUE composta e 3 FKs: nomes, colunas ordenadas, tabelas referenciadas e NO ACTION.')
    conferir('Modeler: CHECKs', normalizados(normalizar_checks(checks_modelo)) == normalizados(normalizar_checks(metadata['CHECK'])),
             '3 CHECKs nomeados com regras equivalentes e habilitados no banco.')
    conferir('Modeler: identity', normalizados(identity_modelo) == normalizados(metadata['IDENTITY']),
             'ALERTA.ALERTA_ID GENERATED ALWAYS AS IDENTITY.')

    comparacao = dict(resultados=resultados, banco=metadata,
        modelo=dict(colunas=colunas_modelo, chaves=chaves_modelo, checks=checks_modelo, identity=identity_modelo),
        sha256_sql={nome: hashlib.sha256((raiz / 'DataScience/oracle' / nome).read_bytes()).hexdigest()
                    for nome in ('03_consultas.sql', '04_verificacao.sql')})
    (evidencias / 'oracle_comparacao_modelo_final.json').write_text(json.dumps(comparacao, ensure_ascii=False, indent=2), encoding='utf-8')
    aprovado = all(r['passou'] for r in resultados)
    horario = re.search(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} -03:00', texto)
    linhas = ['# Relatório final — Oracle SQL CitizenTech', '',
        f'Execução real: {horario.group() if horario else "ver saída SQL"} (America/Sao_Paulo).', '',
        '**Oracle pronto para a entrega da FIAP no escopo solicitado.**' if aprovado else '**Há verificações com falha; revisar antes de entregar.**', '',
        'Conexão existente: container citizentech-oracle, usuário CITIZENTECH, PDB FREEPDB1, '
        'Oracle AI Database 26ai Free 23.26.3.0.0. Credencial DPAPI lida fora do repositório; senha não registrada.', '',
        '| Verificação | Resultado | Evidência |', '| --- | --- | --- |']
    linhas += [f"| {r['verificacao']} | {'PASSOU' if r['passou'] else 'FALHOU'} | {r['detalhe']} |" for r in resultados]
    linhas += ['', f"Falhas observadas: {sum(not r['passou'] for r in resultados)}.", '',
        'As contagens totais são 1 BUEIRO, 1 DISPOSITIVO, 2 SENSOR e 3 ALERTA. '
        'Os snapshots completos antes/depois demonstram a preservação dos registros. '
        'Não foram executados os scripts de criação 01 ou inserção 02. '
        'O script 04 usa tentativas rejeitadas e rollback. Backend e Hardware não foram alterados.', '',
        '## Arquivos para entregar', '',
        '- [Saída real completa](oracle_validacao_final.txt): COUNT(*), JOINs, testes e metadados antes/depois.',
        '- [Comparação detalhada](oracle_comparacao_modelo_final.json): banco versus XML nativo e hashes dos SQL testados.',
        '- [Design nativo](../../diagramas/citizentech.dmd) junto com toda a pasta `../../diagramas/citizentech/`.',
        '- [Captura do diagrama](data_modeler_diagrama.png) e [log de importação](data_modeler_importacao.png), capturados na etapa anterior.', '',
        '## Pendências e limites', '',
        'Nenhuma pendência técnica encontrada para os oito itens desta validação, se todos estiverem aprovados na tabela. '
        'Ainda cabe conferir o enunciado/rubrica oficial da FIAP e anexar os arquivos exigidos; '
        'a aprovação acadêmica não é determinada por estes testes. '
        'A conexão gráfica do Modeler ao banco e importadores Python não fazem parte desta validação. '
        'O design usa dialeto Oracle 21c; a comparação confirmou sua estrutura no servidor 26ai local. '
        'A comparação usa o modelo relacional nativo, não interpretação dos pixels da captura. '
        'O modelo lógico do design permanece vazio e só precisa ser desenvolvido se a rubrica exigir.', '',
        '## Reproduzir sem recriar tabelas', '', 'Da raiz do repositório, com Docker e o container ativos:', '',
        '```powershell', 'powershell -NoProfile -ExecutionPolicy Bypass -File DataScience/oracle/validar_final.ps1',
        'py -3 DataScience/oracle/comparar_modelo_final.py', '```', '']
    (evidencias / 'oracle_relatorio_final.md').write_text('\n'.join(linhas), encoding='utf-8')
    for resultado in resultados:
        print(('PASSOU' if resultado['passou'] else 'FALHOU') + ': ' + resultado['verificacao'])
    raise SystemExit(0 if aprovado else 1)


if __name__ == '__main__':
    main()
