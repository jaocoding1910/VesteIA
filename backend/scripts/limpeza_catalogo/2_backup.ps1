# Backup das tabelas do catálogo. Pede a senha do PostgreSQL de forma interativa (não grava em arquivo).
param(
  [string]$DbHost = "localhost",
  [string]$Port = "5432",
  [Parameter(Mandatory = $true)][string]$User,
  [Parameter(Mandatory = $true)][string]$Database
)
$arquivo = "backup-catalogo-$(Get-Date -Format yyyyMMdd-HHmmss).dump"
pg_dump -h $DbHost -p $Port -U $User -d $Database -F c `
  -t catalog_products -t catalog_variants -t catalog_sizes -t produtos -f $arquivo
if ($LASTEXITCODE -ne 0) { Write-Error "Backup falhou. Nada foi alterado."; exit 1 }
Write-Host "Backup criado: $arquivo"
