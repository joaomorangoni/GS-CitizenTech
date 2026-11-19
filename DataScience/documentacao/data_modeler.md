# Reprodução no Oracle SQL Developer Data Modeler

## Instalação encontrada neste computador

Em 17/11/2026 foi localizada a distribuição 24.3.1 já extraída em
`%USERPROFILE%\Downloads\datamodeler-24.3.1.351.0831-x64\datamodeler`.
O Java incluído respondeu à verificação de versão: 17.0.13. Não foi necessário
instalar outro Java nem reinstalar o aplicativo. Seu executável foi iniciado:
`datamodeler\bin\datamodeler64W.exe` dentro dessa distribuição.
O aplicativo foi aberto e a importação do DDL foi executada na interface gráfica.

O arquivo a selecionar em **File > Import > DDL File** é
`C:\Users\jaovi\Desktop\gs citizen\GS-CitizenTech\DataScience\oracle\01_criacao.sql`.
O design foi salvo em `DataScience/diagramas/citizentech.dmd`, com sua pasta
associada `citizentech/`. O log registrou sete instruções importadas e zero
falhas; a mesclagem gerou quatro tabelas e três FKs. O dialeto selecionado foi
Oracle Database 21c, disponível nessa versão do Modeler. O mesmo DDL foi
executado com sucesso no servidor local Oracle 26ai Free 23.26.3.0.0.
O identity GENERATED ALWAYS de ALERTA foi preservado nos XMLs nativos.

Capturas reais, sem recriação artificial, em `documentacao/evidencias/`:
`data_modeler_importacao.png` e `data_modeler_diagrama.png`. Para reabrir,
use **File > Open** em `citizentech.dmd`; mantenha a pasta associada junto dele.
O arquivo lógico incluído no design permanece vazio: o modelo validado é o
relacional, equivalente ao ER Mermaid. A engenharia de modelo lógico é opcional.
Os parâmetros para conexão ao banco local estão em `oracle_local.md`.

## Procedimento de importação

1. Instale o Oracle SQL Developer Data Modeler standalone e o Java exigido pela
   distribuição escolhida. Consulte a página oficial de download para os requisitos
   da sua versão. A importação do arquivo DDL dispensa conexão a banco.
2. Abra **File > Import > DDL File** (na interface integrada ao SQL Developer,
   procure **File > Data Modeler > Import > DDL File**).
3. Adicione `DataScience/oracle/01_criacao.sql`, selecione Oracle como dialeto e
   uma versão 19c ou superior. Importe as quatro tabelas e relacionamentos.
4. Abra o modelo relacional criado. Organize BUEIRO, DISPOSITIVO e os filhos
   SENSOR e ALERTA. Confira as três FKs, PKs, campos opcionais, identity de ALERTA,
   unicidade composta de origem/leitura e CHECKs. Compare com `modelo_er.mmd`.
5. Se desejar modelo lógico, use **Engineer to Logical Model** no modelo relacional
   e revise as cardinalidades: pai 1, filho 0..N, FK obrigatória no filho.
6. Salve o design `.dmd` e sua pasta associada. Exporte o diagrama pelo comando
   de impressão/exportação **To Image File** disponível na versão instalada.
   Gere PNG/PDF e mantenha as quatro entidades, atributos e linhas legíveis.
7. Gere DDL pelo modelo físico Oracle e compare-o ao script de criação antes de
   executar. Não execute o DDL gerado por cima das mesmas tabelas existentes.

O Mermaid é representação textual, não um arquivo nativo do Data Modeler.
Foram produzidas capturas reais da importação e do modelo relacional nesta entrega.

Fonte: [Oracle — Data Modeler Concepts and Usage](https://docs.oracle.com/en/database/oracle/sql-developer-data-modeler/24.3/dmdug/data-modeler-concepts-usage.html).
