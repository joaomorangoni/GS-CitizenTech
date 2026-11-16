"""Processamento das medições, preservando os critérios do ESP32."""

from .alertas import gerar_alerta
from .config import DISTANCIA_ATENCAO_CM, DISTANCIA_CRITICA_CM, UMIDADE_ALTA_PERCENT


def processar_distancia(distancia):
    if distancia is None:
        return "SEM_LEITURA"
    if distancia <= DISTANCIA_CRITICA_CM:
        return "CRITICA"
    if distancia <= DISTANCIA_ATENCAO_CM:
        return "CURTA"
    return "ACIMA_DO_LIMITE_DE_ATENCAO"


def analisar_ambiente(temperatura, umidade):
    return {
        "temperatura_disponivel": temperatura is not None,
        "umidade_elevada": None if umidade is None else umidade >= UMIDADE_ALTA_PERCENT,
    }


def classificar_risco(distancia, umidade):
    """Recebe valores previamente validados; temperatura não determina o risco."""
    if distancia is None or umidade is None:
        return "DADOS_INVALIDOS"
    if distancia <= DISTANCIA_CRITICA_CM and umidade >= UMIDADE_ALTA_PERCENT:
        return "RISCO_ALTO"
    if distancia <= DISTANCIA_ATENCAO_CM or umidade >= UMIDADE_ALTA_PERCENT:
        return "ATENCAO"
    return "SEM_RISCO_DETECTADO"


def processar_leitura(dados):
    risco = classificar_risco(dados["distancia_cm"], dados["umidade_relativa"])
    return {
        "distancia_cm": dados["distancia_cm"],
        "temperatura_c": dados["temperatura_c"],
        "umidade_relativa": dados["umidade_relativa"],
        "risco_esp32": dados["risco"],
        "risco_python": risco,
        "tempo_ms": dados["tempo_ms"],
    }


def apresentar_leitura(leitura):
    resultado = dict(leitura)
    resultado.update(
        alerta=gerar_alerta(leitura["risco_python"]),
        risco_divergente=leitura["risco_esp32"] != leitura["risco_python"],
        sensores_sem_leitura=[campo for campo in ("distancia_cm", "temperatura_c", "umidade_relativa")
                             if leitura[campo] is None],
        analise_distancia=processar_distancia(leitura["distancia_cm"]),
        ambiente=analisar_ambiente(leitura["temperatura_c"], leitura["umidade_relativa"]),
    )
    return resultado
