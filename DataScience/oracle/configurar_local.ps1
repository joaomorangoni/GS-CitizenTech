# Execute da raiz: powershell -File DataScience/oracle/configurar_local.ps1
# Nao remove, substitui ou reinicializa containers/volumes existentes.
$ErrorActionPreference = 'Stop'
$nomeContainerOracle = 'citizentech-oracle'
$nomeVolumeOracle = 'citizentech-oracle-data'
$imagemOracle = 'container-registry.oracle.com/database/free:latest-lite'
$pastaCredencialOracle = Join-Path $env:LOCALAPPDATA 'GS-CitizenTech'
$arquivoCredencialOracle = Join-Path $pastaCredencialOracle 'oracle-local.clixml'

docker info --format '{{.ServerVersion}}'
if ($LASTEXITCODE -ne 0) { throw 'Inicie Docker Desktop antes de continuar.' }
$containersOracle = @(docker ps -a --format '{{.Names}}')
if ($containersOracle -contains $nomeContainerOracle) {
    throw 'Container citizentech-oracle ja existe. Use docker start; nao recrie o banco.'
}
$volumesOracle = @(docker volume ls --format '{{.Name}}')
if ($volumesOracle -contains $nomeVolumeOracle) { throw 'Volume ja existe; revisar antes de reutilizar.' }
if (Test-Path -LiteralPath $arquivoCredencialOracle) { throw 'Credencial local ja existe; revisar antes de substituir.' }
if (Get-NetTCPConnection -LocalPort 1521 -State Listen -ErrorAction SilentlyContinue) { throw 'Porta 1521 ocupada.' }

function NovaSenhaOracle {
    $bytesOracle = New-Object byte[] 24
    $geradorOracle = [Security.Cryptography.RandomNumberGenerator]::Create()
    try { $geradorOracle.GetBytes($bytesOracle) } finally { $geradorOracle.Dispose() }
    return 'Aa1' + ([BitConverter]::ToString($bytesOracle).Replace('-', ''))
}
$senhaAplicacaoOracle = NovaSenhaOracle
$senhaAdminOracle = NovaSenhaOracle
New-Item -ItemType Directory -Path $pastaCredencialOracle -Force | Out-Null
$credencialOracle = New-Object System.Management.Automation.PSCredential('CITIZENTECH', (ConvertTo-SecureString $senhaAplicacaoOracle -AsPlainText -Force))
$credencialOracle | Export-Clixml -LiteralPath $arquivoCredencialOracle
docker volume create $nomeVolumeOracle
if ($LASTEXITCODE -ne 0) { throw 'Nao foi possivel criar volume.' }
try {
    $env:ORACLE_PWD = $senhaAdminOracle
    docker run -d --name $nomeContainerOracle --publish 127.0.0.1:1521:1521 --memory 3g --shm-size 1g --env ORACLE_PWD --volume "${nomeVolumeOracle}:/opt/oracle/oradata" $imagemOracle
    if ($LASTEXITCODE -ne 0) { throw 'Falha ao iniciar container; preservar volume e diagnosticar.' }
} finally { Remove-Item Env:ORACLE_PWD -ErrorAction SilentlyContinue }

Write-Output 'Aguardando Oracle; isso pode levar alguns minutos.'
$prontoOracle = $false
for ($tentativaOracle = 0; $tentativaOracle -lt 90; $tentativaOracle++) {
    $estadoOracle = docker inspect --format '{{.State.Health.Status}}' $nomeContainerOracle
    if ($estadoOracle -eq 'healthy') { $prontoOracle = $true; break }
    if (($tentativaOracle % 6) -eq 0) { Write-Output "Inicializando Oracle: $estadoOracle" }
    Start-Sleep -Seconds 5
}
if (-not $prontoOracle) { throw 'Tempo excedido. Preserve container e volume; confira docker logs.' }

& (Join-Path $PSScriptRoot 'criar_usuario_local.ps1')
Write-Output 'Oracle pronto: 127.0.0.1:1521/FREEPDB1, usuario CITIZENTECH.'
Write-Output 'Credencial protegida pelo Windows em %LOCALAPPDATA%/GS-CitizenTech/oracle-local.clixml.'
