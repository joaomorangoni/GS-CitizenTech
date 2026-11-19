# Checklist final — Cognitive Data Science, GS 2026.2

## Concluído

- [x] Oracle: criação, dados fictícios, três consultas JOIN e testes PK/FK/CHECK.
- [x] Oracle validado no banco real: 1 bueiro, 1 dispositivo, 2 sensores, 3 alertas.
- [x] MongoDB: coleção com validator/índices, cinco documentos simulados, inserção,
  histórico, alertas, estatísticas, intervalo temporal e testes de validação.
- [x] Evidências reais de Oracle e MongoDB, incluindo rejeições e reinserção MongoDB.
- [x] ER Mermaid com quatro entidades, PKs/FKs e relações não identificadoras 1:N.
- [x] Design nativo Data Modeler: `.dmd` com toda a pasta associada, quatro tabelas,
  16 colunas e três FKs. Comparação com o banco real aprovada.
- [x] Capturas reais do Data Modeler: importação sem falhas e diagrama completo.
- [x] Dicionário de dados, hipóteses de cadastro e justificativa Oracle/MongoDB.
- [x] Exemplos de integração que preservam o PostgreSQL operacional existente.
- [x] Auditoria e empacotamento sem executar comandos nos bancos existentes.
- [x] Exclusão de ambientes virtuais, caches, Git interno, arquivos `.env`,
  credenciais DPAPI, bancos locais e sessões `.local/.localz` do pacote.

O empacotador gera um manifesto SHA-256, audita nomes/conteúdo, verifica os CRCs
do ZIP e compara cada arquivo compactado ao manifesto. O resultado efetivo fica
em `entrega/VERIFICACAO_ZIP.txt`, fora do ZIP, e a auditoria fica dentro da pasta.

## Ação manual antes de enviar

- [ ] Conferir a rubrica oficial: enunciado completo, formato, tamanho máximo,
  prazo, identificação do grupo, RAs/turma, vídeo e eventual link do GitHub não
  foram fornecidos. Não foram inventados dados de integrantes.
- [ ] Se a rubrica exigir um modelo lógico separado do relacional, criá-lo e
  validá-lo no Data Modeler; o modelo lógico nativo atual está vazio.
- [ ] Se a rubrica exigir PNG/PDF exportado pelo aplicativo além da captura,
  exportá-lo; o pacote inclui Mermaid, design nativo e captura real legível.
- [ ] Se forem obrigatórias capturas gráficas MongoDB ou vídeo, produzi-los com
  os comandos documentados. As evidências MongoDB atuais são saídas textuais reais.
- [ ] Revisar e publicar as fontes no GitHub se solicitado pela FIAP; nenhum
  add, commit ou push é executado pelo empacotamento.
- [ ] Enviar o ZIP indicado no LEIA-ME da entrega ao Portal do Aluno e guardar
  o comprovante de submissão. Não enviar senhas junto com o trabalho.

## Dependências declaradas

O pacote contém somente a disciplina DataScience. Scripts Oracle/MongoDB e
o design são independentes de Backend/Hardware; dados de exemplo são sintéticos.
Os testes Python de contrato importam `Backend/`, portanto devem ser executados
no repositório completo, conforme README. Testes de integração via PyMongo e
python-oracledb e comunicação real Wokwi não foram executados. Isso não invalida
os testes reais de SQL/mongosh, mas não deve ser apresentado como integração
automática de produção já comprovada.

Metadados originais de evidências e do Modeler podem identificar o nome local da
conta Windows (`jaovi`), caminhos de arquivos e horários. Foram preservados para
não adulterar evidências; não são senhas nem credenciais de acesso. Não há dados
de cidadãos, medições reais de campo ou identificação de integrantes inventada.

## GitHub

Versionar a pasta `DataScience/` inteira respeitando seus `.gitignore`, incluindo
scripts, JSON fictício, documentação, evidências, `.dmd` e todos os XMLs associados.
Versionar também `entrega/.gitignore` para ignorar os pacotes derivados.
A alteração preexistente no `README.md` da raiz é independente e deve ser revisada
por você antes de adicioná-la. O ZIP e sua cópia expandida ficam ignorados em
`entrega/`; não precisam ser duplicados no GitHub.
