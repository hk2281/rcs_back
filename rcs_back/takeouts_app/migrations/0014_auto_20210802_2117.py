# Generated by Django 3.2.5 on 2021-08-02 18:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('takeouts_app', '0013_containerstakeoutrequest_building_part'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='TakeoutCompany',
            new_name='TankTakeoutCompany',
        ),
        migrations.AlterModelOptions(
            name='tanktakeoutcompany',
            options={'verbose_name': 'компания, вывоза бака', 'verbose_name_plural': 'компании, вывоз бака'},
        ),
    ]
