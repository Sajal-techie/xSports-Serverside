from rest_framework import generics,views,response,status,viewsets
from django.db.models import Q
from rest_framework.decorators import action
from .models import Chat, Users, Notification
from .serializers import ChatSerializer,ChatListUserSerializer, NotificationSerializer


class ChatView(generics.ListCreateAPIView):
    serializer_class = ChatSerializer
    queryset = Chat.objects.all()

    def list(self, request, *args, **kwargs):
        thread_name = request.query_params.get('threadName')
        queryset = Chat.objects.filter(thread_name=thread_name).select_related('sender').order_by('date')
        print(thread_name, queryset)
        serializer = self.get_serializer(queryset, many=True)
        print('in list',serializer.data)
        return response.Response(data=serializer.data, status=status.HTTP_200_OK)

    # to create new thread name or fetch existing thread name
    def create(self, request, *args, **kwargs):
        print(request.user,request.data,args,kwargs)
        sender_id = request.data.get('sender_id', None)
        receiver_id = request.data.get('receiver_id', None)
        print(sender_id,receiver_id)
        user_ids = sorted([sender_id,receiver_id])
        thread_name = f"chat_{user_ids[0]}_{user_ids[1]}"
        print(user_ids,thread_name,'useid thread name')

        existing_chat = Chat.objects.filter(
            thread_name=thread_name
        ).first()

        if not existing_chat:

            sender = Users.objects.get(id=sender_id)
            receiver = Users.objects.get(id=receiver_id)
            Chat.objects.create(
                sender=sender,
                receiver=receiver,
                thread_name=thread_name,
            )
        return response.Response({'thread_name':thread_name})
    

class ChatListView(views.APIView):
    def get(self, request):
        current_user = request.user

        # Get unique users the current user has chatted with
        chat_users = Users.objects.filter(
            Q(send_message__receiver=current_user) | 
            Q(receive_message__sender=current_user)
        ).distinct()

        serializer = ChatListUserSerializer(chat_users, many=True,  context={'request': request})
        return response.Response(serializer.data, status=status.HTTP_200_OK)
    

class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    lookup_field = 'id'

    def get_queryset(self):
        return Notification.objects.filter(receiver=self.request.user)
    
    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, id=None):
        notification = Notification.objects.get(id=id)
        notification.seen = True
        notification.save()
        return response.Response(data='notification',status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'])
    def mark_all_as_read(self, request):
        notification = self.get_queryset()
        print(notification)
        notification.update(seen=True)
        return response.Response(data="All notification marked as read", status=status.HTTP_200_OK)
    
    def destroy(self, request, id, *args, **kwargs):
        print(id)
        instance = self.get_object()
        self.perform_destroy(instance)
        return response.Response(status=status.HTTP_204_NO_CONTENT)
    