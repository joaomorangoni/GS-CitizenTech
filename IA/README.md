# IA — CitizenTech

Estimativa da concentração horária de CO com uma rede neural MLP, usando o arquivo
local `dataset/AirQualityUCI.csv`. O notebook contém explicações em Markdown,
preparação dos dados, treinamento, comparação de configurações, avaliação e demonstração.

| Caminho | Conteúdo |
| --- | --- |
| [rede_neural/qualidade_ar_mlp.ipynb](rede_neural/qualidade_ar_mlp.ipynb) | Notebook principal, com saídas da execução |
| [rede_neural/inferencia.py](rede_neural/inferencia.py) | Função para carregar o pacote e estimar CO |
| `rede_neural/artefatos/` | Modelo, métricas, históricos e exemplos exportados |
| [documentacao/README.md](documentacao/README.md) | Relatório técnico e resultados |
| [documentacao/roteiro_video.md](documentacao/roteiro_video.md) | Roteiro da demonstração solicitada no enunciado |
| `documentacao/figuras/` | Gráficos produzidos pelo notebook |

## Como executar

No PowerShell, a partir da raiz `GS-CitizenTech`:

```powershell
python -m venv IA/.venv
IA/.venv/Scripts/python.exe -m pip install -r IA/requirements.txt
IA/.venv/Scripts/python.exe IA/executar_notebook.py
```

O último comando executa o notebook completo, atualiza suas saídas e exporta os
artefatos. No VS Code, também é possível abrir o `.ipynb`, selecionar o interpretador
de `IA/.venv` e usar **Executar Tudo**. O notebook localiza o dataset a partir da raiz
do repositório, de `IA` ou de `IA/rede_neural`; não baixa dados durante a execução.

Dependências em `requirements.txt` usam intervalos de compatibilidade. Para repetir
as versões exatas usadas na entrega, em um ambiente compatível, instale
`IA/rede_neural/artefatos/versoes_executadas.txt`. Python e o hash do dataset ficam
registrados em `resumo_execucao.json`. Resultados podem variar entre versões de
Python, bibliotecas e implementações numéricas, apesar da semente fixa.

`gerar_notebook.py` é o gerador da estrutura original. Ele sobrescreve o notebook e
remove as saídas existentes; **não é necessário para executar ou usar a entrega**.
Depois de alterar células diretamente, preserve o `.ipynb` como fonte principal.

## Usar a inferência sem treinar novamente

Em um kernel/terminal com as dependências instaladas, a partir da raiz do repositório:

```python
from IA.rede_neural.inferencia import estimar_co

leituras = [{
    "PT08.S1(CO)": 1360, "PT08.S2(NMHC)": 1046,
    "PT08.S3(NOx)": 1056, "PT08.S4(NO2)": 1692,
    "PT08.S5(O3)": 1268, "T": 13.6, "RH": 48.9, "AH": 0.7578,
}]
print(estimar_co(leituras))
```

Esse exemplo ilustra o contrato e usa uma linha conhecida do CSV; a evidência com
amostras não usadas no treino está na seção 8 do notebook e em `demonstracao.csv`.
Use o pacote `modelo_co.joblib` produzido por este projeto e versões compatíveis.
Campos ausentes, `None`, `NaN` e `-200` são tratados pelo pré-processador do treino;
uma linha totalmente ausente, campos desconhecidos, infinito ou texto não numérico
são recusados. A função não detecta todas as medições fisicamente inválidas e não
produz intervalo de confiança, classificação sanitária nem previsão de alagamento.

## Itens que dependem do grupo

- Conferir os nomes e RMs informados nos materiais.
- Confirmar a aderência do módulo de qualidade do ar ao problema interdisciplinar
  de monitoramento de bueiros. O dataset não contém variáveis de alagamento.
- Gravar e entregar o vídeo exigido pelo critério de avaliação, seguindo o roteiro.
  O roteiro não substitui o vídeo.

Nenhum arquivo de Backend ou Hardware foi alterado para simular uma integração inexistente.
