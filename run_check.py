#!/usr/bin/env python
import os
import sys
import time
import schedule
from datetime import datetime, time as dtime
from stocks.log_config import setup_logging, logging_info

def run_check_stocks():
    """執行 check_stocks 命令"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stock_alert.settings')
    try:
        from django.core.management import execute_from_command_line
        sys.argv = [sys.argv[0], 'check_stocks']
        execute_from_command_line(sys.argv)
    except Exception as e:
        logging_info(f"執行 check_stocks 時發生錯誤: {str(e)}")

def run_final_stocks():
    """執行 final_stocks 命令"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
    try:
        from django.core.management import execute_from_command_line
        sys.argv = [sys.argv[0], 'final_stocks']
        execute_from_command_line(sys.argv)
    except Exception as e:
        logging_info(f"執行 final_stocks 時發生錯誤: {str(e)}")

def should_run():
    """檢查是否應該執行（只在工作日執行）"""
    now = datetime.now()
    # 0 = 星期一, 6 = 星期日
    if now.weekday() >= 5:  # 週末不執行
        return False
    return True

def main():
    setup_logging()
    logging_info("排程開始執行...")

    # 檢查當前時間是否在交易時間內
    now = datetime.now()
    if should_run() and dtime(9,0) <= now.time() <= dtime(13,30):
        logging_info("執行初始檢查...")
        run_check_stocks()

    # 設定 check_stocks 在 9:00 到 13:30 之間每五分鐘執行一次
    for minute in range(0, 60, 5):  # 每五分鐘執行一次：0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55
        schedule.every().hour.at(f":{minute:02d}").do(
            lambda: run_check_stocks() if should_run() and 
            dtime(9,0) <= datetime.now().time() <= dtime(13,30) 
            else None
        )

    # 設定 final_stocks 在每天 14:00 執行
    schedule.every().day.at("14:00").do(
        lambda: run_final_stocks() if should_run() else None
    )

    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    main()
