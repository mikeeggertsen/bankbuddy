# Generated by Django 3.2.13 on 2022-06-01 16:18

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('authsystem', '0015_alter_verificationcode_expires_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='verificationcode',
            name='expires_at',
            field=models.DateTimeField(default=datetime.datetime(2022, 6, 1, 16, 33, 29, 351375, tzinfo=utc)),
        ),
    ]
