# Generated by Django 5.0.6 on 2024-06-30 18:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_alter_userprofile_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='users',
            name='auth_provider',
            field=models.CharField(default='email', max_length=50),
        ),
    ]
