from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.validators import validate_email
from django.http import JsonResponse
from django.db.models import Q, Count
from django.conf import settings
from users.serializers.user_serializer import (
    CustomUsersSerializer,
    UserProfileSerializer,
)
from users.serializers.google_serializer import GoogleSignInSerializer
from .models import Users, Academy
from user_profile.models import FriendRequest, Follow
from .task import send_otp
from selection_trial.models import Trial
from real_time.models import Notification


class Signup(APIView):
    def post(self, request):
        data = request.data

        # validations
        errors = {}
        if "email" in data:
            if not data["email"]:
                errors["email"] = "Email field is Required"
        else:
            try:
                validate_email(email)
            except:
                errors["email"] = "Email is not Valid"

        email = data["email"]

        if "is_academy" in data:
            if data["is_academy"] == "true":
                data.setlist("sport", request.data.getlist("sport[]", []))

        if "username" in data:
            if not data["username"]:
                errors["username"] = "Name is required"
        if "sport" in data:
            if not data["sport"]:
                errors["sport"] = "Sport is Required"
        if "state" in data:
            if not data["state"]:
                errors["state"] = "State is required"
        if "district" in data:
            if not data["district"]:
                errors["district"] = "District is required"
        if "dob" in data:
            if not data["dob"]:
                errors["dob"] = "Date of birth is required"
        if "password" in data:
            if not data["password"]:
                errors["password"] = "Password is required"
        if "license" in data:
            if not data["license"]:
                errors["license"] = "License is required"

        print(errors, "errors")
        if Users.objects.filter(email=email).exists():
            errors["email"] = "Account with Email already exist try login"

        if errors:
            return Response(
                {"status": status.HTTP_400_BAD_REQUEST, "message": errors.values()}
            )
        user_serializer = CustomUsersSerializer(data=data)
        try:
            user_serializer.is_valid(raise_exception=True)
            user_serializer.save()
            send_otp.delay(email)
            return Response(
                {
                    "status": status.HTTP_200_OK,
                    "message": "Registration Successful, Check Email For Verification",
                }
            )
        except Exception as e:
            print(str(e), "exeption errorrrrr")
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)


class VerifyOtp(APIView):
    def put(self, request):
        try:
            data = request.data
            email = data["email"] if "email" in data else None
            otp = data["otp"] if "otp" in data else None
            user = Users.objects.get(email=email)
            if not user.otp:
                return Response(
                    {
                        "status": status.HTTP_400_BAD_REQUEST,
                        "message": "OTP Expired try resending otp",
                    }
                )
            if user.otp == otp:
                user.otp = None
                user.is_verified = True
                user.save()
                return Response(
                    {"status": status.HTTP_200_OK, "message": "OTP Verified"}
                )
            return Response(
                {"status": status.HTTP_400_BAD_REQUEST, "message": "Invalid OTP"}
            )
        except Exception as e:
            print(e, "verify OTP error")
            return Response(
                {
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": "Your token has been expired try login again ",
                }
            )


class Login(APIView):
    def post(self, request):
        data = request.data
        email = data["email"] if "email" in data else None
        password = data["password"] if "password" in data else None
        if email is None:
            return Response(
                {
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": "email field is required",
                }
            )
        if password is None:
            return Response(
                {
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": "password field is required",
                }
            )
        is_academy = False
        if "is_academy" in data:
            is_academy = data["is_academy"]
        is_staff = True if "is_staff" in data else False
        if not Users.objects.filter(email=email).exists():
            return Response(
                {
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": "Email Does Not Exists",
                }
            )
        user = Users.objects.get(email=email)
        if not user.check_password(password):
            return Response(
                {"status": status.HTTP_400_BAD_REQUEST, "message": "Invalid Password"}
            )
        if (not is_staff and user.is_superuser) or (user.is_staff and not is_staff):
            return Response(
                {
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": "Admin cannot loggin as user",
                }
            )
        if is_staff and not user.is_staff:
            return Response(
                {
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": "You are not an admin ",
                }
            )
        if not user.is_active:
            return Response(
                {"status": status.HTTP_400_BAD_REQUEST, "message": "You are blocked"}
            )
        if user.is_academy and not is_academy:
            return Response(
                {
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": "You are signed in as acadmey try academy login",
                }
            )
        if not user.is_academy and is_academy:
            return Response(
                {
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": "You are signed in as player try player login",
                }
            )

        role = (
            "admin"
            if is_staff and user.is_staff
            else "academy" if is_academy else "player"
        )
        if role == "admin":
            return Response(
                {
                    "status": status.HTTP_200_OK,
                    "message": "Login Successful",
                    "user": user.username,
                    "role": role,
                    "user_id": user.id,
                }
            )

        if not user.is_verified:
            send_otp.delay(email)
            return Response(
                {"status": status.HTTP_403_FORBIDDEN, "message": "You are not verified"}
            )
        if is_academy:
            academy = Academy.objects.get(user=user)
            if not academy.is_certified:
                return Response(
                    {
                        "status": status.HTTP_400_BAD_REQUEST,
                        "message": "You are not approved by admin ",
                    }
                )

        profile_photo = UserProfileSerializer(user.userprofile).data.get(
            "profile_photo", None
        )
        notification_count = Notification.objects.filter(
            receiver=user, seen=False
        ).count()

        return Response(
            {
                "status": status.HTTP_200_OK,
                "message": "Login Successful",
                "user": user.username,
                "role": role,
                "dob": user.dob,
                "user_id": user.id,
                "profile_photo": profile_photo,
                "notification_count": notification_count,
            }
        )


