# Generated by Django 4.0.4 on 2022-05-25 10:26

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('authsystem', '0002_verificationcode_expires_at_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='verificationcode',
            name='expires_at',
            field=models.DateTimeField(default=datetime.datetime(2022, 5, 25, 10, 27, 32, 751741, tzinfo=utc)),
        ),
    ]