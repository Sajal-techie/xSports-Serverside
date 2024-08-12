import os

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from common.custom_permission_classes import (IsPlayer,
                                              IsUser)
from django.core.cache import cache
from django.db.models import Q
from real_time.models import Notification
from rest_framework import generics, status, views, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from users.models import Sport, UserProfile, Users
from users.serializers.user_serializer import (CustomUsersSerializer,
                                               SportSerializer,
                                               UserProfileSerializer)

from .models import Achievements, Follow, FriendRequest, UserAcademy
from .serializers.about_serializer import AboutSerializer
from .serializers.achievement_serializer import AchievementSerializer
from .serializers.connection_serializer import (FollowSerializer,
                                                FriendListSerializer,
                                                FriendRequestSerializer)
from .serializers.useracademy_serializer import UserAcademySerializer


class ProfileData(views.APIView):
    """
    API View to get and update profile data of users.

    Permissions:
        - IsUser: User must be authenticated and have the correct permissions.
    """

    permission_classes = [IsUser, IsAuthenticated]

    def get(self, request, id=None):
        """
        Get the profile data of a user.

        If `id` is provided, fetch the profile for the user with that `id`.
        Otherwise, fetch the profile of the currently authenticated user.

        Args:
            request: The HTTP request object.
            id (int, optional): The ID of the user to fetch.

        Returns:
            Response: The profile data in JSON format.
        """
        try:
            if id:
                user = Users.objects.get(id=id)
            else:
                user = request.user
            own_profile = user = request.user  # Determine if viewing own profile 
            cache_key = f"profile_{user.id}"
            user_data = cache.get(cache_key)

            friend_status = None
            if user.is_academy:
                followers = Follow.objects.filter(academy=user).count()

            if not own_profile:
                if user.is_academy:
                    print("if user is acadey")
                    following = Follow.objects.filter(
                        player=request.user, academy=user
                    ).first()
                    if following:
                        friend_status = "following"
                    else:
                        friend_status = "follow"
                elif request.user.is_academy:
                    print("if requested user is academy")
                    following = Follow.objects.filter(
                        player=user, academy=request.user
                    ).first()
                    if following:
                        friend_status = "follower"
                    else:
                        friend_status = "notfollower"
                else:
                    friend_request = FriendRequest.objects.filter(
                        from_user=user, to_user=request.user
                    ).first()
                    if friend_request:
                        friend_status = "received"
                    else:
                        friend_request = FriendRequest.objects.filter(
                            from_user=request.user, to_user=user
                        ).first()
                        if friend_request:
                            friend_status = "sent"
                        else:
                            if user.friends.filter(id=request.user.id).exists():
                                friend_status = "friends"
                            else:
                                friend_status = "none"

            #  if there is no cached data fetch new datas
            if not user_data:
                profile = (
                    UserProfile.objects.get(user=user)
                    if UserProfile.objects.filter(user=user).exists()
                    else None
                )
                sports = Sport.objects.filter(user=user)
                sport_data = [SportSerializer(sport).data for sport in sports]
                achievements = Achievements.objects.filter(user=user)
                achievement_data = [
                    AchievementSerializer(achievement).data
                    for achievement in achievements
                ]
                user_academies = UserAcademy.objects.filter(user=user)
                user_academy_data = [
                    UserAcademySerializer(user_academy).data
                    for user_academy in user_academies
                ]

                user_data = {
                    "user": CustomUsersSerializer(
                        user
                    ).data,  # it will contain datas in Users model
                    "profile": UserProfileSerializer(
                        profile
                    ).data,  # it will contain data from UserProfile model
                    "sport": sport_data,  # it will contain data from Sport model
                    "own_profile": own_profile,
                    "achievements": achievement_data,
                    "user_academies": user_academy_data,
                }

                cache.set(cache_key, user_data, timeout=60 * 15)  # Cache the user data

            user_data["own_profile"] = own_profile
            user_data["friend_status"] = friend_status
            if user.is_academy:
                user_data["followers"] = (
                    followers  # add followers count with responce if user is academy
                )

            return Response({"status": status.HTTP_200_OK, "user_details": user_data})
        except Users.DoesNotExist as e:
            print(e, "user does not exist")
            return Response(
                {"status": status.HTTP_404_NOT_FOUND, "message": "User does not exist"}
            )
        except Exception as e:
            print(e, "error in getting userdata")
            return Response(
                {"status": status.HTTP_400_BAD_REQUEST, "message": "server error !..."}
            )

    def post(self, request):
        """
        Update the profile data of the authenticated user.

        Args:
            request: The HTTP request object containing the data to update.

        Returns:
            Response: The result of the update operation.
        """

        try:
            if isinstance(request.user, Users):
                instance = request.user
                instance = request.user
                if "phone" in request.data:
                    instance.phone = request.data["phone"]
                if "username" in request.data:
                    instance.username = request.data["username"]
                if UserProfile.objects.filter(user=instance).exists():
                    profile = UserProfile.objects.get(user=instance)
                else:
                    profile = UserProfile.objects.create(user=instance)
                if "state" in request.data:
                    profile.state = request.data["state"]
                if "district" in request.data:
                    profile.district = request.data["district"]
                if "bio" in request.data:
                    profile.bio = request.data["bio"]
                if "dob" in request.data:
                    instance.dob = request.data["dob"]
                if "sport" in request.data:
                    Sport.objects.filter(user=instance).exclude(
                        sport_name__in=[request.data["sport"]]
                    ).delete()
                    for sport in request.data["sport"]:
                        if not Sport.objects.filter(
                            user=instance, sport_name=sport
                        ).exists():
                            Sport.objects.create(user=instance, sport_name=sport)

                instance.save()
                profile.save()
                cache_key = f"profile_{instance.id}"
                cache.delete(cache_key)  # Invalidate cache after update
                return Response(
                    {
                        "status": status.HTTP_200_OK,
                        "message": "User details Updated Successfully ...",
                    }
                )
            else:
                return Response(
                    {
                        "status": status.HTTP_400_BAD_REQUEST,
                        "message": "service not available",
                    }
                )
        except Exception as e:
            print(e)
            return Response(
                {"status": status.HTTP_400_BAD_REQUEST, "message": "some error !..."}
            )


