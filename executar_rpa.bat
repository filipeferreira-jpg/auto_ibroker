@echo off
setlocal

if not exist "%~dp0.venv\Scripts\activate.bat" (
    echo [ERRO] Ambiente .venv nao encontrado na pasta do projeto. 1>&2
    exit /b 1
)

if not exist "%~dp0.venv\Scripts\python.exe" (
    echo [ERRO] Python da .venv nao encontrado. 1>&2
    exit /b 1
)

if not exist "%~dp0main.py" (
    echo [ERRO] main.py nao encontrado na pasta do projeto. 1>&2
    exit /b 1
)

pushd "%~dp0"
if errorlevel 1 (
    echo [ERRO] Nao foi possivel acessar a pasta do projeto. 1>&2
    exit /b 1
)

call "%~dp0.venv\Scripts\activate.bat"
if errorlevel 1 (
    echo [ERRO] Falha ao ativar a .venv. 1>&2
    popd
    exit /b 1
)

"%~dp0.venv\Scripts\python.exe" -u "%~dp0main.py"
set "RPA_EXIT_CODE=%ERRORLEVEL%"
popd
endlocal & exit /b %RPA_EXIT_CODE%
