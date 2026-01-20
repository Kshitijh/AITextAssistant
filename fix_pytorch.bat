@echo off
echo ========================================
echo   Fixing PyTorch DLL Error
echo ========================================
echo.

echo Uninstalling existing PyTorch...
pip uninstall torch torchvision torchaudio -y

echo.
echo Installing Visual C++ Redistributable dependencies...
echo Please download and install if not already installed:
echo https://aka.ms/vs/17/release/vc_redist.x64.exe
echo.
pause

echo.
echo Installing PyTorch CPU version...
pip install torch --index-url https://download.pytorch.org/whl/cpu

echo.
echo Verifying PyTorch installation...
python -c "import torch; print(f'PyTorch {torch.__version__} installed successfully')"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ========================================
    echo   ERROR: PyTorch installation failed
    echo ========================================
    echo.
    echo SOLUTION: Python 3.14 is very new and may not be fully compatible.
    echo.
    echo Please try one of these options:
    echo.
    echo Option 1: Install Python 3.11 and recreate the virtual environment
    echo   1. Download Python 3.11 from https://www.python.org/downloads/
    echo   2. Remove current venv: rmdir /s .venv
    echo   3. Create new venv: python -m venv .venv
    echo   4. Activate: .venv\Scripts\activate
    echo   5. Run: pip install -r requirements.txt
    echo.
    echo Option 2: Use pip with --only-binary flag
    echo   pip install torch --only-binary :all: --index-url https://download.pytorch.org/whl/cpu
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo   SUCCESS: PyTorch installed!
echo ========================================
echo.
echo Now run: python main.py
pause
