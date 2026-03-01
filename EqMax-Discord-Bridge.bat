@echo off
setlocal
cd /d %~dp0

echo ==========================================
echo    EqMax Discord Bridge - Startup Manager
echo ==========================================
echo [Status]  : Initializing system...
echo [Version] : v5.4.5 (Auto-Repair & Guide)
echo ==========================================

:PYTHON_CHECK
rem 1. Python自体の存在チェック
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [Error] Python が見つかりません。
    start https://www.python.org/downloads/
    pause
    exit /b
)

:LIBRARY_CHECK
rem 2. 必須ライブラリのチェック
echo [Step 1/2] Checking libraries...
python -c "import psutil, requests, PIL, customtkinter" >nul 2>&1
if %errorlevel% neq 0 (
    echo [Notice] ライブラリをインストールしています...
    python -m pip install --upgrade pip
    python -m pip install psutil requests Pillow customtkinter --prefer-binary
    
    rem インストール失敗時の誘導
    if %errorlevel% neq 0 goto :VER_GUIDE
)

:BOOT_HUB
rem 3. メインシステムの起動
if exist "Core\00-TOP_HUB.py" (
    echo [Step 2/2] Booting Hub System...
    python "Core\00-TOP_HUB.py"
    
    rem 実行中にエラーで落ちた場合の誘導
    if %errorlevel% neq 0 goto :VER_GUIDE
) else (
    echo [Error] Core\00-TOP_HUB.py が見つかりません。
    pause
    exit /b
)

goto :EOF

:VER_GUIDE
echo.
echo ------------------------------------------
echo [!] トラブルが発生しました (Error Code: %errorlevel%)
echo ------------------------------------------
echo 原因として、使用中の Python バージョンとの互換性が考えられます。
echo.
echo 【解決策】
echo 現在の Python をアンインストールし、より安定した
echo 「Python 3.10」または「Python 3.11」の導入を推奨します。
echo.
echo [DLページ] https://www.python.org/downloads/windows/
echo ------------------------------------------
pause
exit /b

:EOF
endlocal