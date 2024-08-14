from django.conf import settings
from django.core.validators import validate_email
from django.db.models import Count, Q
from django.http import JsonResponse
from real_time.models import Notification
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from selection_trial.models import Trial
from user_profile.models import Follow, FriendRequest
from users.serializers.google_serializer import GoogleSignInSerializer
from users.serializers.user_serializer import (CustomUsersSerializer,
                                               UserProfileSerializer)

from .models import Academy, Users
from .task import send_otp


class Signup(APIView):
    """
    API endpoint to handle user signup.

    This view handles the creation of new users (players or academies) 
    and validates the provided data. It also sends an OTP to the user's 
    email for verification.
    """
    def post(self, request):
        data = request.data

        # Initialize an empty dictionary for validation errors
        errors = {}

        # validate email
        email = data.get("email", None)
        if not email:
            errors["email"] = "Email field is Required"
        else:
            try:
                validate_email(email)
            except Exception:
                errors["email"] = "Email is not Valid"

        # If the user is an academy, set the 'sport' field
        if "is_academy" in data:
            if data["is_academy"] == "true":
                data.setlist("sport", request.data.getlist("sport[]", []))

        # Validate required fields
        if "username" in data and not data["username"]:
            errors["username"] = "Name is required"
        if "sport" in data and not data["sport"]:
            errors["sport"] = "Sport is Required"
        if "state" in data and not data["state"]:
            errors["state"] = "State is required"
        if "district" in data and not data["district"]:
            errors["district"] = "District is required"
        if "dob" in data and not data["dob"]:
            errors["dob"] = "Date of birth is required"
        if "password" in data and not data["password"]:
            errors["password"] = "Password is required"
        if "license" in data and not data["license"]:
            errors["license"] = "License is required"

        # Check if an account with the provided email already exists
        if Users.objects.filter(email=email).exists():
            errors["email"] = "Account with Email already exist try login"

        # If there are validation errors, return them in the response
        if errors:
            return Response(
                {"message": errors.values()},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Serialize user data and save the new user
        user_serializer = CustomUsersSerializer(data=data)
        try:
            user_serializer.is_valid(raise_exception=True)
            user_serializer.save()

            # Send OTP for email verification
            send_otp.delay(email)
            return Response(
                {
                    "message": "Registration Successful, Check Email For Verification",
                },status.HTTP_200_OK
            )
        except Exception as e:
            print(str(e), "exeption errorrrrr")
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)


