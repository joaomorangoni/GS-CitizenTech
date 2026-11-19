-- Dados ficticios; executar uma vez apos 01_criacao.sql.
INSERT INTO BUEIRO VALUES (1, 'Bueiro simulado CitizenTech', NULL);
INSERT INTO DISPOSITIVO VALUES (1, 1, 'ESP32 simulado Wokwi');
INSERT INTO SENSOR VALUES (1, 1, 'HC-SR04');
INSERT INTO SENSOR VALUES (2, 1, 'DHT22');
INSERT INTO ALERTA (dispositivo_id, origem_api, leitura_api_id, recebido_em, risco_python, mensagem)
VALUES (1, 'simulacao-v1', 2, TO_TIMESTAMP_TZ('2026-11-17T12:00:05+00:00', 'YYYY-MM-DD"T"HH24:MI:SSTZH:TZM'),
 'ATENCAO', 'Atenção: distância curta ou umidade elevada. Verifique as condições do bueiro.');
INSERT INTO ALERTA (dispositivo_id, origem_api, leitura_api_id, recebido_em, risco_python, mensagem)
VALUES (1, 'simulacao-v1', 3, TO_TIMESTAMP_TZ('2026-11-17T12:00:10+00:00', 'YYYY-MM-DD"T"HH24:MI:SSTZH:TZM'),
 'RISCO_ALTO', 'Alerta: distância crítica e umidade elevada. Solicite avaliação do local e evite áreas alagadas.');
INSERT INTO ALERTA (dispositivo_id, origem_api, leitura_api_id, recebido_em, risco_python, mensagem)
VALUES (1, 'simulacao-v1', 4, TO_TIMESTAMP_TZ('2026-11-17T12:00:15+00:00', 'YYYY-MM-DD"T"HH24:MI:SSTZH:TZM'),
 'DADOS_INVALIDOS', 'Falha de leitura: verifique o sensor de distância ou umidade.');
COMMIT;
