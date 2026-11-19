# Auditoria final da entrega — CitizenTech

Escopo: artefatos de Cognitive Data Science. Nenhuma consulta, insercao, DDL ou teste foi executado contra bancos existentes durante o empacotamento. Evidencias reais anteriores foram auditadas.

- PASSOU: cinco SQL Oracle e quatro scripts MongoDB, alem da fixture ficticia e auxiliares.
- PASSOU: 15 verificacoes Oracle com base nas evidencias reais; resultados e SQL consistentes.
- PASSOU: design nativo com 32 XMLs, quatro tabelas, 16 colunas, tres FKs e dominios dependentes presentes.
- PASSOU: Mermaid corresponde aos campos e relacionamentos do modelo relacional; linhas nao identificadoras corrigidas.
- PASSOU: evidencias reais MongoDB, cinco documentos, codigos 121/11000 e reinsercao sem duplicacao.
- PASSOU: justificativa dos dois bancos, hipoteses, dicionario e limites documentados.
- PASSOU: quatro testes de contrato executados nesta preparacao; SQLite somente temporario.
- PASSOU: nenhum padrao de segredo ou URL autenticada detectado nos arquivos selecionados. Credencial Oracle local comparada sem revelar o valor.
- PASSOU: Backend e Hardware sem diff; nenhum push, commit ou staging realizado.

## Integridade do pacote

O manifesto SHA-256 cobre todos os arquivos, exceto o proprio manifesto. O empacotador verifica os CRCs do ZIP e cada conteudo compactado, preservando bytes das evidencias. O resultado final dessa verificacao fica em entrega/VERIFICACAO_ZIP.txt.

## Limites e acoes manuais

Rubrica oficial nao fornecida: conferir identificacao de integrantes/RAs, formato, limite de arquivo, modelo logico separado, PDF, capturas adicionais, video e link GitHub. O modelo logico nativo esta vazio; o relacional esta completo. O ZIP somente DataScience nao inclui Backend/Hardware; testes Python e exemplos com API exigem o repositorio completo. Metadados originais de autoria/caminhos locais e horarios foram preservados, sem segredos. Nao foram inventados nomes de integrantes nem capturas.

## Git no momento da auditoria

```text
 M README.md
?? DataScience/
?? entrega/
```

Enviar ao GitHub DataScience/ inteira respeitando .gitignore e entrega/.gitignore. A modificacao preexistente no README.md da raiz deve ser revisada separadamente. ZIP e pasta expandida sao derivados ignorados; submissao ao Portal e push sao manuais.

## Arquivos locais excluidos

- `__pycache__/__init__.cpython-314.pyc`
- `__pycache__/integracao.cpython-314.pyc`
- `diagramas/citizentech/ChangeRequests.local`
- `diagramas/citizentech/businessinfo/Objects.local`
- `diagramas/citizentech/datatypes/DDLSelection.local`
- `diagramas/citizentech/datatypes/Diagrams.local`
- `diagramas/citizentech/datatypes/Objects.local`
- `diagramas/citizentech/logical/Diagrams.local`
- `diagramas/citizentech/logical/Objects.local`
- `diagramas/citizentech/pm/Objects.local`
- `diagramas/citizentech/rel/CAF918AD-AB2EB6DDDE7B/DDLSelection.local`
- `diagramas/citizentech/rel/CAF918AD-AB2EB6DDDE7B/Diagrams.local`
- `diagramas/citizentech/rel/CAF918AD-AB2EB6DDDE7B/Objects.local`
- `diagramas/citizentech/rel/CAF918AD-AB2EB6DDDE7B/phys/01F6E6D1-3988D1813575/DDLSelection.local`
- `diagramas/citizentech/rel/CAF918AD-AB2EB6DDDE7B/phys/01F6E6D1-3988D1813575/Objects.local`
- `testes/__pycache__/test_datascience.cpython-314.pyc`
