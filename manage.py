#!/usr/bin/env python
import os
import sys
from stocks.log_config import setup_logging
def main():
    setup_logging()
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stock_alert.settings')
    # 確保在腳本中正確加載 Django
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    # 確保執行 check_stocks 命令
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
