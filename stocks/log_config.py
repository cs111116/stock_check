# log_config.py
import logging
from datetime import datetime
import os
def setup_logging(log_file='stock_check.log', log_level=logging.INFO):
    try:
        today = datetime.today().strftime('%Y-%m-%d')
        log_dir = os.path.join(os.path.dirname(__file__), 'logs')  # 指定日誌目錄
        os.makedirs(log_dir, exist_ok=True)  # 確保目錄存在
        log_file = os.path.join(log_dir, f"stock_check_{today}.log")  # 在 logs 資料夾內創建日誌文件

        logging.basicConfig(
            filename=log_file,  # 設定基於日期的 log 文件名稱
            level=log_level,  # 設定日誌等級
            format='%(asctime)s - %(levelname)s - %(message)s',  # 日誌格式
            encoding='utf-8'
        )
    except PermissionError as e:
        print(f"日誌檔案創建失敗，權限錯誤: {e}")
    except Exception as e:
        print(f"其他錯誤: {e}")
def logging_info(message):
    logging.info(message)
def logging_error(message):
    logging.error(message)