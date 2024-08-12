from django.conf import settings
from django.contrib.auth import authenticate
from google.auth.transport import requests
from google.oauth2 import id_token
from real_time.models import Notification
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from users.serializers.user_serializer import UserProfileSerializer

from .models import UserProfile, Users


class Google:
    """
    A class for handling Google OAuth2 token validation.
    """
    @staticmethod
    def validate(access_token):
        """
        Validates the provided Google OAuth2 access token.
        
        Args:
            access_token (str): The Google OAuth2 access token to validate.
        
        Returns:
            dict or str: The token information if valid, otherwise an error message.
        """
        try:
            # Verify the OAuth2 token with Google's servers
            id_info = id_token.verify_oauth2_token(
                access_token,
                requests.Request(),
                audience=None,
                clock_skew_in_seconds=60,
            )
            # Check if the issuer is Google
            if "accounts.google.com" in id_info["iss"]:
                return id_info
        except Exception as e:
            print(e, "exception in validate")
            return "Token is invalid or has expired"


def login_social_user(email, password):
    """
    Authenticates a user and returns user details along with JWT tokens.

    Args:
        email (str): The email of the user.
        password (str): The password of the user.

    Returns:
        dict: A dictionary containing user details and JWT tokens.

    Raises:
        AuthenticationFailed: If authentication fails.
    """
    user = authenticate(email=email, password=password)
    token_serializer = TokenObtainPairSerializer(
        data={"email": email, "password": password}
    )
    profile_photo = UserProfileSerializer(user.userprofile).data.get(
        "profile_photo", None
    )
    notification_count = Notification.objects.filter(receiver=user, seen=False).count()
    try:
        if token_serializer.is_valid():
            access = token_serializer.validated_data.get("access")
            refresh = token_serializer.validated_data.get("refresh")
            return {
                "email": user.email,
                "username": user.username,
                "access": str(access),
                "refresh": str(refresh),
                "dob": user.dob,
                "user_id": user.id,
                "profile_photo": profile_photo,
                "notification_count": notification_count,
            }
    except Exception as e:
        print(e, 'authentication failed')
        raise AuthenticationFailed(detail=str(e))


def register_social_user(provider, email, username):
    """
    Registers a new user or logs in an existing user based on social authentication.

    Args:
        provider (str): The social authentication provider (e.g., Google).
        email (str): The email of the user.
        username (str): The username of the user.

    Returns:
        dict: A dictionary containing user details and JWT tokens.

    Raises:
        AuthenticationFailed: If the user exists but is registered with a different provider.
    """

    user = Users.objects.filter(email=email)
    if user.exists():
        if provider == user[0].auth_provider:
            # Log in the user if the provider matches
            auth_user = login_social_user(email, settings.SOCIAL_AUTH_PASSWORD)
            return auth_user
        else:
            raise AuthenticationFailed(
                detail=f"please continue login with {user[0].auth_provider}"
            )
    else:
        # Register a new user if they do not exist
        new_user = {
            "email": email,
            "username": username,
        }
        register_user = Users.objects.create(**new_user)
        register_user.set_password(settings.SOCIAL_AUTH_PASSWORD)
        register_user.auth_provider = provider
        register_user.is_verified = True
        register_user.save()
        UserProfile.objects.create(user=register_user)
        reg_user = login_social_user(email, settings.SOCIAL_AUTH_PASSWORD)
        return reg_user
