# Generated by Django 3.0.5 on 2020-05-04 10:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0013_auto_20200504_1743'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='delivered_quantity',
            field=models.SmallIntegerField(),
        ),
        migrations.AlterField(
            model_name='order',
            name='ordered_quantity',
            field=models.SmallIntegerField(),
        ),
        migrations.AlterField(
            model_name='order',
            name='recommended_quantity',
            field=models.SmallIntegerField(),
        ),
        migrations.AlterField(
            model_name='order',
            name='stock_quantity',
            field=models.SmallIntegerField(),
        ),
    ]
