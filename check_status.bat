@echo off 
chcp 65001 
echo 檢查股票監控系統狀態... 
tasklist /FI "WINDOWTITLE eq run_check.py" | find "python.exe" 
if %errorlevel% equ 0 ( 
    echo 系統正在運行中 
    echo 最近的日誌內容： 
    type stock_check.log 
) else ( 
    echo 系統未在運行！ 
) 
pause 
