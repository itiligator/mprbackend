# Generated by Django 3.0.5 on 2020-05-04 11:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0014_auto_20200504_1753'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='visit',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='api.Visit'),
        ),
    ]
