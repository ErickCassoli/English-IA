Write-Host "Starting English IA Environment..." -ForegroundColor Cyan

# Check for .venv in api folder
if (-not (Test-Path "api\.venv")) {
    Write-Host "Creating virtual environment in api/..." -ForegroundColor Yellow
    Set-Location api
    python -m venv .venv
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    .\.venv\Scripts\pip install -r requirements.txt
    Set-Location ..
}

# Start Backend
Write-Host "Starting Backend (Port 8000)..." -ForegroundColor Green
$backendProcess = Start-Process -FilePath "powershell" -ArgumentList "-NoExit", "-Command", "& { Set-Location api; . .\.venv\Scripts\activate; uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 }" -PassThru

# Start Frontend
Write-Host "Starting Frontend..." -ForegroundColor Green
Set-Location web
$frontendProcess = Start-Process -FilePath "powershell" -ArgumentList "-NoExit", "-Command", "npm run dev" -PassThru
Set-Location ..

Write-Host "------------------------------------------------" -ForegroundColor Cyan
Write-Host "Backend running at: http://localhost:8000" -ForegroundColor White
Write-Host "Frontend running at: http://localhost:5173" -ForegroundColor White
Write-Host "------------------------------------------------" -ForegroundColor Cyan
Write-Host "Press any key to stop all services..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

Stop-Process -Id $backendProcess.Id -ErrorAction SilentlyContinue
Stop-Process -Id $frontendProcess.Id -ErrorAction SilentlyContinue
Write-Host "Services stopped." -ForegroundColor Red
