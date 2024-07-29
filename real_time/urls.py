from django.urls import path
from .import views


urlpatterns = [
    path("chat", views.ChatView.as_view(), name="chat"),
    path("chat_list", views.ChatListView.as_view(), name="chat_list")

]
