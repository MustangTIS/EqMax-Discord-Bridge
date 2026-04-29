@echo off
setlocal
cd /d %~dp0

echo ==========================================
echo    EqMax Discord Bridge - Startup Manager
echo ==========================================
echo [Status]  : Initializing system...
echo [AppName] : EqMax Discord Bridge
echo [Author]  : Mustang_TIS
echo ==========================================
echo.
echo Checking Booting Systems.....
echo [Step 1/2] Checking Python Environment...

:PYTHON_CHECK
:: まず python コマンドを試す
python --version >nul 2>&1
if %errorlevel% equ 0 (
    set PY=python
    goto :PYTHON_OK
)

:: だめなら py コマンドを試す
py --version >nul 2>&1
if %errorlevel% equ 0 (
    set PY=py
    goto :PYTHON_OK
)

:: どちらもだめな場合
echo [Error] Python が見つかりません。
start https://www.python.org/downloads/
pause
exit /b

:PYTHON_OK
echo [Status] Using command: %PY%

:LIBRARY_CHECK
echo [Step 1/2] Checking libraries...
%PY% -c "import psutil, requests, PIL, customtkinter" >nul 2>&1
if %errorlevel% neq 0 (
    echo [Notice] ライブラリをインストールしています...
    %PY% -m pip install --upgrade pip
    %PY% -m pip install psutil requests Pillow customtkinter --prefer-binary
    if %errorlevel% neq 0 goto :VER_GUIDE
)

:BOOT_HUB
if exist "Core\00-TOP_HUB.py" (
    echo.
    echo [  OK  ] Booting System Check Complete!!
    echo ------------------------------------------
    echo  Launching Discord Bridge Hub System...
    echo ------------------------------------------
    echo [Step 2/2] Booting Hub System...
    %PY% "Core\00-TOP_HUB.py"
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
echo 【解決策】 Python 3.10 以上（3.12推奨）の導入を確認してください。
echo ------------------------------------------
pause
exit /b

:EOF
endlocal