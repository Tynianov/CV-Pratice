# Generated by Django 2.2.11 on 2020-05-21 14:19

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='LogEntry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('authorization_type', models.CharField(choices=[('face', 'Face'), ('fingerprint', 'Fingerprint'), ('iris', 'Iris')], default='face', max_length=11)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('result', models.BooleanField(default=False)),
                ('image', models.ImageField(upload_to='log_entries')),
            ],
        ),
    ]
