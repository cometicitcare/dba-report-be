# Local Development Start Script (Windows)
# Sets UTF-8 encoding to handle Unicode characters
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"

Write-Host "[INFO] Starting dba-report-be local dev server..." -ForegroundColor Cyan
Write-Host "[INFO] Using .venv Python + live Railway DB" -ForegroundColor Yellow
Write-Host "[INFO] Server: http://localhost:8000" -ForegroundColor Green
Write-Host "[INFO] API Docs: http://localhost:8000/docs" -ForegroundColor Green
Write-Host ""

.venv\Scripts\python.exe run.py
