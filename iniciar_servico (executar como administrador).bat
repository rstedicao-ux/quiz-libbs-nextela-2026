@echo off
setlocal
cd /d "%~dp0"
where docker >nul 2>&1
if errorlevel 1 (
  echo Instale o Docker Desktop com Docker Compose e execute novamente.
  goto :erro
)
docker info >nul 2>&1
if not errorlevel 1 goto :subir
if exist "%ProgramFiles%\Docker\Docker\Docker Desktop.exe" (
  powershell -NoProfile -Command "Start-Process -FilePath ($env:ProgramFiles + '\Docker\Docker\Docker Desktop.exe') -WindowStyle Hidden"
) else (
  echo Inicie o Docker Desktop e tente novamente.
  goto :erro
)
echo Aguardando o Docker iniciar...
for /l %%i in (1,1,60) do (
  docker info >nul 2>&1
  if not errorlevel 1 goto :subir
  timeout /t 2 /nobreak >nul
)
echo O Docker nao ficou disponivel em 120 segundos.
goto :erro
:subir
docker compose up -d --wait --wait-timeout 120
if errorlevel 1 goto :erro
start "" "http://localhost:8090/index.html"
exit /b 0
:erro
echo Nao foi possivel iniciar o servico. Verifique os erros acima.
pause
exit /b 1
