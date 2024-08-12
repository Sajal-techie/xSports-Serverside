# Generated by Django 5.0.6 on 2024-07-25 06:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("user_profile", "0005_follow_friendrequest"),
    ]

    operations = [
        migrations.AlterField(
            model_name="friendrequest",
            name="status",
            field=models.CharField(
                choices=[("pending", "Pending"), ("accepted", "Accepted")],
                default="pending",
                max_length=20,
            ),
        ),
    ]
