from django.conf import settings
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed

from ..utils import Google, register_social_user


class GoogleSignInSerializer(serializers.Serializer):
    """
    Serializer for handling Google Sign-In requests.

    Attributes:
        access_token (str): Google OAuth2 access token.
    """

    access_token = serializers.CharField(min_length=6)

    def validate_access_token(self, access_token):
        """
        Validate the Google OAuth2 access token and register or login the user.

        Args:
            access_token (str): Google OAuth2 access token.

        Returns:
            dict: User information and tokens if validation and registration are successful.

        Raises:
            serializers.ValidationError: If the access token is invalid or expired.
            AuthenticationFailed: If the user could not be verified.
        """
        
        google_user_data = Google.validate(access_token)
        try:
            userid = google_user_data["sub"]
        except Exception as e:
            print(e, "exeption in acesstoken validate")
            raise serializers.ValidationError("this token is expired")

        if google_user_data["aud"] != settings.GOOGLE_CLIENT_ID:
            raise AuthenticationFailed(detail="could not verify user")
        email = google_user_data["email"]
        username = google_user_data["name"]
        provider = "google"

        return register_social_user(provider=provider, email=email, username=username)
