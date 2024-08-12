from django.urls import path, include
from . import views

mark_as_read = views.NotificationViewSet.as_view({"post": "mark_as_read"})

mark_all_as_read = views.NotificationViewSet.as_view({"post": "mark_all_as_read"})

urlpatterns = [
    path("chat", views.ChatView.as_view(), name="chat"),
    path("chat_list", views.ChatListView.as_view(), name="chat_list"),
    path(
        "notification",
        views.NotificationViewSet.as_view({"get": "list"}),
        name="notification",
    ),
    path(
        "notification/<int:id>",
        views.NotificationViewSet.as_view({"delete": "destroy"}),
        name="notification",
    ),
    path("mark_as_read/<int:id>", mark_as_read, name="mark_as_read"),
    path("mark_all_as_read", mark_all_as_read, name="mark_all_as_read"),
]
