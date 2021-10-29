# Generated by Django 3.2.5 on 2021-09-06 10:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('containers_app', '0038_containeractivationtoken'),
        ('takeouts_app', '0025_takeoutcondition_building'),
    ]

    operations = [
        migrations.AlterField(
            model_name='takeoutcondition',
            name='building',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='takeout_condition', to='containers_app.building', verbose_name='здание'),
        ),
        migrations.AlterField(
            model_name='takeoutcondition',
            name='building_part',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='takeout_condition', to='containers_app.buildingpart', verbose_name='корпус здания'),
        ),
    ]