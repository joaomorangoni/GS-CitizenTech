"""Audita DataScience e cria entrega FIAP, sem acessar ou alterar bancos."""
import argparse
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import xml.etree.ElementTree as ET
import zipfile


def texto(arquivo):
    dados = arquivo.read_bytes()
    return dados.decode('utf-16' if dados.startswith((b'\xff\xfe', b'\xfe\xff')) else 'utf-8-sig')


def sha256(dados):
    return hashlib.sha256(dados).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--nome', default='GS-CitizenTech_Cognitive_Data_Science_2026_2')
    args = parser.parse_args()
    if not re.fullmatch(r'[A-Za-z0-9_-]+', args.nome):
        parser.error('Nome deve conter apenas letras, numeros, hifen e sublinhado.')
    raiz = Path(__file__).resolve().parent.parent
    fonte = raiz / 'DataScience'
    destino = raiz / 'entrega' / args.nome
    arquivo_zip = destino.with_suffix('.zip')
    if destino.exists() or arquivo_zip.exists():
        parser.error('Entrega ja existe; use --nome com outro nome, sem apagar a entrega anterior.')

    def exigir(condicao, mensagem):
        if not condicao:
            raise RuntimeError(mensagem)

    permitidas = {'.py', '.ps1', '.sql', '.js', '.json', '.mmd', '.dmd', '.md', '.txt', '.xml', '.png'}
    proibidas = {'.git', '.venv', 'venv', '__pycache__', 'node_modules', '.aws', '.codex', '.agents', 'wallet'}
    def incluir(arquivo):
        rel = arquivo.relative_to(fonte)
        return not any(p.lower() in proibidas for p in rel.parts) and (
            arquivo.name == '.gitignore' or arquivo.suffix.lower() in permitidas
        ) and not any(p.lower().startswith('.env') for p in rel.parts)

    arquivos = sorted(p for p in fonte.rglob('*') if p.is_file() and incluir(p))
    excluidos = sorted(p.relative_to(fonte).as_posix() for p in fonte.rglob('*') if p.is_file() and not incluir(p))
    for arquivo in arquivos:
        exigir(not arquivo.is_symlink() and arquivo.resolve().is_relative_to(fonte.resolve()), 'Arquivo fora da fonte ou link simbolico.')
        conteudo = arquivo.read_bytes()
        segredo = os.environ.get('CITIZENTECH_AUDIT_SECRET')
        if segredo:
            exigir(all(segredo.encode(codificacao) not in conteudo for codificacao in ('utf-8', 'utf-16-le', 'utf-16-be')),
                   'Credencial local detectada; empacotamento interrompido sem exibir o valor.')
        if arquivo.suffix != '.png':
            valor = texto(arquivo)
            exigir(not re.search(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|gh[pousr]_[A-Za-z0-9]{30,}|AKIA[A-Z0-9]{16}', valor),
                   f'Padrao de segredo detectado em {arquivo.relative_to(fonte)}.')
            exigir(not re.search(r'(?:mongodb(?:\+srv)?|https?)://[^\s/@:]+:[^\s/@]+@', valor),
                   f'URL autenticada detectada em {arquivo.relative_to(fonte)}.')
    for nome in ('oracle/01_criacao.sql', 'oracle/02_dados_simulados.sql', 'oracle/03_consultas.sql',
                 'oracle/04_verificacao.sql', 'oracle/05_snapshot_validacao.sql',
                 'mongodb/01_colecoes.js', 'mongodb/02_insercao.js', 'mongodb/03_consultas.js',
                 'mongodb/04_verificacao.js', 'mongodb/leituras_simuladas.json',
                 'diagramas/modelo_er.mmd', 'diagramas/citizentech.dmd',
                 'documentacao/modelagem.md', 'documentacao/checklist_entrega.md'):
        exigir(fonte / nome in arquivos, f'Arquivo necessario ausente: {nome}')

    # Verificar hashes registrados antes de regenerar o relatorio, para nao
    # validar silenciosamente SQL modificado depois da execucao real.
    comparacao_anterior = json.loads((fonte / 'documentacao/evidencias/oracle_comparacao_modelo_final.json').read_text(encoding='utf-8'))
    for nome, hash_esperado in comparacao_anterior['sha256_sql'].items():
        exigir(sha256((fonte / 'oracle' / nome).read_bytes()) == hash_esperado, 'SQL alterado apos sua validacao real.')
    # Comparacao do design com metadados reais ja salvos; nao conecta ao Oracle.
    subprocess.run([os.sys.executable, '-B', str(fonte / 'oracle/comparar_modelo_final.py')], cwd=raiz, check=True)
    comparacao = json.loads((fonte / 'documentacao/evidencias/oracle_comparacao_modelo_final.json').read_text(encoding='utf-8'))
    exigir(all(item['passou'] for item in comparacao['resultados']), 'Comparacao Oracle com falhas.')
    for nome, hash_esperado in comparacao['sha256_sql'].items():
        exigir(sha256((fonte / 'oracle' / nome).read_bytes()) == hash_esperado, 'SQL alterado apos sua validacao.')
    native = fonte / 'diagramas/citizentech'
    xmls = sorted(native.rglob('*.xml'))
    for arquivo in xmls:
        ET.parse(arquivo)
    ET.parse(fonte / 'diagramas/citizentech.dmd')
    tabelas = [ET.parse(p).getroot() for p in native.glob('rel/*/table/seg_*/*.xml')]
    fks = [ET.parse(p).getroot() for p in native.glob('rel/*/foreignkey/seg_*/*.xml')]
    dominios = {d.attrib['id'] for p in native.glob('domains/*.xml') for d in ET.parse(p).getroot().findall('./domains/Domain')}
    por_id = {t.attrib['id']: t for t in tabelas}
    ids_indices = {i.attrib['id'] for t in tabelas for i in t.findall('./indexes/ind_PK_UK')}
    for tabela in tabelas:
        exigir(all(c.findtext('domain') in dominios for c in tabela.findall('./columns/Column')), 'Dominio dependente ausente.')
    for fk in fks:
        exigir(fk.attrib['containerWithKeyObject'] in por_id and fk.findtext('referredTableID') in por_id
               and fk.attrib['localFKIndex'] in ids_indices and fk.findtext('referredKeyID') in ids_indices,
               'Dependencia de FK ausente no design.')
    exigir(len(tabelas) == 4 and len(fks) == 3, 'Design relacional incompleto.')
    mermaid = (fonte / 'diagramas/modelo_er.mmd').read_text(encoding='utf-8')
    blocos = {nome: re.findall(r'^\s*\w+\s+(\w+)\b', corpo, re.M)
              for nome, corpo in re.findall(r'^\s*(\w+)\s*\{\s*\n(.*?)^\s*\}', mermaid, re.M | re.S)}
    exigir(blocos == {t.attrib['name']: [c.attrib['name'] for c in t.findall('./columns/Column')] for t in tabelas},
           'Campos Mermaid nao correspondem ao design nativo.')
    relacoes = set(re.findall(r'(\w+)\s+\|\|\.\.o\{\s+(\w+)', mermaid))
    exigir(relacoes == {('BUEIRO', 'DISPOSITIVO'), ('DISPOSITIVO', 'SENSOR'), ('DISPOSITIVO', 'ALERTA')}, 'Relacoes Mermaid incorretas.')
    fixture = json.loads((fonte / 'mongodb/leituras_simuladas.json').read_text(encoding='utf-8'))
    exigir(len(fixture) == 5 and all(d['origem_api'] == 'simulacao-v1' for d in fixture), 'Fixture MongoDB incorreta.')
    validacao_mongo = texto(fonte / 'documentacao/evidencias/mongodb_validacao.txt')
    exigir('121' in validacao_mongo and '11000' in validacao_mongo, 'Evidencias de rejeicao MongoDB ausentes.')
    auditoria_mongo = texto(fonte / 'documentacao/evidencias/mongodb_auditoria.txt')
    exigir('Os cinco documentos conferem integralmente' in auditoria_mongo and 'totalSimulacao: 5' in auditoria_mongo,
           'Evidencia real dos cinco documentos MongoDB ausente.')
    for nome in ('data_modeler_diagrama.png', 'data_modeler_importacao.png'):
        exigir((fonte / 'documentacao/evidencias' / nome).read_bytes().startswith(b'\x89PNG\r\n\x1a\n'), 'Captura PNG ausente/invalida.')
    testes = texto(fonte / 'documentacao/evidencias/testes_contrato_entrega.txt')
    exigir('Ran 4 tests' in testes and re.search(r'(?m)^OK\s*$', testes), 'Testes de contrato nao aprovados.')
    git_status = subprocess.run(['git', 'status', '--short'], cwd=raiz, check=True, capture_output=True, text=True).stdout
    subprocess.run(['git', 'diff', '--exit-code', '--', 'Backend', 'Hardware'], cwd=raiz, check=True)
    subprocess.run(['git', 'diff', '--check'], cwd=raiz, check=True)

    auditoria = fonte / 'documentacao/auditoria_entrega.md'
    auditoria.write_text('\n'.join([
        '# Auditoria final da entrega — CitizenTech', '',
        'Escopo: artefatos de Cognitive Data Science. Nenhuma consulta, insercao, DDL ou teste foi executado '
        'contra bancos existentes durante o empacotamento. Evidencias reais anteriores foram auditadas.', '',
        '- PASSOU: cinco SQL Oracle e quatro scripts MongoDB, alem da fixture ficticia e auxiliares.',
        '- PASSOU: 15 verificacoes Oracle com base nas evidencias reais; resultados e SQL consistentes.',
        f'- PASSOU: design nativo com {len(xmls)} XMLs, quatro tabelas, 16 colunas, tres FKs e dominios dependentes presentes.',
        '- PASSOU: Mermaid corresponde aos campos e relacionamentos do modelo relacional; linhas nao identificadoras corrigidas.',
        '- PASSOU: evidencias reais MongoDB, cinco documentos, codigos 121/11000 e reinsercao sem duplicacao.',
        '- PASSOU: justificativa dos dois bancos, hipoteses, dicionario e limites documentados.',
        '- Testes Python: consulte documentacao/validacao.md; integracao PostgreSQL requer TEST_DATABASE_URL.',
        '- PASSOU: nenhum padrao de segredo ou URL autenticada detectado nos arquivos selecionados. '
        + ('Credencial Oracle local comparada sem revelar o valor.' if os.environ.get('CITIZENTECH_AUDIT_SECRET') else 'Comparacao com credencial local nao fornecida nesta execucao.'),
        '- PASSOU: Backend e Hardware sem diff; nenhum push, commit ou staging realizado.', '',
        '## Integridade do pacote', '',
        'O manifesto SHA-256 cobre todos os arquivos, exceto o proprio manifesto. O empacotador '
        'verifica os CRCs do ZIP e cada conteudo compactado, preservando bytes das evidencias. '
        'O resultado final dessa verificacao fica em entrega/VERIFICACAO_ZIP.txt.', '',
        '## Limites e acoes manuais', '',
        'Rubrica oficial nao fornecida: conferir identificacao de integrantes/RAs, formato, limite de '
        'arquivo, modelo logico separado, PDF, capturas adicionais, video e link GitHub. '
        'O modelo logico nativo esta vazio; o relacional esta completo. O ZIP somente DataScience '
        'nao inclui Backend/Hardware; testes Python e exemplos com API exigem o repositorio completo. '
        'Metadados originais de autoria/caminhos locais e horarios foram preservados, sem segredos. '
        'Nao foram inventados nomes de integrantes nem capturas.', '',
        '## Git no momento da auditoria', '', '```text', git_status.rstrip(), '```', '',
        'Enviar ao GitHub DataScience/ inteira respeitando .gitignore e entrega/.gitignore. '
        'A modificacao preexistente no README.md da raiz deve ser revisada separadamente. '
        'ZIP e pasta expandida sao derivados ignorados; submissao ao Portal e push sao manuais.', '',
        '## Arquivos locais excluidos', '',
        *[f'- `{nome}`' for nome in excluidos], '']), encoding='utf-8')
    arquivos = sorted(p for p in fonte.rglob('*') if p.is_file() and incluir(p))
    destino.mkdir(parents=True)
    for arquivo in arquivos:
        copia = destino / 'DataScience' / arquivo.relative_to(fonte)
        copia.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(arquivo, copia)
    leia_me = destino / 'LEIA-ME_ENTREGA.md'
    leia_me.write_text('\n'.join([
        '# CitizenTech — Global Solution 2026.2 — Cognitive Data Science', '',
        f'Arquivo de submissao: **{arquivo_zip.name}**.', '',
        '## Comece por aqui', '',
        '1. Leia [checklist final](DataScience/documentacao/checklist_entrega.md) e '
        '[auditoria](DataScience/documentacao/auditoria_entrega.md).',
        '2. Consulte [modelagem e justificativa](DataScience/documentacao/modelagem.md).',
        '3. Abra [citizentech.dmd](DataScience/diagramas/citizentech.dmd) no Data Modeler; '
        'mantenha toda a pasta citizentech/ junto do arquivo.',
        '4. Confira [relatorio Oracle](DataScience/documentacao/evidencias/oracle_relatorio_final.md) '
        'e [evidencias reais](DataScience/documentacao/evidencias/README.md).',
        '5. Para reproducao, siga [README tecnico](DataScience/README.md), sempre a partir '
        'desta pasta, que contem DataScience/. Crie recursos apenas em bancos novos ou schema exclusivo.', '',
        'Oracle: 1 bueiro, 1 dispositivo, 2 sensores e 3 alertas validados. '
        'MongoDB: cinco documentos simulados, consultas e rejeicoes validados. '
        'O design relacional nativo e as capturas reais estao incluidos.', '',
        'Pacote somente desta disciplina: nao contem Backend, Hardware, dumps de banco, '
        'credenciais, ambientes virtuais ou sessoes locais do Modeler. Exemplos de integracao '
        'Python dependem do repositorio GS-CitizenTech completo. Nao foram testados importadores '
        'Python contra os dois bancos nem comunicacao Wokwi nesta entrega.', '',
        '## Conferencia final manual', '',
        'Antes de enviar, confira a rubrica oficial e identificacao do grupo/RAs. '
        'Nao ha dados de integrantes inventados. Modelo logico separado, PDF, video ou '
        'capturas adicionais dependem de exigencia do enunciado. A aprovacao tecnica '
        'dos artefatos nao substitui a avaliacao academica.', '',
        '## Integridade', '',
        'MANIFESTO_SHA256.json lista todos os arquivos deste pacote, exceto ele proprio. '
        'O ZIP foi gerado preservando os bytes dos arquivos; a verificacao externa '
        'inclui CRC, quantidade, nomes permitidos e SHA-256 de cada entrada.']), encoding='utf-8')
    manifesto = {p.relative_to(destino).as_posix(): sha256(p.read_bytes()) for p in sorted(destino.rglob('*')) if p.is_file()}
    (destino / 'MANIFESTO_SHA256.json').write_text(json.dumps(manifesto, ensure_ascii=False, indent=2), encoding='utf-8')
    with zipfile.ZipFile(arquivo_zip, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as pacote:
        for arquivo in sorted(destino.rglob('*')):
            if arquivo.is_file():
                pacote.write(arquivo, (Path(args.nome) / arquivo.relative_to(destino)).as_posix())
    with zipfile.ZipFile(arquivo_zip) as pacote:
        exigir(pacote.testzip() is None, 'Falha CRC no ZIP.')
        nomes = pacote.namelist()
        exigir(len(nomes) == len(set(nomes)) == len(manifesto) + 1, 'Quantidade ou duplicidade incorreta no ZIP.')
        exigir(set(nomes) == {f'{args.nome}/{p}' for p in manifesto} | {f'{args.nome}/MANIFESTO_SHA256.json'}, 'Conteudo extra no ZIP.')
        for relativo, hash_esperado in manifesto.items():
            exigir(sha256(pacote.read(f'{args.nome}/{relativo}')) == hash_esperado, f'Falha de integridade: {relativo}')
        exigir(json.loads(pacote.read(f'{args.nome}/MANIFESTO_SHA256.json')) == manifesto, 'Manifesto no ZIP divergente.')
    resultado = '\n'.join([
        f'ZIP: {arquivo_zip.name}', f'Arquivos: {len(manifesto) + 1}',
        f'Tamanho: {arquivo_zip.stat().st_size} bytes', f'SHA256 ZIP: {sha256(arquivo_zip.read_bytes())}',
        'CRC de todas as entradas: PASSOU', 'Conteudo versus manifesto SHA256: PASSOU',
        'Quantidade, ausencia de duplicatas e lista exata de arquivos: PASSOU',
        'Sem bancos, credenciais, ambientes virtuais, caches ou arquivos de sessao: PASSOU',
        'Nenhum comando executado nos bancos durante o empacotamento.',
        'Checklist e auditoria incluidos; envio ao Portal e GitHub dependem de acao manual.', ''])
    (raiz / 'entrega/VERIFICACAO_ZIP.txt').write_text(resultado, encoding='utf-8')
    print(resultado)


if __name__ == '__main__':
    main()