class UpdatePhoto(views.APIView):
    """
    API View to update or delete profile and cover photos.

    Permissions:
        - IsUser: User must be authenticated and have the correct permissions.
    """
    permission_classes = [IsUser, IsAuthenticated]

    def post(self, request, id):
        """
        Update profile or cover photo for the authenticated user.

        Args:
            request: The HTTP request object containing the photo data.
            id (int): The ID of the user whose photo is to be updated.

        Returns:
            Response: The result of the update operation.
        """
        try:
            user = request.user
            serializer = UserProfileSerializer(user, data=request.data)
            if serializer.is_valid(raise_exception=True):
                profile = UserProfile.objects.get(user=user)
                if serializer.validated_data.get(
                    "profile_photo", None
                ):  # check whether data has profile photo or cover photo
                    new_photo = serializer.validated_data.get("profile_photo", None)
                    oldpath = (
                        profile.profile_photo.path
                        if (profile.profile_photo and new_photo)
                        else None
                    )
                    profile.profile_photo = new_photo
                    message = "Profile Photo updated successfully"

                elif serializer.validated_data.get("cover_photo", None):
                    new_photo = serializer.validated_data.get("cover_photo", None)
                    oldpath = (
                        profile.cover_photo.path
                        if (profile.cover_photo and new_photo)
                        else None
                    )
                    profile.cover_photo = new_photo
                    message = "Cover Photo updated successfully"
                else:  # if data does not contain profile or cover return failed
                    return Response(
                        {
                            "status": status.HTTP_400_BAD_REQUEST,
                            "message": "No valied data updation failed",
                        }
                    )
                profile.save()
                serializer.save()
                if oldpath and os.path.exists(oldpath):
                    os.remove(oldpath)

                cache_key = f"profile_{user.id}"
                cache.delete(cache_key)  # Invalidate cache after update
                return Response({"status": status.HTTP_200_OK, "message": message})
            return Response(
                {
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": "photo updation failed ",
                }
            )
        except Exception as e:
            print(e, "erro in uplaod image")
            return Response(
                {
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": "Photo updation failed",
                }
            )

    def delete(self, request, id):
        """
        Delete profile or cover photo for the authenticated user.

        Args:
            request: The HTTP request object containing the type of photo to delete.
            id (int): The ID of the user whose photo is to be deleted.

        Returns:
            Response: The result of the delete operation.
        """
        try:
            user = request.user
            data = request.data
            profile = UserProfile.objects.get(user=user)
            oldpath = None
            if "type" in data and data["type"] == "profile":
                oldpath = profile.profile_photo.path if profile.profile_photo else None
                profile.profile_photo = None
                message = "Profile Photo deleted successfully"
            elif "type" in data and data["type"] == "cover":
                oldpath = profile.cover_photo.path if profile.cover_photo else None
                profile.cover_photo = None
                message = "Cover Photo deleted successfully"
            else:
                return Response(
                    {
                        "status": status.HTTP_400_BAD_REQUEST,
                        "message": "No valid data photo deletion Failed",
                    }
                )
            profile.save()
            if oldpath and os.path.exists(oldpath):
                os.remove(oldpath)

            cache_key = f"profile_{user.id}"
            cache.delete(cache_key)  # Invalidate cache after delete
            return Response({"status": status.HTTP_200_OK, "message": message})
        except Exception as e:
            print(e, "error deleting")
            return Response(
                {
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": "Photo deletion failed",
                }
            )


