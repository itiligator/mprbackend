# Generated by Django 3.0.5 on 2020-04-13 08:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_auto_20200410_0003'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderitem',
            name='quantity',
            field=models.PositiveSmallIntegerField(),
        ),
    ]
