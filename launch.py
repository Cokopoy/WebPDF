#!/usr/bin/env python3
"""
Zzzuper PDF - Web Application Launcher
Auto-starts Flask server dan membuka browser
"""

import subprocess
import time
import webbrowser
import sys
import os
from pathlib import Path

def main():
    print("\n" + "="*50)
    print("  🚀 Zzzuper PDF - Web Application")
    print("="*50 + "\n")
    
    # Check if virtual environment exists
    venv_path = Path(".venv")
    if not venv_path.exists():
        print("[*] Virtual environment tidak ditemukan.")
        print("[*] Membuat virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", ".venv"], check=True)
        print("[+] Virtual environment berhasil dibuat.\n")
    
    # Determine Python executable
    if sys.platform == "win32":
        python_exe = venv_path / "Scripts" / "python.exe"
    else:
        python_exe = venv_path / "bin" / "python"
    
    # Check if dependencies are installed
    print("[*] Mengecek dependencies...")
    result = subprocess.run([str(python_exe), "-c", "import flask"], 
                          capture_output=True)
    if result.returncode != 0:
        print("[*] Menginstall dependencies...")
        subprocess.run([str(python_exe), "-m", "pip", "install", "-r", "requirements.txt"],
                      check=True)
        print("[+] Dependencies berhasil diinstall.\n")
    else:
        print("[+] Semua dependencies sudah terinstall.\n")
    
    # Start Flask server
    print("[*] Memulai Flask server...")
    print("\n" + "="*50)
    print("  ✨ Aplikasi dimulai di:")
    print("  🌐 http://localhost:5000")
    print("="*50)
    print("\nMembuka browser dalam 2 detik...\n")
    
    # Start Flask in a separate process
    flask_process = subprocess.Popen([str(python_exe), "app.py"])
    
    # Wait a bit for Flask to start
    time.sleep(2)
    
    # Open browser
    try:
        webbrowser.open("http://localhost:5000")
        print("[+] Browser dibuka.\n")
    except Exception as e:
        print(f"[!] Gagal membuka browser: {e}")
        print("[*] Silakan buka manual: http://localhost:5000\n")
    
    print("Tekan CTRL+C untuk menghentikan aplikasi.\n")
    
    try:
        flask_process.wait()
    except KeyboardInterrupt:
        print("\n[*] Menghentikan aplikasi...")
        flask_process.terminate()
        flask_process.wait()
        print("[+] Aplikasi berhasil dihentikan.")
        sys.exit(0)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[+] Aplikasi dihentikan.")
        sys.exit(0)
    except Exception as e:
        print(f"\n[!] Error: {e}")
        sys.exit(1)
