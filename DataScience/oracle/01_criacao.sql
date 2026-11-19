-- Oracle 19c ou superior. Executar em schema academico vazio.
-- IDs de cadastro sao atribuidos pelo operador, nao recebidos pela API.
CREATE TABLE BUEIRO (
    bueiro_id NUMBER(10) CONSTRAINT pk_bueiro PRIMARY KEY,
    descricao VARCHAR2(200 CHAR),
    localizacao VARCHAR2(300 CHAR)
);
CREATE TABLE DISPOSITIVO (
    dispositivo_id NUMBER(10) CONSTRAINT pk_dispositivo PRIMARY KEY,
    bueiro_id NUMBER(10) NOT NULL,
    descricao VARCHAR2(200 CHAR),
    CONSTRAINT fk_dispositivo_bueiro FOREIGN KEY (bueiro_id) REFERENCES BUEIRO(bueiro_id)
);
CREATE TABLE SENSOR (
    sensor_id NUMBER(10) CONSTRAINT pk_sensor PRIMARY KEY,
    dispositivo_id NUMBER(10) NOT NULL,
    modelo VARCHAR2(30 CHAR) NOT NULL,
    CONSTRAINT ck_sensor_modelo CHECK (modelo IN ('HC-SR04', 'DHT22')),
    CONSTRAINT fk_sensor_dispositivo FOREIGN KEY (dispositivo_id) REFERENCES DISPOSITIVO(dispositivo_id)
);
-- Uma ocorrencia por leitura selecionada, nao um evento distinto de enchente.
CREATE TABLE ALERTA (
    alerta_id NUMBER GENERATED ALWAYS AS IDENTITY CONSTRAINT pk_alerta PRIMARY KEY,
    dispositivo_id NUMBER(10) NOT NULL,
    origem_api VARCHAR2(100 CHAR) NOT NULL,
    leitura_api_id NUMBER(19) NOT NULL,
    recebido_em TIMESTAMP(6) WITH TIME ZONE NOT NULL,
    risco_python VARCHAR2(20 CHAR) NOT NULL,
    mensagem VARCHAR2(500 CHAR) NOT NULL,
    CONSTRAINT fk_alerta_dispositivo FOREIGN KEY (dispositivo_id) REFERENCES DISPOSITIVO(dispositivo_id),
    CONSTRAINT uq_alerta_origem UNIQUE (origem_api, leitura_api_id),
    CONSTRAINT ck_alerta_id CHECK (leitura_api_id > 0),
    CONSTRAINT ck_alerta_risco CHECK (risco_python IN ('ATENCAO', 'RISCO_ALTO', 'DADOS_INVALIDOS'))
);
CREATE INDEX ix_dispositivo_bueiro ON DISPOSITIVO(bueiro_id);
CREATE INDEX ix_sensor_dispositivo ON SENSOR(dispositivo_id);
CREATE INDEX ix_alerta_dispositivo_data ON ALERTA(dispositivo_id, recebido_em);
