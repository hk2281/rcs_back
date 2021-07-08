# Generated by Django 3.2.5 on 2021-07-07 16:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('containers_app', '0007_building_is_full'),
    ]

    operations = [
        migrations.AddField(
            model_name='building',
            name='enough_full_containers_count',
            field=models.PositiveSmallIntegerField(default=2, verbose_name='достаточное количество контейнеров для выноса'),
            preserve_default=False,
        ),
    ]