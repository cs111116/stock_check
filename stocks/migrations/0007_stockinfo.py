# Generated by Django 5.1.6 on 2025-03-12 08:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stocks', '0006_alter_stockdata_unique_together'),
    ]

    operations = [
        migrations.CreateModel(
            name='StockInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stock_code', models.CharField(max_length=10, unique=True)),
                ('stock_name', models.CharField(max_length=100)),
                ('market_type', models.IntegerField(choices=[(1, 'Listed'), (2, 'OTC')])),
                ('security_type', models.IntegerField(choices=[(1, 'Stock'), (2, 'ETF')])),
                ('industry', models.CharField(max_length=50)),
            ],
        ),
    ]
