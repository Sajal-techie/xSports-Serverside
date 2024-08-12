from django.core.paginator import Paginator
from django.db.models import Q
from rest_framework import generics, response, status, views, viewsets
from rest_framework.decorators import action

from .models import Chat, Notification, Users
from .serializers import (ChatListUserSerializer, ChatSerializer,
                          NotificationSerializer)


class ChatView(generics.ListCreateAPIView):
    serializer_class = ChatSerializer
    queryset = Chat.objects.all()

    def list(self, request, *args, **kwargs):
        thread_name = request.query_params.get("threadName")
        page = int(request.query_params.get("page", 1))
        per_page = 50

        queryset = (
            Chat.objects.filter(thread_name=thread_name)
            .select_related("sender")
            .order_by("date")
        )

        paginator = Paginator(queryset, per_page)
        total_pages = paginator.num_pages
        current_page = paginator.page(total_pages - page + 1)

        serializer = self.get_serializer(current_page, many=True)
        return response.Response(
            {
                "data": serializer.data,
                "has_previous": current_page.has_previous(),
                "total_pages": total_pages,
                "current_page": total_pages - page + 1,
            },
            status=status.HTTP_200_OK,
        )

    # to create new thread name or fetch existing thread name
    def create(self, request, *args, **kwargs):
        sender_id = request.data.get("sender_id", None)
        receiver_id = request.data.get("receiver_id", None)
        user_ids = sorted([sender_id, receiver_id])
        thread_name = f"chat_{user_ids[0]}_{user_ids[1]}"

        existing_chat = Chat.objects.filter(thread_name=thread_name).first()

        if not existing_chat:

            sender = Users.objects.get(id=sender_id)
            receiver = Users.objects.get(id=receiver_id)
            Chat.objects.create(
                sender=sender,
                receiver=receiver,
                thread_name=thread_name,
            )
        return response.Response({"thread_name": thread_name})


class ChatListView(views.APIView):
    def get(self, request):
        current_user = request.user

        # Get unique users the current user has chatted with
        chat_users = Users.objects.filter(
            Q(send_message__receiver=current_user)
            | Q(receive_message__sender=current_user)
        ).distinct()

        serializer = ChatListUserSerializer(
            chat_users, many=True, context={"request": request}
        )
        return response.Response(serializer.data, status=status.HTTP_200_OK)


class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    lookup_field = "id"

    def get_queryset(self):
        return Notification.objects.filter(receiver=self.request.user)

    @action(detail=True, methods=["post"])
    def mark_as_read(self, request, id=None):
        notification = Notification.objects.get(id=id)
        notification.seen = True
        notification.save()
        return response.Response(data="notification", status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"])
    def mark_all_as_read(self, request):
        notification = self.get_queryset()
        notification.update(seen=True)
        return response.Response(
            data="All notification marked as read", status=status.HTTP_200_OK
        )

    def destroy(self, request, id, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return response.Response(status=status.HTTP_204_NO_CONTENT)
