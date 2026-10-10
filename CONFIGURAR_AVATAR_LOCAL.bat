@echo off
setlocal
set "AVATAR_ENV=%USERPROFILE%\VesteIA-Avatar-Local\.venv"
echo Feche somente a IA CatVTON para liberar memoria antes de configurar.
if not exist "%AVATAR_ENV%\Scripts\python.exe" py -3.12 -m venv "%AVATAR_ENV%"
if errorlevel 1 goto :erro
"%AVATAR_ENV%\Scripts\python.exe" -m pip install torch==2.5.1 torchvision==0.20.1 --index-url https://download.pytorch.org/whl/cu121
if errorlevel 1 goto :erro
"%AVATAR_ENV%\Scripts\python.exe" -m pip install -r "%~dp0integracao\avatar\requirements.txt"
if errorlevel 1 goto :erro
"%AVATAR_ENV%\Scripts\python.exe" "%~dp0integracao\avatar\engine.py" --download
if errorlevel 1 goto :erro
echo Configuracao concluida. Execute INICIAR_AVATAR_LOCAL.bat.
pause
exit /b 0
:erro
echo Configuracao nao concluida. Mantenha este terminal e envie o erro.
pause
exit /b 1
