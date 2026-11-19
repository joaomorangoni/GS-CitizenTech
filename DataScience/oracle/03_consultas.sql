-- Inventario: esperado na amostra, 2 sensores fisicos (DHT22 mede duas grandezas).
SELECT b.bueiro_id, b.descricao, d.dispositivo_id, s.sensor_id, s.modelo
FROM BUEIRO b JOIN DISPOSITIVO d ON d.bueiro_id = b.bueiro_id
JOIN SENSOR s ON s.dispositivo_id = d.dispositivo_id
ORDER BY b.bueiro_id, d.dispositivo_id, s.sensor_id;
-- Rastreabilidade: origem_api + leitura_api_id corresponde a origem_api + leitura.id no MongoDB.
SELECT b.bueiro_id, d.dispositivo_id, a.origem_api, a.leitura_api_id,
       a.recebido_em, a.risco_python, a.mensagem
FROM ALERTA a JOIN DISPOSITIVO d ON d.dispositivo_id = a.dispositivo_id
JOIN BUEIRO b ON b.bueiro_id = d.bueiro_id
ORDER BY a.recebido_em, a.leitura_api_id;
-- Inclui bueiros sem alertas; nao juntar sensores aqui (multiplicaria contagens).
SELECT b.bueiro_id, COUNT(a.alerta_id) AS ocorrencias
FROM BUEIRO b LEFT JOIN DISPOSITIVO d ON d.bueiro_id = b.bueiro_id
LEFT JOIN ALERTA a ON a.dispositivo_id = d.dispositivo_id
GROUP BY b.bueiro_id ORDER BY b.bueiro_id;
