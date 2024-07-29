from rest_framework import generics,views,response,status
from django.db.models import Q
from .models import Chat,Users
from .serializers import ChatSerializer,ChatListUserSerializer


class ChatView(generics.ListCreateAPIView):
    serializer_class = ChatSerializer
    queryset = Chat.objects.all()

    # def get_queryset(self):
    #     print('in getquery set')
    #     thread_name = self.request.query_params.get('threadName')
    #     return 

    def list(self, request, *args, **kwargs):
        thread_name = request.query_params.get('threadName')
        queryset = Chat.objects.filter(thread_name=thread_name).exclude(message__isnull=True).select_related('sender').order_by('date')
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