-- Leitura somente. Parametro &1: ANTES ou DEPOIS dos testes.
SET HEADING OFF FEEDBACK OFF PAGESIZE 0 LINESIZE 32767 LONG 1000000 LONGCHUNKSIZE 32767 TRIMSPOOL ON
SELECT 'DADOS|&1|BUEIRO|' || JSON_ARRAYAGG(JSON_OBJECT(*) ORDER BY bueiro_id RETURNING CLOB) FROM BUEIRO;
SELECT 'DADOS|&1|DISPOSITIVO|' || JSON_ARRAYAGG(JSON_OBJECT(*) ORDER BY dispositivo_id RETURNING CLOB) FROM DISPOSITIVO;
SELECT 'DADOS|&1|SENSOR|' || JSON_ARRAYAGG(JSON_OBJECT(*) ORDER BY sensor_id RETURNING CLOB) FROM SENSOR;
SELECT 'DADOS|&1|ALERTA|' || JSON_ARRAYAGG(JSON_OBJECT(*) ORDER BY alerta_id RETURNING CLOB) FROM ALERTA;
SELECT 'COLUNA|' || JSON_OBJECT('tabela' VALUE table_name, 'coluna' VALUE column_name,
  'posicao' VALUE column_id, 'tipo' VALUE data_type, 'precisao' VALUE data_precision,
  'escala' VALUE data_scale, 'tamanho' VALUE char_length, 'semantica' VALUE char_used,
  'nulo' VALUE nullable, 'identity' VALUE identity_column)
FROM user_tab_columns WHERE table_name IN ('BUEIRO','DISPOSITIVO','SENSOR','ALERTA')
ORDER BY table_name, column_id;
SELECT 'CHAVE|' || JSON_OBJECT('tabela' VALUE c.table_name, 'nome' VALUE c.constraint_name,
  'tipo' VALUE c.constraint_type, 'coluna' VALUE cc.column_name, 'posicao' VALUE cc.position,
  'pai' VALUE pc.table_name, 'coluna_pai' VALUE pcc.column_name,
  'exclusao' VALUE c.delete_rule, 'estado' VALUE c.status)
FROM user_constraints c JOIN user_cons_columns cc ON cc.constraint_name = c.constraint_name
LEFT JOIN user_constraints pc ON pc.constraint_name = c.r_constraint_name
LEFT JOIN user_cons_columns pcc ON pcc.constraint_name = pc.constraint_name AND pcc.position = cc.position
WHERE c.table_name IN ('BUEIRO','DISPOSITIVO','SENSOR','ALERTA') AND c.constraint_type IN ('P','U','R')
ORDER BY c.table_name, c.constraint_name, cc.position;
SELECT 'CHECK|' || JSON_OBJECT('tabela' VALUE table_name, 'nome' VALUE constraint_name,
  'regra' VALUE search_condition_vc, 'estado' VALUE status)
FROM user_constraints WHERE table_name IN ('BUEIRO','DISPOSITIVO','SENSOR','ALERTA')
AND constraint_type = 'C' AND constraint_name LIKE 'CK_%' ORDER BY constraint_name;
SELECT 'IDENTITY|' || JSON_OBJECT('tabela' VALUE table_name, 'coluna' VALUE column_name,
  'geracao' VALUE generation_type) FROM user_tab_identity_cols
WHERE table_name IN ('BUEIRO','DISPOSITIVO','SENSOR','ALERTA');
