# Generated by Django 3.0.5 on 2020-05-05 09:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0018_userprofile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='manager_ID',
            field=models.CharField(max_length=200, null=True),
        ),
    ]