class VerifyOtp(APIView):
    """
    API endpoint to verify the OTP sent to the user's email during signup, login or forget password.
    
    This view checks the OTP provided by the user and marks the account as verified if correct.
    """
    def put(self, request):
        try:
            data = request.data
            email = data["email"] if "email" in data else None
            otp = data["otp"] if "otp" in data else None
            user = Users.objects.get(email=email)

            # Check if the OTP has expired
            if not user.otp:
                return Response(
                    {
                        "message": "OTP Expired try resending otp",
                    },status.HTTP_400_BAD_REQUEST
                )
            
            # Verify the OTP
            if user.otp == otp:
                user.otp = None
                user.is_verified = True
                user.save()
                return Response(
                    {"message": "OTP Verified"},
                    status=status.HTTP_200_OK
                )
            return Response(
                {"message": "Invalid OTP"},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            print(e, "verify OTP error")
            return Response(
                {
                    "message": "Your token has been expired try login again ",
                },status.HTTP_400_BAD_REQUEST
            )


class Login(APIView):
    """
    API endpoint to handle user login.
    
    This view authenticates users (players, academies, or admins) based on their email and password.
    It also checks the user's role and returns the appropriate response.
    """
    def post(self, request):
        data = request.data
        email = data.get("email", None)
        password = data.get("password", None)

        # Validate email and password fields
        if email is None:
            return Response(
                {
                    "message": "email field is required",
                },status=status.HTTP_400_BAD_REQUEST
            )
        if password is None:
            return Response(
                {
                    "message": "password field is required",
                },status=status.HTTP_400_BAD_REQUEST
            )
        
        # Determine if the user is an academy or admin
        is_academy = False
        if "is_academy" in data:
            is_academy = data["is_academy"]
        is_staff = True if "is_staff" in data else False

        # Check if the email exists in the database
        if not Users.objects.filter(email=email).exists():
            return Response(
                {
                    "message": "Email Does Not Exists",
                },status=status.HTTP_400_BAD_REQUEST
            )
        
        user = Users.objects.get(email=email)

        # Check if the password is correct
        if not user.check_password(password):
            return Response(
                {"message": "Invalid Password"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if an admin is trying to log in as a regular user or vice versa
        if (not is_staff and user.is_superuser) or (user.is_staff and not is_staff):
            return Response(
                {
                    "message": "Admin cannot loggin as user",
                },status=status.HTTP_400_BAD_REQUEST
            )
        if is_staff and not user.is_staff:
            return Response(
                {
                    "message": "You are not an admin ",
                },status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if the user account is active
        if not user.is_active:
            return Response(
                { "message": "You are blocked"},status=status.HTTP_400_BAD_REQUEST
            )
        
        # Ensure the academy/user if logging in with the correct role
        if user.is_academy and not is_academy:
            return Response(
                {
                    "message": "You are signed in as acadmey try academy login",
                },status=status.HTTP_400_BAD_REQUEST
            )
        if not user.is_academy and is_academy:
            return Response(
                {
                    "message": "You are signed in as player try player login",
                },status=status.HTTP_400_BAD_REQUEST
            )

        # Determine user role
        role = (
            "admin"
            if is_staff and user.is_staff
            else "academy" if is_academy else "player"
        )

        # Handle admin login response
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

        # Send OTP if the user is not verified
        if not user.is_verified:
            send_otp.delay(email)
            return Response(
                {"message": "You are not verified"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check academy certification if the user if an academy
        if is_academy:
            academy = Academy.objects.get(user=user)
            if not academy.is_certified:
                return Response(
                    {
                        "message": "You are not approved by admin ",
                    },status=status.HTTP_400_BAD_REQUEST
                )

        # Get user's profile photo and notification count
        profile_photo = UserProfileSerializer(user.userprofile).data.get(
            "profile_photo", None
        ) if hasattr(user, 'userprofile') else None

        notification_count = Notification.objects.filter(
            receiver=user, seen=False
        ).count()

        return Response(
            {
                "message": "Login Successful",
                "user": user.username,
                "role": role,
                "dob": user.dob,
                "user_id": user.id,
                "profile_photo": profile_photo,
                "notification_count": notification_count,
            },
            status=status.HTTP_200_OK
        )


class GoogleSignIn(GenericAPIView):
    """
    API endpoint to handle Google sign-in.
    
    This view verifies the Google sign-in token and returns the user's data.
    """
    serializer_class = GoogleSignInSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = (serializer.validated_data)["access_token"]
        return Response(data, status=status.HTTP_200_OK)


class Logout(APIView):
    """
    API endpoint to handle user logout.
    
    This view invalidates the user's JWT tokens upon logout.
    """
    def post(self, request):
        refresh_token = request.data.get("refresh")
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        return Response(status=200, data="Logged out successfully")


class ResendOtp(APIView):
    """
    API endpoint to resend OTP
    
    This view resend the OTP to the users email
    """
    def post(self, request):
        try:
            email = request.data["email"]
            send_otp.delay(email)
            return Response(
                {"message": "OTP sended successfully"},status=status.HTTP_200_OK

            )
        except Exception as e:
            print(e, 'error in resend otp')
            return Response(
                {"message": "Error sending otp"},status=status.HTTP_400_BAD_REQUEST 
            )


class ForgetPassword(APIView):
    """
    View to handle password reset functionality.

    If the email exists in the request data, it checks for the presence of a 
    new password. If provided, it resets the user's password. If not, it sends 
    an OTP to the email if the user exists. Returns appropriate messages for 
    each case.
    """
    def post(self, request):
        try:
            if "email" in request.data:
                email = request.data["email"]

                # Check if the request includes a new password
                if "password" in request.data:
                    # Get the user by email and reset the password
                    user = Users.objects.get(email=email)
                    user.set_password(request.data["password"])
                    user.save()
                    return Response(
                        {
                            "message": "Password Resetted successfully",
                        },status=status.HTTP_200_OK
                    )
                if Users.objects.filter(email=email).exists():
                    send_otp.delay(email)
                    return Response(
                        {"message": "Email is valid"},status=status.HTTP_200_OK
                    )
            return Response(
                {
                    "message": "Email is not valid, Try signin",
                },status=status.HTTP_400_BAD_REQUEST
            )
        except Users.DoesNotExist as e:
            print(e, "does not exist")
            return Response(
                {
                    "message": "Account does not exist",
                }, status=status.HTTP_400_BAD_REQUEST,
            )

        except Exception as e:
            print(e, "error")
            return Response(
                {
                    "message": "Internal Server Error",
                },status=status.HTTP_400_BAD_REQUEST
            )


class SearchResult(APIView):
    """
    View to handle search functionality.
    
    Searches for users, trials, and other entities based on the query 
    provided in the request. The search results include additional 
    information like friend and follow status, allowing for a more 
    detailed and contextual response.
    """
    def get(self, request):
        current_user = request.user
        query = request.GET.get("q", "")
        if query:
            # search for user based on username or bio content
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

            # Search  for trials based on the current user's role (academy/player)
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

            # Fetch friend requests related to the current user
            friend_requests = FriendRequest.objects.filter(
                Q(from_user_id=current_user) | Q(to_user_id=current_user)
            ).values("from_user", "to_user", "status")

            # Fetch academies followed by the current user
            follows = Follow.objects.filter(player=current_user).values_list(
                "academy", flat=True
            )
            followers = Follow.objects.filter(academy=current_user).values_list(
                "player", flat=True
            )

            base_url = request.build_absolute_uri(settings.MEDIA_URL)
            suggestions = []

            # Using user results determine friend adn follow status
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
                ):  # Player following the academy
                    follow_status = "following"

                if (
                    not user["is_academy"] and user["id"] in followers
                ):  # Academy followed by the player
                    follow_status = "follower"

                # Compile the user data
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

        return JsonResponse({"message": "No query provided."}, status=status.HTTP_200_OK)
