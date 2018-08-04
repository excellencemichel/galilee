# Generated by Django 2.0.7 on 2018-07-31 22:26

import django.core.files.storage
from django.db import migrations, models
import products.models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0003_productfile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productfile',
            name='file',
            field=models.FileField(storage=django.core.files.storage.FileSystemStorage(location='/home/michel/galilee/static_cdn/protected_root'), upload_to=products.models.upload_product_file_loc),
        ),
    ]
