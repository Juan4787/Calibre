param([int]$Port = 8765)
$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..")
& ".\.venv\Scripts\freight-audit.exe" serve --port $Port
