# Generated by Django 5.1.5 on 2025-01-15 19:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_remove_user_two_factor_enabled_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='verification_token_expiry',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]