# Generated by Django 5.1.6 on 2025-03-11 09:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stocks', '0005_rename_close_price_stockdata_close_and_more'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='stockdata',
            unique_together={('symbol', 'date')},
        ),
    ]
