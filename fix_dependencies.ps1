# Fix PyTorch DLL Error on Windows
# This script reinstalls dependencies with the correct CPU-only PyTorch

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "  Fixing PyTorch DLL Error on Windows" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment is activated
if (-not $env:VIRTUAL_ENV) {
    Write-Host "ERROR: Virtual environment is not activated!" -ForegroundColor Red
    Write-Host "Please run: .\.venv\Scripts\Activate.ps1" -ForegroundColor Yellow
    exit 1
}

Write-Host "Step 1: Uninstalling problematic PyTorch..." -ForegroundColor Yellow
pip uninstall torch torchvision torchaudio -y

Write-Host ""
Write-Host "Step 2: Clearing pip cache..." -ForegroundColor Yellow
pip cache purge

Write-Host ""
Write-Host "Step 3: Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

Write-Host ""
Write-Host "Step 4: Installing CPU-only PyTorch..." -ForegroundColor Yellow
pip install torch==2.9.0 --index-url https://download.pytorch.org/whl/cpu

Write-Host ""
Write-Host "Step 5: Installing remaining dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

Write-Host ""
Write-Host "==================================================" -ForegroundColor Green
Write-Host "  ✓ Installation Complete!" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Green
Write-Host ""
Write-Host "You can now run: python main.py" -ForegroundColor Cyan
