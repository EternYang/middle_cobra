# Generated by Django 2.0.6 on 2018-07-26 04:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app01', '0008_auto_20180726_1150'),
    ]

    operations = [
        migrations.AddField(
            model_name='member',
            name='is_active',
            field=models.IntegerField(choices=[(0, '未激活(no active)'), (1, '已激活(activation)')], default=0, verbose_name='是否激活'),
        ),
    ]
