# Generated by Django 4.0.3 on 2023-08-23 06:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pets', '0010_order_seller'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='total_price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='total_price'),
        ),
    ]