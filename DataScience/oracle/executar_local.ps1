param([switch]$Criar)
# -Criar: executa 01 e 02 apenas se nao houver objetos do projeto.
# Sem -Criar: somente consultas e testes com rollback, preservando cadastros.
$ErrorActionPreference = 'Stop'
$OutputEncoding = New-Object System.Text.UTF8Encoding($false)
$credencialExecucaoOracle = Import-Clixml -LiteralPath (Join-Path $env:LOCALAPPDATA 'GS-CitizenTech/oracle-local.clixml')
$senhaExecucaoOracle = $credencialExecucaoOracle.GetNetworkCredential().Password
$pastaScriptsOracle = Join-Path (Get-Location) 'DataScience/oracle'
if (-not (Test-Path -LiteralPath (Join-Path $pastaScriptsOracle '01_criacao.sql'))) { throw 'Execute da raiz do repositorio.' }
docker exec --user oracle citizentech-oracle mkdir -p /tmp/citizentech-sql
if ($LASTEXITCODE -ne 0) { throw 'Container Oracle indisponivel.' }
docker cp (Join-Path $pastaScriptsOracle '.') 'citizentech-oracle:/tmp/citizentech-sql'
if ($LASTEXITCODE -ne 0) { throw 'Nao foi possivel copiar scripts para container.' }
$criacaoOracle = ''
if ($Criar) {
    $criacaoOracle = @'
DECLARE
  total NUMBER;
BEGIN
  SELECT COUNT(*) INTO total FROM user_objects
  WHERE object_name IN ('BUEIRO', 'DISPOSITIVO', 'SENSOR', 'ALERTA',
    'IX_DISPOSITIVO_BUEIRO', 'IX_SENSOR_DISPOSITIVO', 'IX_ALERTA_DISPOSITIVO_DATA');
  IF total > 0 THEN RAISE_APPLICATION_ERROR(-20010, 'Objetos ja existem. Execute sem -Criar.'); END IF;
END;
/
@/tmp/citizentech-sql/01_criacao.sql
@/tmp/citizentech-sql/02_dados_simulados.sql
'@
}
$comandosExecucaoOracle = @"
SET ECHO OFF VERIFY OFF
WHENEVER OSERROR EXIT FAILURE ROLLBACK
WHENEVER SQLERROR EXIT SQL.SQLCODE ROLLBACK
CONNECT CITIZENTECH/"$senhaExecucaoOracle"@//localhost:1521/FREEPDB1
SET LINESIZE 240 PAGESIZE 100 TRIMSPOOL ON
COLUMN descricao FORMAT A30
COLUMN modelo FORMAT A10
COLUMN origem_api FORMAT A20
COLUMN mensagem FORMAT A100
COLUMN recebido_em FORMAT A35
COLUMN risco_python FORMAT A20
COLUMN table_name FORMAT A15
COLUMN constraint_name FORMAT A35
COLUMN banner_full FORMAT A100
SELECT banner_full FROM v`$version;
SELECT USER AS usuario, sys_context('USERENV', 'CON_NAME') AS pdb FROM dual;
$criacaoOracle
@/tmp/citizentech-sql/03_consultas.sql
@/tmp/citizentech-sql/04_verificacao.sql
EXIT SUCCESS
"@
$saidaExecucaoOracle = $comandosExecucaoOracle | docker exec -i --user oracle --env NLS_LANG=.AL32UTF8 citizentech-oracle sqlplus -s /nolog 2>&1
$codigoExecucaoOracle = $LASTEXITCODE
$saidaSeguraOracle = @($saidaExecucaoOracle | ForEach-Object { ([string]$_).Replace($senhaExecucaoOracle, '[SEGREDO]') })
$arquivoEvidenciaOracle = 'DataScience/documentacao/evidencias/oracle_execucao.txt'
if (-not $Criar) { $arquivoEvidenciaOracle = 'DataScience/documentacao/evidencias/oracle_reverificacao.txt' }
$saidaSeguraOracle | Set-Content -LiteralPath $arquivoEvidenciaOracle -Encoding UTF8
$saidaSeguraOracle | Write-Output
if ($codigoExecucaoOracle -ne 0) { throw "Execucao Oracle falhou; codigo $codigoExecucaoOracle. Consulte a evidencia." }
