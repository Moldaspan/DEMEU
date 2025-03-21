# Generated by Django 5.1.5 on 2025-03-16 18:46

import django.db.models.deletion
import profiles.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('country', models.CharField(blank=True, max_length=100, null=True)),
                ('city', models.CharField(blank=True, max_length=100, null=True)),
                ('phone_number', models.CharField(blank=True, max_length=15, null=True)),
                ('bio', models.TextField(blank=True, null=True)),
                ('instagram', models.URLField(blank=True, max_length=255, null=True)),
                ('whatsapp', models.URLField(blank=True, max_length=255, null=True)),
                ('facebook', models.URLField(blank=True, max_length=255, null=True)),
                ('telegram', models.URLField(blank=True, max_length=255, null=True)),
                ('birth_date', models.DateField(blank=True, null=True)),
                ('avatar', models.ImageField(blank=True, null=True, upload_to='avatars/', validators=[profiles.models.validate_image_size])),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ProfileView',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('viewed_at', models.DateTimeField(auto_now_add=True)),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='views', to='profiles.profile')),
                ('viewer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('profile', 'viewer')},
            },
        ),
    ]
