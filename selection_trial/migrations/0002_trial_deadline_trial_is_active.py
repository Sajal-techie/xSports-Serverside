# Generated by Django 5.0.6 on 2024-07-05 06:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("selection_trial", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="trial",
            name="deadline",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="trial",
            name="is_active",
            field=models.BooleanField(default=True),
        ),
    ]
