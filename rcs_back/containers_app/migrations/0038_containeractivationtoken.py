# Generated by Django 3.2.5 on 2021-09-06 10:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('containers_app', '0037_remove_container_sticker'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContainerActivationToken',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.CharField(blank=True, max_length=32, verbose_name='токен')),
                ('container', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='activation_token', to='containers_app.container', verbose_name='контейнер')),
            ],
            options={
                'verbose_name': 'токен для активации контейнера',
                'verbose_name_plural': 'токены для активации контейнеров',
            },
        ),
    ]