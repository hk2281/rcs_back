# Generated by Django 3.2.5 on 2021-09-25 16:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('containers_app', '0042_building_precollected_mass'),
    ]

    operations = [
        migrations.AddField(
            model_name='building',
            name='passage_scheme',
            field=models.ImageField(blank=True, null=True, upload_to='', verbose_name='схема проезда'),
        ),
    ]