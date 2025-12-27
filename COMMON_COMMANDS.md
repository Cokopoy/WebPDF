# ZZZUPER PDF - COMMON COMMANDS & SCRIPTS

## 🚀 QUICK START COMMANDS

### Windows (Easiest)
```batch
# Double-click this file:
run.bat
```

### PowerShell
```powershell
# Run this:
.\run.ps1
```

### Python Launcher
```bash
python launch.py
```

### Manual Setup
```bash
# Activate virtual environment
.\.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run application
python app.py
```

## 🔧 COMMON MAINTENANCE COMMANDS

### Check Python Version
```bash
python --version
# Should be 3.8 or higher
```

### List Installed Packages
```bash
pip list
```

### Check Specific Package
```bash
pip show Flask
```

### Upgrade Packages
```bash
pip install --upgrade -r requirements.txt
```

### Reinstall All Dependencies
```bash
pip install -r requirements.txt --force-reinstall
```

## 🐛 DEBUGGING & TROUBLESHOOTING

### Check if Port 5000 is in Use
```powershell
# PowerShell
Get-NetTcpConnection -LocalPort 5000

# Command Prompt
netstat -ano | findstr :5000
```

### Kill Process on Port 5000
```powershell
# PowerShell (Admin)
Get-Process | Where-Object {$_.Port -eq 5000} | Stop-Process

# Command Prompt (Admin)
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

### Check Flask Status
```bash
# In Python
python -c "import flask; print(flask.__version__)"
```

### Test API Endpoints
```bash
# Get file list
curl http://localhost:5000/api/files

# Test server
curl -I http://localhost:5000

# Verbose output
curl -v http://localhost:5000
```

## 📦 DEPENDENCY MANAGEMENT

### Create New requirements.txt
```bash
pip freeze > requirements.txt
```

### Install from requirements.txt
```bash
pip install -r requirements.txt
```

### Add New Package
```bash
# Install
pip install package-name

# Add to requirements.txt
pip freeze > requirements.txt
```

### Remove Package
```bash
# Uninstall
pip uninstall package-name

# Update requirements.txt
pip freeze > requirements.txt
```

## 🔄 VIRTUAL ENVIRONMENT COMMANDS

### Create Virtual Environment
```bash
python -m venv .venv
```

### Activate Virtual Environment
```bash
# Windows CMD
.\.venv\Scripts\activate.bat

# PowerShell
.\.venv\Scripts\Activate.ps1

# Linux/Mac
source .venv/bin/activate
```

### Deactivate Virtual Environment
```bash
deactivate
```

### Delete Virtual Environment (if needed)
```bash
# Remove folder
rm -r .venv

# Then recreate
python -m venv .venv
```

## 📁 FILE & FOLDER MANAGEMENT

### List All Files
```bash
ls -la
# or (Windows)
dir /a
```

### Remove Uploads Folder (Clean)
```bash
# PowerShell
Remove-Item -Path "uploads" -Recurse -Force

# Cmd
rmdir /s /q uploads
```

### Check Disk Usage
```bash
# PowerShell
Get-Item uploads | Get-ChildItem -Recurse | Measure-Object -Property Length -Sum

# Cmd
dir uploads /s
```

### Create Backup
```bash
# Backup entire project
xcopy . backup\ /E /Y

# Backup only source files
xcopy *.py backup\ /Y
xcopy requirements.txt backup\ /Y
```

## 🧪 TESTING COMMANDS

### Test If Application Starts
```bash
python app.py &
# Wait 2 seconds
curl http://localhost:5000
# Should return HTML content
```

### Test File Upload
```bash
curl -X POST \
  -F "files=@test.pdf" \
  http://localhost:5000/api/upload
```

### Test PDF Merge
```bash
curl -X POST http://localhost:5000/api/merge -o output.pdf
```

### Performance Test
```bash
# Using Apache Bench (if installed)
ab -n 100 -c 10 http://localhost:5000

# Using hey (if installed)
hey -n 100 -c 10 http://localhost:5000
```

## 📊 MONITORING & LOGS

### Check Application Log (from Flask output)
```bash
# Flask debug info printed to terminal
python app.py

# Look for:
# * Running on http://127.0.0.1:5000
# * Debugger is active!
```

### Monitor File System
```bash
# Watch for file uploads
# PowerShell
Get-ChildItem uploads -Recurse | Measure-Object

