# Retoma cadastro apos banco healthy; usa credencial DPAPI ja gerada.
$ErrorActionPreference = 'Stop'
$OutputEncoding = New-Object System.Text.UTF8Encoding($false)
$credencialCadastroOracle = Import-Clixml -LiteralPath (Join-Path $env:LOCALAPPDATA 'GS-CitizenTech/oracle-local.clixml')
$senhaCadastroOracle = $credencialCadastroOracle.GetNetworkCredential().Password
$sqlUsuarioOracle = @"
SET ECHO OFF VERIFY OFF SERVEROUTPUT ON
WHENEVER SQLERROR EXIT SQL.SQLCODE ROLLBACK
ALTER SESSION SET CONTAINER = FREEPDB1;
DECLARE
  total NUMBER;
BEGIN
  SELECT COUNT(*) INTO total FROM dba_users WHERE username = 'CITIZENTECH';
  IF total > 0 THEN RAISE_APPLICATION_ERROR(-20011, 'Usuario ja existe; nao alterar senha ou objetos.'); END IF;
  SELECT COUNT(*) INTO total FROM dba_tablespaces WHERE tablespace_name = 'CITIZENTECH_DATA';
  IF total = 0 THEN
    EXECUTE IMMEDIATE 'CREATE TABLESPACE CITIZENTECH_DATA DATAFILE ''/opt/oracle/oradata/FREE/FREEPDB1/citizentech_data01.dbf'' SIZE 20M AUTOEXTEND ON NEXT 10M MAXSIZE 100M';
  END IF;
END;
/
CREATE USER CITIZENTECH IDENTIFIED BY "$senhaCadastroOracle" DEFAULT TABLESPACE CITIZENTECH_DATA QUOTA 100M ON CITIZENTECH_DATA;
GRANT CREATE SESSION, CREATE TABLE, CREATE SEQUENCE TO CITIZENTECH;
SELECT username, account_status, default_tablespace FROM dba_users WHERE username = 'CITIZENTECH';
EXIT
"@
$saidaCadastroOracle = $sqlUsuarioOracle | docker exec -i --user oracle citizentech-oracle sqlplus -s / as sysdba 2>&1
$codigoUsuarioOracle = $LASTEXITCODE
$saidaCadastroOracle | ForEach-Object { ([string]$_).Replace($senhaCadastroOracle, '[SEGREDO]') }
if ($codigoUsuarioOracle -ne 0) { throw 'Cadastro falhou. Diagnosticar sem recriar container ou volume.' }
