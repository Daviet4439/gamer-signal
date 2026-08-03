$ErrorActionPreference = "Stop"

$origen = $PSScriptRoot
$destino = "C:\Users\jense\Buscador-geek"

if (-not (Test-Path -LiteralPath $destino)) {
    throw "No se encontró la carpeta local de Gamer Signal: $destino"
}

# Copiar dependencias primero para que Streamlit nunca cargue app.py incompleto.
Copy-Item -LiteralPath (Join-Path $origen "guia_marcas.json") -Destination (Join-Path $destino "guia_marcas.json") -Force
Copy-Item -LiteralPath (Join-Path $origen "editorial_engine_final.py") -Destination (Join-Path $destino "editorial_engine_final.py") -Force
Copy-Item -LiteralPath (Join-Path $origen "app.py") -Destination (Join-Path $destino "app.py") -Force

Write-Host "Gamer Signal local actualizado con la integración de Ollama." -ForegroundColor Green
