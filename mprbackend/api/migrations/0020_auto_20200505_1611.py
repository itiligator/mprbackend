# Generated by Django 3.0.5 on 2020-05-05 09:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0019_auto_20200505_1609'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='manager_ID',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
