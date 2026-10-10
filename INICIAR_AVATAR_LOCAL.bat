@echo off
setlocal
set "AVATAR_PY=%USERPROFILE%\VesteIA-Avatar-Local\.venv\Scripts\python.exe"
if not exist "%AVATAR_PY%" (
 echo Execute CONFIGURAR_AVATAR_LOCAL.bat primeiro.
 pause
 exit /b 1
)
"%AVATAR_PY%" "%~dp0integracao\avatar\server.py"
pause
