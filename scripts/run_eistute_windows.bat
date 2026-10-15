@echo off
setlocal EnableExtensions
cd /d "%~dp0.."

if exist results\eistute rmdir /s /q results\eistute
mkdir results\eistute
if not "%ERRORLEVEL%"=="0" exit /b 1

build\bin\ap_mesh.exe --config configs\eistute\article.conf > results\eistute\run.log 2>&1
set "RUN_RC=%ERRORLEVEL%"

if not "%RUN_RC%"=="0" (
  echo ERROR: Eistute execution failed before verification. Exit code: %RUN_RC%
  if exist results\eistute\run.log type results\eistute\run.log
  exit /b 1
)

type results\eistute\run.log

python scripts\verify_eistute.py results\eistute
set "VERIFY_RC=%ERRORLEVEL%"
if not "%VERIFY_RC%"=="0" exit /b 1

exit /b 0
