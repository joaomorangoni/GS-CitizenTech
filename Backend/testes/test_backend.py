import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from Backend.app import create_app
from Backend.monitoramento import classificar_risco


class TestMonitoramento(unittest.TestCase):
    def test_classificacoes_e_limites(self):
        casos = [(50, 50, "SEM_RISCO_DETECTADO"), (30, 50, "ATENCAO"),
                 (31, 80, "ATENCAO"), (10, 79, "ATENCAO"),
                 (10, 80, "RISCO_ALTO"), (0, 100, "RISCO_ALTO"),
                 (None, 80, "DADOS_INVALIDOS"), (10, None, "DADOS_INVALIDOS")]
        for distancia, umidade, esperado in casos:
            with self.subTest(distancia=distancia, umidade=umidade):
                self.assertEqual(classificar_risco(distancia, umidade), esperado)


class TestAPI(unittest.TestCase):
    def setUp(self):
        self.pasta = tempfile.TemporaryDirectory()
        self.addCleanup(self.pasta.cleanup)
        self.config = {"TESTING": True, "DATABASE": str(Path(self.pasta.name) / "teste.sqlite3")}
        self.app = create_app(self.config)
        self.client = self.app.test_client()
        self.dados = dict(distancia_cm=15.0, temperatura_c=27.0, umidade_relativa=85.0,
                          risco="ATENCAO", tempo_ms=5000)

    def enviar(self, **alteracoes):
        return self.client.post("/api/leituras", json=dict(self.dados, **alteracoes))

    def test_estado_inicial(self):
        self.assertEqual(self.client.get("/health").json, {"status": "ok"})
        self.assertIsNone(self.client.get("/api/status").json["ultima_leitura"])
        resumo = self.client.get("/api/resumo").json
        self.assertEqual(resumo["total_leituras"], 0)
        self.assertIsNone(resumo["medias"]["distancia_cm"])

    def test_recebimento_historico_persistencia_e_status(self):
        resposta = self.enviar()
        self.assertEqual(resposta.status_code, 201)
        leitura = resposta.json
        self.assertEqual(leitura["risco_python"], "ATENCAO")
        self.assertFalse(leitura["risco_divergente"])
        self.assertIn("+00:00", leitura["recebido_em"])
        self.assertEqual(leitura["tempo_ms"], 5000)
        outro_cliente = create_app(self.config).test_client()
        self.assertEqual(outro_cliente.get("/api/leituras").json["leituras"][0], leitura)
        self.assertEqual(outro_cliente.get("/api/status").json["ultima_leitura"], leitura)

    def test_risco_recalculado_alerta_e_resumo(self):
        self.enviar(distancia_cm=50, umidade_relativa=50, risco="SEM_RISCO_DETECTADO")
        self.enviar()
        resposta = self.enviar(distancia_cm=10, risco="SEM_RISCO_DETECTADO")
        self.assertEqual(resposta.json["risco_python"], "RISCO_ALTO")
        self.assertTrue(resposta.json["risco_divergente"])
        self.assertIn("Alerta", resposta.json["alerta"])
        resumo = self.client.get("/api/resumo").json
        self.assertEqual(resumo["total_leituras"], 3)
        self.assertEqual(resumo["por_risco"]["ATENCAO"], 1)
        self.assertEqual(resumo["por_risco"]["RISCO_ALTO"], 1)
        self.assertEqual(resumo["riscos_divergentes"], 1)
        self.assertEqual(resumo["medias"]["distancia_cm"], 25)

    def test_falhas_de_sensor_sao_registradas(self):
        resposta = self.enviar(distancia_cm=None, risco="DADOS_INVALIDOS")
        self.assertEqual(resposta.status_code, 201)
        self.assertEqual(resposta.json["risco_python"], "DADOS_INVALIDOS")
        self.assertEqual(resposta.json["sensores_sem_leitura"], ["distancia_cm"])
        resposta = self.enviar(temperatura_c=None)
        self.assertEqual(resposta.json["risco_python"], "ATENCAO")
        self.assertFalse(resposta.json["ambiente"]["temperatura_disponivel"])

    def test_valores_invalidos_nao_sao_armazenados(self):
        for campo, valor in [("distancia_cm", -1), ("distancia_cm", True),
                             ("distancia_cm", "15"), ("distancia_cm", float("inf")),
                             ("temperatura_c", float("nan")), ("temperatura_c", 81),
                             ("umidade_relativa", 101), ("umidade_relativa", -1),
                             ("risco", []), ("risco", None), ("risco", "ALTO"),
                             ("tempo_ms", None), ("tempo_ms", 1.2), ("tempo_ms", True),
                             ("tempo_ms", -1), ("tempo_ms", 4294967296)]:
            with self.subTest(campo=campo, valor=valor):
                self.assertEqual(self.enviar(**{campo: valor}).status_code, 400)
        self.assertEqual(self.client.get("/api/resumo").json["total_leituras"], 0)

    def test_campos_ausentes(self):
        for campo in self.dados:
            dados = self.dados.copy()
            del dados[campo]
            with self.subTest(campo=campo):
                self.assertEqual(self.client.post("/api/leituras", json=dados).status_code, 400)

    def test_json_e_erros_http(self):
        for corpo in ["{", "[]", "null", "42"]:
            self.assertEqual(self.client.post("/api/leituras", data=corpo,
                             content_type="application/json").status_code, 400)
        self.assertEqual(self.client.post("/api/leituras", data="texto").status_code, 415)
        self.assertEqual(self.client.post("/api/leituras", data="x" * 17000,
                         content_type="application/json").status_code, 413)
        self.assertEqual(self.client.get("/inexistente").status_code, 404)

    def test_paginacao(self):
        self.enviar(tempo_ms=100)
        self.enviar(tempo_ms=200)
        resposta = self.client.get("/api/leituras?limite=1&offset=1")
        self.assertEqual(resposta.json["leituras"][0]["tempo_ms"], 100)
        for query in ["limite=0", "limite=1001", "limite=abc", "offset=-1"]:
            self.assertEqual(self.client.get("/api/leituras?" + query).status_code, 400)

    def test_falha_banco_retorna_503_e_servidor_continua(self):
        with patch("Backend.armazenamento.salvar", side_effect=sqlite3.OperationalError("teste")):
            self.assertEqual(self.enviar().status_code, 503)
        self.assertEqual(self.enviar().status_code, 201)


if __name__ == "__main__":
    unittest.main()
