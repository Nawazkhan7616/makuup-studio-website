# MakuUP Studio — Dev Server Startup Script
# Run from the backend/ directory: .\run_dev.ps1

$ErrorActionPreference = "Stop"
$BackendDir = $PSScriptRoot

Write-Host "`n🎨 MakuUP Studio Backend — Starting Dev Server`n" -ForegroundColor Magenta

# ── 1. Check / create virtual environment ─────────────────────────────
$VenvPython = Join-Path $BackendDir "venv\Scripts\python.exe"
$VenvPip    = Join-Path $BackendDir "venv\Scripts\pip.exe"

if (-not (Test-Path $VenvPython)) {
    Write-Host "⚙️  Virtual environment not found. Creating one..." -ForegroundColor Yellow
    python -m venv "$BackendDir\venv"
    Write-Host "✅ venv created." -ForegroundColor Green
}

# ── 2. Install / upgrade dependencies ─────────────────────────────────
Write-Host "📦 Installing/verifying packages from requirements.txt..." -ForegroundColor Cyan
& $VenvPip install -q -r "$BackendDir\requirements.txt"
Write-Host "✅ Packages ready." -ForegroundColor Green

# ── 3. Verify .env exists ─────────────────────────────────────────────
$EnvFile = Join-Path $BackendDir ".env"
if (-not (Test-Path $EnvFile)) {
    Write-Host "⚠️  .env not found! Copying from .env.example..." -ForegroundColor Yellow
    Copy-Item "$BackendDir\.env.example" $EnvFile
    Write-Host "   Edit .env with your real credentials before deploying." -ForegroundColor Yellow
}

# ── 4. Run Django check ───────────────────────────────────────────────
Write-Host "`n🔍 Running Django system check..." -ForegroundColor Cyan
$CheckResult = & $VenvPython "$BackendDir\manage.py" check 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Django check failed:`n$CheckResult" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Django check passed." -ForegroundColor Green

# ── 5. Start server ───────────────────────────────────────────────────
Write-Host "`n🚀 Starting Django dev server at http://127.0.0.1:8000/" -ForegroundColor Magenta
Write-Host "   API root: http://127.0.0.1:8000/api/" -ForegroundColor Cyan
Write-Host "   Press Ctrl+C to stop.`n" -ForegroundColor Gray

& $VenvPython "$BackendDir\manage.py" runserver
