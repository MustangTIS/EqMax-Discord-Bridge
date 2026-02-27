@echo off
setlocal
cd /d %~dp0

echo ==========================================
echo    EqMax Discord Bridge Hub System
echo ==========================================

rem 1. Pythonチェック
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [エラー] Pythonが見つかりません。
    start https://www.python.org/downloads/
    pause
    exit /b
)

rem 2. メインハブの起動を試みる
if exist "Core\00-TOP_HUB.py" (
    python "Core\00-TOP_HUB.py"
) else (
    echo [エラー] Core\00-TOP_HUB.py が見つかりません。
    pause
    exit /b
)

rem 3. 失敗時の自動修復 (ここを独立させる)
if %errorlevel% neq 0 (
    echo.
    echo [情報] 起動に失敗しました。ライブラリを更新します...
    if exist "Pythonset\Python_SET.bat" (
        call "Pythonset\Python_SET.bat"
        echo 再起動しています...
        python "Core\00-TOP_HUB.py"
    ) else (
        echo [エラー] Python_SET.bat が見つかりません。
        pause
    )
)

endlocal