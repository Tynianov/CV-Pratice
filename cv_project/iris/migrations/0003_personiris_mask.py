# Generated by Django 2.2.11 on 2020-05-20 20:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('iris', '0002_personiriscompare'),
    ]

    operations = [
        migrations.AddField(
            model_name='personiris',
            name='mask',
            field=models.BinaryField(blank=True, null=True),
        ),
    ]
