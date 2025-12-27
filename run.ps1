# Zzzuper PDF - Web Application Startup Script

Write-Host ""
Write-Host "===================================" -ForegroundColor Cyan
Write-Host "  Zzzuper PDF - Web Application" -ForegroundColor Cyan
Write-Host "===================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (-Not (Test-Path ".\.venv")) {
    Write-Host "[*] Virtual environment tidak ditemukan. Membuat virtual environment..." -ForegroundColor Yellow
    python -m venv .venv
    Write-Host "[+] Virtual environment berhasil dibuat." -ForegroundColor Green
    Write-Host ""
}

# Activate virtual environment
Write-Host "[*] Mengaktifkan virtual environment..." -ForegroundColor Yellow
& ".\.venv\Scripts\Activate.ps1"
Write-Host "[+] Virtual environment aktif." -ForegroundColor Green
Write-Host ""

# Check if dependencies are installed
Write-Host "[*] Mengecek dependencies..." -ForegroundColor Yellow
$hasFlask = pip list | Select-String "Flask"
if (-Not $hasFlask) {
    Write-Host "[*] Menginstall dependencies..." -ForegroundColor Yellow
    pip install -r requirements.txt
    Write-Host "[+] Dependencies berhasil diinstall." -ForegroundColor Green
    Write-Host ""
}

# Run the Flask application
Write-Host "[*] Memulai aplikasi Flask..." -ForegroundColor Yellow
Write-Host ""
Write-Host "===================================" -ForegroundColor Green
Write-Host "  Aplikasi dimulai di:" -ForegroundColor Green
Write-Host "  http://localhost:5000" -ForegroundColor Green
Write-Host "===================================" -ForegroundColor Green
Write-Host ""
Write-Host "Tekan CTRL+C untuk menghentikan aplikasi" -ForegroundColor Cyan
Write-Host ""

python app.py
