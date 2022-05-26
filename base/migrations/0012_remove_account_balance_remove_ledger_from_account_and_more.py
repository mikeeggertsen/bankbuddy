# Generated by Django 4.0.4 on 2022-05-25 14:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0011_remove_ledger_bank'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='account',
            name='balance',
        ),
        migrations.RemoveField(
            model_name='ledger',
            name='from_account',
        ),
        migrations.RemoveField(
            model_name='ledger',
            name='to_account',
        ),
        migrations.AddField(
            model_name='ledger',
            name='account',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='base.account'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='employee',
            name='department',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Support'), (2, 'Manager')]),
        ),
    ]
