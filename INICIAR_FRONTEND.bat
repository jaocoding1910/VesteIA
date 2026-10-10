@echo off
setlocal
cd /d "%~dp0frontend"
if not exist "node_modules" (
  call npm install
  if errorlevel 1 goto failed
)
call npm run dev -- --host 127.0.0.1 --port 5173 --strictPort
pause
exit /b
:failed
echo Nao foi possivel iniciar. Confira Node.js e o erro acima.
pause
exit /b 1
