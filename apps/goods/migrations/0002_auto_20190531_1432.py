# Generated by Django 2.2.1 on 2019-05-31 06:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('goods', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='goods',
            name='image',
            field=models.ImageField(upload_to='goods/', verbose_name='商品图片'),
        ),
    ]
