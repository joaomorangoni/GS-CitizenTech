-- Executar APOS 01, 02 e 03 no schema exclusivo da demonstracao.
-- SQL Developer: Run Script (F5). SQL*Plus/SQLcl: @04_verificacao.sql
-- Somente SELECTs e tentativas de INSERT com rollback a savepoint.
SET SERVEROUTPUT ON
WHENEVER SQLERROR EXIT SQL.SQLCODE ROLLBACK

DECLARE
    total NUMBER;
    PROCEDURE conferir(verdade BOOLEAN, mensagem VARCHAR2) IS
    BEGIN
        IF verdade IS NULL OR NOT verdade THEN
            RAISE_APPLICATION_ERROR(-20001, mensagem);
        END IF;
    END;
BEGIN
    SELECT COUNT(*) INTO total FROM user_tables
    WHERE table_name IN ('BUEIRO', 'DISPOSITIVO', 'SENSOR', 'ALERTA');
    conferir(total = 4, 'Esperadas quatro tabelas do projeto.');
    SELECT COUNT(*) INTO total FROM user_constraints
    WHERE table_name IN ('BUEIRO', 'DISPOSITIVO', 'SENSOR', 'ALERTA')
      AND constraint_type = 'R' AND status = 'ENABLED';
    conferir(total = 3, 'Esperadas tres FKs habilitadas.');
    SELECT COUNT(*) INTO total FROM BUEIRO WHERE bueiro_id = 1;
    conferir(total = 1, 'Cadastro simulado do bueiro ausente.');
    SELECT COUNT(*) INTO total FROM DISPOSITIVO WHERE dispositivo_id = 1 AND bueiro_id = 1;
    conferir(total = 1, 'Vinculo simulado dispositivo/bueiro ausente.');
    SELECT COUNT(*) INTO total FROM SENSOR WHERE dispositivo_id = 1
      AND ((sensor_id = 1 AND modelo = 'HC-SR04') OR (sensor_id = 2 AND modelo = 'DHT22'));
    conferir(total = 2, 'Esperados os dois sensores simulados.');
    SELECT COUNT(*) INTO total FROM ALERTA WHERE origem_api = 'simulacao-v1';
    conferir(total = 3, 'Esperadas tres ocorrencias simuladas.');
    DBMS_OUTPUT.PUT_LINE('Cadastros, ocorrencias e tres FKs conferidos.');

    SAVEPOINT verificacao_citizentech;
    -- A PK 1 ja existe: nao pode inserir nem modificar o registro existente.
    BEGIN
        INSERT INTO BUEIRO (bueiro_id) VALUES (1);
        RAISE_APPLICATION_ERROR(-20002, 'PK duplicada foi aceita indevidamente.');
    EXCEPTION WHEN DUP_VAL_ON_INDEX THEN
        DBMS_OUTPUT.PUT_LINE('PK duplicada rejeitada: ORA-00001.');
    END;
    -- Escolher identificadores livres, sem presumir ausencia de outros cadastros.
    DECLARE
        id_sensor NUMBER;
        id_inexistente NUMBER;
    BEGIN
        SELECT NVL(MIN(sensor_id), 0) - 1 INTO id_sensor FROM SENSOR;
        SELECT NVL(MIN(dispositivo_id), 0) - 1 INTO id_inexistente FROM DISPOSITIVO;
        BEGIN
            INSERT INTO SENSOR VALUES (id_sensor, id_inexistente, 'HC-SR04');
            RAISE_APPLICATION_ERROR(-20003, 'FK invalida foi aceita indevidamente.');
        EXCEPTION WHEN OTHERS THEN
            IF SQLCODE != -2291 THEN RAISE; END IF;
            DBMS_OUTPUT.PUT_LINE('FK sem pai rejeitada: ORA-02291.');
        END;
        BEGIN
            INSERT INTO SENSOR VALUES (id_sensor, 1, 'MODELO_INVALIDO');
            RAISE_APPLICATION_ERROR(-20004, 'Modelo invalido foi aceito indevidamente.');
        EXCEPTION WHEN OTHERS THEN
            IF SQLCODE != -2290 THEN RAISE; END IF;
            DBMS_OUTPUT.PUT_LINE('CHECK do modelo rejeitou valor invalido: ORA-02290.');
        END;
    END;
    ROLLBACK TO verificacao_citizentech;
    DBMS_OUTPUT.PUT_LINE('Verificacao concluida; nenhuma alteracao dos testes persistida.');
EXCEPTION WHEN OTHERS THEN
    ROLLBACK;
    RAISE;
END;
/

SELECT table_name, constraint_name, constraint_type, status
FROM user_constraints
WHERE table_name IN ('BUEIRO', 'DISPOSITIVO', 'SENSOR', 'ALERTA')
ORDER BY table_name, constraint_type, constraint_name;