# Check recently modified files
Get-ChildItem uploads -Recurse -File | Sort-Object LastWriteTime -Descending | Select-Object -First 10
```

### Check Memory Usage
```bash
# PowerShell
Get-Process python | Select-Object Name, @{Name="MemMB";Expression={[math]::Round($_.WorkingSet/1MB,2)}}
```

## 🔐 SECURITY COMMANDS

### Generate New Secret Key
```bash
python -c "import secrets; print(secrets.token_hex(16))"
```

### Check for Vulnerabilities
```bash
# Install safety
pip install safety

# Check packages
safety check
```

### Audit Requirements
```bash
pip install pip-audit
pip-audit
```

## 🚀 DEPLOYMENT COMMANDS

### Install Production Server
```bash
pip install gunicorn
pip freeze > requirements.txt
```

### Run with Gunicorn
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Run with Multiple Workers
```bash
gunicorn -w 4 -b 127.0.0.1:5000 --timeout 120 app:app
```

### Run in Background (Windows)
```bash
# Using start
start "" python app.py

# Or create service
```

## 📝 COMMON WORKFLOWS

### Fresh Start (Clean Everything)
```bash
# 1. Stop application (Ctrl+C)
# 2. Remove virtual environment
rmdir /s /q .venv

# 3. Remove uploads
rmdir /s /q uploads

# 4. Create new venv
python -m venv .venv

# 5. Activate venv
.\.venv\Scripts\activate

# 6. Install dependencies
pip install -r requirements.txt

# 7. Run application
python app.py
```

### Create Desktop Shortcut
```bash
# Run this:
create_shortcut.bat
```

### Update Application
```bash
# 1. Stop running application
# 2. Pull/download updates
# 3. Reinstall dependencies (in case updated)
pip install -r requirements.txt --force-reinstall

# 4. Start application
python app.py
```

### Migrate to New Folder
```bash
# 1. Copy entire project folder
# 2. Create new venv in new folder
python -m venv .venv

# 3. Activate and install
.\.venv\Scripts\activate
pip install -r requirements.txt

# 4. Run in new location
python app.py
```

## 🎯 QUICK REFERENCE TABLE

| Task | Command |
|------|---------|
| Start app | `run.bat` or `python app.py` |
| Activate venv | `.\.venv\Scripts\activate` |
| Install deps | `pip install -r requirements.txt` |
| Check version | `python --version` |
| List packages | `pip list` |
| Test API | `curl http://localhost:5000/api/files` |
| Stop app | `Ctrl+C` |
| Clear uploads | `rmdir /s /q uploads` |
| Reinstall venv | `rmdir /s /q .venv` then `python -m venv .venv` |
| Run in background | `start "" python app.py` |

## 🛠️ TROUBLESHOOTING COMMANDS

### Port Already in Use
```bash
# Find process using port 5000
netstat -ano | findstr :5000

# Kill process (replace PID with actual number)
taskkill /PID 1234 /F

# Or use different port - edit app.py last line:
# app.run(port=5001)
```

### Python Not Found
```bash
# Check if Python installed
python --version

# Add to PATH or use full path
C:\Python311\python.exe app.py
```

### Import Error
```bash
# Make sure venv is activated
.\.venv\Scripts\activate

# Reinstall package
pip install flask --force-reinstall

# Check installation
pip show flask
```

### Browser Can't Connect
```bash
# Check if server is running
curl http://localhost:5000

# Try with IP instead
http://127.0.0.1:5000

# Check firewall
netstat -ano | findstr LISTENING
```

## 📚 ADDITIONAL RESOURCES

### View this file
```bash
# Print this file
type COMMON_COMMANDS.txt
# or
cat COMMON_COMMANDS.txt
```

### Get Help
```bash
# Flask help
python -c "import flask; help(flask)"

# pip help
pip --help

# Python help
python --help
```

### Documentation Shortcuts
```bash
# Open documentation files
readme
README.md
API_DOCUMENTATION.md
QUICKSTART.md
```

═══════════════════════════════════════════════════════════════════════

📌 NOTES:

1. Always activate virtual environment before working
2. Use the shortcut scripts (run.bat, run.ps1) for convenience
3. Keep requirements.txt updated
4. Monitor uploads folder size
5. Backup important data

═══════════════════════════════════════════════════════════════════════

Last Updated: December 27, 2025
