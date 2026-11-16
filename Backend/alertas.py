"""Mensagens informativas, sem promessa de previsão de enchentes."""

MENSAGENS = {
    "SEM_RISCO_DETECTADO": "Nenhum risco detectado pelos critérios atuais. Continue o monitoramento.",
    "ATENCAO": "Atenção: distância curta ou umidade elevada. Verifique as condições do bueiro.",
    "RISCO_ALTO": "Alerta: distância crítica e umidade elevada. Solicite avaliação do local e evite áreas alagadas.",
    "DADOS_INVALIDOS": "Falha de leitura: verifique o sensor de distância ou umidade.",
}


def gerar_alerta(risco):
    return MENSAGENS[risco]
