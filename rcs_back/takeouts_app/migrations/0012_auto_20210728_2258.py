# Generated by Django 3.2.5 on 2021-07-28 19:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('containers_app', '0020_delete_takeoutconditionmet'),
        ('takeouts_app', '0011_auto_20210725_1230'),
    ]

    operations = [
        migrations.AlterField(
            model_name='takeoutcondition',
            name='type',
            field=models.PositiveSmallIntegerField(choices=[(1, 'не больше N дней в офисе'), (2, 'не больше N дней в общественном месте'), (3, 'суммарная масса бумаги в корпусе не больше N кг'), (4, 'игнорировать первые N сообщений о заполненности контейнера в общественном месте')], verbose_name='тип условия'),
        ),
        migrations.CreateModel(
            name='TakeoutConditionMet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='время создания')),
                ('building', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='full_containers_notifications', to='containers_app.building', verbose_name='здание')),
            ],
            options={
                'verbose_name': 'выполнено условие для выноса',
                'verbose_name_plural': 'выполнены условия для выноса',
            },
        ),
    ]
