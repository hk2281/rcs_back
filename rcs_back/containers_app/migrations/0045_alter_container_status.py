# Generated by Django 3.2.5 on 2021-09-25 18:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('containers_app', '0044_remove_tanktakeoutcompany_is_active'),
    ]

    operations = [
        migrations.AlterField(
            model_name='container',
            name='status',
            field=models.PositiveSmallIntegerField(choices=[(1, 'ожидает подключения'), (2, 'активный'), (3, 'не активный'), (4, 'распечатан стикер, контейнер не выбран')], default=2, verbose_name='состояние'),
        ),
    ]