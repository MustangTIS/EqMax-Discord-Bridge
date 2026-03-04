@echo off
setlocal
cd /d %~dp0

echo ==========================================
echo      EqMax Discord Bridge - Booter
echo ==========================================

:PYTHON_CHECK
echo [Step 1] Checking Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [Error] Python path is not found.
    pause
    exit /b
)

:LIBRARY_CHECK
echo [Step 2] Checking Libraries...
:: 特殊な記号を使わずシンプルに実行します
python -c "import psutil, requests, PIL, customtkinter" >nul 2>&1
if %errorlevel% neq 0 (
    echo [Notice] Installing missing libraries...
    python -m pip install --upgrade pip
    python -m pip install psutil requests Pillow customtkinter --prefer-binary
)

:BOOT_MAIN
if exist "eqmax_discord.py" (
    echo [Step 3] Launching System...
    echo.
    
    :: ここで Python を実行。終了後に必ず停止。
    cmd /c python "eqmax_discord.py"
    
    echo.
    echo ------------------------------------------
    echo [System] Process finished. Code: %errorlevel%
    echo ------------------------------------------
    pause
) else (
    echo [Error] eqmax_discord.py not found.
    pause
)

exit /b