# Generated by Django 3.0.5 on 2020-06-01 02:52

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api', '0033_auto_20200520_1030'),
    ]

    operations = [
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('INN', models.CharField(max_length=12, unique=True)),
                ('client_type', models.CharField(blank=True, max_length=100, null=True)),
                ('price_type', models.CharField(blank=True, max_length=100, null=True)),
                ('delay', models.IntegerField(default=0)),
                ('limit', models.IntegerField(default=0)),
                ('email', models.CharField(blank=True, max_length=50, null=True)),
                ('phone', models.CharField(blank=True, max_length=10, null=True)),
                ('status', models.BooleanField(default=True)),
                ('database', models.BooleanField(default=True)),
                ('authorized_managers', models.ManyToManyField(blank=True, related_name='authorized_managers', to=settings.AUTH_USER_MODEL)),
                ('manager', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='clientmanager', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]