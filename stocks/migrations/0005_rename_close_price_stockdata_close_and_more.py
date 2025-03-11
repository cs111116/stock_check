# Generated by Django 5.1.6 on 2025-03-11 08:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stocks', '0004_stockdata'),
    ]

    operations = [
        migrations.RenameField(
            model_name='stockdata',
            old_name='close_price',
            new_name='close',
        ),
        migrations.RenameField(
            model_name='stockdata',
            old_name='high_price',
            new_name='high',
        ),
        migrations.RenameField(
            model_name='stockdata',
            old_name='low_price',
            new_name='low',
        ),
        migrations.RenameField(
            model_name='stockdata',
            old_name='open_price',
            new_name='open',
        ),
        migrations.AddField(
            model_name='stockdata',
            name='stock_splits',
            field=models.DecimalField(decimal_places=2, default=1, max_digits=10),
        ),
    ]
