from django.urls import path, re_path

from . import consumers

websocket_urlpatterns = [
    re_path(
        r"^ws/chat/(?P<thread_name>[\w-]+)/$", consumers.PersonalChatConsumer.as_asgi()
    ),
    path("ws/notifications/<str:user_id>/", consumers.NotificationConsumer.as_asgi()),
]
