from django.db import models
from common.base_models import DataBaseModels
from users.models import Users


class UserAcademy(DataBaseModels):
    user = models.ForeignKey(
        Users, on_delete=models.SET_NULL, null=True, related_name="userDetails"
    )
    academy = models.ForeignKey(
        Users, on_delete=models.SET_NULL, null=True, related_name="academyDetails"
    )
    start_month = models.CharField(max_length=20, null=True, blank=True)
    start_year = models.CharField(max_length=20, null=True, blank=True)
    end_month = models.CharField(max_length=20, null=True, blank=True)
    end_year = models.CharField(max_length=20, null=True, blank=True)
    position = models.CharField(max_length=20, null=True, blank=True)
    is_current = models.BooleanField(default=False)
    location = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField()
    sport = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.user.username} played in {self.academy.username}"


class Achievements(DataBaseModels):
    user = models.ForeignKey(
        Users, on_delete=models.SET_NULL, null=True, related_name="user_achievements"
    )
    title = models.CharField(max_length=255, null=True, blank=True)
    issued_by = models.CharField(max_length=255, null=True, blank=True)
    issued_month = models.CharField(max_length=20, null=True, blank=True)
    issued_year = models.CharField(max_length=10, null=True, blank=True)
    image = models.ImageField(upload_to="images/", null=True, blank=True)
    description = models.TextField(null=True)

    def __str__(self) -> str:
        return f"{self.user.username}'s {self.title}"


class FriendRequest(DataBaseModels):
    PENDING = "pending"
    ACCEPTED = "accepted"
    STATUS_CHOICES = [
        (PENDING, "Pending"),
        (ACCEPTED, "Accepted"),
    ]

    from_user = models.ForeignKey(
        Users, related_name="sent_friend_requests", on_delete=models.CASCADE
    )
    to_user = models.ForeignKey(
        Users, related_name="recieved_friend_requests", on_delete=models.CASCADE
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)

    class Meta:
        unique_together = ("from_user", "to_user")

    def accept(self):
        self.status = self.ACCEPTED
        self.save()

        self.from_user.friends.add(self.to_user)
        self.to_user.friends.add(self.from_user)


class Follow(DataBaseModels):
    player = models.ForeignKey(
        Users, related_name="following", on_delete=models.CASCADE
    )
    academy = models.ForeignKey(
        Users, related_name="followers", on_delete=models.CASCADE
    )

    class Meta:
        unique_together = ("player", "academy")
