from rest_framework import serializers
from ..utils import Google, register_social_user
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed


class GoogleSignInSerializer(serializers.Serializer):
    access_token = serializers.CharField(min_length=6)

    def validate_access_token(self, access_token):
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
