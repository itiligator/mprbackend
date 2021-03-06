# Generated by Django 3.0.5 on 2020-05-18 04:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0030_checklistquestion_section'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='checklistanswer',
            unique_together={('visit', 'question')},
        ),
        migrations.AlterOrderWithRespectTo(
            name='checklistanswer',
            order_with_respect_to='visit',
        ),
        migrations.AlterOrderWithRespectTo(
            name='checklistquestion',
            order_with_respect_to='client_type',
        ),
    ]
