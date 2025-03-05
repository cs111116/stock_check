from django.core.management.base import BaseCommand
from stocks.utils import check_stock_prices

class Command(BaseCommand):
    help = 'Check stock prices and send alerts'

    def handle(self, *args, **kwargs):
        check_stock_prices()
        self.stdout.write(self.style.SUCCESS('Successfully checked stock prices'))
