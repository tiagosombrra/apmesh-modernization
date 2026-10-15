@echo off
setlocal
cd /d "%~dp0"

call scripts\build_windows.bat || exit /b 1
call scripts\run_book_windows.bat || exit /b 1
call scripts\run_eistute_windows.bat || exit /b 1
call scripts\run_decor_shelf_windows.bat || exit /b 1

echo.
echo All three article model runs completed successfully.
