import random

from common.base_models import DataBaseModels
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from users.models import Users


class Trial(DataBaseModels):
    """
    Model representing a sports trial.

    Attributes:
        academy (ForeignKey): The academy organizing the trial.
        sport (str): The sport for which the trial is conducted.
        name (str): The name of the trial.
        state (str): The state where the trial will be held.
        district (str): The district where the trial will be held.
        location (str): The specific location of the trial.
        venue (str): The venue where the trial will be held.
        trial_date (date): The date of the trial.
        trial_time (time): The time of the trial.
        deadline (date): The registration deadline for the trial.
        is_participant_limit (bool): Whether there is a participant limit.
        total_participant_limit (int): The total participant limit for the trial.
        is_registration_fee (bool): Whether there is a registration fee.
        registration_fee (int): The amount of the registration fee.
        image (ImageField): An image associated with the trial.
        description (TextField): A description of the trial.
        is_active (bool): Whether the trial is currently active.
    """

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
    """
    Model representing additional requirements for a trial.

    Attributes:
        trial (ForeignKey): The trial for which the requirement is set.
        requirement (str): The specific requirement for the trial.
    """
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
    """
    Model represents a player's registration in a trial. It includes
    personal details of the player and their status within the trial.

    Attributes:
        player (ForeignKey): The player who is registering for the trial.
        trial (ForeignKey): The trial in which the player is registering.
        status (str): The registration status of the player (default is "registered").
        name (str): The name of the player.
        dob (DateField): The date of birth of the player.
        number (str): The contact number of the player.
        email (EmailField): The email address of the player.
        state (str): The state of the player.
        district (str): The district of the player.
        unique_id (str): A unique ID assigned to the player for the trial.
        achievement (str): Any achievements of the player.
        payment_status (str): The payment status of the player for the trial.
    """
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
    """
    This model stores additional details provided by players when registering
    for a trial. Each detail is linked to a specific player's trial registration.

    Attributes:
        player_trial (ForeignKey): The player's trial registration.
        requirement (str): The specific requirement the player is fulfilling.
        value (str): The value provided by the player for the requirement.
    """
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
    """
    Signal to create a unique ID for a player upon registration for a trial.

    This function is triggered whenever a new PlayersInTrial instance is created.
    It generates a unique ID by combining the player's name, the trial ID, and
    a random two-digit number.

    Args:
        sender (Model class): The model class that triggered the signal.
        instance (PlayersInTrial): The actual instance being saved.
        created (bool): A boolean indicating whether a new instance was created.
    """
    if created and not instance.unique_id:
        num = random.randint(10, 99)
        instance.unique_id = (
            instance.name.replace(" ", "") + str(instance.id) + str(num)
        )
        instance.save()
