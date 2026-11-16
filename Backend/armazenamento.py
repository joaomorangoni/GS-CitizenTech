"""Persistência SQLite com conexão por operação e consultas parametrizadas."""

import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

from .config import RISCOS


@contextmanager
def conectar(caminho):
    conexao = sqlite3.connect(caminho, timeout=5)
    conexao.row_factory = sqlite3.Row
    try:
        with conexao:
            yield conexao
    finally:
        conexao.close()


def inicializar(caminho):
    Path(caminho).parent.mkdir(parents=True, exist_ok=True)
    with conectar(caminho) as conexao:
        conexao.execute("""CREATE TABLE IF NOT EXISTS leituras (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            distancia_cm REAL, temperatura_c REAL, umidade_relativa REAL,
            risco_esp32 TEXT NOT NULL, risco_python TEXT NOT NULL,
            tempo_ms INTEGER NOT NULL, recebido_em TEXT NOT NULL
        )""")


def salvar(caminho, leitura):
    registro = dict(leitura, recebido_em=datetime.now(timezone.utc).isoformat())
    with conectar(caminho) as conexao:
        cursor = conexao.execute("""INSERT INTO leituras
            (distancia_cm, temperatura_c, umidade_relativa, risco_esp32,
             risco_python, tempo_ms, recebido_em)
            VALUES (:distancia_cm, :temperatura_c, :umidade_relativa, :risco_esp32,
                    :risco_python, :tempo_ms, :recebido_em)""", registro)
        registro["id"] = cursor.lastrowid
    return registro


def consultar(caminho, limite=100, offset=0):
    with conectar(caminho) as conexao:
        return [dict(linha) for linha in conexao.execute(
            "SELECT * FROM leituras ORDER BY id DESC LIMIT ? OFFSET ?", (limite, offset))]


def resumir(caminho):
    contagens = dict.fromkeys(RISCOS, 0)
    with conectar(caminho) as conexao:
        for linha in conexao.execute("SELECT risco_python, COUNT(*) AS total FROM leituras GROUP BY risco_python"):
            contagens[linha["risco_python"]] = linha["total"]
        medias = dict(conexao.execute("""SELECT AVG(distancia_cm) AS distancia_cm,
            AVG(temperatura_c) AS temperatura_c, AVG(umidade_relativa) AS umidade_relativa
            FROM leituras""").fetchone())
        divergencias = conexao.execute(
            "SELECT COUNT(*) FROM leituras WHERE risco_esp32 != risco_python").fetchone()[0]
    return {"total_leituras": sum(contagens.values()), "por_risco": contagens,
            "medias": medias, "riscos_divergentes": divergencias}
