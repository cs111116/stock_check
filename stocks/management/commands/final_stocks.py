from django.core.management.base import BaseCommand
from stocks.utils import check_final_stocks

class Command(BaseCommand):
    help = '檢查所有用戶的股票並發送每日收盤提醒'

    def handle(self, *args, **options):
        self.stdout.write('開始檢查股票收盤數據...')
        check_final_stocks()
        self.stdout.write(self.style.SUCCESS('成功完成股票收盤檢查')) 