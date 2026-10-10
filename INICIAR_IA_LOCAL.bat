@echo off
setlocal
set "VESTEIA_AJUSTES=%~dp0integracao\catvton\ajustes_ia.json"
set "CAT_ROOT=%USERPROFILE%\VesteIA-IA-Local\CatVTON"
set "CAT_PY=%USERPROFILE%\VesteIA-IA-Local\.venv\Scripts\python.exe"
if not exist "%CAT_ROOT%\app.py" (
 echo Nao encontrei %CAT_ROOT%\app.py. Ajuste CAT_ROOT neste arquivo.
 pause
 exit /b 1
)
if not exist "%CAT_PY%" (
 echo Nao encontrei o ambiente Python do CatVTON. Ajuste CAT_PY neste arquivo.
 pause
 exit /b 1
)
copy /Y "%~dp0integracao\catvton\vesteia_worker.py" "%CAT_ROOT%\vesteia_worker.py" >nul
if errorlevel 1 (
 echo Nao consegui copiar a ponte para a pasta CatVTON.
 pause
 exit /b 1
)
echo Feche o CatVTON antigo em 7860 antes de continuar para liberar a GPU.
cd /d "%CAT_ROOT%"
"%CAT_PY%" vesteia_worker.py --output_dir resource/demo/output --width 384 --height 512 --mixed_precision bf16 --allow_tf32
pause
