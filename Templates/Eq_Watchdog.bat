@echo off
setlocal
:: 実行されている場所へ移動
cd /d "%~dp0"

echo ==========================================
echo     EqMax Watchdog - Boot Loader
echo ==========================================
echo [Status]  : Initializing system...
echo [Author]  : Mustang_TIS
echo ==========================================
echo.

:PYTHON_CHECK
echo [Step 1] Checking Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [Error] Pythonが見つかりません。パスが通っているか確認してください。
    pause
    exit /b
)

:LIBRARY_CHECK
echo [Step 2] Checking Libraries...
:: 2>&1 を外して、エラーが出たら画面で見えるようにします
python -c "import psutil, requests, PIL, customtkinter"
if %errorlevel% neq 0 (
    echo [Notice] 不足しているライブラリをインストールします...
    python -m pip install psutil requests Pillow customtkinter --prefer-binary
    if %errorlevel% neq 0 (
        echo [Error] インストールに失敗しました。
        pause
    )
)

:BOOT_Guardian
:: ★ここを Eq_Watchdog.py に修正しました★
if exist "Eq_Watchdog.py" (
    echo [Step 3] Launching Guardian System...
    echo.
    
    :: 実行
    python "Eq_Watchdog.py"
    
    echo.
    echo ------------------------------------------
    echo [System] プロセスが終了しました。 Code: %errorlevel%
    echo ------------------------------------------
    pause
) else (
    echo [Error] Eq_Watchdog.py が見つかりません。
    echo 現在地: %cd%
    echo フォルダ内に Eq_Watchdog.py があるか確認してください。
    pause
)

exit /b