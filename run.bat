@echo off
cls
echo.
echo ===================================
echo  Zzzuper PDF - Web Application
echo ===================================
echo.

REM Check if virtual environment exists
if not exist ".\.venv" (
    echo [*] Virtual environment tidak ditemukan. Membuat virtual environment...
    python -m venv .venv
    echo [+] Virtual environment berhasil dibuat.
    echo.
)

REM Activate virtual environment
call .\.venv\Scripts\activate.bat

REM Check if dependencies are installed
echo [*] Mengecek dependencies...
pip list | find "Flask" >nul
if errorlevel 1 (
    echo [*] Menginstall dependencies...
    pip install -r requirements.txt
    echo [+] Dependencies berhasil diinstall.
    echo.
)

REM Run the Flask application
echo [*] Memulai aplikasi Flask...
echo.
echo ===================================
echo  Aplikasi dimulai di:
echo  http://localhost:5000
echo ===================================
echo.
echo Tekan CTRL+C untuk menghentikan aplikasi
echo.

python app.py

pause
