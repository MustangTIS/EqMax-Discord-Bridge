@echo off
setlocal
cd /d %~dp0

echo ==========================================
echo    EqMax Discord Bridge - Startup Manager
echo ==========================================
echo [Status]  : Initializing system...
echo [Version] : v5.0.2 Hotfix (Config Sync)
echo [Author]  : Mustang_TIS
echo ==========================================
echo.

rem 1. Pythonチェック
echo [Step 1/2] Checking Python environment...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [Error] Python not found.
    echo [Action] Redirecting to download page...
    start https://www.python.org/downloads/
    pause
    exit /b
)

rem 2. メインハブの起動を試みる
if exist "Core\00-TOP_HUB.py" (
    echo [Step 2/2] Booting Hub System...
    echo [Message] Please wait a moment...
    python "Core\00-TOP_HUB.py"
) else (
    echo [Error] Core\00-TOP_HUB.py not found.
    echo [Path]  Current: %cd%
    pause
    exit /b
)

rem 3. 失敗時の自動修復
if %errorlevel% neq 0 (
    echo.
    echo [Warning] Startup failed.
    echo [Repair]  Running library maintenance...
    if exist "Pythonset\Python_SET.bat" (
        call "Pythonset\Python_SET.bat"
        echo [Action]  Restarting Hub...
        python "Core\00-TOP_HUB.py"
    ) else (
        echo [Fatal]   Python_SET.bat not found.
        pause
    )
)

endlocal