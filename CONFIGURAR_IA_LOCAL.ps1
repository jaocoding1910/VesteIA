$ErrorActionPreference = 'Stop'
$envPath = Join-Path $PSScriptRoot 'backend\.env'
if (-not (Test-Path $envPath)) {
    Copy-Item (Join-Path $PSScriptRoot 'backend\.env.example') $envPath
}
$lines = [System.IO.File]::ReadAllLines($envPath)
$lines = @($lines | Where-Object { $_ -notmatch '^\s*TRYON_(ENABLED|PROVIDER|CATVTON_URL)\s*=' })
$lines += @('TRYON_ENABLED=true', 'TRYON_PROVIDER=catvton', 'TRYON_CATVTON_URL=http://127.0.0.1:7861')
[System.IO.File]::WriteAllLines($envPath, $lines, (New-Object System.Text.UTF8Encoding($false)))
Write-Host 'CatVTON local configurado. As demais configurações do banco foram preservadas.'
Write-Host 'Reinicie o backend e abra INICIAR_IA_LOCAL.bat.'
