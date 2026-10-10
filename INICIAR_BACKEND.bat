@echo off
setlocal
cd /d "%~dp0backend"
if not exist ".env" (
  copy ".env.example" ".env" >nul
  echo Criamos backend\.env a partir do modelo. O provador inicia SEM banco de dados.
)
if not exist ".venv312\Scripts\python.exe" (
  py -3.12 -m venv .venv312
  if errorlevel 1 goto failed
)
".venv312\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto failed
".venv312\Scripts\python.exe" -m uvicorn app.main:app --host 127.0.0.1 --port 8000
pause
exit /b
:failed
echo Nao foi possivel iniciar. Confira o erro acima. E necessario Python 3.12.
pause
exit /b 1
