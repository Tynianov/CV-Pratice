# Generated by Django 2.2.11 on 2020-05-20 19:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('person', '0002_auto_20200520_0720'),
    ]

    operations = [
        migrations.AlterField(
            model_name='personimage',
            name='encoding',
            field=models.BinaryField(blank=True, null=True),
        ),
    ]
