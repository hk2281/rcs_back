# Generated by Django 3.2.5 on 2021-08-08 11:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('takeouts_app', '0016_auto_20210805_2211'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='masstakeoutconditioncommit',
            options={'verbose_name': 'выполнено условие для сбора', 'verbose_name_plural': 'выполнены условия для сбора'},
        ),
    ]