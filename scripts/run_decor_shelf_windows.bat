@echo off
setlocal EnableExtensions
cd /d "%~dp0.."

if exist results\decor_shelf rmdir /s /q results\decor_shelf
mkdir results\decor_shelf
if not "%ERRORLEVEL%"=="0" exit /b 1

build\bin\ap_mesh.exe --config configs\decor_shelf\article.conf > results\decor_shelf\run.log 2>&1
set "RUN_RC=%ERRORLEVEL%"

if not "%RUN_RC%"=="0" (
  echo ERROR: Decor Shelf execution failed before verification. Exit code: %RUN_RC%
  if exist results\decor_shelf\run.log type results\decor_shelf\run.log
  exit /b 1
)

type results\decor_shelf\run.log

python scripts\verify_decor_shelf.py results\decor_shelf
set "VERIFY_RC=%ERRORLEVEL%"
if not "%VERIFY_RC%"=="0" exit /b 1

exit /b 0
