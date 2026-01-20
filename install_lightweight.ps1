# AI Text Assistant - Lightweight Version
# Installation Guide for Python 3.14+

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  AI Text Assistant - Lightweight Setup" -ForegroundColor Cyan  
Write-Host "  (Python 3.14+ Compatible)" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Check Python version
Write-Host "Checking Python version..." -ForegroundColor Yellow
python --version

Write-Host ""
Write-Host "Installing lightweight dependencies..." -ForegroundColor Yellow
Write-Host "(No PyTorch - uses scikit-learn instead)" -ForegroundColor Green
Write-Host ""

# Upgrade pip
python -m pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "  ✓ Installation Complete!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Key Differences in Lightweight Version:" -ForegroundColor Cyan
Write-Host "  • Uses TF-IDF instead of sentence-transformers" -ForegroundColor White
Write-Host "  • Uses sklearn NearestNeighbors instead of FAISS" -ForegroundColor White
Write-Host "  • Uses template-based suggestions instead of LLM" -ForegroundColor White
Write-Host "  • Smaller memory footprint (~200MB vs 2GB+)" -ForegroundColor White
Write-Host "  • Faster startup time" -ForegroundColor White
Write-Host "  • No DLL dependencies" -ForegroundColor White
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Place documents in the 'data' folder" -ForegroundColor White
Write-Host "  2. Run: python main.py" -ForegroundColor White
Write-Host "  3. Click 'Build Index'" -ForegroundColor White
Write-Host "  4. Click 'Start Assistant'" -ForegroundColor White
Write-Host ""
Write-Host "Ready to run: python main.py" -ForegroundColor Cyan
