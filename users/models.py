from common.base_models import DataBaseModels
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class CustomUserManager(BaseUserManager):
    """
    Custom manager for the Users model to handle user creation and superuser creation.
    """

    def create_user(self, email, username=None, password=None, **extra_fields):
        """
        Create and return a regular user with an email address.

        Args:
            email (str): User's email address.
            username (str, optional): User's username. Defaults to None.
            password (str, optional): User's password. Defaults to None.
            **extra_fields: Additional fields to be added to the user.

        Raises:
            ValueError: If email is not provided.

        Returns:
            Users: The created user instance.
        """

        if not email:
            raise ValueError("Users must have an email address")
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, username=None, **extra_fields):
        """
        Create and return a superuser with the specified email and password.

        Args:
            email (str): Superuser's email address.
            password (str): Superuser's password.
            username (str, optional): Superuser's username. Defaults to None.
            set is_staff and is_superuser to True.
            **extra_fields: Additional fields to be added to the superuser.

        Raises:
            ValueError: If `is_staff` or `is_superuser` flags are not set to True.

        Returns:
            Users: The created superuser instance.
        """
        
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        print("create superuser", username)
        return self.create_user(
            email=email, password=password, username=username, **extra_fields
        )


class Users(AbstractUser):
    """
    Custom user model extending Django's AbstractUser with additional fields.

    Attributes:
        username (str): User's username.
        email (str): User's email address.
        phone (str): User's phone number.
        otp (str): One-time password for verification.
        dob (date): Date of birth of the player, established date for academy.
        is_academy (bool): Indicates if the user is an academy.
        is_active (bool): Indicates if the user account is active.
        is_verified (bool): Indicates if the user email is verified.
        auth_provider (str): Authentication provider used by the user.
        friends (ManyToManyField): Many-to-many relationship with other users.
        created_at (datetime): Timestamp when the user was created.
        updated_at (datetime): Timestamp when the user was last updated.
    """

    username = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    email = models.EmailField(unique=True, max_length=255)
    phone = models.CharField(max_length=15, null=True, blank=True)
    otp = models.CharField(max_length=10, null=True, blank=True)
    dob = models.DateField(null=True, blank=True) 
    is_academy = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    auth_provider = models.CharField(max_length=50, default="email")
    friends = models.ManyToManyField("self", symmetrical=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = [
        "username",
    ]
    objects = CustomUserManager()

    def __str__(self) -> str:
        return f"{self.username}user instance"

    class Meta:
        indexes = [models.Index(fields=["username"])]


class Sport(DataBaseModels):
    """
    Model representing a sport associated with a user.

    Attributes:
        sport_name (str): Name of the sport.
        user (ForeignKey): User associated with the sport.
    
    Users can have multile sports.
    """

    sport_name = models.CharField(max_length=255)
    user = models.ForeignKey(Users, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return str(self.user.username) + str(self.sport_name) + "sport instance"


class UserProfile(DataBaseModels):
    """
    Profile model for additional user details.

    Attributes:
        user (OneToOneField): User associated with the profile.
        bio (TextField): User's bio.
        about (TextField): Additional information about the user.
        state (str): User's state.
        district (str): User's district.
        profile_photo (ImageField): Profile photo of the user.
        cover_photo (ImageField): Cover photo of the user.
    """
    user = models.OneToOneField(
        Users, on_delete=models.CASCADE, null=True, related_name="userprofile"
    )
    bio = models.TextField(null=True, blank=True)
    about = models.TextField(null=True, blank=True)
    state = models.CharField(max_length=255, null=True, blank=True)
    district = models.CharField(max_length=255, null=True, blank=True)
    profile_photo = models.ImageField(upload_to="images/", null=True, blank=True)
    cover_photo = models.ImageField(upload_to="images/", null=True, blank=True)

    def __str__(self):
        return str(self.user.username) + "profile instance" + str(self.bio)


class Academy(DataBaseModels):
    """
    Model representing details of academy for certification.

    Attributes:
        user (ForeignKey): User associated with the academy.
        license (FileField): License file for the academy.
        is_certified (bool): Indicates if the academy is certified.
    """
    user = models.ForeignKey(
        Users, on_delete=models.CASCADE, related_name="academy_user", null=True
    )
    license = models.FileField(upload_to="images/", null=True, blank=True)
    is_certified = models.BooleanField(default=False)
