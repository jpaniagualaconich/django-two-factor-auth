# Generated by Django 3.1.5 on 2021-02-02 13:17

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('two_factor', '0007_auto_20201201_1019'),
    ]

    operations = [
        migrations.CreateModel(
            name='WebauthnDevice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='The human-readable name of this device.', max_length=64)),
                ('confirmed', models.BooleanField(default=True, help_text='Is this device ready for use?')),
                ('throttling_failure_timestamp', models.DateTimeField(blank=True, default=None, help_text='A timestamp of the last failed verification attempt. Null if last attempt succeeded.', null=True)),
                ('throttling_failure_count', models.PositiveIntegerField(default=0, help_text='Number of successive failed attempts.')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_used_at', models.DateTimeField(null=True)),
                ('public_key', models.TextField(unique=True)),
                ('key_handle', models.TextField()),
                ('sign_count', models.IntegerField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='webauthn_keys', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