class UpdateAbout(generics.UpdateAPIView):
    """
    API View to update the 'about' section of a user's profile.

    Permissions:
        - IsUser: User must be authenticated and have the correct permissions.
    """
    permission_classes = [IsUser, IsAuthenticated]
    serializer_class = AboutSerializer

    def get_object(self):
        return UserProfile.objects.get(user=self.request.user)

    def perform_update(self, serializer):
        cache_key = f"profile_{self.request.user.id}"
        cache.delete(cache_key)
        return super().perform_update(serializer)


class UserAcademyManage(viewsets.ModelViewSet):
    """
    Manage player academy  associations (academies joined by player).

    Permissions:
        - IsPlayer: Player must be authenticated and have the correct permissions.
    """
    permission_classes = [IsPlayer, IsAuthenticated]
    serializer_class = UserAcademySerializer
    lookup_field = "id"

    def get_queryset(self):
        """
        Return the queryset of academies associated with the current player.
        """
        return (
            UserAcademy.objects.filter(user=self.request.user)
            .select_related("academy")
            .order_by("-id")
        )

    def perform_update(self, serializer):
        """
        Delete the cached profile of the user after updating the user-academy.
        """
        cache_key = f"profile_{self.request.user.id}"
        cache.delete(cache_key)
        return super().perform_update(serializer)

    def perform_create(self, serializer):
        """
        Delete the cached profile of the user after creating a new user-academy.
        """
        cache_key = f"profile_{self.request.user.id}"
        cache.delete(cache_key)
        return super().perform_create(serializer)

    def perform_destroy(self, instance):
        """
        Delete the cached profile of the user after removing a user-academy.
        """
        cache_key = f"profile_{self.request.user.id}"
        cache.delete(cache_key)
        return super().perform_destroy(instance)


class AchievementManage(viewsets.ModelViewSet):
    """
    Manage user achievements.

    Permissions:
        - IsUser: User must be authenticated and have the correct permissions.
    """
    permission_classes = [IsUser, IsAuthenticated]
    serializer_class = AchievementSerializer
    lookup_field = "id"

    def get_queryset(self):
        """
        Return the queryset of achievements for the current user.
        """
        return Achievements.objects.filter(user=self.request.user).order_by("-id")

    def perform_update(self, serializer):
        """
        Delete the cached profile of the user after updating an achievement.
        """
        cache_key = f"profile_{self.request.user.id}"
        cache.delete(cache_key)
        return super().perform_update(serializer)

    def perform_create(self, serializer):
        """
        Delete the cached profile of the user after creating a new achievement.
        """
        cache_key = f"profile_{self.request.user.id}"
        cache.delete(cache_key)
        return super().perform_create(serializer)

    def perform_destroy(self, instance):
        """
        Delete the cached profile of the user after removing an achievement.
        """
        cache_key = f"profile_{self.request.user.id}"
        cache.delete(cache_key)
        return super().perform_destroy(instance)


