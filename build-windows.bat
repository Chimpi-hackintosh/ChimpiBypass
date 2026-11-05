@echo off
setlocal
cd /d "%~dp0"
py -3 -m pip install --upgrade pyinstaller || exit /b 1
py -3 -m PyInstaller --clean --onefile --windowed --name ChimpiBypass chimpibypass.py || exit /b 1
echo dist\ChimpiBypass.exe
pause
