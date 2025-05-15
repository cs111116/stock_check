@echo off
chcp 65001
echo 啟動股票監控系統...

:: 切換到腳本所在目錄
cd /d "%~dp0"

:: 檢查是否已經在運行
tasklist /FI "WINDOWTITLE eq run_check.py" | find "python.exe" > nul
if %errorlevel% equ 0 (
    echo 股票監控系統已經在運行中！
    echo 您可以查看 stock_check.log 來監控運行狀況
    echo.
    echo 按任意鍵退出...
    pause > nul
    exit
)

:: 設定虛擬環境路徑
set VENV_PATH=venv\Scripts\activate

:: 啟動虛擬環境
call %VENV_PATH%

:: 執行 Python 腳本（添加標題以便識別）
start /B "run_check.py" python run_check.py > stock_check.log 2>&1

echo 股票監控系統已在背景啟動
echo 您可以查看 stock_check.log 來監控運行狀況
echo.

:: 創建檢查腳本
echo @echo off > check_status.bat
echo chcp 65001 >> check_status.bat
echo echo 檢查股票監控系統狀態... >> check_status.bat
echo tasklist /FI "WINDOWTITLE eq run_check.py" ^| find "python.exe" >> check_status.bat
echo if %%errorlevel%% equ 0 ( >> check_status.bat
echo     echo 系統正在運行中 >> check_status.bat
echo     echo 最近的日誌內容： >> check_status.bat
echo     type stock_check.log >> check_status.bat
echo ) else ( >> check_status.bat
echo     echo 系統未在運行！ >> check_status.bat
echo ) >> check_status.bat
echo pause >> check_status.bat

echo 已創建 check_status.bat 用於檢查系統狀態
echo 按任意鍵退出...
pause > nul