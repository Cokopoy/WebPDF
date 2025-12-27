@echo off
REM Create Desktop Shortcut for Zzzuper PDF

setlocal enabledelayedexpansion

echo Creating desktop shortcut for Zzzuper PDF...

REM Get desktop path
for /f "tokens=3" %%a in ('reg query "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders" /v Desktop') do (
    set DESKTOP=%%a
)

if "!DESKTOP!"=="" (
    echo Error: Could not find Desktop path
    goto :eof
)

REM Get current directory
cd /d "%~dp0"
set APPDIR=%CD%

REM Create batch file for launcher
(
    echo @echo off
    echo cd /d "%APPDIR%"
    echo call .\.venv\Scripts\activate.bat
    echo python app.py
    echo pause
) > "%APPDIR%\launcher_temp.bat"

REM Create VBScript to create shortcut (Windows-specific)
(
    echo Set oWS = WScript.CreateObject("WScript.Shell"^)
    echo sLinkFile = "%DESKTOP%\Zzzuper PDF.lnk"
    echo Set oLink = oWS.CreateShortcut(sLinkFile^)
    echo oLink.TargetPath = "%APPDIR%\launcher_temp.bat"
    echo oLink.WorkingDirectory = "%APPDIR%"
    echo oLink.Description = "Zzzuper PDF - Web Application"
    echo oLink.IconLocation = "%APPDIR%\icon.ico"
    echo oLink.Save
) > "%APPDIR%\create_shortcut.vbs"

REM Run VBScript
cscript //nologo "%APPDIR%\create_shortcut.vbs"

REM Clean up
del "%APPDIR%\create_shortcut.vbs"

echo.
echo Shortcut created on Desktop!
echo Double-click "Zzzuper PDF" on your desktop to launch the application.
echo.
pause
