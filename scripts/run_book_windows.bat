@echo off
setlocal EnableExtensions
cd /d "%~dp0.."

if exist results\book rmdir /s /q results\book
mkdir results\book
if not "%ERRORLEVEL%"=="0" exit /b 1

build\bin\ap_mesh.exe --config configs\book\article.conf > results\book\run.log 2>&1
set "RUN_RC=%ERRORLEVEL%"

if not "%RUN_RC%"=="0" (
  echo ERROR: Book execution failed before verification. Exit code: %RUN_RC%
  if exist results\book\run.log type results\book\run.log
  exit /b 1
)

type results\book\run.log

python scripts\verify_book.py results\book
set "VERIFY_RC=%ERRORLEVEL%"
if not "%VERIFY_RC%"=="0" exit /b 1

exit /b 0