class GoogleSignIn(GenericAPIView):
    serializer_class = GoogleSignInSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = (serializer.validated_data)["access_token"]
        return Response(data, status=status.HTTP_200_OK)


class Logout(APIView):
    def post(self, request):
        try:
            refresh = request.data.get("refresh")
            token = RefreshToken(refresh)
            token.blacklist()
            return Response(status=200)
        except Exception as e:
            print(e, "error in logout")
            return Response(status=400)


class ResendOtp(APIView):
    def post(self, request):
        try:
            email = request.data["email"]
            send_otp.delay(email)
            return Response(
                {"status": status.HTTP_200_OK, "message": "OTP sended successfully"}
            )
        except Exception as e:
            return Response(
                {"status": status.HTTP_400_BAD_REQUEST, "message": "Error sending otp"}
            )


class ForgetPassword(APIView):
    def post(self, request):
        try:
            if "email" in request.data:
                email = request.data["email"]
                if "password" in request.data:
                    user = Users.objects.get(email=email)
                    user.set_password(request.data["password"])
                    user.save()
                    return Response(
                        {
                            "status": status.HTTP_200_OK,
                            "message": "Password Resetted successfully",
                        }
                    )
                if Users.objects.filter(email=email).exists():
                    send_otp.delay(email)
                    return Response(
                        {"status": status.HTTP_200_OK, "message": "Email is valid"}
                    )
            return Response(
                {
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": "Email is not valid, Try signin",
                }
            )
        except Users.DoesNotExist as e:
            print(e, "does not exist")
            return Response(
                {
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": "Account does not exist",
                }
            )

        except Exception as e:
            print(e, "error")
            return Response(
                {
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": "Internal Server Error",
                }
            )


class SearchResult(APIView):
    def get(self, request):
        current_user = request.user
        query = request.GET.get("q", "")
        if query:
            users = (
                Users.objects.filter(
                    Q(username__icontains=query) | Q(userprofile__bio__icontains=query),
                )
                .select_related("userprofile")
                .exclude(is_staff=True)
                .annotate(
                    friends_count=Count("friends", distinct=True),
                    followers_count=Count("followers", distinct=True),
                    is_friend=Count(
                        "friends", filter=Q(friends__id=current_user.id), distinct=True
                    ),
                )
                .values(
                    "id",
                    "username",
                    "is_academy",
                    "userprofile__profile_photo",
                    "userprofile__bio",
                    "friends_count",
                    "followers_count",
                    "is_friend",
                )
            )

            if current_user.is_academy:
                trials = (
                    Trial.objects.filter(name__icontains=query, academy=current_user)
                    .annotate(registered_players_count=Count("trial", distinct=True))
                    .values("id", "name", "image", "sport", "registered_players_count")
                )
            else:
                trials = (
                    Trial.objects.filter(name__icontains=query)
                    .annotate(registered_players_count=Count("trial", distinct=True))
                    .values("id", "name", "image", "sport", "registered_players_count")
                )

            # posts = Post.objects.filter(title__icontains=query).values('id', 'title')

            friend_requests = FriendRequest.objects.filter(
                Q(from_user_id=current_user) | Q(to_user_id=current_user)
            ).values("from_user", "to_user", "status")

            follows = Follow.objects.filter(player=current_user).values_list(
                "academy", flat=True
            )
            followers = Follow.objects.filter(academy=current_user).values_list(
                "player", flat=True
            )

            base_url = request.build_absolute_uri(settings.MEDIA_URL)
            suggestions = []
            for user in users:
                friend_status = "none"

                if user["id"] == current_user.id:
                    friend_status = "self"
                elif friend_requests.filter(
                    from_user=current_user, to_user=user["id"], status="pending"
                ).exists():
                    friend_status = "request_sent"
                elif friend_requests.filter(
                    from_user=user["id"], to_user=current_user, status="pending"
                ).exists():
                    friend_status = "request_received"
                elif current_user.friends.filter(id=user["id"]).exists():
                    friend_status = "friends"

                follow_status = "not_following"
                if (
                    user["is_academy"] and user["id"] in follows
                ):  # if the user is player and player is following the resulted academy
                    follow_status = "following"

                if (
                    not user["is_academy"] and user["id"] in followers
                ):  # if the user is academy and academy is followed by the player
                    follow_status = "follower"

                suggestions.append(
                    {
                        "id": user["id"],
                        "name": user["username"],
                        "isAcademy": user["is_academy"],
                        "photoUrl": (
                            base_url + user["userprofile__profile_photo"]
                            if user["userprofile__profile_photo"]
                            else ""
                        ),
                        "bio": user["userprofile__bio"],
                        "type": "Academy" if user["is_academy"] else "Player",
                        "count": (
                            user["friends_count"]
                            if not user["is_academy"]
                            else user["followers_count"]
                        ),
                        "friend_status": friend_status,
                        "follow_status": follow_status,
                    }
                )

            suggestions.extend(
                [
                    {
                        "id": trial["id"],
                        "name": trial["name"],
                        "photoUrl": base_url + trial["image"] if trial["image"] else "",
                        "bio": trial["sport"],
                        "type": "Trial",
                        "count": trial["registered_players_count"],
                    }
                    for trial in trials
                ]
            )
            # suggestions.extend([
            #     {'id': post['id'], 'name': post['title'], 'type': 'Post'}
            #     for post in posts
            # ])
            suggestions.sort(key=lambda x: x["count"], reverse=True)
            return JsonResponse(suggestions, safe=False)

        return JsonResponse({"message": "No query provided."}, status=400)
