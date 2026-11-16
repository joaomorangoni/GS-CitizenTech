"""Validação do contrato JSON; null de sensor representa falha de leitura."""

import math

from .config import RISCOS, TEMPERATURA_MAX_C, TEMPERATURA_MIN_C


class DadosInvalidos(ValueError):
    """Erros de entrada que podem ser apresentados ao cliente."""

    def __init__(self, erros):
        self.erros = erros
        super().__init__("Dados recebidos inválidos.")


def validar_leitura(dados):
    if not isinstance(dados, dict):
        raise DadosInvalidos({"json": "Envie um objeto JSON."})
    erros = {}
    limites = {
        "distancia_cm": (0, None),
        "temperatura_c": (TEMPERATURA_MIN_C, TEMPERATURA_MAX_C),
        "umidade_relativa": (0, 100),
    }
    for campo, (minimo, maximo) in limites.items():
        if campo not in dados:
            erros[campo] = "Campo obrigatório; use null quando o sensor falhar."
            continue
        valor = dados[campo]
        if valor is None:
            continue
        if type(valor) not in (int, float):
            erros[campo] = "Informe um número ou null."
            continue
        try:
            finito = math.isfinite(valor)
        except OverflowError:
            finito = False
        if not finito or valor < minimo or (maximo is not None and valor > maximo):
            erros[campo] = "Valor fora da faixa permitida ou não finito."
    if not isinstance(dados.get("risco"), str) or dados["risco"] not in RISCOS:
        erros["risco"] = "Informe uma classificação válida do firmware."
    tempo = dados.get("tempo_ms")
    if type(tempo) is not int or not 0 <= tempo <= 4294967295:
        erros["tempo_ms"] = "Informe um inteiro entre 0 e 4294967295 (millis do ESP32)."
    if erros:
        raise DadosInvalidos(erros)
    return {campo: dados[campo] for campo in (*limites, "risco", "tempo_ms")}
