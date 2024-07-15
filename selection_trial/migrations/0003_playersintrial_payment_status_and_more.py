# Generated by Django 5.0.6 on 2024-07-14 08:14

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('selection_trial', '0002_trial_deadline_trial_is_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='playersintrial',
            name='payment_status',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='playersintrial',
            name='status',
            field=models.CharField(blank=True, default='registered', max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='trialrequirement',
            name='trial',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='additional_requirements', to='selection_trial.trial'),
        ),
    ]
