# Generated by Django 2.2.11 on 2020-05-21 14:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('person', '0003_auto_20200520_1903'),
        ('log_entry', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='logentry',
            name='person',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='person.Person'),
        ),
    ]