class FriendRequestViewSet(viewsets.ModelViewSet):
    """
    ViewSet to handle operation related to friend requests.

    Permissions:
        - IsPlayer: Player must be authenticated and have the correct permissions.
    """
    queryset = FriendRequest.objects.all()
    serializer_class = FriendRequestSerializer

    def get_queryset(self):
        """
        Return the queryset of friend requests where the current user 
        is the recipient and the request is not yet accepted.
        """
        return (
            FriendRequest.objects.filter(to_user=self.request.user)
            .exclude(status="accepted")
            .select_related("to_user")
        )

    def create(self, request):
        """
        Create a new friend request and notify the recipient.
        """
        data = request.data
        from_user = request.user
        to_user = Users.objects.get(id=data["to_user"])

        if from_user == to_user:
            return Response(
                {"message": "You can't send friend request to yourself"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if FriendRequest.objects.filter(from_user=from_user, to_user=to_user).exists():
            return Response(
                {"message": "Friend Request already sent.."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        friend_request = FriendRequest.objects.create(
            from_user=from_user, to_user=to_user
        )
        serializer = self.get_serializer(friend_request)
        cache_key1 = f"profile_{from_user.id}"
        cache_key2 = f"profile_{to_user.id}"
        cache.delete(cache_key1)
        cache.delete(cache_key2)

        if friend_request:
            notification_type = "friend_request"
            text = f"{from_user.username} sent you a friend request"
            link = f"/profile/{from_user.id}"
            Notification.objects.create(
                receiver=to_user,
                sender=from_user,
                notification_type=notification_type,
                text=text,
                link=link,
                seen=False,
            )

            # sent notification to request recipient
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"notification_{to_user.id}",
                {
                    "type": "send_notification",
                    "data": {
                        "type": notification_type,
                        "sender": friend_request.to_user.username,
                        "text": text,
                        "link": link,
                    },
                },
            )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get"])
    def sent_request_list(self):
        """
        Return a list of friend requests sent by the current user that have not been accepted.
        """
        sent_requests = (
            FriendRequest.objects.filter(from_user=self.request.user)
            .exclude(status="accepted")
            .select_related("from_user")
        )
        serializer = self.get_serializer(sent_requests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def accept_request(self, request, id=None):
        """
        Accept a friend request and notify the sender.
        """
        try:
            friend_request = FriendRequest.objects.get(
                from_user=id, to_user=request.user
            )
        except FriendRequest.DoesNotExist:
            return Response(
                data="Freind request not found", status=status.HTTP_404_NOT_FOUND
            )

        friend_request.accept()  # Use the model method to establish friendship

        notification_type = "friend_request_accept"
        text = f"{friend_request.to_user.username} accepted your friend request"
        link = f"/profile/{friend_request.to_user.id}"

        Notification.objects.create(
            receiver=friend_request.from_user,
            sender=friend_request.to_user,
            notification_type=notification_type,
            text=text,
            link=link,
            seen=False,
        )

        # Send notification to the request sender
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"notification_{friend_request.from_user.id}",
            {
                "type": "send_notification",
                "data": {
                    "type": notification_type,
                    "sender": friend_request.to_user.username,
                    "text": text,
                    "link": link,
                },
            },
        )

        friend_request.delete()  # Remove the friend request
        cache_key1 = f"profile_{id}"
        cache_key2 = f"profile_{request.user.id}"
        cache.delete(cache_key1)
        cache.delete(cache_key2)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"])
    def cancel_request(self, request, id=None):
        """
        Cancel a sent friend request.
        """
        to_user = Users.objects.get(id=id)
        try:
            friend_request = FriendRequest.objects.get(
                from_user=request.user, to_user=to_user
            )
        except FriendRequest.DoesNotExist:
            return Response(
                data="friend request does not exist", status=status.HTTP_404_NOT_FOUND
            )

        friend_request.delete()
        cache_key1 = f"profile_{id}"
        cache_key2 = f"profile_{request.user.id}"
        cache.delete(cache_key1)
        cache.delete(cache_key2)
        return Response(status=status.HTTP_204_NO_CONTENT)


class FriendViewSet(viewsets.ModelViewSet):
    """
    Manage friendships between users.

    Permissions:
        - IsPlayer: Player must be authenticated and have the correct permissions.
    """
    serializer_class = FriendListSerializer
    lookup_field = "id"

    def get_queryset(self):
        """
        Return the queryset of friends for the current user.
        """
        user = self.request.user
        return (
            user.friends.all()
            .select_related("userprofile")
            .prefetch_related("sport_set")
        )

    def destroy(self, request, id):
        """
        Remove a friend from the current user's friend list.
        """
        user = self.request.user

        try:
            friend = Users.objects.get(id=id)

            user.friends.remove(friend)
            friend.friends.remove(user)

            cache_key1 = f"profile_{id}"
            cache_key2 = f"profile_{user.id}"
            cache.delete(cache_key1)
            cache.delete(cache_key2)

            return Response(
                {
                    "status": status.HTTP_204_NO_CONTENT,
                    "message": "Friend removed successfully",
                }
            )
        except Users.DoesNotExist:
            return Response(
                {"status": status.HTTP_404_NOT_FOUND, "message": "Friend not found"}
            )
        except Exception as e:
            return Response({"status": status.HTTP_400_BAD_REQUEST, "message": str(e)})


class FollowViewSet(viewsets.ModelViewSet):
    """
    Manage follow actions between players and academies.

    Permissions:
        - IsPlayer: Player must be authenticated and have the correct permissions.
    """
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer

    def get_queryset(self):
        """
        Return the queryset of follows for the current user.
        """
        return Follow.objects.filter(player=self.request.user)

    def create(self, request):
        """
        Follow an academy and notify the academy.
        """
        data = request.data
        player = request.user
        academy_id = data["academy"]
        academy = Users.objects.get(id=academy_id)

        if Follow.objects.filter(player=player, academy=academy).exists():
            return Response(
                {"message": "Already following this academy"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        follow = Follow.objects.create(player=player, academy=academy)

        # Notify the academy about the new follower
        notification_type = "follow"
        text = f"{player.username} started following you"
        link = f"/profile/{player.id}"

        Notification.objects.create(
            receiver=academy,
            sender=player,
            notification_type=notification_type,
            text=text,
            link=link,
            seen=False,
        )

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"notification_{academy.id}",
            {
                "type": "send_notification",
                "data": {
                    "type": notification_type,
                    "sender": player.username,
                    "text": text,
                    "link": link,
                },
            },
        )
        serializer = FollowSerializer(follow)
        cache_key1 = f"profile_{player.id}"
        cache_key2 = f"profile_{academy.id}"
        cache.delete(cache_key1)
        cache.delete(cache_key2)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def unfollow(self, request):
        """
        Unfollow an academy.
        """

        player = request.user
        academy_id = request.data.get("academy", None)
        if not academy_id:
            return Response(
                {"message": "academy id is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        follow = Follow.objects.filter(player=player, academy=academy_id).first()
        if follow:
            follow.delete()
            cache_key1 = f"profile_{player.id}"
            cache_key2 = f"profile_{academy_id}"
            cache.delete(cache_key1)
            cache.delete(cache_key2)
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {"message": "You are not following this academy"},
            status=status.HTTP_400_BAD_REQUEST,
        )


class FriendSuggestion(views.APIView):
    def get(self, request, *args, **kwargs):
        user = request.user

        user_profile = UserProfile.objects.get(user=user)

        friends = user.friends.all()

        friends_of_friends = Users.objects.filter(friends__in=friends)

        suggestions = (
            (
                friends_of_friends
                | Users.objects.filter(
                    Q(userprofile__district=user_profile.district)
                    | Q(
                        sport__sport_name__in=user.sport_set.values_list(
                            "sport_name", flat=True
                        )
                    )
                )
            )
            .exclude(is_academy=True)
            .distinct()
        )

        suggestions = suggestions.exclude(Q(id=user.id) | Q(id__in=friends))

        serializer = FriendListSerializer(suggestions[:7], many=True)

        return Response(serializer.data)
