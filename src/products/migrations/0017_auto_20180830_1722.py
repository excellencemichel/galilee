# Generated by Django 2.0.7 on 2018-08-30 16:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0016_auto_20180829_0352'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='price',
            field=models.DecimalField(decimal_places=2, default=39.99, max_digits=20),
        ),
    ]
