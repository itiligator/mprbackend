# Generated by Django 3.0.5 on 2020-05-16 08:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0029_auto_20200516_1448'),
    ]

    operations = [
        migrations.AddField(
            model_name='checklistquestion',
            name='section',
            field=models.CharField(default='default section', max_length=200),
            preserve_default=False,
        ),
    ]
