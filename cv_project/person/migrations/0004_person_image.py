# Generated by Django 2.2.11 on 2020-05-26 21:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('person', '0003_auto_20200520_1903'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='avatars'),
        ),
    ]