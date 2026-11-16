"""API Flask. Execute a partir da raiz: python -m Backend.app."""

import os
import sqlite3
from pathlib import Path

from flask import Flask, jsonify, request
from werkzeug.exceptions import HTTPException

from . import armazenamento
from .monitoramento import apresentar_leitura, processar_leitura
from .validacoes import DadosInvalidos, validar_leitura


def create_app(config=None):
    app = Flask(__name__)
    app.config.from_mapping(
        DATABASE=os.environ.get("BUEIRO_DATABASE", str(Path(__file__).parent / "dados" / "leituras.sqlite3")),
        MAX_CONTENT_LENGTH=16 * 1024,
    )
    if config:
        app.config.update(config)
    app.json.ensure_ascii = False
    armazenamento.inicializar(app.config["DATABASE"])

    @app.errorhandler(DadosInvalidos)
    def erro_validacao(erro):
        return jsonify(erro=str(erro), campos=erro.erros), 400

    @app.errorhandler(HTTPException)
    def erro_http(erro):
        return jsonify(erro=erro.name, mensagem=erro.description), erro.code

    @app.errorhandler(sqlite3.Error)
    def erro_banco(erro):
        app.logger.exception("Falha no armazenamento SQLite")
        return jsonify(erro="Armazenamento temporariamente indisponível."), 503

    @app.get("/health")
    def health():
        return jsonify(status="ok")

    @app.post("/api/leituras")
    def receber():
        dados = validar_leitura(request.get_json())
        registro = armazenamento.salvar(app.config["DATABASE"], processar_leitura(dados))
        return jsonify(apresentar_leitura(registro)), 201

    @app.get("/api/leituras")
    def historico():
        try:
            limite = int(request.args.get("limite", "100"))
            offset = int(request.args.get("offset", "0"))
            if not 1 <= limite <= 1000 or offset < 0:
                raise ValueError
        except ValueError:
            raise DadosInvalidos({"paginacao": "limite deve estar entre 1 e 1000; offset deve ser >= 0."})
        leituras = armazenamento.consultar(app.config["DATABASE"], limite, offset)
        return jsonify(leituras=[apresentar_leitura(l) for l in leituras], limite=limite, offset=offset)

    @app.get("/api/status")
    def status():
        leituras = armazenamento.consultar(app.config["DATABASE"], 1)
        return jsonify(ultima_leitura=apresentar_leitura(leituras[0]) if leituras else None,
                       mensagem="Última leitura recebida; confira recebido_em para avaliar sua atualidade."
                       if leituras else "Nenhuma leitura recebida.")

    @app.get("/api/resumo")
    def resumo():
        return jsonify(armazenamento.resumir(app.config["DATABASE"]))

    return app


if __name__ == "__main__":
    create_app().run(host=os.environ.get("BUEIRO_HOST", "127.0.0.1"), port=5000, debug=False)
