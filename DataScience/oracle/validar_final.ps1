# Validacao final: nao executa DDL nem dados simulados (01/02).
$ErrorActionPreference = 'Stop'
$OutputEncoding = New-Object System.Text.UTF8Encoding($false)
$credencialValidacaoOracle = Import-Clixml (Join-Path $env:LOCALAPPDATA 'GS-CitizenTech/oracle-local.clixml')
$senhaValidacaoOracle = $credencialValidacaoOracle.GetNetworkCredential().Password
$pastaValidacaoOracle = Join-Path (Get-Location) 'DataScience/oracle'
docker exec --user oracle citizentech-oracle mkdir -p /tmp/citizentech-final
if ($LASTEXITCODE -ne 0) { throw 'Container indisponivel.' }
foreach ($nomeSqlOracle in @('03_consultas.sql','04_verificacao.sql','05_snapshot_validacao.sql')) {
    docker cp (Join-Path $pastaValidacaoOracle $nomeSqlOracle) "citizentech-oracle:/tmp/citizentech-final/$nomeSqlOracle"
    if ($LASTEXITCODE -ne 0) { throw 'Falha ao copiar SQL de validacao.' }
}
$sqlValidacaoOracle = @"
SET ECHO OFF VERIFY OFF
WHENEVER OSERROR EXIT FAILURE ROLLBACK
WHENEVER SQLERROR EXIT SQL.SQLCODE ROLLBACK
CONNECT CITIZENTECH/"$senhaValidacaoOracle"@//localhost:1521/FREEPDB1
SET LINESIZE 240 PAGESIZE 100
SELECT TO_CHAR(SYSTIMESTAMP AT TIME ZONE 'America/Sao_Paulo', 'YYYY-MM-DD HH24:MI:SS TZH:TZM') AS executado_em FROM dual;
SELECT USER AS usuario, SYS_CONTEXT('USERENV','CON_NAME') AS pdb FROM dual;
SELECT banner_full FROM v`$version;
PROMPT CONTAGENS TOTAIS ANTES DOS TESTES
SELECT 'BUEIRO' AS tabela, COUNT(*) AS total FROM BUEIRO
UNION ALL SELECT 'DISPOSITIVO', COUNT(*) FROM DISPOSITIVO
UNION ALL SELECT 'SENSOR', COUNT(*) FROM SENSOR
UNION ALL SELECT 'ALERTA', COUNT(*) FROM ALERTA;
@/tmp/citizentech-final/05_snapshot_validacao.sql ANTES
SET HEADING ON FEEDBACK ON PAGESIZE 100 LINESIZE 240
COLUMN descricao FORMAT A30
COLUMN modelo FORMAT A10
COLUMN origem_api FORMAT A20
COLUMN recebido_em FORMAT A35
COLUMN risco_python FORMAT A20
COLUMN mensagem FORMAT A100
COLUMN table_name FORMAT A15
COLUMN constraint_name FORMAT A35
PROMPT INICIO JOINs 03_consultas.sql
SET ECHO ON
@/tmp/citizentech-final/03_consultas.sql
SET ECHO OFF
PROMPT FIM JOINs 03_consultas.sql
PROMPT INICIO PK FK CHECK 04_verificacao.sql
@/tmp/citizentech-final/04_verificacao.sql
PROMPT FIM PK FK CHECK 04_verificacao.sql
@/tmp/citizentech-final/05_snapshot_validacao.sql DEPOIS
PROMPT VALIDACAO SQL CONCLUIDA
EXIT SUCCESS
"@
$saidaValidacaoOracle = $sqlValidacaoOracle | docker exec -i --user oracle --env NLS_LANG=.AL32UTF8 citizentech-oracle sqlplus -s /nolog 2>&1
$codigoValidacaoOracle = $LASTEXITCODE
$saidaSeguraValidacaoOracle = @($saidaValidacaoOracle | ForEach-Object { ([string]$_).Replace($senhaValidacaoOracle, '[SEGREDO]') })
$saidaSeguraValidacaoOracle | Set-Content 'DataScience/documentacao/evidencias/oracle_validacao_final.txt' -Encoding UTF8
$saidaSeguraValidacaoOracle | Write-Output
if ($codigoValidacaoOracle -ne 0) { throw "Falha SQL; codigo $codigoValidacaoOracle. Evidencia salva." }
