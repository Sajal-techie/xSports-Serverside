from django.db import models
from common.base_models import DataBaseModels
from users.models import Users
from django.dispatch import receiver
from django.db.models.signals import post_save
import random


class Trial(DataBaseModels):
    academy = models.ForeignKey(
        Users, on_delete=models.CASCADE, related_name="academy", null=True
    )
    sport = models.CharField(max_length=50, null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    district = models.CharField(max_length=100, null=True, blank=True)
    location = models.CharField(max_length=200, null=True, blank=True)
    venue = models.CharField(max_length=255, null=True, blank=True)
    trial_date = models.DateField(null=True, blank=True)
    trial_time = models.TimeField(null=True, blank=True)
    deadline = models.DateField(null=True, blank=True)
    is_participant_limit = models.BooleanField(default=False)
    total_participant_limit = models.IntegerField(null=True, blank=True)
    is_registration_fee = models.BooleanField(default=True)
    registration_fee = models.IntegerField(null=True, blank=True)
    image = models.ImageField(upload_to="images/", null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.name + " " + self.academy.username


class TrialRequirement(DataBaseModels):
    trial = models.ForeignKey(
        Trial,
        on_delete=models.CASCADE,
        related_name="additional_requirements",
        null=True,
    )
    requirement = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self) -> str:
        return self.requirement + " " + self.trial.academy.username


class PlayersInTrial(DataBaseModels):
    player = models.ForeignKey(Users, on_delete=models.CASCADE, related_name="player")
    trial = models.ForeignKey(Trial, on_delete=models.CASCADE, related_name="trial")
    status = models.CharField(
        max_length=200, null=True, blank=True, default="registered"
    )
    name = models.CharField(max_length=255, null=True, blank=True)
    dob = models.DateField(null=True, blank=True)
    number = models.CharField(max_length=30, null=True, blank=True)
    email = models.EmailField(max_length=200, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    district = models.CharField(max_length=100, null=True, blank=True)
    unique_id = models.CharField(max_length=255, null=True, blank=True)
    achievement = models.CharField(max_length=255, null=True, blank=True)
    payment_status = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self) -> str:
        return self.name + " " + self.trial.name


class PlayersInTrialDetails(DataBaseModels):
    player_trial = models.ForeignKey(
        PlayersInTrial,
        on_delete=models.CASCADE,
        related_name="playersintrial",
        null=True,
    )
    requirement = models.CharField(max_length=255, null=True, blank=True)
    value = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self) -> str:
        return (
            self.requirement
            + " "
            + self.player_trial.name
            + " "
            + self.player_trial.player.username
        )


@receiver(post_save, sender=PlayersInTrial)
def create_unique_id_on_joining_trials(sender, instance, created, *args, **kwargs):
    if created and not instance.unique_id:
        num = random.randint(10, 99)
        instance.unique_id = (
            instance.name.replace(" ", "") + str(instance.id) + str(num)
        )
        instance.save()
