from django.core.paginator import Paginator
from django.db.models import Q
from rest_framework import generics, response, status, views, viewsets
from rest_framework.decorators import action

from .models import Chat, Notification, Users
from .serializers import (ChatListUserSerializer, ChatSerializer,
                          NotificationSerializer)


class ChatView(generics.ListCreateAPIView):
    """
    A view that provides `list` and `create` actions for the Chat model.
    
    `list` method returns paginated chat messages for a given thread.
    `create` method creates a new thread or retrieves the existing thread name.
    """
    serializer_class = ChatSerializer
    queryset = Chat.objects.all()

    def list(self, request):
        """
        List chat messages for a specific thread name.
        
        Query Params:
            - threadName: The name of the thread to retrieve messages from.
            - page: The page number for pagination (default is 1).
        
        Returns:
            - Paginated chat messages in reverse chronological order.
        """
        thread_name = request.query_params.get("threadName")
        page = int(request.query_params.get("page", 1))
        per_page = 50

        # Filter messages by thread name and order them by date.
        queryset = (
            Chat.objects.filter(thread_name=thread_name)
            .select_related("sender")
            .order_by("date")
        )

        paginator = Paginator(queryset, per_page)
        total_pages = paginator.num_pages

        # Adjust page to reverse order (latest messages first)
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

    def create(self, request, *args, **kwargs):
        """
        Create a new chat thread or retrieve an existing thread name.
        
        If a chat thread between the given sender and receiver exists, return the thread name.
        If not, create a new thread and return the newly created thread name.
        
        Request Data:
            - sender_id: The ID of the user sending the message.
            - receiver_id: The ID of the user receiving the message.
        
        Returns:
            - The thread name for the chat between the sender and receiver.
        """

        sender_id = request.data.get("sender_id", None)
        receiver_id = request.data.get("receiver_id", None)

        # Create a unique thread name based on sender and receiver IDs.
        user_ids = sorted([sender_id, receiver_id])
        thread_name = f"chat_{user_ids[0]}_{user_ids[1]}"

        # Check if the thread already exists.
        existing_chat = Chat.objects.filter(thread_name=thread_name).first()

        if not existing_chat:
            # If not, create a new chat thread.
            sender = Users.objects.get(id=sender_id)
            receiver = Users.objects.get(id=receiver_id)
            Chat.objects.create(
                sender=sender,
                receiver=receiver,
                thread_name=thread_name,
            )
        return response.Response({"thread_name": thread_name})


class ChatListView(views.APIView):
    """
    A view to list all users the current user has had a chat with.
    """
    def get(self, request):
        current_user = request.user

        # Get unique users who have exchanged messages with the current user.
        chat_users = Users.objects.filter(
            Q(send_message__receiver=current_user)
            | Q(receive_message__sender=current_user)
        ).distinct()

        serializer = ChatListUserSerializer(
            chat_users, many=True, context={"request": request}
        )
        return response.Response(serializer.data, status=status.HTTP_200_OK)


class NotificationViewSet(viewsets.ModelViewSet):
    """
    A viewset that provides CRUD operations for the Notification model,
    including additional actions to mark notifications as read.
    """
    serializer_class = NotificationSerializer
    lookup_field = "id"

    def get_queryset(self):
        return Notification.objects.filter(receiver=self.request.user)

    @action(detail=True, methods=["post"])
    def mark_as_read(self, request, id=None):
        """
        Mark a specific notification as read.
        
        URL Params:
            - id: The ID of the notification to mark as read.
        
        Returns:
            - Success message indicating the notification has been marked as read.
        """
        notification = Notification.objects.get(id=id)
        notification.seen = True
        notification.save()
        return response.Response(data="notification", status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"])
    def mark_all_as_read(self, request):
        """
        Mark all notifications for the current user as read.
        
        Returns:
            - Success message indicating all notifications have been marked as read.
        """
        notification = self.get_queryset()
        notification.update(seen=True)
        return response.Response(
            data="All notification marked as read", status=status.HTTP_200_OK
        )

    def destroy(self, request, id):
        """
        Delete a specific notification.
        
        URL Params:
            - id: The ID of the notification to delete.
        
        Returns:
            - No content response indicating successful deletion.
        """
        instance = self.get_object()
        self.perform_destroy(instance)
        return response.Response(status=status.HTTP_204_NO_CONTENT)
