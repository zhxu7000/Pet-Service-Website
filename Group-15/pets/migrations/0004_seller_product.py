# Generated by Django 4.0.3 on 2023-08-18 10:10

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('pets', '0003_pet_temperament'),
    ]

    operations = [
        migrations.CreateModel(
            name='Seller',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=255, verbose_name='username')),
                ('password', models.CharField(max_length=255, verbose_name='password')),
                ('email', models.CharField(max_length=255, verbose_name='email')),
                ('age', models.IntegerField(verbose_name='age')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='create time')),
            ],
            options={
                'verbose_name': 'seller',
                'verbose_name_plural': 'seller',
                'db_table': 'seller',
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='title')),
                ('desc', models.TextField(verbose_name='desc')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='price')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='create time')),
                ('image', models.ImageField(upload_to='', verbose_name='image')),
                ('seller', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pets.seller', verbose_name='seller')),
            ],
            options={
                'verbose_name': 'product',
                'verbose_name_plural': 'product',
                'db_table': 'product',
            },
        ),
    ]
