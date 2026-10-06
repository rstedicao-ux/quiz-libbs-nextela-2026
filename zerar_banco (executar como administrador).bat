@echo off
setlocal
cd /d "%~dp0"
where docker >nul 2>&1
if errorlevel 1 (
  echo Docker nao encontrado. Instale o Docker Desktop.
  goto :erro
)
docker info >nul 2>&1
if errorlevel 1 (
  echo Inicie o Docker Desktop e execute este arquivo novamente.
  goto :erro
)
docker compose run --rm --build --no-deps -T backend python reset_db.py
if errorlevel 1 goto :erro
echo Contadores zerados: numero_usuarios, pergunta_N_acertos e usuarios_com_N_acertos.
echo Todas as participacoes e respostas foram apagadas.
echo Recarregue as paginas abertas antes de iniciar um novo quiz.
pause
exit /b 0
:erro
echo Nao foi possivel zerar o banco. Verifique os erros acima.
pause
exit /b 1
