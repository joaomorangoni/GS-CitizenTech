# Roteiro de demonstração funcional

**CitizenTech — Global Solution 2026.2**

**Integrantes:**

- João Pedro Morangoni — RM 570073
- João Vitor Xavier de Carvalho — RM 570633

- Jo?o Pedro Morangoni ? RM 570073
- Jo?o Vitor Xavier de Carvalho ? RM 570633

O enunciado inclui demonstração funcional em vídeo no critério de avaliação.
Este arquivo prepara a gravação; nenhum vídeo foi gravado ou submetido automaticamente.
Sugestão de duração: 4 a 6 minutos, ajustável às orientações do professor.

## 1. Problema e contexto — aproximadamente 40 segundos

Apresente o grupo e o monitoramento urbano de bueiros do repositório. Explique que
a rede demonstra um módulo complementar de qualidade do ar em superfície.
Mostre a capa e a seção 1 do notebook. Declare que os dados não permitem inferir
alagamentos ou segurança em espaços confinados.

## 2. Dados e preparação — aproximadamente 50 segundos

Mostre `IA/dataset/AirQualityUCI.csv`, a fonte UCI e os exemplos carregados.
Explique a entrada com oito medições, o CO de referência como alvo e o tratamento
de `-200`. Mostre a tabela de divisão cronológica: treino, validação e teste.
Explique que medianas e escalas são aprendidas apenas no treino.

## 3. Rede e refinamento — aproximadamente 60 segundos

Mostre a MLP, ReLU, saída linear, Adam, L2 e os parâmetros das quatro configurações.
Apresente a tabela comparativa de validação, a melhor época e os gráficos de perda
e RMSE. Explique o early stopping cronológico e a preservação do melhor checkpoint.
Leia os valores reais exibidos no notebook; não apresente melhoria de treino como
prova de melhoria no teste.

## 4. Avaliação — aproximadamente 50 segundos

Mostre MAE, RMSE e R² no teste, comparando a rede com a média e a Ridge.
Explique as unidades em mg/m³ e o significado de ganho negativo, caso exista.
Mostre resíduos, série temporal e desempenho na faixa de maior concentração.
Comente a diferença entre validação e teste e as limitações de generalização.

## 5. Demonstração executável — aproximadamente 60 segundos

Execute a célula da seção 8 com o modelo salvo. Mostre os cinco exemplos do teste,
suas oito entradas, o CO estimado e o valor de referência. Explique que o valor de
referência só aparece para conferir o resultado, sem entrar na função de inferência.
Mostre a mensagem de recusa para uma leitura totalmente ausente.
Os exemplos já executados estão em `rede_neural/artefatos/demonstracao.csv`.

## 6. Integração e conclusão — aproximadamente 40 segundos

Mostre o pacote do modelo e descreva o futuro fluxo de estação ambiental compatível
em superfície → médias horárias → inferência → painel territorial.
Declare que o backend e o ESP32 atuais não fornecem os sensores químicos do dataset
e que a integração apresentada é uma simulação funcional independente.
Conclua com validação local, monitoramento de deriva e acessibilidade do painel.

## Antes de entregar

- Conferir os nomes e RMs informados nos materiais.
- Conferir que o notebook abre com gráficos e saídas preservados.
- Mostrar entradas e saídas legíveis no vídeo, com narração ou legendas claras.
- Conferir acesso ao arquivo/link de vídeo conforme o canal de entrega da disciplina.
- Incluir o vídeo junto aos demais materiais. O repositório não contém o vídeo.
