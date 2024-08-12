from django.urls import path

from .views import *

sent_request_list = FriendRequestViewSet.as_view({"get": "sent_request_list"})

friend_request_accept = FriendRequestViewSet.as_view({"post": "accept_request"})

cancel_request = FriendRequestViewSet.as_view({"post": "cancel_request"})

unfollow = FollowViewSet.as_view({"post": "unfollow"})

urlpatterns = [
    path("profile", ProfileData.as_view(), name="profile"),
    path("profile/<int:id>", ProfileData.as_view(), name="profile_with_id"),
    path("update_photo/<int:id>", UpdatePhoto.as_view(), name="update_photo"),
    path("delete_photo/<int:id>", UpdatePhoto.as_view(), name="delete_photo"),
    path("update_about", UpdateAbout.as_view(), name="update_about"),
    path(
        "user_academy",
        UserAcademyManage.as_view({"get": "list", "post": "create"}),
        name="user_academy",
    ),
    path(
        "user_academy/<int:id>",
        UserAcademyManage.as_view({"put": "update", "delete": "destroy"}),
        name="user_academy",
    ),
    path(
        "user_achievement",
        AchievementManage.as_view({"get": "list", "post": "create"}),
        name="user_achievement",
    ),
    path(
        "user_achievement/<int:id>",
        AchievementManage.as_view({"put": "update", "delete": "destroy"}),
        name="user_achievement",
    ),
    path(
        "friend_request",
        FriendRequestViewSet.as_view({"get": "list", "post": "create"}),
        name="friend_request",
    ),
    path("sent_request_list", sent_request_list, name="friend_request_list"),
    path(
        "friend_request_accept/<int:id>",
        friend_request_accept,
        name="friend_request_accept",
    ),
    path("cancel_request/<int:id>", cancel_request, name="cancel_request"),
    path("friends", FriendViewSet.as_view({"get": "list"}), name="friends"),
    path(
        "friends/<int:id>", FriendViewSet.as_view({"delete": "destroy"}), name="friends"
    ),
    path(
        "follow",
        FollowViewSet.as_view({"get": "list", "post": "create"}),
        name="follow",
    ),
    path("unfollow", unfollow, name="unfollow"),
    path("friend_suggestion", FriendSuggestion.as_view(), name="friend_suggestion"),
]
