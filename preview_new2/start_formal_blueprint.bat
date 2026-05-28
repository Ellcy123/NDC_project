@echo off
setlocal

cd /d "%~dp0"
set PORT=8790
set PYTHON_EXE=D:\NDC\.uv-python\cpython-3.11.14-windows-x86_64-none\python.exe
set URL=http://127.0.0.1:%PORT%/flow_blueprint.html

echo Starting NDC formal blueprint...
echo %URL%
start "" "%URL%"
"%PYTHON_EXE%" -m http.server %PORT% --bind 127.0.0.1 --directory "%CD%"

endlocal
