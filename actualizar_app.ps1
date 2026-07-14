$ErrorActionPreference = "Stop"

Set-Location $PSScriptRoot

$stamp = Get-Date -Format "yyyy.MM.dd-HHmm"
$appFile = Join-Path $PSScriptRoot "app.py"

Write-Host "Actualizando version de Gamer Signal: $stamp" -ForegroundColor Yellow

$contenido = Get-Content $appFile -Raw
$contenido = $contenido -replace 'APP_VERSION = "[^"]+"', "APP_VERSION = `"$stamp`""
Set-Content -Path $appFile -Value $contenido -Encoding UTF8

Write-Host "Verificando app.py..." -ForegroundColor Yellow
python -m py_compile app.py

Write-Host "Preparando cambios para GitHub..." -ForegroundColor Yellow
git add .

$estado = git status --short
if (-not $estado) {
    Write-Host "No hay cambios nuevos para subir." -ForegroundColor Green
    exit 0
}

git commit -m "Update Gamer Signal $stamp"
git push origin main

Write-Host ""
Write-Host "Listo. Streamlit debe actualizar el link en 1 a 3 minutos." -ForegroundColor Green
Write-Host "Publico: https://gamer-signal.streamlit.app/"
Write-Host "Dueno:   https://gamer-signal.streamlit.app/?owner=daviet"
