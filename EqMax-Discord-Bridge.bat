@echo off
setlocal
cd /d %~dp0

echo ==========================================
echo    EqMax Discord Bridge - Startup Manager
echo ==========================================
echo [Status]  : Initializing system...
echo [Version] : v7.0.2
echo [Author]  : Mustang_TIS
echo ==========================================
echo.
echo Checking Booting Systems.....
echo [Step 1/2] Checking libraries...

:PYTHON_CHECK
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [Error] Python が見つかりません。
    start https://www.python.org/downloads/
    pause
    exit /b
)

:LIBRARY_CHECK
python -c "import psutil, requests, PIL, customtkinter" >nul 2>&1
if %errorlevel% neq 0 (
    echo [Notice] ライブラリをインストールしています...
    python -m pip install --upgrade pip
    python -m pip install psutil requests Pillow customtkinter --prefer-binary
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
    python "Core\00-TOP_HUB.py"
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
echo 【解決策】 Python 3.10 または 3.11 の導入を推奨します。
echo ------------------------------------------
pause
exit /b

:EOF
endlocal