from common.base_models import DataBaseModels
from django.db import models
from users.models import Users


class UserAcademy(DataBaseModels):
    """
    Represents a user's association with an academy.

    Attributes:
        user: The user associated with the academy.
        academy: The academy associated with the user.
        start_month: The month when the user started with the academy.
        start_year: The year when the user started with the academy.
        end_month: The month when the user ended with the academy (if applicable).
        end_year: The year when the user ended with the academy (if applicable).
        position: The position or role of the user in the academy.
        is_current: Boolean indicating if the association is currently active.
        location: The location of the academy.
        description: A description of the user's experience with the academy.
        sport: The sport the user was involved with at the academy.
    """

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
    """
    Represents a user's achievement.

    Attributes:
        user: The user who received the achievement.
        title: The title of the achievement.
        issued_by: The entity or person who issued the achievement.
        issued_month: The month when the achievement was issued.
        issued_year: The year when the achievement was issued.
        image: An image representing the achievement.
        description: A description of the achievement.
    """

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
    """
    Represents a friend request between users.

    Attributes:
        from_user: The user who sent the friend request.
        to_user: The user who received the friend request.
        status: The status of the friend request (e.g., pending or accepted).
    """

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
        """
        Accept the friend request and establish a friendship between users.
        """
        self.status = self.ACCEPTED
        self.save()

        # Add each user to the other's friends list
        self.from_user.friends.add(self.to_user)
        self.to_user.friends.add(self.from_user)


class Follow(DataBaseModels):
    """
    Represents a follow relationship where a player follows an academy.

    Attributes:
        player: The player who follows the academy.
        academy: The academy being followed by the player.
    """
    
    player = models.ForeignKey(
        Users, related_name="following", on_delete=models.CASCADE
    )
    academy = models.ForeignKey(
        Users, related_name="followers", on_delete=models.CASCADE
    )

    class Meta:
        unique_together = ("player", "academy")
